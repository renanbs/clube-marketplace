"""Shared UI helpers: scoring, badges, tables, runlog."""

import json

import pytest


def issue(severity="MEDIUM", kind="Some Type"):
    return {"severity": severity, "type": kind}


def test_no_issues_scores_100(ui):
    assert ui.calculate_weighted_score([]) == 100


def test_severity_changes_the_score(ui):
    """The flat counter weighed a LOW the same as a HIGH, so severity carried no signal."""
    low = ui.calculate_weighted_score([issue("LOW", "A")])
    high = ui.calculate_weighted_score([issue("HIGH", "A")])
    critical = ui.calculate_weighted_score([issue("CRITICAL", "A")])
    assert critical < high < low < 100


def test_distinct_types_accumulate_at_full_weight(ui):
    two_types = ui.calculate_weighted_score([issue("HIGH", "A"), issue("HIGH", "B")])
    assert two_types == 100 - 2 * ui.SEVERITY_WEIGHTS["HIGH"]


def test_repeated_type_decays(ui):
    """N occurrences of one pattern are one defect repeated, not N defects."""
    once = ui.calculate_weighted_score([issue("HIGH", "A")])
    twice = ui.calculate_weighted_score([issue("HIGH", "A")] * 2)
    assert twice < once
    # Second occurrence costs half of the first.
    assert twice == round(100 - ui.SEVERITY_WEIGHTS["HIGH"] * 1.5)


def test_many_repeats_do_not_saturate_immediately(ui):
    """The flat score hit zero at the fourth finding, so 4 problems looked like 40."""
    assert ui.calculate_weighted_score([issue("HIGH", "A")] * 4) > 0


def test_score_is_clamped_at_zero(ui):
    assert ui.calculate_weighted_score([issue("CRITICAL", f"T{i}") for i in range(20)]) == 0


def test_unknown_severity_uses_medium_weight(ui):
    assert ui.calculate_weighted_score([issue("BOGUS", "A")]) == 100 - ui.SEVERITY_WEIGHTS["MEDIUM"]


def test_legacy_flat_score_still_available(ui):
    """audit-all.py and older callers still use it."""
    assert ui.calculate_health_score(0) == 100
    assert ui.calculate_health_score(2, penalty_per_issue=25) == 50
    assert ui.calculate_health_score(99) == 0


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("status", ["PASS", "WARN", "FAIL", "INFO", "SKIP", "ACTION REQUIRED"])
def test_badges_render_without_error(ui, status):
    assert status in ui.format_badge(status)


def test_badge_custom_label(ui):
    assert "3 FINDINGS" in ui.format_badge("FAIL", "3 FINDINGS")


def test_health_bar_is_clamped(ui):
    assert "100%" in ui.render_health_bar(150)
    assert "0%" in ui.render_health_bar(-20)


def test_table_renders_all_rows(ui):
    out = ui.render_table(["A", "B"], [["1", "2"], ["3", "4"]])
    lines = out.splitlines()
    assert len(lines) == 4  # header + separator + 2 rows
    assert "1" in lines[2] and "4" in lines[3]


def test_table_with_no_headers_is_empty(ui):
    assert ui.render_table([], []) == ""


def test_visible_len_ignores_ansi(ui):
    assert ui.visible_len("\033[1mabc\033[0m") == 3


# --------------------------------------------------------------------------- #
# Runlog
# --------------------------------------------------------------------------- #

def test_runlog_writes_valid_json(ui, tmp_path):
    out = tmp_path / "nested" / "run.json"
    ui.save_runlog({"audit": "seo", "score": 77}, output_file=str(out))
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["audit"] == "seo"
    assert data["score"] == 77
    assert "timestamp" in data


def test_runlog_preserves_existing_timestamp(ui, tmp_path):
    out = tmp_path / "run.json"
    ui.save_runlog({"timestamp": "2020-01-01T00:00:00+00:00"}, output_file=str(out))
    assert json.loads(out.read_text(encoding="utf-8"))["timestamp"].startswith("2020-01-01")
