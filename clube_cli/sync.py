"""Harness pointer synchronization. Port of scripts/sync-harness-configs.sh.

For every AGENTS.md in the tree, ensure sibling harness files exist containing
`@AGENTS.md`, so AGENTS.md stays the single tool-agnostic source of truth.

A pointer file with any other content is never overwritten — it may be a hand-written
config predating this convention, and clobbering it would lose the user's work.
"""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_POINTERS = ("CLAUDE.md", "GEMINI.md", ".cursorrules")
POINTER_CONTENT = "@AGENTS.md"
PRUNED_DIRS = {"node_modules", ".git", ".specs"}


def find_agents_files(target_dir):
    """All AGENTS.md paths under target_dir, skipping pruned directories."""
    found = []
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in PRUNED_DIRS]
        if "AGENTS.md" in files:
            found.append(Path(root) / "AGENTS.md")
    return sorted(found)


def sync_pointers(target_dir, filenames=DEFAULT_POINTERS):
    """Create missing pointer files next to each AGENTS.md.

    Returns a dict with the created / aligned / preserved paths.
    """
    target = Path(target_dir)
    if not target.is_dir():
        raise NotADirectoryError(f"target directory does not exist: {target_dir}")

    result = {"created": [], "aligned": [], "preserved": []}

    for agents_md in find_agents_files(target):
        for filename in filenames:
            pointer = agents_md.parent / filename

            if not pointer.exists():
                pointer.write_text(POINTER_CONTENT + "\n", encoding="utf-8")
                result["created"].append(pointer)
                continue

            try:
                content = pointer.read_text(encoding="utf-8", errors="ignore").strip()
            except Exception:
                content = ""

            if content == POINTER_CONTENT:
                result["aligned"].append(pointer)
            else:
                result["preserved"].append(pointer)

    return result


AGENTS_TEMPLATE = """# Project AI Instructions

## Project Profile
- **Repository:** Project Name
- **Primary Stack:** (e.g., Go, Python, React, Vue, Node)
- **Single Source of Truth:** This AGENTS.md file is the authoritative AI configuration.

## Development Workflow
- Follow standardized conventions for testing, linting, and building.
- Verify changes before completion.
"""


def ensure_agents_md(target_dir):
    """Create the AGENTS.md template when absent. Returns True when created."""
    path = Path(target_dir) / "AGENTS.md"
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(AGENTS_TEMPLATE, encoding="utf-8")
    return True
