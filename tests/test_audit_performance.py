"""Performance auditor: chunk recovery, edge cache, runtime, and migration safety."""

import pytest

from conftest import types_of

SPA_FILES = {
    "web/vite.config.js": "export default {}\n",
    "web/package.json": '{"dependencies": {"vue-router": "4.0.0", "vite": "5.0.0"}}\n',
}

ROUTER_ONLY_RECOVERY = """
export function installLazyRouteChunkRecovery(router) {
  const CHUNK_RELOAD_KEY = 'app:lazy_chunk_reload'
  router.onError((error, to) => {
    if (!isLazyRouteChunkLoadError(error)) return
    window.location.assign(to.fullPath)
  })
}
export function isLazyRouteChunkLoadError(e) { return true }
"""

FULL_RECOVERY = ROUTER_ONLY_RECOVERY + """
window.addEventListener('vite:preloadError', (event) => {
  event.preventDefault()
  window.location.assign(window.location.href)
})
"""


def test_spa_without_any_recovery_is_flagged(audit_performance, tree):
    root = tree(SPA_FILES)
    assert "SPA Deploy Resilience" in types_of(audit_performance.audit_chunk_recovery(root))


def test_router_only_recovery_is_flagged_as_incomplete(audit_performance, tree):
    """router.onError misses async child components inside an already mounted view —
    a modal that silently refuses to open after a deploy."""
    root = tree({**SPA_FILES, "web/src/chunkRecovery.js": ROUTER_ONLY_RECOVERY})
    findings = audit_performance.audit_chunk_recovery(root)
    assert "SPA Deploy Resilience" in types_of(findings)
    assert any("vite:preloadError" in f["description"] for f in findings)


def test_both_capture_points_pass(audit_performance, tree):
    root = tree({**SPA_FILES, "web/src/chunkRecovery.js": FULL_RECOVERY})
    assert audit_performance.audit_chunk_recovery(root) == []


def test_non_spa_project_is_not_flagged(audit_performance, tree):
    root = tree({"api/main.go": "package main\n"})
    assert audit_performance.audit_chunk_recovery(root) == []


# --------------------------------------------------------------------------- #
# Edge cache configuration — provider agnostic
# --------------------------------------------------------------------------- #

GOOD_VERCEL = """
{"headers": [
  {"source": "/index.html", "headers": [{"key": "Cache-Control", "value": "no-cache, no-store"}]},
  {"source": "/assets/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]}
]}
"""

GOOD_NGINX = """
location /assets/ { add_header Cache-Control "public, max-age=31536000, immutable"; }
location = /index.html { add_header Cache-Control "no-cache, no-store, must-revalidate"; }
"""


@pytest.mark.parametrize("path,content", [
    ("site/vercel.json", GOOD_VERCEL),
    ("site/nginx.conf", GOOD_NGINX),
])
def test_complete_edge_config_passes_for_any_provider(audit_performance, tree, path, content):
    assert audit_performance.audit_cache_headers(tree({path: content})) == []


def test_missing_immutable_is_flagged(audit_performance, tree):
    root = tree({"site/vercel.json": '{"headers": [{"key": "Cache-Control", "value": "no-cache"}]}'})
    findings = audit_performance.audit_cache_headers(root)
    assert any("immutable" in f["description"] for f in findings)


def test_edge_config_found_in_monorepo_subdirectory(audit_performance, tree):
    """Probing only the target root finds nothing when sites live in subdirectories."""
    root = tree({"code/site-lp/vercel.json": '{"cleanUrls": true}'})
    findings = audit_performance.audit_cache_headers(root)
    assert findings, "monorepo subdirectory config must still be audited"
    assert findings[0]["file"].startswith("code/site-lp")


# --------------------------------------------------------------------------- #
# Runtime and connection pool
# --------------------------------------------------------------------------- #

def test_go_without_automaxprocs_is_flagged(audit_performance, tree):
    root = tree({"api/go.mod": "module x\n", "api/main.go": "package main\nfunc main() {}\n"})
    assert "Container Runtime (Go)" in types_of(audit_performance.audit_backend_concurrency(root))


def test_unbounded_connection_pool_is_flagged(audit_performance, tree):
    """This check existed only in the docstring: the value was computed and discarded."""
    root = tree({
        "api/go.mod": "module x\n",
        "api/main.go": 'package main\nimport _ "go.uber.org/automaxprocs"\n',
    })
    assert "Database Connection Pool" in types_of(audit_performance.audit_backend_concurrency(root))


def test_bounded_pool_passes(audit_performance, tree):
    root = tree({
        "api/go.mod": "module x\n",
        "api/main.go": (
            'package main\nimport _ "go.uber.org/automaxprocs"\n'
            "func init() { db.SetMaxOpenConns(20) }\n"
        ),
    })
    assert audit_performance.audit_backend_concurrency(root) == []


def test_python_sqlalchemy_pool_is_audited(audit_performance, tree):
    root = tree({"api/pyproject.toml": '[project]\ndependencies = ["sqlalchemy"]\n'})
    assert "Database Connection Pool" in types_of(audit_performance.audit_backend_concurrency(root))


# --------------------------------------------------------------------------- #
# CREATE INDEX CONCURRENTLY
# --------------------------------------------------------------------------- #

BARE_CONCURRENTLY = """
-- +goose Up
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users (email);
"""

GOOSE_GUARDED = """
-- +goose Up
-- +goose NO TRANSACTION
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users (email);
"""

RAILS_GUARDED = """
class AddIndex < ActiveRecord::Migration[7.0]
  disable_ddl_transaction!
  def change
    execute "CREATE INDEX CONCURRENTLY idx_users_email ON users (email)"
  end
end
"""

DJANGO_GUARDED = """
class Migration(migrations.Migration):
    atomic = False
    operations = [migrations.RunSQL("CREATE INDEX CONCURRENTLY idx_u ON users (email)")]
"""


def test_concurrently_without_transaction_directive_is_flagged(audit_performance, tree):
    """Postgres refuses the statement inside a transaction block, and most migrators
    wrap every migration in one — so this fails at apply time with correct SQL."""
    root = tree({"migrations/0042_index.sql": BARE_CONCURRENTLY})
    findings = audit_performance.audit_concurrent_index_migrations(root)
    assert "Migration Safety" in types_of(findings)
    assert findings[0]["severity"] == "HIGH"


@pytest.mark.parametrize("path,content", [
    ("migrations/0042_index.sql", GOOSE_GUARDED),
    ("db/migrate/0042_index.rb", RAILS_GUARDED),
    ("migrations/0042_index.py", DJANGO_GUARDED),
])
def test_guarded_migrations_pass(audit_performance, tree, path, content):
    assert audit_performance.audit_concurrent_index_migrations(tree({path: content})) == []


def test_plain_create_index_is_not_flagged(audit_performance, tree):
    root = tree({"migrations/1.sql": "CREATE INDEX idx_a ON t (c);\n"})
    assert audit_performance.audit_concurrent_index_migrations(root) == []


def test_clean_tree_scores_100(audit_performance, tree):
    result = audit_performance.audit(tree({"README.md": "# hi\n"}))
    assert result["issues_count"] == 0
    assert result["score"] == 100
