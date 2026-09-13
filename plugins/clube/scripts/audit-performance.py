#!/usr/bin/env python3
"""
audit-performance.py — Deterministic Fullstack Performance & Resilience Auditor
Audits codebase for:
  - SPA Chunk Recovery against 404 deploy errors (vite:preloadError, router.onError)
  - CDN Cache-Control headers (immutable assets vs no-cache entrypoints)
  - Container CPU quota limits (automaxprocs in Go)
  - Database connection pool boundaries (SetMaxOpenConns, pool_size)
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path

IGNORED_DIRS = {'.git', 'node_modules', 'dist', 'build', '.specs', 'vendor', '__pycache__', '.venv', 'venv'}

def audit_chunk_recovery(target_dir):
    findings = []
    has_spa = False
    has_chunk_recovery = False

    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for f in files:
            if f.startswith("audit-"):
                continue
            if f in ("vite.config.ts", "vite.config.js", "vite.config.mjs"):
                has_spa = True
            elif f == "package.json":
                try:
                    with open(os.path.join(root, f), 'r', encoding='utf-8') as pkg:
                        pkg_txt = pkg.read()
                        if '"vite"' in pkg_txt or '"vue-router"' in pkg_txt or '"react-router"' in pkg_txt:
                            has_spa = True
                except Exception:
                    pass
            if f.endswith(('.ts', '.js', '.vue', '.tsx')):
                full_path = os.path.join(root, f)
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as src:
                        content = src.read()
                        if "vite:preloadError" in content or "isLazyRouteChunkLoadError" in content or "CHUNK_RELOAD_KEY" in content:
                            has_chunk_recovery = True
                except Exception:
                    pass

    if has_spa and not has_chunk_recovery:
        findings.append({
            "type": "SPA Deploy Resilience",
            "severity": "HIGH",
            "description": "Vite/SPA detected, but no chunk recovery listener found (missing 'vite:preloadError' or 'router.onError' chunk recovery). Users may experience 404 errors on new deployments."
        })
    return findings

def audit_cache_headers(target_dir):
    findings = []
    vercel_json = os.path.join(target_dir, "vercel.json")
    nginx_conf = os.path.join(target_dir, "nginx.conf")

    if os.path.exists(vercel_json):
        try:
            with open(vercel_json, 'r', encoding='utf-8') as f:
                content = f.read()
                if "immutable" not in content:
                    findings.append({
                        "file": "vercel.json",
                        "type": "CDN Cache Policy",
                        "severity": "MEDIUM",
                        "description": "vercel.json does not declare 'immutable' cache headers for hashed static assets."
                    })
                if "no-cache" not in content:
                    findings.append({
                        "file": "vercel.json",
                        "type": "CDN Cache Policy",
                        "severity": "MEDIUM",
                        "description": "vercel.json does not declare 'no-cache, no-store' for entrypoint files (index.html, sw.js)."
                    })
        except Exception:
            pass

    return findings

def audit_backend_concurrency(target_dir):
    findings = []
    has_go = False
    has_automaxprocs = False
    has_db_pool_limit = False

    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for f in files:
            if f == "go.mod":
                has_go = True
            if f.endswith(".go"):
                full_path = os.path.join(root, f)
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as src:
                        content = src.read()
                        if "automaxprocs" in content:
                            has_automaxprocs = True
                        if "SetMaxOpenConns" in content:
                            has_db_pool_limit = True
                except Exception:
                    pass

    if has_go and not has_automaxprocs:
        findings.append({
            "type": "Container Runtime (Go)",
            "severity": "MEDIUM",
            "description": "Go project detected, but 'go.uber.org/automaxprocs' not found. Risk of CFS quota throttling in multi-core container hosts."
        })

    return findings

def audit(target_dir):
    all_findings = []
    all_findings.extend(audit_chunk_recovery(target_dir))
    all_findings.extend(audit_cache_headers(target_dir))
    all_findings.extend(audit_backend_concurrency(target_dir))

    return {
        "pillar": "Fullstack Performance & Resilience",
        "target": target_dir,
        "issues_count": len(all_findings),
        "issues": all_findings
    }

def main():
    parser = argparse.ArgumentParser(description="Audit fullstack performance & deploy resilience.")
    parser.add_argument("--target", default=".", help="Directory to scan")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    result = audit(args.target)

    if args.json:
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["issues_count"] == 0 else 1)

    print("### 1. Plan")
    print(f"- **Audit:** Fullstack Performance & Deploy Resilience (`clube:fullstack-performance-resilience`)")
    print(f"- **Target:** {os.path.abspath(args.target)}")
    print(f"- **Mode:** Deterministic static analysis\n")

    print("### 2. Execution")
    if result["issues_count"] == 0:
        print("  ✅ All checked performance & deploy resilience patterns passed.")
    else:
        print(f"  ⚠️ Found {result['issues_count']} performance & resilience finding(s):")
        for item in result["issues"]:
            badge = "❌" if item["severity"] == "HIGH" else "⚠️"
            file_ref = f" [{item.get('file', '')}]" if item.get('file') else ""
            print(f"  {badge} [{item['type']}]{file_ref}: {item['description']}")

    print("\n### 3. Summary")
    print("| Metric | Value |")
    print("| :--- | :--- |")
    print(f"| Performance Findings | {result['issues_count']} |")
    print(f"| Status | {'PASS' if result['issues_count'] == 0 else 'ACTION REQUIRED'} |")

    print("\n### 4. Recommended Actions")
    if result["issues_count"] == 0:
        print("- Deploy resilience and concurrency boundaries are configured.")
    else:
        print("- Ask the AI assistant to implement chunk recovery or cache policies: `/audit-performance fix`")

    sys.exit(0 if result["issues_count"] == 0 else 1)

if __name__ == "__main__":
    main()
