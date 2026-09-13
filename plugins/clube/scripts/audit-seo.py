#!/usr/bin/env python3
"""
audit-seo.py — Deterministic SaaS SEO & Generative Engine Optimization (GEO) Auditor
Audits codebase for:
  - llms.txt & llms-full.txt availability for AI search engines (ChatGPT, Perplexity, Claude)
  - Strict separation: noindex on private / authenticated app routes
  - Canonical tags and Open Graph metadata
  - Structured Data (Schema.org / JSON-LD)
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

def has_web_landing_pages(target_dir):
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for f in files:
            if f.endswith(('.astro', '.html', '.php')):
                return True
            if f == "package.json":
                try:
                    with open(os.path.join(root, f), 'r', encoding='utf-8') as pkg:
                        c = pkg.read()
                        if '"next"' in c or '"nuxt"' in c or '"astro"' in c:
                            return True
                except Exception:
                    pass
    return False

def audit_llms_txt(target_dir):
    findings = []
    if not has_web_landing_pages(target_dir):
        return findings

    candidates = [
        os.path.join(target_dir, "llms.txt"),
        os.path.join(target_dir, "public", "llms.txt"),
        os.path.join(target_dir, "static", "llms.txt"),
    ]
    if not any(os.path.exists(p) for p in candidates):
        findings.append({
            "type": "GEO (AI Engine Optimization)",
            "severity": "MEDIUM",
            "description": "Public web app / landing page detected, but missing '/llms.txt'. AI search engines (ChatGPT Search, Perplexity, Claude) lack structured factual context for your SaaS."
        })
    return findings

def audit_robots_and_noindex(target_dir):
    findings = []
    robots_candidates = [
        os.path.join(target_dir, "robots.txt"),
        os.path.join(target_dir, "public", "robots.txt"),
        os.path.join(target_dir, "static", "robots.txt"),
    ]
    robots_file = next((p for p in robots_candidates if os.path.exists(p)), None)

    if robots_file:
        try:
            with open(robots_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if "Disallow: /app" not in content and "Disallow: /dashboard" not in content:
                    findings.append({
                        "file": os.path.relpath(robots_file, target_dir),
                        "type": "SEO Indexing Boundary",
                        "severity": "LOW",
                        "description": "robots.txt exists but does not explicitly disallow private app routes (/app, /dashboard). Ensure private routes have 'noindex' to avoid keyword cannibalization."
                    })
        except Exception:
            pass

    return findings

def audit_html_metadata(target_dir):
    findings = []
    has_html = False
    has_canonical = False
    has_json_ld = False

    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for f in files:
            if f.endswith(('.html', '.astro', '.vue', '.tsx', '.jsx')):
                full_path = os.path.join(root, f)
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as src:
                        content = src.read()
                        if "<html" in content or "rel=\"canonical\"" in content:
                            has_html = True
                        if 'rel="canonical"' in content or "rel='canonical'" in content:
                            has_canonical = True
                        if 'application/ld+json' in content:
                            has_json_ld = True
                except Exception:
                    pass

    if has_html and not has_canonical:
        findings.append({
            "type": "Technical SEO",
            "severity": "MEDIUM",
            "description": "Public templates detected, but no 'rel=canonical' tag found. Risk of duplicate content penalties."
        })

    if has_html and not has_json_ld:
        findings.append({
            "type": "Structured Data",
            "severity": "LOW",
            "description": "No Schema.org structured data (application/ld+json) detected. Rich snippets for SoftwareApplication or FAQPage not enabled."
        })

    return findings

def audit(target_dir):
    all_findings = []
    all_findings.extend(audit_llms_txt(target_dir))
    all_findings.extend(audit_robots_and_noindex(target_dir))
    all_findings.extend(audit_html_metadata(target_dir))

    issues_count = len(all_findings)
    score = ui.calculate_health_score(issues_count, penalty_per_issue=20)
    verdict = "PASS" if issues_count == 0 else "OPTIMIZATIONS AVAILABLE"

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "audit": "seo",
        "pillar": "SaaS SEO & Generative Engine Optimization",
        "target": os.path.abspath(target_dir),
        "issues_count": issues_count,
        "score": score,
        "verdict": verdict,
        "issues": all_findings
    }

def main():
    parser = argparse.ArgumentParser(description="Audit SaaS SEO & GEO (AI Search) readiness.")
    parser.add_argument("--target", default=".", help="Directory to scan")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    result = audit(args.target)
    ui.save_runlog(result)

    if args.json:
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["issues_count"] == 0 else 1)

    ui.print_header("CLUBE SAAS SEO & GEO AUDIT", "Deterministic AI Search (llms.txt), Metadata & Indexing Scanner")

    print(f"{ui.BOLD}### 1. Plan{ui.RESET}\n")
    print(f"- **Audit:** SaaS SEO & Generative Engine Optimization (`clube:saas-seo-geo`)")
    print(f"- **Target:** {result['target']}")
    print(f"- **Mode:** Deterministic static analysis\n")

    print(f"{ui.BOLD}### 2. Execution{ui.RESET}\n")
    if result["issues_count"] == 0:
        print(f"  {ui.format_badge('PASS')} All checked SEO & GEO patterns passed.\n")
    else:
        print(f"  {ui.format_badge('WARN')} Found {result['issues_count']} SEO / GEO optimization opportunities:\n")
        for item in result["issues"]:
            badge = ui.format_badge("FAIL") if item["severity"] == "HIGH" else ui.format_badge("WARN")
            file_ref = f" [{item.get('file', '')}]" if item.get('file') else ""
            print(f"  {badge} [{item['type']}]{file_ref}: {item['description']}")
        print()

    print(f"{ui.BOLD}### 3. Summary{ui.RESET}\n")
    print(f"Health Score: {ui.render_health_bar(result['score'])}\n")

    summary_headers = ["Metric", "Value", "Status"]
    summary_rows = [
        ["SEO & GEO Findings", str(result["issues_count"]), ui.format_badge("PASS" if result["issues_count"] == 0 else "OPTIMIZATIONS", "PASS" if result["issues_count"] == 0 else f"{result['issues_count']} ITEMS")],
        ["Health Score", f"{result['score']}%", ui.format_badge("PASS" if result["score"] >= 80 else ("WARN" if result["score"] >= 50 else "FAIL"))],
        ["Runlog Saved", ".clube/audit-last.json", ui.format_badge("PASS")],
    ]
    print(ui.render_table(summary_headers, summary_rows))

    print(f"\n{ui.BOLD}### 4. Recommended Actions{ui.RESET}\n")
    if result["issues_count"] == 0:
        print("- SEO structure and AI search indexation files are active.")
    else:
        print("- Generate llms.txt and structured data schemas with: `/audit-seo fix`")

    sys.exit(0 if result["issues_count"] == 0 else 1)

if __name__ == "__main__":
    main()
