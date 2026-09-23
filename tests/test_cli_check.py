"""Repository validator.

The bash original could not fail: counters were incremented and never read, and the
success line printed unconditionally. Each scenario below passed with exit 0 before
the port — they are the regression guard for the gate itself.
"""

import json

import pytest

from clube_cli import check

AGENT_OK = """---
name: expert-seo
description: Specialist agent.
tools: Read, Grep
model: inherit
readonly: true
---

Body.
"""

AGENT_MISSING_FIELDS = """---
name: quebrado
---

Body.
"""

AGENT_NO_FRONTMATTER = """# Just a heading

name: sneaky
description: in the body
tools: none
model: none
readonly: false
"""


def build_repo(root, *, version="0.2.0", skills=None, agents=None):
    """Materialise a minimal but structurally valid marketplace repo."""
    for manifest in check.MARKET_MANIFESTS:
        path = root / manifest
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"plugins": [{"name": "clube", "version": version}]}), encoding="utf-8")

    (root / "package.json").write_text(json.dumps({"version": version}), encoding="utf-8")

    plugin = root / "plugins" / "clube"
    for manifest in check.PLUGIN_MANIFESTS:
        path = plugin / manifest
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"version": version}), encoding="utf-8")

    for name, files in (skills or {}).items():
        for rel, content in files.items():
            path = plugin / "skills" / name / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    for name, content in (agents or {}).items():
        path = plugin / "agents" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    # OpenCode integration: adapters + configs, mirroring what a real repo ships.
    opencode_catalog = root / ".opencode-plugin/marketplace.json"
    plugin_names = [
        entry["name"] for entry in json.loads(opencode_catalog.read_text(encoding="utf-8"))["plugins"]
    ]
    for name in plugin_names:
        adapter = root / ".opencode" / "plugins" / name / "index.ts"
        adapter.parent.mkdir(parents=True, exist_ok=True)
        adapter.write_text("export default { id: 'placeholder' }\n", encoding="utf-8")

    agents_config = {
        name: {"mode": "subagent", "system": f"./plugins/clube/agents/{name}"}
        for name in (agents or {})
    }
    config = {
        "plugins": [f"./.opencode/plugins/{name}" for name in plugin_names],
        "agents": agents_config,
    }
    (root / "opencode.json").write_text(json.dumps(config), encoding="utf-8")
    (root / ".opencode" / "opencode.json").write_text(json.dumps(config), encoding="utf-8")

    return root


VERTICAL_SKILL = {
    "SKILL.md": "# Skill\n\nSee [Guide](references/guide.md).\n",
    "references/guide.md": "# Guide\n",
}


def test_valid_repository_has_no_problems(tmp_path):
    build_repo(tmp_path, skills={"saas-seo-geo": VERTICAL_SKILL}, agents={"a.md": AGENT_OK})
    _, problems = check.check_repository(tmp_path)
    assert problems == []


# --------------------------------------------------------------------------- #
# Skills
# --------------------------------------------------------------------------- #

def test_broken_reference_link_is_detected(tmp_path):
    """Deleting a guide used to only change a count; the gate stayed green.

    A broken link makes the deep guide unreachable with no error at all.
    """
    build_repo(tmp_path, skills={"saas-seo-geo": {
        "SKILL.md": "# Skill\n\nSee [Guide](references/missing.md).\n",
        "references/other.md": "# Other\n",
    }})
    _, problems = check.check_repository(tmp_path)
    assert any("Broken reference link" in p.message for p in problems)


def test_orphaned_reference_is_detected(tmp_path):
    build_repo(tmp_path, skills={"saas-seo-geo": {
        "SKILL.md": "# Skill\n\nSee [Guide](references/guide.md).\n",
        "references/guide.md": "# Guide\n",
        "references/orphan.md": "# Nobody links here\n",
    }})
    _, problems = check.check_repository(tmp_path)
    assert any("Orphaned reference" in p.message for p in problems)


def test_new_vertical_skill_without_references_is_detected(tmp_path):
    """The bash version listed the four known skills by name, so a fifth escaped."""
    build_repo(tmp_path, skills={"nova-vertical": {"SKILL.md": "# New\n"}})
    _, problems = check.check_repository(tmp_path)
    assert any("Missing references/" in p.message and "nova-vertical" in p.message
               for p in problems)


@pytest.mark.parametrize("exempt", sorted(check.SKILLS_WITHOUT_REFERENCES))
def test_exempt_skills_may_omit_references(tmp_path, exempt):
    build_repo(tmp_path, skills={exempt: {"SKILL.md": "# Infra skill\n"}})
    _, problems = check.check_repository(tmp_path)
    assert not any("Missing references/" in p.message for p in problems)


def test_flat_skill_file_is_detected(tmp_path):
    root = build_repo(tmp_path)
    flat = root / "plugins" / "clube" / "skills" / "loose.md"
    flat.parent.mkdir(parents=True, exist_ok=True)
    flat.write_text("# flat\n", encoding="utf-8")
    _, problems = check.check_repository(tmp_path)
    assert any("Non-standard flat skill" in p.message for p in problems)


# --------------------------------------------------------------------------- #
# Agent frontmatter
# --------------------------------------------------------------------------- #

def test_agent_missing_fields_is_detected(tmp_path):
    build_repo(tmp_path, agents={"BROKEN.md": AGENT_MISSING_FIELDS})
    _, problems = check.check_repository(tmp_path)
    assert any("missing field(s)" in p.message for p in problems)


def test_frontmatter_fields_must_be_inside_the_block(tmp_path):
    """Grepping the whole file let a body line starting with 'name:' satisfy the check."""
    build_repo(tmp_path, agents={"SNEAKY.md": AGENT_NO_FRONTMATTER})
    _, problems = check.check_repository(tmp_path)
    assert any("no YAML frontmatter block" in p.message for p in problems)


def test_unterminated_frontmatter_is_rejected(tmp_path):
    build_repo(tmp_path, agents={"OPEN.md": "---\nname: x\ndescription: y\n"})
    _, problems = check.check_repository(tmp_path)
    assert any("no YAML frontmatter block" in p.message for p in problems)


def test_agent_missing_fields_names_them(tmp_path):
    missing = check.agent_missing_fields(AGENT_MISSING_FIELDS)
    assert missing == ["description", "tools", "model", "readonly"]


def test_valid_agent_has_no_missing_fields(tmp_path):
    assert check.agent_missing_fields(AGENT_OK) == []


# --------------------------------------------------------------------------- #
# SemVer parity
# --------------------------------------------------------------------------- #

def test_semver_parity_passes_when_aligned(tmp_path):
    build_repo(tmp_path, version="0.2.0")
    target, matched, total, problems = check.check_semver_parity(tmp_path)
    assert (target, matched, total, problems) == ("0.2.0", total, total, [])


def test_semver_target_is_derived_from_package_json(tmp_path):
    """No hardcoded version: cutting a release must not require editing the validator."""
    build_repo(tmp_path, version="9.9.9")
    target, _, _, problems = check.check_semver_parity(tmp_path)
    assert target == "9.9.9"
    assert problems == []


def test_semver_mismatch_is_detected(tmp_path):
    root = build_repo(tmp_path, version="0.2.0")
    (root / "plugins" / "clube" / ".codex-plugin" / "plugin.json").write_text(
        json.dumps({"version": "0.1.0"}), encoding="utf-8"
    )
    _, _, _, problems = check.check_semver_parity(tmp_path)
    assert any("found '0.1.0'" in p.message for p in problems)


def test_missing_manifest_is_detected(tmp_path):
    root = build_repo(tmp_path)
    (root / ".claude-plugin" / "marketplace.json").unlink()
    _, problems = check.check_repository(tmp_path)
    assert any("Missing marketplace catalog" in p.message for p in problems)


# --------------------------------------------------------------------------- #
# Per-plugin versioning
# --------------------------------------------------------------------------- #

def add_plugin(root, name, version, *, catalog_version=None, listed=True):
    """Add a second plugin with its own version, optionally listed in every catalog."""
    plugin = root / "plugins" / name
    for manifest in check.PLUGIN_MANIFESTS:
        path = plugin / manifest
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"version": version}), encoding="utf-8")
    if listed:
        for manifest in check.MARKET_MANIFESTS:
            path = root / manifest
            data = json.loads(path.read_text(encoding="utf-8"))
            data["plugins"].append({"name": name, "version": catalog_version or version})
            path.write_text(json.dumps(data), encoding="utf-8")
        adapter = root / ".opencode" / "plugins" / name / "index.ts"
        adapter.parent.mkdir(parents=True, exist_ok=True)
        adapter.write_text("export default { id: 'placeholder' }\n", encoding="utf-8")
    return plugin


def test_independently_versioned_plugin_is_valid(tmp_path):
    """A second plugin on its own version must not trip the repo-wide parity check."""
    root = build_repo(tmp_path, version="0.3.0")
    add_plugin(root, "code-review", "0.1.0")
    report, problems = check.check_repository(root)
    assert problems == []
    assert report["plugins"]["code-review"]["version"] == "0.1.0"


def test_plugin_missing_from_catalog_is_detected(tmp_path):
    root = build_repo(tmp_path)
    add_plugin(root, "code-review", "0.1.0", listed=False)
    _, problems = check.check_repository(root)
    missing = [p for p in problems if "not listed in" in p.message]
    assert len(missing) == len(check.MARKET_MANIFESTS)
    assert all(p.plugin == "code-review" for p in missing)


def test_catalog_version_drift_is_detected(tmp_path):
    root = build_repo(tmp_path)
    add_plugin(root, "code-review", "0.1.0", catalog_version="0.0.9")
    _, problems = check.check_repository(root)
    assert any("lists '0.0.9', manifests declare '0.1.0'" in p.message for p in problems)


def test_plugin_manifests_disagreeing_is_detected(tmp_path):
    root = build_repo(tmp_path)
    plugin = add_plugin(root, "code-review", "0.1.0")
    (plugin / ".omp-plugin/plugin.json").write_text(json.dumps({"version": "0.2.0"}), encoding="utf-8")
    _, problems = check.check_repository(root)
    assert any("plugin manifests disagree" in p.message for p in problems)


def test_repo_parity_ignores_catalog_order(tmp_path):
    """Parity used to read plugins[0]; listing another plugin first broke it spuriously."""
    root = build_repo(tmp_path, version="0.3.0")
    add_plugin(root, "code-review", "0.1.0")
    for manifest in check.MARKET_MANIFESTS:
        path = root / manifest
        data = json.loads(path.read_text(encoding="utf-8"))
        data["plugins"].reverse()
        path.write_text(json.dumps(data), encoding="utf-8")
    _, problems = check.check_repository(root)
    assert problems == []


def test_problems_are_attributed_to_their_plugin(tmp_path):
    """The CLI prints problems under each plugin; unattributed ones leaked into every plugin."""
    root = build_repo(tmp_path, agents={"BROKEN.md": AGENT_MISSING_FIELDS})
    add_plugin(root, "code-review", "0.1.0")
    _, problems = check.check_repository(root)
    agent_problems = [p for p in problems if p.kind == "agent"]
    assert agent_problems and all(p.plugin == "clube" for p in agent_problems)


# --------------------------------------------------------------------------- #
# Structure
# --------------------------------------------------------------------------- #

def test_missing_plugins_directory_is_detected(tmp_path):
    (tmp_path / "package.json").write_text(json.dumps({"version": "0.2.0"}), encoding="utf-8")
    _, problems = check.check_repository(tmp_path)
    assert any("Missing plugins/ directory" in p.message for p in problems)


def test_parse_frontmatter_returns_none_without_delimiters(tmp_path):
    assert check.parse_frontmatter("# heading\nname: x\n") is None


def test_referenced_links_are_deduplicated(tmp_path):
    text = "[a](references/g.md) and again [a](references/g.md) plus [b](references/h.md)"
    assert check.referenced_links(text) == ["references/g.md", "references/h.md"]


# --------------------------------------------------------------------------- #
# Version drift
# --------------------------------------------------------------------------- #

def test_package_version_is_the_only_source_of_truth():
    """A hardcoded __version__ is one more declaration to keep in sync, and one the
    parity check does not cover — so it drifts silently. It must be derived."""
    import json as _json

    import clube_cli

    declared = _json.loads(
        (cli_repo_root() / "package.json").read_text(encoding="utf-8")
    )["version"]
    assert clube_cli.__version__ == declared


def test_no_hardcoded_version_literal_in_the_package():
    """Guards the fix above: catches someone re-introducing a literal."""
    import re

    for path in (cli_repo_root() / "clube_cli").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert not re.search(r'__version__\s*=\s*["\']\d+\.\d+\.\d+["\']', text), path


def test_real_repository_semver_parity_holds():
    """The repository itself must pass its own parity check."""
    target, matched, total, problems = check.check_semver_parity(cli_repo_root())
    assert problems == []
    assert matched == total
    assert target


# --------------------------------------------------------------------------- #
# OpenCode integration
# --------------------------------------------------------------------------- #

def test_opencode_catalog_plugin_requires_adapter(tmp_path):
    """A plugin listed in the OpenCode catalog needs .opencode/plugins/<name>/index.ts."""
    root = build_repo(tmp_path)
    (root / ".opencode" / "plugins" / "clube" / "index.ts").unlink()
    _, problems = check.check_repository(root)
    assert any(
        "No OpenCode adapter" in p.message and "clube" in p.message
        for p in problems
    )


def test_opencode_agent_system_path_must_resolve(tmp_path):
    """OpenCode loads agent bodies from the canonical plugins/ files — dangling paths
    silently unload the agent, so the gate must resolve them."""
    root = build_repo(tmp_path, agents={"a.md": AGENT_OK})
    config = json.loads((root / "opencode.json").read_text(encoding="utf-8"))
    config["agents"]["expert-seo"] = {"mode": "subagent", "system": "./plugins/clube/agents/missing.md"}
    (root / "opencode.json").write_text(json.dumps(config), encoding="utf-8")
    _, problems = check.check_repository(root)
    assert any("system path not found" in p.message for p in problems)


def test_opencode_agent_requires_system(tmp_path):
    root = build_repo(tmp_path, agents={"a.md": AGENT_OK})
    config = json.loads((root / "opencode.json").read_text(encoding="utf-8"))
    config["agents"]["expert-seo"] = {"mode": "subagent"}
    (root / "opencode.json").write_text(json.dumps(config), encoding="utf-8")
    _, problems = check.check_repository(root)
    assert any("has no system path" in p.message for p in problems)


def test_opencode_config_must_parse(tmp_path):
    root = build_repo(tmp_path)
    (root / ".opencode" / "opencode.json").write_text("{not json", encoding="utf-8")
    _, problems = check.check_repository(root)
    assert any("opencode.json" in p.message for p in problems)


def test_opencode_configs_cannot_be_missing(tmp_path):
    root = build_repo(tmp_path)
    (root / "opencode.json").unlink()
    (root / ".opencode" / "opencode.json").unlink()
    _, problems = check.check_repository(root)
    missing = [p for p in problems if "Missing OpenCode config" in p.message]
    assert len(missing) == len(check.OPCODE_CONFIG_FILES)


def test_real_repository_opencode_integration_passes():
    """The repository itself ships working OpenCode adapters for every catalog plugin
    and every agent system path resolves."""
    assert check.check_opencode_integration(cli_repo_root()) == []


def test_second_plugin_requires_its_own_adapter(tmp_path):
    root = build_repo(tmp_path)
    add_plugin(root, "code-review", "0.1.0")
    (root / ".opencode" / "plugins" / "code-review" / "index.ts").unlink()
    _, problems = check.check_repository(root)
    assert any("code-review" in p.message and "No OpenCode adapter" in p.message
               for p in problems)


def cli_repo_root():
    from pathlib import Path

    return Path(__file__).resolve().parent.parent
