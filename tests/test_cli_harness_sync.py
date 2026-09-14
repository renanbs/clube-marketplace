"""Harness detection, pointer sync, runlog and command dispatch."""

import json

import pytest

from clube_cli import cli, harness, runlog, sync


# --------------------------------------------------------------------------- #
# Harness detection
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("env_var,expected", [
    ("OMPCODE", "omp"),
    ("OMP_SESSION_ID", "omp"),
    ("ANTIGRAVITY", "antigravity"),
    ("CURSOR_AGENT", "cursor"),
    ("OPENCODE", "opencode"),
    ("CLAUDE_CONVERSATION_ID", "claude-code"),
])
def test_env_markers_detect_harness(env_var, expected):
    assert harness.detect_from_env({env_var: "1"}) == expected


def test_detection_order_prefers_omp():
    """Order is load-bearing: an OMP session may also export Claude variables."""
    env = {"CLAUDE_CONVERSATION_ID": "1", "OMPCODE": "1"}
    assert harness.detect_from_env(env) == "omp"


def test_empty_env_marker_does_not_count():
    assert harness.detect_from_env({"OMPCODE": ""}) is None


def test_no_markers_returns_none():
    assert harness.detect_from_env({"PATH": "/usr/bin"}) is None


@pytest.mark.parametrize("name,expected", [
    ("omp", "omp"),
    ("OMP-agent", "omp"),
    ("claude", "claude-code"),
    ("Claude Code", "claude-code"),
    ("cursor-helper", "cursor"),
    ("opencode", "opencode"),
    ("bash", None),
    ("", None),
])
def test_process_name_classification(name, expected):
    assert harness.classify_process_name(name) == expected


def test_friendly_names_cover_every_known_harness():
    for key in harness.FRIENDLY_NAMES:
        assert harness.friendly_name(key) != harness.DEFAULT_FRIENDLY_NAME
    assert harness.friendly_name("something-else") == harness.DEFAULT_FRIENDLY_NAME


def test_detect_active_harness_falls_back_to_generic(monkeypatch):
    monkeypatch.setattr(harness, "detect_from_env", lambda *a, **k: None)
    monkeypatch.setattr(harness, "detect_from_process_tree", lambda *a, **k: None)
    assert harness.detect_active_harness() == harness.DEFAULT_HARNESS


# --------------------------------------------------------------------------- #
# Profile persistence
# --------------------------------------------------------------------------- #

def test_profile_roundtrip(tmp_path):
    path = tmp_path / "profile.json"
    harness.save_profile("omp", reasoning="big", code="fast", path=path)
    assert harness.saved_harness(path) == "omp"
    assert harness.saved_model_role("reasoning", path) == "big"
    assert harness.saved_model_role("code", path) == "fast"
    assert harness.saved_model_role("critique", path) == "default"


def test_missing_profile_returns_defaults(tmp_path):
    path = tmp_path / "absent.json"
    assert harness.saved_harness(path) == "none"
    assert harness.saved_model_role("code", path) == "default"


def test_corrupt_profile_returns_defaults(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    assert harness.saved_harness(path) == "none"


# --------------------------------------------------------------------------- #
# Pointer sync
# --------------------------------------------------------------------------- #

def test_pointers_created_next_to_agents_md(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# instructions\n", encoding="utf-8")
    result = sync.sync_pointers(tmp_path)
    assert len(result["created"]) == len(sync.DEFAULT_POINTERS)
    for pointer in sync.DEFAULT_POINTERS:
        assert (tmp_path / pointer).read_text(encoding="utf-8").strip() == "@AGENTS.md"


def test_existing_custom_pointer_is_preserved(tmp_path):
    """Clobbering a hand-written config would lose the user's work."""
    (tmp_path / "AGENTS.md").write_text("# instructions\n", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("# my own rules\n", encoding="utf-8")
    result = sync.sync_pointers(tmp_path)
    assert (tmp_path / "CLAUDE.md").read_text(encoding="utf-8") == "# my own rules\n"
    assert len(result["preserved"]) == 1


def test_aligned_pointer_is_untouched(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# instructions\n", encoding="utf-8")
    (tmp_path / "GEMINI.md").write_text("@AGENTS.md\n", encoding="utf-8")
    result = sync.sync_pointers(tmp_path)
    assert len(result["aligned"]) == 1
    assert len(result["created"]) == len(sync.DEFAULT_POINTERS) - 1


def test_nested_agents_files_each_get_pointers(tmp_path):
    (tmp_path / "AGENTS.md").write_text("root\n", encoding="utf-8")
    nested = tmp_path / "packages" / "api"
    nested.mkdir(parents=True)
    (nested / "AGENTS.md").write_text("nested\n", encoding="utf-8")
    result = sync.sync_pointers(tmp_path)
    assert len(result["created"]) == 2 * len(sync.DEFAULT_POINTERS)


def test_pruned_directories_are_skipped(tmp_path):
    (tmp_path / "AGENTS.md").write_text("root\n", encoding="utf-8")
    vendored = tmp_path / "node_modules" / "pkg"
    vendored.mkdir(parents=True)
    (vendored / "AGENTS.md").write_text("vendored\n", encoding="utf-8")
    result = sync.sync_pointers(tmp_path)
    assert len(result["created"]) == len(sync.DEFAULT_POINTERS)
    assert not (vendored / "CLAUDE.md").exists()


def test_missing_target_directory_raises(tmp_path):
    with pytest.raises(NotADirectoryError):
        sync.sync_pointers(tmp_path / "nope")


def test_ensure_agents_md_creates_then_preserves(tmp_path):
    assert sync.ensure_agents_md(tmp_path) is True
    (tmp_path / "AGENTS.md").write_text("custom\n", encoding="utf-8")
    assert sync.ensure_agents_md(tmp_path) is False
    assert (tmp_path / "AGENTS.md").read_text(encoding="utf-8") == "custom\n"


# --------------------------------------------------------------------------- #
# Runlog
# --------------------------------------------------------------------------- #

def test_runlog_appends_valid_jsonl(tmp_path):
    path = tmp_path / "runs" / "latest.jsonl"
    assert runlog.log_event("info", "check", "passed", path=path) is True
    assert runlog.log_event("error", "check", "FAILED", path=path) is True
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[1])["level"] == "error"


def test_runlog_escapes_quotes(tmp_path):
    """The shell version concatenated strings and emitted invalid JSON on any quote."""
    path = tmp_path / "log.jsonl"
    runlog.log_event("info", "check", 'has "quotes" inside', path=path)
    assert json.loads(path.read_text(encoding="utf-8"))["details"] == 'has "quotes" inside'


def test_runlog_failure_is_not_fatal(tmp_path):
    """Logging must never take down the command the user actually asked for."""
    blocker = tmp_path / "blocker"
    blocker.write_text("not a directory", encoding="utf-8")
    assert runlog.log_event("info", "x", "y", path=blocker / "sub" / "log.jsonl") is False


# --------------------------------------------------------------------------- #
# Dispatch
# --------------------------------------------------------------------------- #

def test_unknown_command_exits_non_zero(capsys):
    assert cli.main(["does-not-exist"]) == 1
    assert "Unknown command" in capsys.readouterr().err


def test_help_exits_zero(capsys):
    assert cli.main(["help"]) == 0
    assert "clube-config" in capsys.readouterr().out


def test_no_args_shows_help(capsys):
    assert cli.main([]) == 0
    assert "Commands:" in capsys.readouterr().out


def test_unknown_audit_pillar_exits_non_zero(capsys):
    assert cli.cmd_audit(["bogus"]) == 1
    assert "Unknown audit pillar" in capsys.readouterr().err


def test_status_is_an_alias_for_check():
    assert cli.COMMANDS["status"] is cli.COMMANDS["check"]


def test_every_audit_pillar_maps_to_an_existing_script():
    for pillar, script in cli.AUDIT_PILLARS.items():
        assert (cli.REPO_ROOT / "plugins" / "clube" / "scripts" / script).is_file(), pillar
