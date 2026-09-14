"""Repository integrity audit. Port of cmd_check from bin/clube-config.

The shell version's central defect was that it could not fail: counters were
incremented and never read, and the success line printed unconditionally. Here every
check returns structured `Problem` records, the caller counts them, and the exit code
is derived from that count — so the gate is falsifiable by construction.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

MARKET_MANIFESTS = (
    ".claude-plugin/marketplace.json",
    ".omp-plugin/marketplace.json",
    ".cursor-plugin/marketplace.json",
    ".agents/plugins/marketplace.json",
)

PLUGIN_MANIFESTS = (
    ".claude-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".omp-plugin/plugin.json",
)

# Manifests that must all agree on one version. (path, kind) — "market" catalogs carry
# the version inside plugins[0] rather than at the top level.
VERSIONED_MANIFESTS = (
    ("package.json", "root"),
    (".claude-plugin/marketplace.json", "market"),
    (".omp-plugin/marketplace.json", "market"),
    (".cursor-plugin/marketplace.json", "market"),
    (".agents/plugins/marketplace.json", "market"),
    ("plugins/clube/.claude-plugin/plugin.json", "plugin"),
    ("plugins/clube/.cursor-plugin/plugin.json", "plugin"),
    ("plugins/clube/.codex-plugin/plugin.json", "plugin"),
    ("plugins/clube/.omp-plugin/plugin.json", "plugin"),
)

# Skills that legitimately ship without a references/ subdirectory. Stated as an
# exemption list rather than an allowlist of vertical skills, so a newly added vertical
# skill is covered by default instead of silently escaping the check.
SKILLS_WITHOUT_REFERENCES = frozenset({"init", "clube-architecture"})

AGENT_REQUIRED_FIELDS = ("name", "description", "tools", "model", "readonly")

REFERENCE_LINK_RE = re.compile(r"\((references/[^)]+\.md)\)")


@dataclass(frozen=True)
class Problem:
    kind: str
    message: str


def read_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_frontmatter(text):
    """Return the raw frontmatter block, or None when the file has none.

    Reads only between the opening and closing `---`. Grepping the whole file (as the
    shell version did) lets a body line starting with "name:" satisfy the check and
    says nothing about the delimiters existing at all.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    body = []
    for line in lines[1:]:
        if line.strip() == "---":
            return "\n".join(body)
        body.append(line)
    return None  # unterminated block


def agent_missing_fields(text, required=AGENT_REQUIRED_FIELDS):
    """Fields absent from the agent's frontmatter. None means there is no frontmatter."""
    frontmatter = parse_frontmatter(text)
    if frontmatter is None:
        return None
    present = {
        match.group(1)
        for match in re.finditer(r"^([A-Za-z_][\w-]*):", frontmatter, re.MULTILINE)
    }
    return [field for field in required if field not in present]


def referenced_links(skill_md_text):
    """Reference paths the entrypoint links to, deduplicated and ordered."""
    seen = []
    for match in REFERENCE_LINK_RE.finditer(skill_md_text):
        link = match.group(1)
        if link not in seen:
            seen.append(link)
    return seen


def check_skill(skill_dir):
    """Validate one skill directory. Returns a list of Problem."""
    skill_dir = Path(skill_dir)
    name = skill_dir.name
    skill_md = skill_dir / "SKILL.md"
    problems = []

    if not skill_md.is_file():
        return [Problem("skill", f"Missing SKILL.md in skill directory: {name}")]

    references_dir = skill_dir / "references"
    if not references_dir.is_dir():
        if name not in SKILLS_WITHOUT_REFERENCES:
            problems.append(
                Problem("skill", f"Missing references/ directory in vertical skill: {name}")
            )
        return problems

    text = skill_md.read_text(encoding="utf-8", errors="ignore")
    links = referenced_links(text)

    # Progressive disclosure only works while the links resolve. A broken link makes the
    # deep guide unreachable with no error at all: the entrypoint promises knowledge
    # that never loads, and the agent proceeds on the shallow version.
    for link in links:
        if not (skill_dir / link).is_file():
            problems.append(
                Problem("skill", f"Broken reference link in {name}/SKILL.md: {link}")
            )

    # An unreferenced guide is dead weight the entrypoint never routes to.
    for reference in sorted(references_dir.glob("*.md")):
        if reference.name not in text:
            problems.append(
                Problem(
                    "skill",
                    f"Orphaned reference (not linked from SKILL.md): {name}/references/{reference.name}",
                )
            )

    return problems


def check_agent(agent_path):
    agent_path = Path(agent_path)
    text = agent_path.read_text(encoding="utf-8", errors="ignore")
    missing = agent_missing_fields(text)
    if missing is None:
        return [Problem("agent", f"Agent has no YAML frontmatter block: {agent_path.name}")]
    if missing:
        return [
            Problem(
                "agent",
                f"Agent frontmatter missing field(s) in {agent_path.name}: {' '.join(missing)}",
            )
        ]
    return []


def manifest_version(path, kind):
    """Extract the declared version, or None when absent/unreadable."""
    data = read_json(path)
    if kind in ("root", "plugin"):
        return data.get("version")
    plugins = data.get("plugins")
    if isinstance(plugins, list) and plugins and isinstance(plugins[0], dict):
        version = plugins[0].get("version")
        if version:
            return version
    return data.get("version")


def check_semver_parity(repo_root, target_version=None):
    """All versioned manifests must agree.

    When no target is given it is taken from the root package.json rather than
    hardcoded, so cutting a release does not require editing the validator.
    Returns (target_version, matched, total, [Problem]).
    """
    repo_root = Path(repo_root)
    problems = []

    if target_version is None:
        try:
            target_version = manifest_version(repo_root / "package.json", "root")
        except Exception:
            target_version = None
        if not target_version:
            return (None, 0, len(VERSIONED_MANIFESTS), [
                Problem("semver", "Cannot determine target version from package.json")
            ])

    matched = 0
    for rel_path, kind in VERSIONED_MANIFESTS:
        full = repo_root / rel_path
        if not full.is_file():
            problems.append(Problem("semver", f"Missing file: {rel_path}"))
            continue
        try:
            found = manifest_version(full, kind)
        except Exception as exc:
            problems.append(Problem("semver", f"{rel_path} ({exc})"))
            continue
        if found == target_version:
            matched += 1
        else:
            problems.append(
                Problem("semver", f"{rel_path} (found '{found}', expected '{target_version}')")
            )

    return (target_version, matched, len(VERSIONED_MANIFESTS), problems)


def check_repository(repo_root):
    """Run every structural check. Returns (report, [Problem])."""
    repo_root = Path(repo_root)
    problems = []
    report = {
        "market_manifests": {},
        "plugins": {},
        "semver": {},
    }

    for manifest in MARKET_MANIFESTS:
        present = (repo_root / manifest).is_file()
        report["market_manifests"][manifest] = present
        if not present:
            problems.append(Problem("catalog", f"Missing marketplace catalog: {manifest}"))

    plugins_dir = repo_root / "plugins"
    if not plugins_dir.is_dir():
        problems.append(Problem("plugins", "Missing plugins/ directory"))
    else:
        plugin_dirs = sorted(p for p in plugins_dir.iterdir() if p.is_dir())
        if not plugin_dirs:
            problems.append(Problem("plugins", "No plugins found in plugins/ directory"))

        for plugin in plugin_dirs:
            entry = {
                "manifests": {m: (plugin / m).is_file() for m in PLUGIN_MANIFESTS},
                "skills": 0,
                "references": 0,
                "agents": 0,
                "invalid_agents": 0,
                "commands": 0,
            }

            skills_dir = plugin / "skills"
            if skills_dir.is_dir():
                for skill in sorted(skills_dir.iterdir()):
                    if skill.is_dir():
                        entry["skills"] += 1
                        refs = skill / "references"
                        if refs.is_dir():
                            entry["references"] += len(list(refs.glob("*.md")))
                        problems.extend(check_skill(skill))
                    elif skill.is_file() and skill.suffix == ".md":
                        problems.append(
                            Problem(
                                "skill",
                                f"Non-standard flat skill: {skill.name} (expected: skills/<name>/SKILL.md)",
                            )
                        )

            agents_dir = plugin / "agents"
            if agents_dir.is_dir():
                for agent in sorted(agents_dir.glob("*.md")):
                    agent_problems = check_agent(agent)
                    if agent_problems:
                        entry["invalid_agents"] += 1
                        problems.extend(agent_problems)
                    else:
                        entry["agents"] += 1

            commands_dir = plugin / "commands"
            if commands_dir.is_dir():
                entry["commands"] = len(list(commands_dir.glob("*.md")))

            report["plugins"][plugin.name] = entry

    target, matched, total, semver_problems = check_semver_parity(repo_root)
    report["semver"] = {"target": target, "matched": matched, "total": total}
    problems.extend(semver_problems)

    return report, problems
