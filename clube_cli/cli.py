"""Command dispatch for clube-config. Port of the bash entrypoint.

Every command keeps the Plan / Execution / Summary output shape of the shell version;
what changed is that `check` now derives its exit code from the problems it found.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from . import check as check_mod
from . import deps, harness, runlog, sync

REPO_ROOT = Path(__file__).resolve().parent.parent

AUDIT_PILLARS = {
    "all": "audit-all.py",
    "360": "audit-all.py",
    "privacy": "audit-privacy.py",
    "performance": "audit-performance.py",
    "seo": "audit-seo.py",
    "geo": "audit-seo.py",
    "tracking": "audit-tracking.py",
    "attribution": "audit-tracking.py",
}

_USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
BOLD = "\033[1m" if _USE_COLOR else ""
RED = "\033[0;31m" if _USE_COLOR else ""
GREEN = "\033[0;32m" if _USE_COLOR else ""
NC = "\033[0m" if _USE_COLOR else ""


def _table(rows):
    print("| Field | Content |")
    print("| :--- | :--- |")
    for field, content in rows:
        print(f"| {field} | {content} |")


def cmd_help(_args=None):
    print(f"{BOLD}Clube AI Marketplace CLI{NC}\n")
    print(f"Usage: {BOLD}clube-config <command> [options]{NC}\n")
    print("Commands:")
    print("  check          Audit active harness, marketplace catalogs, and plugin integrity")
    print("  status         Alias for check")
    print("  audit [TYPE]   Run deterministic production audit (all, privacy, performance, seo, tracking)")
    print("  sync [DIR]     Synchronize @AGENTS.md pointers for CLAUDE.md, GEMINI.md, .cursorrules")
    print("  init [DIR]     Initialize project AI configuration and sync harness pointers")
    print("  doctor         Verify required and optional toolchain dependencies")
    print("  install        Install clube-config CLI into ~/.local/bin")
    print("  test           Run the Python test suite")
    print("  help           Display this help message")
    return 0


def cmd_check(args):
    repo_root = Path(args[0]) if args else REPO_ROOT
    active = harness.detect_active_harness()

    print(f"{BOLD}### 1. Plan{NC}\n")
    print("- **Command:** clube-config check")
    print("- **Action:** Audit AI host harness detection, marketplace catalogs, plugin manifests, and repository configuration")
    print("- **Reversible:** read-only / not applicable\n")

    print(f"{BOLD}### 2. Execution{NC}\n")
    print(f"  ✅ Detected active harness: {BOLD}{harness.friendly_name(active)}{NC} ({active})")

    agents_present = Path("AGENTS.md").is_file()
    print(f"  {'✅ Canonical instructions file found: ' + BOLD + 'AGENTS.md' + NC if agents_present else '⚠️ No ' + BOLD + 'AGENTS.md' + NC + ' found in current directory'}")

    for pointer in sync.DEFAULT_POINTERS:
        path = Path(pointer)
        if not path.is_file():
            print(f"  ⏭️ Missing pointer file: {BOLD}{pointer}{NC}")
        elif path.read_text(encoding="utf-8", errors="ignore").strip() == sync.POINTER_CONTENT:
            print(f"  ✅ Pointer aligned: {BOLD}{pointer}{NC} -> @AGENTS.md")
        else:
            print(f"  ⚠️ Custom/legacy content in: {BOLD}{pointer}{NC} (does not point to @AGENTS.md)")

    report, problems = check_mod.check_repository(repo_root)

    for manifest, present in report["market_manifests"].items():
        if present:
            print(f"  ✅ Marketplace catalog present: {BOLD}{manifest}{NC}")
        else:
            print(f"  ❌ Missing marketplace catalog: {BOLD}{manifest}{NC}")

    by_kind = {}
    for problem in problems:
        by_kind.setdefault(problem.kind, []).append(problem)

    for plugin_name, entry in report["plugins"].items():
        print(f"\n  [Plugin: {BOLD}{plugin_name}{NC}]")
        for manifest, present in entry["manifests"].items():
            if present:
                print(f"    ✅ Plugin manifest: {manifest}")
            else:
                print(f"    ⏭️ Optional plugin manifest omitted: {manifest}")

        skill_problems = by_kind.get("skill", [])
        for problem in skill_problems:
            print(f"    ❌ {problem.message}")
        if skill_problems:
            print(f"    ❌ Skills directory: {len(skill_problems)} problem(s) across {entry['skills']} skills")
        elif entry["references"]:
            print(f"    ✅ Skills directory: {entry['skills']} valid modular skills ({entry['references']} topic references)")
        elif entry["skills"]:
            print(f"    ✅ Skills directory: {entry['skills']} valid modular skills")

        for problem in by_kind.get("agent", []):
            print(f"    ❌ {problem.message}")
        if entry["invalid_agents"]:
            print(f"    ❌ Agents directory: {entry['invalid_agents']} invalid, {entry['agents']} valid specialist agents")
        elif entry["agents"]:
            print(f"    ✅ Agents directory: {entry['agents']} valid specialist agents")

        if entry["commands"]:
            print(f"    ✅ Commands directory: {entry['commands']} slash commands")

    semver = report["semver"]
    semver_problems = by_kind.get("semver", [])
    if semver_problems:
        detail = "; ".join(p.message for p in semver_problems)
        print(f"\n  ❌ SemVer parity mismatch: {detail}")
        semver_status = f"mismatch ({detail})"
    else:
        print(f"\n  ✅ SemVer parity: all manifests aligned at v{semver['target']}")
        semver_status = f"v{semver['target']} (all manifests aligned)"

    failures = len(problems)
    status = "passed (0 problems)" if failures == 0 else f"FAILED ({failures} problem(s))"

    print(f"\n{BOLD}### 3. Summary{NC}\n")
    _table([
        ("Status", status),
        ("Active Harness", harness.friendly_name(active)),
        ("SemVer Parity", semver_status),
        ("AGENTS.md Present", "yes" if agents_present else "no"),
        ("Source of Truth", "AGENTS.md"),
        ("Plugins Directory", "plugins/ (modular marketplace structure)"),
    ])

    runlog.log_event("info" if failures == 0 else "error", "check", status)
    return 0 if failures == 0 else 1


def cmd_sync(args):
    target = args[0] if args else "."
    print(f"{BOLD}### 1. Plan{NC}\n")
    print(f"- **Command:** clube-config sync {target}")
    print("- **Action:** Sync @AGENTS.md harness pointers for CLAUDE.md, GEMINI.md, and .cursorrules")
    print("- **Reversible:** Yes, pointer files can be modified or removed\n")

    print(f"{BOLD}### 2. Execution{NC}\n")
    try:
        result = sync.sync_pointers(target)
    except NotADirectoryError as exc:
        print(f"{RED}Error: {exc}{NC}", file=sys.stderr)
        return 1

    for path in result["created"]:
        print(f"  [CREATED]   {path} -> @AGENTS.md")
    for path in result["preserved"]:
        print(f"  [PRESERVED] {path} has custom/legacy content (not overwritten)")
    print(
        f"Harness sync complete: {len(result['created'])} created, "
        f"{len(result['aligned'])} aligned, {len(result['preserved'])} preserved/custom"
    )

    print(f"\n{BOLD}### 3. Summary{NC}\n")
    _table([
        ("Status", "sync complete"),
        ("Source of Truth", "AGENTS.md"),
        ("Target Directory", target),
    ])
    runlog.log_event("info", "sync", f"{len(result['created'])} created")
    return 0


def _report_dependencies(results):
    """Print the preflight table. Returns the number of blocking problems."""
    for result in results:
        dependency = result.dependency
        if result.ok:
            print(f"  ✅ {dependency.name}: {result.detail}")
        elif dependency.required:
            print(f"  ❌ {dependency.name}: {result.detail}")
            print(f"     {dependency.purpose}")
            print(f"     Install: {dependency.install_hint}")
        else:
            print(f"  ⚠️ {dependency.name}: {result.detail} (optional)")
            print(f"     {dependency.purpose}")
            print(f"     Install: {dependency.install_hint}")
    return len(deps.blocking(results))


def cmd_doctor(_args=None):
    """Verify the toolchain without touching any files."""
    print(f"{BOLD}### 1. Plan{NC}\n")
    print("- **Command:** clube-config doctor")
    print("- **Action:** Verify required and optional toolchain dependencies")
    print("- **Reversible:** read-only / not applicable\n")

    print(f"{BOLD}### 2. Execution{NC}\n")
    results = deps.check_all()
    blocking = _report_dependencies(results)
    optional_missing = len(deps.missing_optional(results))

    status = "passed" if blocking == 0 else f"FAILED ({blocking} required missing)"
    print(f"\n{BOLD}### 3. Summary{NC}\n")
    _table([
        ("Status", status),
        ("Required Missing", str(blocking)),
        ("Optional Missing", str(optional_missing)),
        ("Interpreter", sys.executable),
    ])
    return 0 if blocking == 0 else 1


def cmd_init(args):
    target = args[0] if args else "."
    print(f"{BOLD}=== CLUBE PROJECT AI ONBOARDING ==={NC}")
    print(f"Target directory: {BOLD}{target}{NC}\n")

    # Preflight before writing anything: a missing dependency discovered here is far
    # cheaper than one that surfaces as a cryptic failure three commands later.
    print(f"{BOLD}Checking toolchain...{NC}")
    results = deps.check_all()
    if _report_dependencies(results) > 0:
        print(f"\n{RED}Onboarding aborted: install the required dependencies above and re-run.{NC}",
              file=sys.stderr)
        runlog.log_event("error", "init", "blocked by missing required dependencies")
        return 1

    print()
    if sync.ensure_agents_md(target):
        print(f"  ✅ Created {target}/AGENTS.md")
    else:
        print(f"  ✅ Existing {target}/AGENTS.md preserved.")

    print("\nSyncing harness pointers...")
    return cmd_sync([target])


def cmd_install(_args):
    bin_dir = Path.home() / ".local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    link = bin_dir / "clube-config"
    source = REPO_ROOT / "bin" / "clube-config"
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to(source)
    print(f"{GREEN}✅ Installed clube-config to {link}{NC}")
    return 0


def cmd_audit(args):
    pillar = args[0] if args else "all"
    target = args[1] if len(args) > 1 else "."

    script = AUDIT_PILLARS.get(pillar)
    if not script:
        print(f"{RED}Unknown audit pillar: {pillar}{NC}", file=sys.stderr)
        print("Available pillars: all, privacy, performance, seo, tracking", file=sys.stderr)
        return 1

    return subprocess.call(
        [sys.executable, str(REPO_ROOT / "plugins" / "clube" / "scripts" / script), "--target", target]
    )


def cmd_test(args):
    """Run the test suite, preferring uv when available."""
    from shutil import which

    if which("uv"):
        cmd = ["uv", "run", "--group", "dev", "pytest", *args]
    else:
        cmd = [sys.executable, "-m", "pytest", *args]
    return subprocess.call(cmd, cwd=REPO_ROOT)


COMMANDS = {
    "check": cmd_check,
    "status": cmd_check,
    "audit": cmd_audit,
    "sync": cmd_sync,
    "init": cmd_init,
    "doctor": cmd_doctor,
    "install": cmd_install,
    "test": cmd_test,
    "help": cmd_help,
    "--help": cmd_help,
    "-h": cmd_help,
}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    command = argv[0] if argv else "help"
    handler = COMMANDS.get(command)
    if handler is None:
        print(f"{RED}Unknown command: {command}{NC}", file=sys.stderr)
        cmd_help()
        return 1
    return handler(argv[1:])
