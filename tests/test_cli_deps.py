"""Toolchain preflight.

Without this, a missing dependency surfaces late and cryptically: `make test` on a
machine with neither uv nor pytest dies with ModuleNotFoundError, and an interpreter
below the floor passes the launcher's `command -v python3` only to fail at import.
"""

import pytest

from clube_cli import cli, deps


def finder(available):
    """Fake shutil.which over a set of installed tool names."""
    return lambda name: f"/usr/bin/{name}" if name in available else None


# --------------------------------------------------------------------------- #
# Python floor
# --------------------------------------------------------------------------- #

def test_current_interpreter_satisfies_the_floor():
    """The suite is running, so the interpreter it runs on must be acceptable."""
    assert deps.check_python().ok


def test_interpreter_below_floor_is_blocking():
    result = deps.check_python(version_info=(3, 8), minimum=(3, 10))
    assert not result.ok
    assert result.blocking
    assert "3.10+" in result.detail


def test_interpreter_at_floor_passes():
    assert deps.check_python(version_info=(3, 10), minimum=(3, 10)).ok


def test_minimum_python_is_read_from_pyproject(tmp_path):
    """Derived, not hardcoded — a literal here drifts the moment the floor moves."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nrequires-python = ">=3.12"\n', encoding="utf-8")
    assert deps.min_python_version(pyproject) == (3, 12)


def test_real_pyproject_declares_a_floor():
    assert deps.min_python_version() >= (3, 10)


@pytest.mark.parametrize("content", ["", "[project]\n", "[project]\nrequires-python = 'bogus'\n"])
def test_unreadable_pyproject_falls_back(tmp_path, content):
    path = tmp_path / "pyproject.toml"
    path.write_text(content, encoding="utf-8")
    assert deps.min_python_version(path) == deps.FALLBACK_MIN_PYTHON


def test_missing_pyproject_falls_back(tmp_path):
    assert deps.min_python_version(tmp_path / "absent.toml") == deps.FALLBACK_MIN_PYTHON


# --------------------------------------------------------------------------- #
# Optional tooling
# --------------------------------------------------------------------------- #

def test_uv_missing_is_optional_not_blocking():
    result = deps.check_uv(finder=finder(set()))
    assert not result.ok
    assert not result.blocking


def test_uv_present_is_ok():
    assert deps.check_uv(finder=finder({"uv"})).ok


def test_uv_satisfies_pytest():
    """uv provisions the dev group on demand, so pytest need not be installed."""
    result = deps.check_pytest(finder=finder({"uv"}))
    assert result.ok
    assert "uv" in result.detail


def test_importable_pytest_satisfies_without_uv():
    result = deps.check_pytest(finder=finder(set()), importer=lambda name: object())
    assert result.ok


def test_neither_uv_nor_pytest_is_reported():
    """The combination that actually breaks `make test`."""
    result = deps.check_pytest(finder=finder(set()), importer=lambda name: None)
    assert not result.ok
    assert not result.blocking
    assert "neither" in result.detail


def test_pytest_import_error_is_treated_as_missing():
    def boom(name):
        raise ImportError("broken")

    assert not deps.check_pytest(finder=finder(set()), importer=boom).ok


@pytest.mark.parametrize("check", [deps.check_make, deps.check_git])
def test_convenience_tools_are_optional(check):
    assert not check(finder=finder(set())).blocking


# --------------------------------------------------------------------------- #
# Aggregation
# --------------------------------------------------------------------------- #

def test_check_all_covers_every_declared_dependency():
    names = {result.dependency.name for result in deps.check_all()}
    assert names == {"python3", "uv", "pytest", "make", "git"}


def test_every_dependency_explains_itself():
    """A failing check that does not say what to install is a dead end."""
    for result in deps.check_all():
        assert result.dependency.purpose.strip()
        assert result.dependency.install_hint.strip()


def test_blocking_only_counts_required():
    results = [
        deps.check_python(version_info=(3, 8), minimum=(3, 10)),
        deps.check_uv(finder=finder(set())),
    ]
    blocking = deps.blocking(results)
    assert len(blocking) == 1
    assert blocking[0].dependency.name == "python3"
    assert len(deps.missing_optional(results)) == 1


# --------------------------------------------------------------------------- #
# Wiring into commands
# --------------------------------------------------------------------------- #

def test_doctor_passes_on_this_machine(capsys):
    assert cli.cmd_doctor() == 0
    assert "Status" in capsys.readouterr().out


def test_doctor_fails_when_a_required_dependency_is_missing(monkeypatch, capsys):
    monkeypatch.setattr(
        deps, "check_all",
        lambda: [deps.check_python(version_info=(3, 8), minimum=(3, 10))],
    )
    assert cli.cmd_doctor() == 1
    assert "3.10+" in capsys.readouterr().out


def test_init_aborts_before_writing_when_blocked(monkeypatch, tmp_path, capsys):
    """A missing dependency found here is far cheaper than one surfacing three
    commands later — and the abort must leave the target untouched."""
    monkeypatch.setattr(
        deps, "check_all",
        lambda: [deps.check_python(version_info=(3, 8), minimum=(3, 10))],
    )
    assert cli.cmd_init([str(tmp_path)]) == 1
    assert not (tmp_path / "AGENTS.md").exists()
    assert "Onboarding aborted" in capsys.readouterr().err


def test_init_proceeds_when_only_optional_are_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(
        deps, "check_all",
        lambda: [deps.check_python(), deps.check_uv(finder=finder(set()))],
    )
    assert cli.cmd_init([str(tmp_path)]) == 0
    assert (tmp_path / "AGENTS.md").is_file()


def test_doctor_is_registered():
    assert cli.COMMANDS["doctor"] is cli.cmd_doctor


# --------------------------------------------------------------------------- #
# Test runner availability
# --------------------------------------------------------------------------- #

def test_test_command_explains_itself_when_no_runner_exists(monkeypatch, capsys):
    """A bare ModuleNotFoundError is a poor first contact for a fresh clone."""
    monkeypatch.setattr(cli, "deps", deps)
    monkeypatch.setattr("shutil.which", lambda name: None)
    monkeypatch.setattr(
        deps, "check_pytest",
        lambda *a, **k: deps.DependencyResult(deps.PYTEST, False, "neither uv nor an importable pytest found"),
    )
    assert cli.cmd_test([]) == 1
    err = capsys.readouterr().err
    assert "Cannot run the test suite" in err
    assert "Install:" in err
    assert "doctor" in err


def test_test_command_does_not_shell_out_when_no_runner(monkeypatch):
    """It must fail before spawning a process that would print the raw import error."""
    calls = []
    monkeypatch.setattr("shutil.which", lambda name: None)
    monkeypatch.setattr(
        deps, "check_pytest",
        lambda *a, **k: deps.DependencyResult(deps.PYTEST, False, "none found"),
    )
    monkeypatch.setattr(cli.subprocess, "call", lambda *a, **k: calls.append(a) or 0)
    assert cli.cmd_test([]) == 1
    assert calls == []


def test_test_command_uses_uv_when_available(monkeypatch):
    captured = {}
    monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/uv" if name == "uv" else None)
    monkeypatch.setattr(cli.subprocess, "call", lambda cmd, **k: captured.update(cmd=cmd) or 0)
    assert cli.cmd_test([]) == 0
    assert captured["cmd"][:2] == ["uv", "run"]


def test_test_command_falls_back_to_module_pytest(monkeypatch):
    captured = {}
    monkeypatch.setattr("shutil.which", lambda name: None)
    monkeypatch.setattr(
        deps, "check_pytest",
        lambda *a, **k: deps.DependencyResult(deps.PYTEST, True, "importable"),
    )
    monkeypatch.setattr(cli.subprocess, "call", lambda cmd, **k: captured.update(cmd=cmd) or 0)
    assert cli.cmd_test([]) == 0
    assert captured["cmd"][1:3] == ["-m", "pytest"]
