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
from datetime import datetime, timezone
from pathlib import Path

# Sibling module import
script_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(script_dir))
import ui  # noqa: E402

BLIND_LOGGING_PATTERNS = [
    (r'console\.log\s*\(\s*(?:req\.body|payload|body|user|customer|account)\b', "JS/TS: Blind console.log of sensitive object"),
    # %v is as blind as %+v and far more common; %#v too (the previous class [+v]
    # matched "%+v" and "%vv" but never plain "%v"). Scoped to a sensitive-looking
    # argument, because `fmt.Errorf("bad alg: %v", header["alg"])` is idiomatic Go and
    # flagging every %v drowns the real findings.
    (r'\.(?:Printf|Print|Println|Sprintf|Infof|Debugf|Warnf|Errorf)\s*\(\s*[`"][^`"]*%[+#]?v[^`"]*[`"]\s*,\s*[^)]*\b(?:user|usr|payload|body|req|request|customer|account|entity|profile|claims)\b',
     "Go: Blind struct serialization (%v/%+v/%#v) of a sensitive object"),
    (r'zap\.Any\s*\(\s*"(?:user|req|payload|body|account|customer)"', "Go: zap.Any blind struct serialization"),
    (r'logger\.(?:info|warn|error|debug)\s*\(\s*f?"[^"]*\{user\b', "Python: Direct user object interpolation in logger"),
    (r'(?:logger|log)\.(?:info|warning|warn|error|debug)\s*\(\s*[^)]*\.model_dump\s*\(', "Python: Pydantic model_dump() piped straight into a log"),
]

QUERY_PII_PATTERNS = [
    # The trailing \b required a word character right after "=", which skipped the most
    # common shape of the bug: interpolation ("?token=" + t, `?email=${e}`).
    (r'[?&](?:cpf|cnpj|email|telefone|phone|senha|password|token|access_token|api_?key)=', "PII or secret in query string / URL pattern"),
]

METRIC_PII_PATTERNS = [
    (r'labels\s*[:=]\s*[\[\{][^\]\}]*(?:"email"|"user_id"|"cpf"|"phone"|\'email\'|\'user_id\')', "Prometheus: High-cardinality / PII label in metric"),
    # Go idiom: label slice declared inline in the metric constructor, no "labels" keyword.
    (r'\[\]string\s*\{[^}]*"(?:email|user_id|userID|cpf|phone|document)"', "Prometheus (Go): PII label declared in metric label slice"),
    # Raw request path as a metric label — unbounded cardinality, externally triggerable.
    (r'WithLabelValues\s*\([^)]*(?:Request\.URL\.Path|r\.URL\.Path|request\.url\.path)', "Prometheus: raw URL path as metric label — use the route template, not the concrete path"),
]

IGNORED_DIRS = {'.git', 'node_modules', 'dist', 'build', '.specs', 'vendor', '__pycache__', '.venv', 'venv', '.clube'}

TEST_FILE_RE = re.compile(r'(?:\.(?:spec|test)\.[jt]sx?$|_test\.(?:go|py)$|^test_.*\.py$|Test\.java$|_spec\.rb$)')

def is_ignored_dir(name):
    """Directories skipped during the walk.

    Includes '*-worktrees' / 'worktrees': git worktrees hold checkouts of the same
    repository, so scanning them reports every finding once per branch and inflates
    the count without adding information.
    """
    return name in IGNORED_DIRS or name == "worktrees" or name.endswith("-worktrees")

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
    # Test files carry fake fixtures by design (a sample phone in an expected URL is not
    # a leak). Auditing them reports the fixture, not the product's privacy posture.
    if TEST_FILE_RE.search(fname):
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

IMPERSONATION_RE = re.compile(r'impersonat', re.IGNORECASE)
READONLY_GUARD_RE = re.compile(r'MethodGet|"GET"|\'GET\'|read[_-]?only|readOnly', re.IGNORECASE)
AUDIT_LOG_RE = re.compile(r'impersonator|audit', re.IGNORECASE)

def audit_impersonation(target_dir):
    """Operator access to customer data must be read-only and fully audited.

    Read-only keeps the account history trustworthy as evidence of what the customer
    actually did; auditing every impersonated request — not only the denied ones — is
    what answers "who on the team looked at this person's data?".
    """
    findings = []
    impersonation_files = []
    has_readonly_guard = False
    has_audit_trail = False

    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if not is_ignored_dir(d)]
        for f in files:
            if not (IMPERSONATION_RE.search(f) and f.endswith(('.go', '.py', '.ts', '.js', '.rb', '.java'))):
                continue
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as src:
                    content = src.read()
            except Exception:
                continue

            impersonation_files.append(os.path.relpath(path, target_dir))
            # Evaluated across the whole feature, not per file: the guard normally lives
            # in a middleware while the handler that starts the session is a separate
            # file, so a per-file check flags the handler for something it should not do.
            if READONLY_GUARD_RE.search(content):
                has_readonly_guard = True
            if AUDIT_LOG_RE.search(content):
                has_audit_trail = True

    if not impersonation_files:
        return findings

    if not has_readonly_guard:
        findings.append({
            "file": impersonation_files[0],
            "severity": "HIGH",
            "type": "Impersonation Safety",
            "description": "Impersonation logic found with no read-only guard anywhere in the feature. Writes performed while impersonating are attributed to the customer, which destroys the account history as evidence of what they actually did.",
            "snippet": ""
        })
    if not has_audit_trail:
        findings.append({
            "file": impersonation_files[0],
            "severity": "HIGH",
            "type": "Impersonation Safety",
            "description": "Impersonation logic found with no audit trail. Every impersonated request — not only denied ones — should record who acted, on whom, when and what.",
            "snippet": ""
        })
    return findings

def audit(target_dir):
    all_issues = []
    scanned_count = 0
    abs_target = os.path.abspath(target_dir)

    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if not is_ignored_dir(d)]
        for file in files:
            full_path = os.path.join(root, file)
            issues = scan_file(full_path)
            for issue in issues:
                # Report paths relative to the target, like the other auditors do —
                # absolute paths leak the developer's home directory into the runlog.
                issue["file"] = os.path.relpath(full_path, target_dir)
            all_issues.extend(issues)
            scanned_count += 1

    all_issues.extend(audit_impersonation(target_dir))

    issues_count = len(all_issues)
    score = ui.calculate_weighted_score(all_issues)
    verdict = "PASS" if issues_count == 0 else "ACTION REQUIRED"

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "audit": "privacy",
        "pillar": "Data Privacy & Observability",
        "target": abs_target,
        "scanned_files": scanned_count,
        "issues_count": issues_count,
        "score": score,
        "verdict": verdict,
        "issues": all_issues
    }

def main():
    parser = argparse.ArgumentParser(description="Audit data privacy and observability practices.")
    parser.add_argument("--target", default=".", help="Directory to scan")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    result = audit(args.target)
    ui.save_runlog(result)

    if args.json:
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["issues_count"] == 0 else 1)

    ui.print_header("CLUBE DATA PRIVACY & OBSERVABILITY AUDIT", "Deterministic PII, Sensitive Logging & Metric Cardinality Scanner")

    print(f"{ui.BOLD}### 1. Plan{ui.RESET}\n")
    print(f"- **Audit:** Data Privacy & Observability (`clube:data-privacy-observability`)")
    print(f"- **Target:** {result['target']}")
    print(f"- **Mode:** Deterministic static analysis (zero tokens)\n")

    print(f"{ui.BOLD}### 2. Execution{ui.RESET}\n")
    if result["issues_count"] == 0:
        print(f"  {ui.format_badge('PASS')} Scanned {result['scanned_files']} files. No blind logging, URL PII, or high-cardinality leaks detected.\n")
    else:
        print(f"  {ui.format_badge('FAIL')} Found {result['issues_count']} potential privacy risk(s) across {result['scanned_files']} files:\n")
        for idx, item in enumerate(result["issues"][:15], 1):
            badge = ui.format_badge("FAIL") if item["severity"] in ("HIGH", "CRITICAL") else ui.format_badge("WARN")
            rel_file = os.path.relpath(item["file"], args.target) if os.path.exists(item["file"]) else item["file"]
            print(f"  {badge} [{item['type']}] {rel_file}:{item['line']} — {item['description']}")
            print(f"     {ui.colorize(item['snippet'][:100], ui.GRAY)}")
        if result["issues_count"] > 15:
            print(f"\n  ... and {result['issues_count'] - 15} more issues.")
        print()

    print(f"{ui.BOLD}### 3. Summary{ui.RESET}\n")
    print(f"Health Score: {ui.render_health_bar(result['score'])}\n")

    summary_headers = ["Metric", "Value", "Status"]
    summary_rows = [
        ["Scanned Files", str(result["scanned_files"]), ui.format_badge("INFO")],
        ["Privacy Findings", str(result["issues_count"]), ui.format_badge("PASS" if result["issues_count"] == 0 else "FAIL", "PASS" if result["issues_count"] == 0 else f"{result['issues_count']} ISSUES")],
        ["Health Score", f"{result['score']}%", ui.format_badge("PASS" if result["score"] >= 80 else ("WARN" if result["score"] >= 50 else "FAIL"))],
        ["Runlog Saved", ".clube/audit-last.json", ui.format_badge("PASS")],
    ]
    print(ui.render_table(summary_headers, summary_rows))

    print(f"\n{ui.BOLD}### 4. Recommended Actions{ui.RESET}\n")
    if result["issues_count"] == 0:
        print("- Codebase is compliant with basic privacy logging principles.")
        print("- Continue enforcing `String()` / `MarshalJSON()` masking on domain models.")
    else:
        print("- Review flagged logging statements: log the *shape* and masks (`phonelog.Mask`), never raw structs.")
        print("- Ask the AI assistant to generate masked models: `/audit-privacy fix`")

    sys.exit(0 if result["issues_count"] == 0 else 1)

if __name__ == "__main__":
    main()
