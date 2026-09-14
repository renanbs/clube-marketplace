"""Shared fixtures.

Two things every test module needs:

1. **Importing hyphenated modules.** The auditors are named `audit-seo.py` and friends,
   which is not a valid Python identifier, so a plain import cannot reach them. They
   are loaded by path through importlib instead.

2. **Throwaway source trees.** Every auditor walks a directory, so the tests build
   small fixture repositories in tmp_path rather than asserting against this
   repository — which would make them fail whenever the repo legitimately changes.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "plugins" / "clube" / "scripts"

# So `import clube_cli` works without installing the package.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_script(filename):
    path = SCRIPTS_DIR / filename
    if not path.is_file():
        pytest.skip(f"audit script not found: {path}")
    # The auditors do `import ui`, resolved via their own directory.
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    module_name = "clube_audit_" + filename.replace("-", "_").removesuffix(".py")
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def ui():
    return _load_script("ui.py")


@pytest.fixture(scope="session")
def audit_seo():
    return _load_script("audit-seo.py")


@pytest.fixture(scope="session")
def audit_tracking():
    return _load_script("audit-tracking.py")


@pytest.fixture(scope="session")
def audit_performance():
    return _load_script("audit-performance.py")


@pytest.fixture(scope="session")
def audit_privacy():
    return _load_script("audit-privacy.py")


@pytest.fixture
def tree(tmp_path):
    """Materialise a {relative_path: content} mapping and return the root."""

    def _build(files):
        for rel_path, content in files.items():
            full = tmp_path / rel_path
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(content, encoding="utf-8")
        return str(tmp_path)

    return _build


def types_of(findings):
    """Set of the `type` field across findings — the usual assertion target."""
    return {f.get("type") for f in findings}


def matches(patterns, text, flags=0):
    """True when any (pattern, description) pair matches text."""
    import re

    return any(re.search(pattern, text, flags) for pattern, _ in patterns)
