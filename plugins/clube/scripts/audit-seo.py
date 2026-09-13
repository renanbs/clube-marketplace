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

PUBLIC_DIRS = ("", "public", "static", "www", "dist")

def find_public_file(target_dir, filename):
    """Locate a public-root file (llms.txt, robots.txt, ...).

    Walks the tree instead of probing only target_dir, so the check still works when
    the target is a monorepo whose sites live in sibling subdirectories
    (code/site-lp/public/llms.txt) rather than at the repository root.
    """
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        if filename not in files:
            continue
        # Only accept it when it sits somewhere that is actually served at the URL root.
        if os.path.basename(root) in PUBLIC_DIRS or os.path.abspath(root) == os.path.abspath(target_dir):
            return os.path.join(root, filename)
    return None

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

    llms = find_public_file(target_dir, "llms.txt")
    if not llms:
        findings.append({
            "type": "GEO (AI Engine Optimization)",
            "severity": "MEDIUM",
            "description": "Public web app / landing page detected, but missing '/llms.txt'. AI search engines (ChatGPT Search, Perplexity, Claude) lack structured factual context for your SaaS."
        })
        return findings

    # llms-full.txt only makes sense once llms.txt exists — it is the deep-context
    # companion referenced from the index.
    if not find_public_file(target_dir, "llms-full.txt"):
        findings.append({
            "file": os.path.relpath(llms, target_dir),
            "type": "GEO (AI Engine Optimization)",
            "severity": "LOW",
            "description": "'llms.txt' found but no 'llms-full.txt'. Models with large context windows have no aggregated source for feature detail, full FAQ and comparison tables — generate it at build time from the same content sources."
        })
    return findings

def audit_robots_and_noindex(target_dir):
    findings = []
    robots_file = find_public_file(target_dir, "robots.txt")

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

NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex', re.IGNORECASE)
CANONICAL_RE = re.compile(r'rel=["\']canonical["\']', re.IGNORECASE)

def audit_html_metadata(target_dir):
    findings = []
    has_indexable_html = False
    has_canonical = False
    has_json_ld = False

    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for f in files:
            if not f.endswith(('.html', '.astro', '.vue', '.tsx', '.jsx')):
                continue
            full_path = os.path.join(root, f)
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as src:
                    content = src.read()
            except Exception:
                continue

            is_noindex = bool(NOINDEX_RE.search(content))
            file_has_canonical = bool(CANONICAL_RE.search(content))

            if ("<html" in content or file_has_canonical) and not is_noindex:
                has_indexable_html = True
            if file_has_canonical and not is_noindex:
                has_canonical = True
            if 'application/ld+json' in content:
                has_json_ld = True

            # A noindex page telling crawlers "this is the canonical address to index"
            # is self-contradictory; the canonical is ignored and the pair is a smell
            # that a private entrypoint was copied from a public template.
            if is_noindex and file_has_canonical:
                findings.append({
                    "file": os.path.relpath(full_path, target_dir),
                    "type": "Technical SEO",
                    "severity": "MEDIUM",
                    "description": "Page declares 'noindex' and a 'rel=canonical' at the same time. The two signals contradict each other and the canonical is ignored — remove the canonical from private entrypoints instead of pointing it somewhere."
                })

    # Only indexable templates are expected to carry a canonical.
    if has_indexable_html and not has_canonical:
        findings.append({
            "type": "Technical SEO",
            "severity": "MEDIUM",
            "description": "Indexable public templates detected, but no 'rel=canonical' tag found. Risk of duplicate content penalties."
        })

    if has_indexable_html and not has_json_ld:
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
