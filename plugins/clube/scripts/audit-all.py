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
from pathlib import Path

# Import sibling audit modules
script_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(script_dir))

import importlib
audit_privacy = importlib.import_module("audit-privacy")
audit_performance = importlib.import_module("audit-performance")
audit_seo = importlib.import_module("audit-seo")
audit_tracking = importlib.import_module("audit-tracking")

def audit(target_dir):
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

    return {
        "target": target_dir,
        "total_issues": total_issues,
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

    if args.json:
        print(json.dumps(results, indent=2))
        sys.exit(0 if results["total_issues"] == 0 else 1)

    print("### 1. Plan")
    print(f"- **Audit:** Unified 360° Clube SaaS Production Readiness")
    print(f"- **Target:** {os.path.abspath(args.target)}")
    print(f"- **Mode:** Deterministic static analysis (4 pillars, zero tokens)\n")

    print("### 2. Execution")
    pillars = [
        ("Data Privacy & Observability", results["privacy"]["issues_count"], results["privacy"]["issues"]),
        ("Fullstack Performance & Resilience", results["performance"]["issues_count"], results["performance"]["issues"]),
        ("SaaS SEO & Generative Engine Optimization", results["seo"]["issues_count"], results["seo"]["issues"]),
        ("Marketing Attribution & Analytics", results["tracking"]["issues_count"], results["tracking"]["issues"]),
    ]

    for name, count, issues in pillars:
        if count == 0:
            print(f"  ✅ **{name}:** 0 issues detected (Passed)")
        else:
            badge = "❌" if any(i.get("severity") in ("HIGH", "CRITICAL") for i in issues) else "⚠️"
            print(f"  {badge} **{name}:** {count} issue(s) detected")
            for item in issues[:3]:
                file_ref = f" [{item.get('file', '')}]" if item.get('file') else ""
                print(f"     • [{item.get('type', 'Issue')}]{file_ref}: {item['description']}")
            if count > 3:
                print(f"     • ... and {count - 3} more.")

    print("\n### 3. Summary")
    print("| Audit Pillar | Findings | Status |")
    print("| :--- | :--- | :--- |")
    print(f"| Privacy & PII | {results['privacy']['issues_count']} | {'PASS' if results['privacy']['issues_count'] == 0 else 'ACTION REQUIRED'} |")
    print(f"| Performance & Resilience | {results['performance']['issues_count']} | {'PASS' if results['performance']['issues_count'] == 0 else 'ACTION REQUIRED'} |")
    print(f"| SaaS SEO & GEO | {results['seo']['issues_count']} | {'PASS' if results['seo']['issues_count'] == 0 else 'OPTIMIZATIONS'} |")
    print(f"| Marketing Attribution | {results['tracking']['issues_count']} | {'PASS' if results['tracking']['issues_count'] == 0 else 'ACTION REQUIRED'} |")
    print(f"| **Overall Health** | **{results['total_issues']} total** | **{'HEALTHY' if results['total_issues'] == 0 else 'NEEDS ATTENTION'}** |")

    print("\n### 4. Recommended Actions")
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
