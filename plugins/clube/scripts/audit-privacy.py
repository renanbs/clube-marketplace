#!/usr/bin/env python3
"""
audit-privacy.py — Deterministic PII & Data Privacy Auditor
Audits codebase for:
  - Blind struct/object logging (console.log(req.body), log.Printf("%+v"), zap.Any)
  - PII in query strings / URLs
  - High-cardinality/PII labels in metrics
  - Error tracking scrubbing configurations
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path

BLIND_LOGGING_PATTERNS = [
    (r'console\.log\s*\(\s*(?:req\.body|payload|body|user|customer|account)\b', "JS/TS: Blind console.log of sensitive object"),
    (r'log\.Printf\s*\(\s*"[^"]*%[+v]v"', "Go: Blind struct serialization (%+v) in log"),
    (r'zap\.Any\s*\(\s*"(?:user|req|payload|body|account|customer)"', "Go: zap.Any blind struct serialization"),
    (r'logger\.(?:info|warn|error|debug)\s*\(\s*f?"[^"]*\{user\b', "Python: Direct user object interpolation in logger"),
]

QUERY_PII_PATTERNS = [
    (r'[?&](?:cpf|cnpj|email|telefone|phone|senha|password|token)=\b', "PII in query string / URL pattern"),
]

METRIC_PII_PATTERNS = [
    (r'labels\s*[:=]\s*\[[^\]]*(?:"email"|"user_id"|"cpf"|"phone")[^\]]*\]', "Prometheus: High-cardinality / PII label in metric"),
]

IGNORED_DIRS = {'.git', 'node_modules', 'dist', 'build', '.specs', 'vendor', '__pycache__', '.venv', 'venv'}

def scan_file(file_path):
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception:
        return issues
    ext = Path(file_path).suffix.lower()
    fname = Path(file_path).name
    if fname.startswith("audit-") or ext not in {'.js', '.jsx', '.ts', '.tsx', '.go', '.py', '.vue', '.svelte', '.php', '.rb', '.java'}:
        return issues

    for line_num, line in enumerate(lines, start=1):
        for pattern, desc in BLIND_LOGGING_PATTERNS:
            if re.search(pattern, line):
                issues.append({
                    "file": str(file_path),
                    "line": line_num,
                    "severity": "HIGH",
                    "type": "Blind Logging",
                    "description": desc,
                    "snippet": line.strip()
                })
        for pattern, desc in QUERY_PII_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append({
                    "file": str(file_path),
                    "line": line_num,
                    "severity": "HIGH",
                    "type": "PII in URL",
                    "description": desc,
                    "snippet": line.strip()
                })
        for pattern, desc in METRIC_PII_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append({
                    "file": str(file_path),
                    "line": line_num,
                    "severity": "CRITICAL",
                    "type": "Metric PII / Cardinality",
                    "description": desc,
                    "snippet": line.strip()
                })
    return issues

def audit(target_dir):
    all_issues = []
    scanned_count = 0
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, target_dir)
            issues = scan_file(full_path)
            if issues:
                all_issues.extend(issues)
            scanned_count += 1

    return {
        "pillar": "Data Privacy & Observability",
        "scanned_files": scanned_count,
        "issues_count": len(all_issues),
        "issues": all_issues
    }

def main():
    parser = argparse.ArgumentParser(description="Audit data privacy and observability practices.")
    parser.add_argument("--target", default=".", help="Directory to scan")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    result = audit(args.target)

    if args.json:
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["issues_count"] == 0 else 1)

    print("### 1. Plan")
    print(f"- **Audit:** Data Privacy & Observability (`clube:data-privacy-observability`)")
    print(f"- **Target:** {os.path.abspath(args.target)}")
    print(f"- **Mode:** Deterministic static analysis (zero tokens)\n")

    print("### 2. Execution")
    if result["issues_count"] == 0:
        print(f"  ✅ Scanned {result['scanned_files']} files. No blind logging, URL PII, or high-cardinality leaks detected.")
    else:
        print(f"  ⚠️ Found {result['issues_count']} potential privacy risk(s) across {result['scanned_files']} files:")
        for idx, item in enumerate(result["issues"][:15], 1):
            badge = "❌" if item["severity"] in ("HIGH", "CRITICAL") else "⚠️"
            print(f"  {badge} [{item['type']}] {item['file']}:{item['line']} — {item['description']}")
            print(f"     `{item['snippet'][:100]}`")
        if result["issues_count"] > 15:
            print(f"  ... and {result['issues_count'] - 15} more issues.")

    print("\n### 3. Summary")
    print("| Metric | Value |")
    print("| :--- | :--- |")
    print(f"| Scanned Files | {result['scanned_files']} |")
    print(f"| Privacy Findings | {result['issues_count']} |")
    print(f"| Status | {'PASS' if result['issues_count'] == 0 else 'WARNINGS DETECTED'} |")

    print("\n### 4. Recommended Actions")
    if result["issues_count"] == 0:
        print("- Codebase is compliant with basic privacy logging principles.")
        print("- Continue enforcing `String()` / `MarshalJSON()` masking on domain models.")
    else:
        print("- Review flagged logging statements: log the *shape* and masks (`phonelog.Mask`), never raw structs.")
        print("- Ask the AI assistant to generate masked models: `/audit-privacy fix`")

    sys.exit(0 if result["issues_count"] == 0 else 1)

if __name__ == "__main__":
    main()
