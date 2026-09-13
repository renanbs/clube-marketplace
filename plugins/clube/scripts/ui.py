#!/usr/bin/env python3
"""
ui.py — Shared Terminal UI & Runlog Engine for Clube Audit Scripts
Provides ANSI color formatting, TTY detection, ASCII header cards,
status badges, Markdown-compatible aligned tables, visual health bars,
and JSON runlog persistence.
"""

import os
import sys
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Auto-detect TTY and respect NO_COLOR environment variable
_USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

if _USE_COLOR:
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"
else:
    BOLD = ""
    DIM = ""
    RESET = ""
    GREEN = ""
    RED = ""
    YELLOW = ""
    CYAN = ""
    BLUE = ""
    MAGENTA = ""
    WHITE = ""
    GRAY = ""

ANSI_REGEX = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


def strip_ansi(text: str) -> str:
    """Removes ANSI escape codes from string to accurately measure visible length."""
    return ANSI_REGEX.sub('', str(text))


def visible_len(text: str) -> int:
    """Calculates visible character count of a string ignoring ANSI styling."""
    return len(strip_ansi(text))


def colorize(text: str, color: str) -> str:
    """Wraps text in ANSI color code if coloring is active."""
    if not _USE_COLOR or not color:
        return str(text)
    return f"{color}{text}{RESET}"


def print_header(title: str, subtitle: str = "", width: int = 68) -> None:
    """Prints a beautiful ASCII boxed header card for audit scripts."""
    box_width = max(width, visible_len(title) + 6, visible_len(subtitle) + 6)
    inner_width = box_width - 2

    top_border = "┌" + "─" * inner_width + "┐"
    bottom_border = "└" + "─" * inner_width + "┘"

    def pad_line(content: str, color_code: str = "") -> str:
        vis_len = visible_len(content)
        total_padding = inner_width - vis_len
        left_pad = total_padding // 2
        right_pad = total_padding - left_pad
        formatted = f"{' ' * left_pad}{colorize(content, color_code)}{' ' * right_pad}"
        return f"│{formatted}│"

    print(colorize(top_border, CYAN))
    print(pad_line(title.upper(), BOLD + CYAN))
    if subtitle:
        print(pad_line(subtitle, DIM + WHITE))
    print(colorize(bottom_border, CYAN))
    print()


def format_badge(status: str, text: Optional[str] = None) -> str:
    """
    Renders a colored status badge.
    Status types: PASS, WARN, FAIL, INFO, SKIP, HEALTHY, ACTION REQUIRED, OPTIMIZATIONS
    """
    st_upper = status.upper().strip()
    label = text if text is not None else st_upper

    if st_upper in ("PASS", "OK", "SUCCESS", "HEALTHY"):
        return colorize(f"[{label}]", BOLD + GREEN)
    elif st_upper in ("WARN", "WARNING", "OPTIMIZATIONS", "OPTIMIZATION", "NEEDS ATTENTION"):
        return colorize(f"[{label}]", BOLD + YELLOW)
    elif st_upper in ("FAIL", "ERROR", "CRITICAL", "ACTION REQUIRED", "FAILED"):
        return colorize(f"[{label}]", BOLD + RED)
    elif st_upper in ("INFO", "SCAN"):
        return colorize(f"[{label}]", BOLD + CYAN)
    elif st_upper in ("SKIP", "OMITTED"):
        return colorize(f"[{label}]", BOLD + GRAY)
    else:
        return colorize(f"[{label}]", BOLD)


def render_health_bar(score_percent: Union[int, float], width: int = 20) -> str:
    """
    Renders a graphical block progress bar: [████████░░░░] 60%
    Color dynamically adjusts: Green (>=80%), Yellow (>=50%), Red (<50%).
    """
    clamped = max(0.0, min(100.0, float(score_percent)))
    fill_count = int(round((clamped / 100.0) * width))
    empty_count = width - fill_count

    filled_blocks = "█" * fill_count
    empty_blocks = "░" * empty_count

    if clamped >= 80:
        bar_color = BOLD + GREEN
    elif clamped >= 50:
        bar_color = BOLD + YELLOW
    else:
        bar_color = BOLD + RED

    bar_str = f"{colorize(filled_blocks, bar_color)}{colorize(empty_blocks, GRAY)}"
    return f"[{bar_str}] {colorize(f'{int(round(clamped))}%', BOLD)}"


def render_table(headers: List[str], rows: List[List[Any]], alignments: Optional[List[str]] = None) -> str:
    """
    Renders a cleanly padded Markdown-compatible table.
    alignments: list of 'left', 'center', 'right' (defaults to 'left')
    """
    if not headers:
        return ""

    num_cols = len(headers)
    if not alignments or len(alignments) != num_cols:
        alignments = ["left"] * num_cols

    # Calculate column widths based on visible length of headers and all rows
    col_widths = [visible_len(h) for h in headers]
    for row in rows:
        for idx in range(num_cols):
            val = str(row[idx]) if idx < len(row) else ""
            col_widths[idx] = max(col_widths[idx], visible_len(val))

    def format_cell(content: str, width: int, align: str) -> str:
        vis = visible_len(content)
        pad = max(0, width - vis)
        if align == "right":
            return " " * pad + content
        elif align == "center":
            left = pad // 2
            right = pad - left
            return " " * left + content + " " * right
        else:  # left
            return content + " " * pad

    lines = []

    # Header Row
    header_cells = [
        format_cell(colorize(headers[i], BOLD), col_widths[i], alignments[i])
        for i in range(num_cols)
    ]
    lines.append(f"| {' | '.join(header_cells)} |")

    # Separator Row (Markdown alignment syntax)
    sep_cells = []
    for i, align in enumerate(alignments):
        w = max(col_widths[i], 3)
        if align == "right":
            sep_cells.append("-" * (w - 1) + ":")
        elif align == "center":
            sep_cells.append(":" + "-" * (w - 2) + ":")
        else:  # left
            sep_cells.append(":" + "-" * (w - 1))
    lines.append(f"| {' | '.join(sep_cells)} |")

    # Data Rows
    for row in rows:
        row_cells = []
        for i in range(num_cols):
            val = str(row[i]) if i < len(row) else ""
            row_cells.append(format_cell(val, col_widths[i], alignments[i]))
        lines.append(f"| {' | '.join(row_cells)} |")

    return "\n".join(lines)


def calculate_health_score(issues_count: int, penalty_per_issue: int = 20) -> int:
    """Calculates a 0-100 health score given an issue count."""
    if issues_count <= 0:
        return 100
    return max(0, 100 - (issues_count * penalty_per_issue))


SEVERITY_WEIGHTS = {"CRITICAL": 30, "HIGH": 20, "MEDIUM": 10, "LOW": 4}


def calculate_weighted_score(issues: List[Dict[str, Any]]) -> int:
    """Severity-aware health score.

    Two problems with the flat count-based score this replaces:

    1. A LOW weighed the same as a HIGH, so severity carried no signal.
    2. Line-level auditors saturated at zero after a handful of findings, so a file
       with 4 blind logs scored the same as one with 40.

    Repeated findings of the same *type* are usually one defect repeated, so each
    additional instance of a type penalises less than the previous one. Distinct types
    still accumulate at full weight.
    """
    if not issues:
        return 100

    seen: Dict[str, int] = {}
    penalty = 0.0
    for issue in issues:
        severity = str(issue.get("severity", "MEDIUM")).upper()
        kind = str(issue.get("type", severity))
        occurrences = seen.get(kind, 0)
        seen[kind] = occurrences + 1
        penalty += SEVERITY_WEIGHTS.get(severity, 10) / (1 + occurrences)

    return max(0, round(100 - penalty))


def save_runlog(data: Dict[str, Any], output_file: str = ".clube/audit-last.json") -> str:
    """
    Persists structured audit execution results to JSON runlog.
    Ensures directory exists and stamps current UTC timestamp if not present.
    """
    out_path = Path(output_file)
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    log_payload = dict(data)
    if "timestamp" not in log_payload:
        log_payload["timestamp"] = datetime.now(timezone.utc).isoformat()

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(log_payload, f, indent=2, ensure_ascii=False)

    return str(out_path.resolve())
