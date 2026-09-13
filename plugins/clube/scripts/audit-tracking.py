#!/usr/bin/env python3
"""
audit-tracking.py — Deterministic Marketing Attribution & Tracking Auditor
Audits codebase for:
  - First-touch UTM & ad-click cookie persistence (root domain cookie flags)
  - Meta CAPI / Server-Side conversion tracking deduplication (event_id)
  - Database persistence for acquisition context (acquisition_context JSONB column)
"""

import os
import sys
import re
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

# Sibling module import
script_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(script_dir))
import ui  # noqa: E402

IGNORED_DIRS = {'.git', 'node_modules', 'dist', 'build', '.specs', 'vendor', '__pycache__', '.venv', 'venv', '.clube'}

def audit_cookie_domain(target_dir):
    findings = []
    has_tracking = False
    has_root_domain_cookie = False

    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for f in files:
            if f.endswith(('.ts', '.js', '.vue', '.jsx', '.tsx')):
                full_path = os.path.join(root, f)
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as src:
                        content = src.read()
                        if "utm_source" in content or "fbclid" in content or "gclid" in content:
                            has_tracking = True
                            if "domain=" in content or "domain:" in content or ".clube" in content or "rootDomain" in content:
                                has_root_domain_cookie = True
                except Exception:
                    pass

    if has_tracking and not has_root_domain_cookie:
        findings.append({
            "type": "Attribution Cookie Scope",
            "severity": "MEDIUM",
            "description": "UTM/ad tracking parameters detected, but no root domain cookie configuration found. Cookies set without root domain will not persist across subdomains (e.g., from landing page to app.domain.com)."
        })

    return findings

def audit_event_id_dedup(target_dir):
    findings = []
    has_fb_pixel = False
    has_event_id = False

    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for f in files:
            if f.endswith(('.ts', '.js', '.vue', '.jsx', '.tsx', '.go', '.py')):
                full_path = os.path.join(root, f)
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as src:
                        content = src.read()
                        if "fbq('track'" in content or 'fbq("track"' in content or "conversions_api" in content:
                            has_fb_pixel = True
                        if "eventID" in content or "event_id" in content or "eventId" in content:
                            has_event_id = True
                except Exception:
                    pass

    if has_fb_pixel and not has_event_id:
        findings.append({
            "type": "CAPI Deduplication",
            "severity": "HIGH",
            "description": "Meta Pixel or Conversions API tracking found without 'event_id'. Without matching event_id, browser and server conversions will be counted twice."
        })

    return findings

def audit_acquisition_persistence(target_dir):
    findings = []
    has_migrations = False
    has_acquisition_context = False

    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for f in files:
            if "migration" in f.lower() or f.endswith(('.sql', 'schema.prisma', 'models.py')):
                has_migrations = True
                full_path = os.path.join(root, f)
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as src:
                        content = src.read()
                        if "acquisition_context" in content or "utm_source" in content:
                            has_acquisition_context = True
                except Exception:
                    pass

    if has_migrations and not has_acquisition_context:
        findings.append({
            "type": "Marketing Data Persistence",
            "severity": "LOW",
            "description": "Database models/migrations detected, but no 'acquisition_context' JSONB column found on user/lead tables. Future purchase attribution to original ad campaigns will be lost."
        })

    return findings

def audit(target_dir):
    all_findings = []
    all_findings.extend(audit_cookie_domain(target_dir))
    all_findings.extend(audit_event_id_dedup(target_dir))
    all_findings.extend(audit_acquisition_persistence(target_dir))

    issues_count = len(all_findings)
    score = ui.calculate_health_score(issues_count, penalty_per_issue=25)
    verdict = "PASS" if issues_count == 0 else "ACTION RECOMMENDED"

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "audit": "tracking",
        "pillar": "Marketing Attribution & Analytics",
        "target": os.path.abspath(target_dir),
        "issues_count": issues_count,
        "score": score,
        "verdict": verdict,
        "issues": all_findings
    }

def main():
    parser = argparse.ArgumentParser(description="Audit marketing attribution & tracking.")
    parser.add_argument("--target", default=".", help="Directory to scan")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    result = audit(args.target)
    ui.save_runlog(result)

    if args.json:
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["issues_count"] == 0 else 1)

    ui.print_header("CLUBE ATTRIBUTION & TRACKING AUDIT", "Deterministic UTM Cookies, Meta CAPI event_id & DB Persistence Scanner")

    print(f"{ui.BOLD}### 1. Plan{ui.RESET}\n")
    print(f"- **Audit:** Marketing Attribution & Tracking (`clube:marketing-attribution-analytics`)")
    print(f"- **Target:** {result['target']}")
    print(f"- **Mode:** Deterministic static analysis\n")

    print(f"{ui.BOLD}### 2. Execution{ui.RESET}\n")
    if result["issues_count"] == 0:
        print(f"  {ui.format_badge('PASS')} All checked marketing attribution patterns passed.\n")
    else:
        print(f"  {ui.format_badge('WARN')} Found {result['issues_count']} attribution & tracking finding(s):\n")
        for item in result["issues"]:
            badge = ui.format_badge("FAIL") if item["severity"] == "HIGH" else ui.format_badge("WARN")
            file_ref = f" [{item.get('file', '')}]" if item.get('file') else ""
            print(f"  {badge} [{item['type']}]{file_ref}: {item['description']}")
        print()

    print(f"{ui.BOLD}### 3. Summary{ui.RESET}\n")
    print(f"Health Score: {ui.render_health_bar(result['score'])}\n")

    summary_headers = ["Metric", "Value", "Status"]
    summary_rows = [
        ["Attribution Findings", str(result["issues_count"]), ui.format_badge("PASS" if result["issues_count"] == 0 else "ACTION RECOMMENDED", "PASS" if result["issues_count"] == 0 else f"{result['issues_count']} ITEMS")],
        ["Health Score", f"{result['score']}%", ui.format_badge("PASS" if result["score"] >= 80 else ("WARN" if result["score"] >= 50 else "FAIL"))],
        ["Runlog Saved", ".clube/audit-last.json", ui.format_badge("PASS")],
    ]
    print(ui.render_table(summary_headers, summary_rows))

    print(f"\n{ui.BOLD}### 4. Recommended Actions{ui.RESET}\n")
    if result["issues_count"] == 0:
        print("- Tracking cookies and attribution persistence are aligned.")
    else:
        print("- Implement root domain cookies and acquisition_context schema with: `/audit-tracking fix`")

    sys.exit(0 if result["issues_count"] == 0 else 1)

if __name__ == "__main__":
    main()
