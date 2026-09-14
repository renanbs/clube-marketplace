"""Structured JSONL event log. Port of scripts/lib-runlog.sh.

Logging is best-effort: a broken state directory must never take down a command the
user actually asked for.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path


def state_dir() -> Path:
    base = os.environ.get("XDG_STATE_HOME") or os.path.join(Path.home(), ".local", "state")
    return Path(base) / "clube-marketplace"


def runs_dir() -> Path:
    return state_dir() / "runs"


def current_run_log() -> Path:
    return runs_dir() / "latest.jsonl"


def log_event(level="info", event="unknown", details="", path: Path | None = None) -> bool:
    """Append one event. Returns True when written, False when it could not be."""
    target = current_run_log() if path is None else Path(path)
    entry = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "level": level,
        "event": event,
        "details": details,
    }
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "a", encoding="utf-8") as handle:
            # json.dumps handles quoting; the shell version built the JSON by string
            # concatenation and produced invalid lines whenever details had a quote.
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return True
    except Exception:
        return False
