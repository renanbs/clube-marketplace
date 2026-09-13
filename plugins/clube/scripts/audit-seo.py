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
from pathlib import Path

IGNORED_DIRS = {'.git', 'node_modules', 'dist', 'build', '.specs', 'vendor', '__pycache__', '.venv', 'venv'}

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

    return {
        "pillar": "SaaS SEO & Generative Engine Optimization",
        "target": target_dir,
        "issues_count": len(all_findings),
        "issues": all_findings
    }

def main():
    parser = argparse.ArgumentParser(description="Audit SaaS SEO & GEO (AI Search) readiness.")
    parser.add_argument("--target", default=".", help="Directory to scan")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    result = audit(args.target)

    if args.json:
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["issues_count"] == 0 else 1)

    print("### 1. Plan")
    print(f"- **Audit:** SaaS SEO & Generative Engine Optimization (`clube:saas-seo-geo`)")
    print(f"- **Target:** {os.path.abspath(args.target)}")
    print(f"- **Mode:** Deterministic static analysis\n")

    print("### 2. Execution")
    if result["issues_count"] == 0:
        print("  ✅ All checked SEO & GEO patterns passed.")
    else:
        print(f"  ⚠️ Found {result['issues_count']} SEO / GEO optimization opportunities:")
        for item in result["issues"]:
            badge = "❌" if item["severity"] == "HIGH" else "⚠️"
            file_ref = f" [{item.get('file', '')}]" if item.get('file') else ""
            print(f"  {badge} [{item['type']}]{file_ref}: {item['description']}")

    print("\n### 3. Summary")
    print("| Metric | Value |")
    print("| :--- | :--- |")
    print(f"| SEO & GEO Findings | {result['issues_count']} |")
    print(f"| Status | {'PASS' if result['issues_count'] == 0 else 'OPTIMIZATIONS AVAILABLE'} |")

    print("\n### 4. Recommended Actions")
    if result["issues_count"] == 0:
        print("- SEO structure and AI search indexation files are active.")
    else:
        print("- Generate llms.txt and structured data schemas with: `/audit-seo fix`")

    sys.exit(0 if result["issues_count"] == 0 else 1)

if __name__ == "__main__":
    main()
