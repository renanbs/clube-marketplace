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
        path.write_text(json.dumps({"plugins": [{"version": version}]}), encoding="utf-8")

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
