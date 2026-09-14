"""Clube AI Marketplace CLI."""

from __future__ import annotations

import json
from pathlib import Path

_PACKAGE_JSON = Path(__file__).resolve().parent.parent / "package.json"


def _read_version() -> str:
    """The single source of truth for the version is package.json.

    Hardcoding it here would add one more declaration to keep in sync — and one the
    SemVer parity check does not cover, so it would drift silently.
    """
    try:
        with open(_PACKAGE_JSON, "r", encoding="utf-8") as handle:
            return json.load(handle).get("version") or "0.0.0"
    except Exception:
        return "0.0.0"


__version__ = _read_version()
