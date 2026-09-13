#!/usr/bin/env python3
"""
audit-all.py — Unified 360° SaaS Engineering & Production Readiness Auditor
Executes all 4 deterministic audit checks:
  1. Data Privacy & Observability
  2. Fullstack Performance & Resilience
  3. SaaS SEO & Generative Engine Optimization
  4. Marketing Attribution & Analytics
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

# Sibling module imports
script_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(script_dir))
import ui  # noqa: E402

import importlib
audit_privacy = importlib.import_module("audit-privacy")
audit_performance = importlib.import_module("audit-performance")
audit_seo = importlib.import_module("audit-seo")
audit_tracking = importlib.import_module("audit-tracking")

def audit(target_dir):
    abs_target = os.path.abspath(target_dir)
    res_privacy = audit_privacy.audit(target_dir)
    res_perf = audit_performance.audit(target_dir)
    res_seo = audit_seo.audit(target_dir)
    res_tracking = audit_tracking.audit(target_dir)

    total_issues = (
        res_privacy["issues_count"]
        + res_perf["issues_count"]
        + res_seo["issues_count"]
        + res_tracking["issues_count"]
    )

    avg_score = int(round((res_privacy["score"] + res_perf["score"] + res_seo["score"] + res_tracking["score"]) / 4.0))
    verdict = "HEALTHY" if total_issues == 0 else "NEEDS ATTENTION"

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "audit": "all",
        "target": abs_target,
        "total_issues": total_issues,
        "score": avg_score,
        "verdict": verdict,
        "privacy": res_privacy,
        "performance": res_perf,
        "seo": res_seo,
        "tracking": res_tracking
    }

def main():
    parser = argparse.ArgumentParser(description="Unified 360° Clube SaaS Production Audit.")
    parser.add_argument("--target", default=".", help="Directory to scan")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    results = audit(args.target)
    ui.save_runlog(results)

    if args.json:
        print(json.dumps(results, indent=2))
        sys.exit(0 if results["total_issues"] == 0 else 1)

    ui.print_header("CLUBE SAAS 360° PRODUCTION READINESS AUDIT", "Deterministic Multi-Pillar Engineering & Observability Scanner")

    print(f"{ui.BOLD}### 1. Plan{ui.RESET}\n")
    print(f"- **Audit:** Unified 360° Clube SaaS Production Readiness")
    print(f"- **Target:** {results['target']}")
    print(f"- **Mode:** Deterministic static analysis (4 pillars, zero tokens)\n")

    print(f"{ui.BOLD}### 2. Execution{ui.RESET}\n")
    pillars = [
        ("Data Privacy & Observability", results["privacy"]["issues_count"], results["privacy"]["issues"]),
        ("Fullstack Performance & Resilience", results["performance"]["issues_count"], results["performance"]["issues"]),
        ("SaaS SEO & Generative Engine Optimization", results["seo"]["issues_count"], results["seo"]["issues"]),
        ("Marketing Attribution & Analytics", results["tracking"]["issues_count"], results["tracking"]["issues"]),
    ]

    for name, count, issues in pillars:
        if count == 0:
            print(f"  {ui.format_badge('PASS')} {ui.BOLD}{name}:{ui.RESET} 0 issues detected")
        else:
            has_crit = any(i.get("severity") in ("HIGH", "CRITICAL") for i in issues)
            badge = ui.format_badge("FAIL" if has_crit else "WARN")
            print(f"  {badge} {ui.BOLD}{name}:{ui.RESET} {count} issue(s) detected")
            for item in issues[:3]:
                file_ref = f" [{item.get('file', '')}]" if item.get('file') else ""
                print(f"     • [{item.get('type', 'Issue')}]{file_ref}: {item['description']}")
            if count > 3:
                print(f"     • ... and {count - 3} more.")
    print()

    print(f"{ui.BOLD}### 3. Summary{ui.RESET}\n")
    print(f"Overall Health: {ui.render_health_bar(results['score'])}\n")

    summary_headers = ["Audit Pillar", "Findings", "Score", "Status"]
    summary_rows = [
        [
            "Data Privacy & Observability",
            str(results["privacy"]["issues_count"]),
            f"{results['privacy']['score']}%",
            ui.format_badge("PASS" if results["privacy"]["issues_count"] == 0 else "FAIL", "PASS" if results["privacy"]["issues_count"] == 0 else "ACTION REQUIRED")
        ],
        [
            "Fullstack Performance & Resilience",
            str(results["performance"]["issues_count"]),
            f"{results['performance']['score']}%",
            ui.format_badge("PASS" if results["performance"]["issues_count"] == 0 else "FAIL", "PASS" if results["performance"]["issues_count"] == 0 else "ACTION REQUIRED")
        ],
        [
            "SaaS SEO & GEO",
            str(results["seo"]["issues_count"]),
            f"{results['seo']['score']}%",
            ui.format_badge("PASS" if results["seo"]["issues_count"] == 0 else "OPTIMIZATIONS", "PASS" if results["seo"]["issues_count"] == 0 else "OPTIMIZATIONS")
        ],
        [
            "Marketing Attribution & Analytics",
            str(results["tracking"]["issues_count"]),
            f"{results['tracking']['score']}%",
            ui.format_badge("PASS" if results["tracking"]["issues_count"] == 0 else "ACTION REQUIRED", "PASS" if results["tracking"]["issues_count"] == 0 else "ACTION REQUIRED")
        ],
        [
            f"{ui.BOLD}Overall Readiness{ui.RESET}",
            f"{ui.BOLD}{results['total_issues']} total{ui.RESET}",
            f"{ui.BOLD}{results['score']}%{ui.RESET}",
            ui.format_badge("HEALTHY" if results["total_issues"] == 0 else "NEEDS ATTENTION")
        ],
    ]
    print(ui.render_table(summary_headers, summary_rows))

    print(f"\n{ui.BOLD}### 4. Recommended Actions{ui.RESET}\n")
    if results["total_issues"] == 0:
        print("- All 4 pillars are compliant with Clube engineering playbooks.")
    else:
        print("- Run targeted AI audits to generate patches:")
        if results["privacy"]["issues_count"] > 0:
            print("  • `/audit-privacy` — Review PII leaks and generate masked logging models.")
        if results["performance"]["issues_count"] > 0:
            print("  • `/audit-performance` — Install chunk recovery and CDN cache policies.")
        if results["seo"]["issues_count"] > 0:
            print("  • `/audit-seo` — Scaffold llms.txt and structured data.")
        if results["tracking"]["issues_count"] > 0:
            print("  • `/audit-tracking` — Configure root domain cookies and acquisition context.")

    sys.exit(0 if results["total_issues"] == 0 else 1)

if __name__ == "__main__":
    main()
