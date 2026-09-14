"""Privacy auditor.

The regexes here were calibrated against real repositories after an uncalibrated
version produced 18 false positives that drowned the real findings. Every
"must NOT flag" case below is a real line from production code — they are the point
of this file, not filler.
"""

import re

import pytest

from conftest import matches, types_of


# --------------------------------------------------------------------------- #
# Blind logging
# --------------------------------------------------------------------------- #

BLIND_POSITIVES = [
    'log.Printf("payload: %+v", req)',
    'logger.Infof("user %v", user)',
    'fmt.Sprintf("%#v", customer)',
    "console.log(req.body)",
    "logger.info(payload.model_dump())",
]

# Idiomatic code that must stay quiet. A %v on a scalar is ordinary Go; flagging it
# makes the auditor unusable on any real codebase.
BLIND_NEGATIVES = [
    'return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])',
    'log.Printf("listening on %v", addr)',
    'fmt.Errorf("parse: %w", err)',
    'log.Println("done")',
]


@pytest.mark.parametrize("line", BLIND_POSITIVES)
def test_blind_logging_flags_sensitive_serialization(audit_privacy, line):
    assert matches(audit_privacy.BLIND_LOGGING_PATTERNS, line)


@pytest.mark.parametrize("line", BLIND_NEGATIVES)
def test_blind_logging_ignores_idiomatic_formatting(audit_privacy, line):
    assert not matches(audit_privacy.BLIND_LOGGING_PATTERNS, line)


# --------------------------------------------------------------------------- #
# PII in URLs
# --------------------------------------------------------------------------- #

URL_POSITIVES = [
    'url += "?token=" + t',
    "`/x?email=${e}`",
    "?email=foo",
    'fetch("/api?cpf=" + doc)',
]

URL_NEGATIVES = [
    "/users?id=3",
    "?page=2&limit=50",
]


@pytest.mark.parametrize("line", URL_POSITIVES)
def test_pii_in_url_flags_interpolation(audit_privacy, line):
    """The earlier pattern required a word char after '=', missing every
    interpolated form — which is how the bug actually appears in JS."""
    assert matches(audit_privacy.QUERY_PII_PATTERNS, line, re.IGNORECASE)


@pytest.mark.parametrize("line", URL_NEGATIVES)
def test_pii_in_url_ignores_benign_params(audit_privacy, line):
    assert not matches(audit_privacy.QUERY_PII_PATTERNS, line, re.IGNORECASE)


# --------------------------------------------------------------------------- #
# Metric labels
# --------------------------------------------------------------------------- #

METRIC_POSITIVES = [
    '[]string{"method","path","user_id"}',
    "WithLabelValues(c.Request.URL.Path, m)",
    'labels: ["email", "count"]',
]

METRIC_NEGATIVES = [
    '[]string{"method","path","status"}',
    "WithLabelValues(c.FullPath(), method)",
]


@pytest.mark.parametrize("line", METRIC_POSITIVES)
def test_metric_labels_flag_pii_and_raw_path(audit_privacy, line):
    assert matches(audit_privacy.METRIC_PII_PATTERNS, line, re.IGNORECASE)


@pytest.mark.parametrize("line", METRIC_NEGATIVES)
def test_metric_labels_allow_route_template(audit_privacy, line):
    """c.FullPath() is the correct form — it must never be flagged."""
    assert not matches(audit_privacy.METRIC_PII_PATTERNS, line, re.IGNORECASE)


# --------------------------------------------------------------------------- #
# Scope rules
# --------------------------------------------------------------------------- #

def test_test_files_are_skipped(audit_privacy, tree):
    """A sample phone in an expected URL is a fixture, not a leak."""
    root = tree({
        "src/notificationUi.spec.js": "expect(isWhatsAppUrl('https://wa.me/send?phone=5511999999999'))\n",
    })
    assert audit_privacy.audit(root)["issues_count"] == 0


def test_production_file_with_same_content_is_flagged(audit_privacy, tree):
    """Guards the test-file skip: identical content outside a test must still fire."""
    root = tree({"src/notificationUi.js": "const u = '/send?phone=' + p\n"})
    assert audit_privacy.audit(root)["issues_count"] > 0


def test_worktree_directories_are_ignored(audit_privacy, tree):
    """Worktrees are checkouts of the same repo — counting them multiplies findings."""
    leak = "const u = '?token=' + t\n"
    root = tree({
        "app/src/a.js": leak,
        "app-worktrees/branch-x/src/a.js": leak,
        "worktrees/branch-y/src/a.js": leak,
    })
    assert audit_privacy.audit(root)["issues_count"] == 1


# --------------------------------------------------------------------------- #
# Impersonation
# --------------------------------------------------------------------------- #

GUARDED_MIDDLEWARE = """
package middlewares
func ImpersonationReadOnly() gin.HandlerFunc {
    logger.Log.Info("impersonated request", zap.String("impersonator_id", impID))
    if c.Request.Method != http.MethodGet {
        c.AbortWithStatusJSON(http.StatusForbidden, gin.H{"error": "read-only"})
    }
}
"""

BARE_HANDLER = """
package admin
func StartImpersonation(c *gin.Context) {
    token := issueToken(c.Param("user_id"))
    c.JSON(200, token)
}
"""


def test_impersonation_evaluated_across_the_feature(audit_privacy, tree):
    """The guard lives in the middleware while the handler is a separate file.

    A per-file check flags the handler for something that is not its job.
    """
    root = tree({
        "middlewares/impersonate.go": GUARDED_MIDDLEWARE,
        "controllers/admin/impersonate_handler.go": BARE_HANDLER,
    })
    findings = audit_privacy.audit_impersonation(root)
    assert findings == []


def test_impersonation_without_guard_is_flagged(audit_privacy, tree):
    root = tree({"controllers/impersonate_handler.go": BARE_HANDLER})
    findings = audit_privacy.audit_impersonation(root)
    assert "Impersonation Safety" in types_of(findings)
    assert any("read-only" in f["description"] for f in findings)
    assert any("audit trail" in f["description"] for f in findings)


def test_no_impersonation_code_means_no_findings(audit_privacy, tree):
    root = tree({"src/app.go": "package main\n"})
    assert audit_privacy.audit_impersonation(root) == []


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #

def test_paths_are_relative_not_absolute(audit_privacy, tree):
    """Absolute paths leak the developer's home directory into the runlog."""
    root = tree({"src/a.js": "const u = '?token=' + t\n"})
    for issue in audit_privacy.audit(root)["issues"]:
        assert not issue["file"].startswith("/")
        assert issue["file"].startswith("src/")


def test_clean_tree_scores_100(audit_privacy, tree):
    root = tree({"src/a.js": "export const x = 1\n"})
    result = audit_privacy.audit(root)
    assert result["issues_count"] == 0
    assert result["score"] == 100
    assert result["verdict"] == "PASS"
