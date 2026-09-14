"""AI host harness detection and profile persistence.

Port of scripts/lib-harness.sh. Detection order matters and is preserved from the
shell original: explicit environment markers first (cheapest and most reliable),
process-tree inspection only as a fallback.
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Ordered: the first harness whose environment markers are present wins.
ENV_MARKERS = [
    ("omp", ("OMPCODE", "ORCA_OMP_SOURCE_AGENT_DIR", "OMP_SESSION_ID", "OMP_VERSION", "OMP_AGENT")),
    ("antigravity", ("ANTIGRAVITY", "ANTIGRAVITY_SESSION")),
    ("cursor", ("CURSOR_PROJECT_DIR", "CURSOR_TRACE", "CURSOR_AGENT")),
    ("opencode", ("OPENCODE", "OPENCODE_SESSION")),
    ("claude-code", ("CLAUDE_CONVERSATION_ID",)),
]

# Process-name prefix -> harness, used only when no environment marker matched.
PROCESS_PREFIXES = [
    ("omp", "omp"),
    ("claude", "claude-code"),
    ("cursor", "cursor"),
    ("opencode", "opencode"),
]

FRIENDLY_NAMES = {
    "omp": "Oh My Pi (OMP) + Antigravity",
    "claude-code": "Claude Code (CLI)",
    "cursor": "Cursor (IDE / Agent)",
    "antigravity": "Google Antigravity",
    "opencode": "OpenCode",
}

DEFAULT_HARNESS = "generic-shell"
DEFAULT_FRIENDLY_NAME = "Generic Terminal / Shell"


def config_dir() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(Path.home(), ".config")
    return Path(base) / "clube-marketplace"


def profile_file() -> Path:
    return config_dir() / "harness-profile.json"


def detect_from_env(environ=None) -> str | None:
    """Return the harness implied by environment markers, or None."""
    env = os.environ if environ is None else environ
    for harness, markers in ENV_MARKERS:
        if any(env.get(marker) for marker in markers):
            return harness
    return None


def classify_process_name(name: str) -> str | None:
    """Map a process name to a harness by prefix, case-insensitively."""
    lowered = (name or "").strip().lower()
    for prefix, harness in PROCESS_PREFIXES:
        if lowered.startswith(prefix):
            return harness
    return None


def _ps_field(pid: int, field: str) -> str:
    try:
        out = subprocess.run(
            ["ps", "-o", f"{field}=", "-p", str(pid)],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return out.stdout.strip()
    except Exception:
        return ""


def detect_from_process_tree(pid: int | None = None, max_depth: int = 32) -> str | None:
    """Walk up the parent chain looking for a known harness process name.

    max_depth guards against a malformed ppid chain looping forever — the shell
    original relied on the pid reaching 1, which never terminates if ps fails.
    """
    current = os.getpid() if pid is None else pid
    for _ in range(max_depth):
        if current <= 1:
            break
        harness = classify_process_name(_ps_field(current, "comm"))
        if harness:
            return harness
        parent = _ps_field(current, "ppid")
        if not parent.isdigit():
            break
        current = int(parent)
    return None


def detect_active_harness() -> str:
    return detect_from_env() or detect_from_process_tree() or DEFAULT_HARNESS


def friendly_name(harness: str) -> str:
    return FRIENDLY_NAMES.get(harness, DEFAULT_FRIENDLY_NAME)


def _read_profile(path: Path | None = None) -> dict:
    target = profile_file() if path is None else path
    try:
        with open(target, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except Exception:
        # A missing or corrupt profile is not an error: the caller falls back to
        # defaults, exactly as the shell version did by swallowing grep failures.
        return {}


def saved_harness(path: Path | None = None) -> str:
    return _read_profile(path).get("harness") or "none"


def saved_model_role(role: str, path: Path | None = None) -> str:
    roles = _read_profile(path).get("roles")
    if isinstance(roles, dict) and roles.get(role):
        return roles[role]
    return "default"


def save_profile(harness, reasoning="default", code="default", critique="default",
                 security="default", path: Path | None = None) -> Path:
    target = profile_file() if path is None else Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "harness": harness,
        "roles": {
            "reasoning": reasoning,
            "code": code,
            "critique": critique,
            "security": security,
        },
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with open(target, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    return target
