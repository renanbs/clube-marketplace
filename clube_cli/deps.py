"""Toolchain preflight.

Onboarding is where a missing dependency should surface. Without this, failures
appear late and cryptically — `make test` on a machine with neither uv nor pytest dies
with ModuleNotFoundError, and an old interpreter passes the launcher's `command -v
python3` only to fail at import time.

Requirements are declared as data so the checks stay testable and the install hints
live next to the condition they fix.
"""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from shutil import which

REPO_ROOT = Path(__file__).resolve().parent.parent
FALLBACK_MIN_PYTHON = (3, 10)


@dataclass(frozen=True)
class Dependency:
    name: str
    required: bool
    purpose: str
    install_hint: str


@dataclass(frozen=True)
class DependencyResult:
    dependency: Dependency
    ok: bool
    detail: str

    @property
    def blocking(self) -> bool:
        return self.dependency.required and not self.ok


def min_python_version(pyproject=None) -> tuple[int, int]:
    """Minimum interpreter, read from pyproject's requires-python.

    Derived rather than hardcoded, for the same reason the version is: a literal here
    is a second declaration that drifts the moment the real floor moves.
    tomllib is 3.11+, so the field is read with a regex to stay usable on 3.10.
    """
    path = Path(pyproject) if pyproject else REPO_ROOT / "pyproject.toml"
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return FALLBACK_MIN_PYTHON

    match = re.search(r'requires-python\s*=\s*["\']>=\s*(\d+)\.(\d+)', text)
    if not match:
        return FALLBACK_MIN_PYTHON
    return (int(match.group(1)), int(match.group(2)))


def _tool_version(executable) -> str:
    try:
        out = subprocess.run(
            [executable, "--version"], capture_output=True, text=True, timeout=5
        )
        return (out.stdout or out.stderr).strip().splitlines()[0]
    except Exception:
        return ""


PYTHON = Dependency(
    name="python3",
    required=True,
    purpose="Runs the CLI and every audit detector.",
    install_hint="Install Python from https://www.python.org/downloads/ or your package manager.",
)

UV = Dependency(
    name="uv",
    required=False,
    purpose="Preferred runner for the test suite; resolves the dev dependency group.",
    install_hint="curl -LsSf https://astral.sh/uv/install.sh | sh",
)

PYTEST = Dependency(
    name="pytest",
    required=False,
    purpose="Test framework behind `make test`. Provided automatically when uv is present.",
    install_hint="Install uv (preferred), or: python3 -m pip install pytest",
)

MAKE = Dependency(
    name="make",
    required=False,
    purpose="Convenience entrypoints (`make check`, `make audit`, `make test`).",
    install_hint="Install build-essential / Xcode command line tools, or call ./bin/clube-config directly.",
)

GIT = Dependency(
    name="git",
    required=False,
    purpose="Version control for the project being onboarded.",
    install_hint="Install git from https://git-scm.com/downloads",
)


def check_python(version_info=None, minimum=None) -> DependencyResult:
    current = tuple(version_info or sys.version_info[:2])[:2]
    floor = minimum or min_python_version()
    rendered = ".".join(str(part) for part in current)
    if current >= floor:
        return DependencyResult(PYTHON, True, f"{rendered}")
    wanted = ".".join(str(part) for part in floor)
    return DependencyResult(PYTHON, False, f"{rendered} found, {wanted}+ required")


def check_uv(finder=which) -> DependencyResult:
    path = finder("uv")
    if not path:
        return DependencyResult(UV, False, "not found")
    return DependencyResult(UV, True, _tool_version("uv") or path)


def check_pytest(finder=which, importer=None) -> DependencyResult:
    """Satisfied by uv (which provisions it on demand) or by an importable pytest."""
    if finder("uv"):
        return DependencyResult(PYTEST, True, "provided on demand by uv")

    if importer is None:
        import importlib.util

        importer = importlib.util.find_spec

    try:
        found = importer("pytest") is not None
    except Exception:
        found = False

    if found:
        return DependencyResult(PYTEST, True, "importable")
    return DependencyResult(PYTEST, False, "neither uv nor an importable pytest found")


def _simple_tool_check(dependency, finder=which) -> DependencyResult:
    path = finder(dependency.name)
    if not path:
        return DependencyResult(dependency, False, "not found")
    return DependencyResult(dependency, True, _tool_version(dependency.name) or path)


def check_make(finder=which) -> DependencyResult:
    return _simple_tool_check(MAKE, finder)


def check_git(finder=which) -> DependencyResult:
    return _simple_tool_check(GIT, finder)


def check_all() -> list[DependencyResult]:
    return [
        check_python(),
        check_uv(),
        check_pytest(),
        check_make(),
        check_git(),
    ]


def blocking(results) -> list[DependencyResult]:
    return [result for result in results if result.blocking]


def missing_optional(results) -> list[DependencyResult]:
    return [r for r in results if not r.ok and not r.dependency.required]
