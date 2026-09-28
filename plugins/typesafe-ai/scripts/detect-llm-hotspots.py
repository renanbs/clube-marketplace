#!/usr/bin/env python3
"""
detect-llm-hotspots.py — TypeSafe AI System 1 Opportunity Detector
Scans project repositories for expensive generative LLM calls (OpenAI, Anthropic,
LangChain, LiteLLM, PydanticAI) that can be offloaded to TypeSafe Jev System 1
for sub-20ms typed decision-making, token reduction, and calibrated confidence gating.
"""

import os
import sys
import re
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

IGNORED_DIRS = {
    '.git', 'node_modules', 'dist', 'build', '.specs', 'vendor',
    '__pycache__', '.venv', 'venv', '.clube', '.typesafe', '.omp'
}

EXTENSIONS = {'.py', '.ts', '.tsx', '.js', '.jsx', '.go', '.rs'}

# Patterns indicating generative LLM calls performing deterministic decision tasks
HOTSPOT_PATTERNS = [
    (
        re.compile(r'(?:response_format\s*=\s*\{\s*["\']type["\']\s*:\s*["\']json_object["\']|type:\s*["\']json_schema["\'])', re.I),
        "JSON Schema mode on generative LLM (System 1 offload candidate)",
        750,
        "High"
    ),
    (
        re.compile(r'(?:response_model\s*=|Instructor|extract_with_llm|parse_with_model)', re.I),
        "Pydantic / Instructor structured extraction via generative LLM",
        850,
        "High"
    ),
    (
        re.compile(r'(?:classify|triage|sentiment|intent|routing|categorize|priority)\b.*(?:prompt|message|query)', re.I),
        "Classification / Intent routing prompt routed to generative LLM",
        1200,
        "High"
    ),
    (
        re.compile(r'(?:["\'](?:YES\s+or\s+NO|True\s+or\s+False|true\s*\/\s*false|Return\s+a\s+JSON)\b)', re.I),
        "Binary or JSON-only prompt burned on auto-regressive tokens",
        600,
        "Critical"
    ),
    (
        re.compile(r'(?:client\.chat\.completions\.create|anthropic\.messages\.create|generateText|streamText)\(', re.I),
        "Direct Generative LLM SDK call (evaluate for System 1 offload)",
        500,
        "Medium"
    ),
]

def is_ignored_dir(name: str) -> bool:
    return name in IGNORED_DIRS or name.endswith("-worktrees") or name == "worktrees"

def scan_file(filepath: Path) -> list:
    candidates = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return candidates

    lines = content.splitlines()
    for idx, line in enumerate(lines, 1):
        # Ignore comments
        stripped = line.strip()
        if stripped.startswith(("//", "#", "/*", "*")):
            continue

        for pattern, description, est_tokens, viability in HOTSPOT_PATTERNS:
            if pattern.search(line):
                snippet = stripped[:120]
                candidates.append({
                    "file": str(filepath),
                    "line": idx,
                    "description": description,
                    "snippet": snippet,
                    "est_tokens_saved": est_tokens,
                    "est_latency_drop": "1,800ms -> 18ms",
                    "viability": viability,
                })
                break  # match highest precedence pattern per line
    return candidates

def main():
    parser = argparse.ArgumentParser(description="TypeSafe AI LLM Hotspot Detector")
    parser.add_argument("--target", default=".", help="Target directory to scan")
    parser.add_argument("--json", action="store_true", help="Output pure JSON to stdout")
    args = parser.parse_args()

    target_dir = Path(args.target).resolve()
    all_candidates = []

    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if not is_ignored_dir(d)]
        for f in files:
            p = Path(root) / f
            if f == "detect-llm-hotspots.py" or re.search(r'(?:\.(?:spec|test)\.[jt]sx?$|_test\.(?:go|py|rs)$)', f):
                continue
            try:
                rel_p = p.relative_to(target_dir)
            except ValueError:
                rel_p = p
            matches = scan_file(p)
            for m in matches:
                m["file"] = str(rel_p)
                all_candidates.append(m)

    total_tokens_per_run = sum(c["est_tokens_saved"] for c in all_candidates)

    report_payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target": str(target_dir),
        "candidates_count": len(all_candidates),
        "est_tokens_saved_per_turn": total_tokens_per_run,
        "candidates": all_candidates,
    }

    # Persist runlog in .typesafe/
    runlog_dir = target_dir / ".typesafe"
    try:
        runlog_dir.mkdir(parents=True, exist_ok=True)
        (runlog_dir / "optimize-last.json").write_text(json.dumps(report_payload, indent=2), encoding="utf-8")
    except Exception:
        pass

    if args.json:
        print(json.dumps(report_payload, indent=2))
        return 0

    print("=" * 72)
    print("  TypeSafe AI — System 1 Decision Offload Detector")
    print("=" * 72)
    print(f"Target: {target_dir}")
    print(f"Candidates Found: {len(all_candidates)}")
    print(f"Est. Tokens Saved / Call Batch: ~{total_tokens_per_run:,} tokens")
    print("-" * 72)

    if not all_candidates:
        print("✅ No expensive LLM decision bottlenecks found. Codebase is clean!")
        return 0

    print(f"{'Location':<35} | {'Viability':<8} | {'Description'}")
    print("-" * 72)
    for c in all_candidates[:25]:
        loc = f"{c['file']}:{c['line']}"
        if len(loc) > 34:
            loc = "..." + loc[-31:]
        print(f"{loc:<35} | {c['viability']:<8} | {c['description']}")

    if len(all_candidates) > 25:
        print(f"... and {len(all_candidates) - 25} more candidates in .typesafe/optimize-last.json")

    print("-" * 72)
    print("Run `cat .typesafe/optimize-last.json` or invoke `/typesafe-ai:optimize` for refactoring patches.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
