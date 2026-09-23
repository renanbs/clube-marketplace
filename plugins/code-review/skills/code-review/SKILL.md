---
name: code-review
description: |
  Cross-project code review discipline: correctness, naming, error handling, performance,
  security surface, test quality, and project conventions. Language-agnostic core with
  on-demand language-specific references (Go, TypeScript, Rust).
  Activate this skill whenever reviewing a diff, PR, branch, or staged changes.
license: Apache-2.0
metadata:
  version: v0.1.0
  author: clubedepontos
---

# Code Review — Core Discipline

Structured, evidence-based code review workflow. The reviewer loads this entrypoint, detects languages in the diff, and navigates to the relevant language references on demand.

---

## 1. Severity Scale

| Severity | Definition | Blocks Merge? |
| :--- | :--- | :--- |
| **CRITICAL** | Security vulnerability, data loss, or crash in production path | Yes |
| **HIGH** | Incorrect behavior, broken contract, or regression | Yes |
| **MEDIUM** | Performance hazard, poor error handling, or missing edge case | Author discretion |
| **LOW** | Naming, readability, style, or minor improvement | No |
| **NIT** | Cosmetic preference with no functional impact | No |

---

## 2. Review Checklist

| Category | What to examine |
| :--- | :--- |
| **Correctness** | Logic, edge cases, off-by-one, null/nil/undefined safety, concurrency races, state transitions |
| **Error Handling** | Errors propagated not swallowed, user-facing messages safe, retries idempotent, panics/unwrap guarded |
| **Naming & Readability** | Names reveal intent, no abbreviation soup, consistent vocabulary, functions ≤40 lines |
| **Performance** | Unbounded allocations, N+1 queries, unnecessary copies, hot-path allocations, missing pagination |
| **Security Surface** | Injection (SQL, XSS, command), auth/authz on every endpoint, secrets not in code, input validation at boundary |
| **Test Quality** | Tests defend observable behavior not implementation, boundaries covered, deterministic, no mock echoes |
| **API & Contract** | Breaking changes flagged, backwards compatibility, documented public surface, error codes stable |
| **Conventions** | Project AGENTS.md rules, 4-phase output (if skill/agent PR), naming conventions, file placement |

---

## 3. Review Workflow

1. **Scope:** Identify changed files, additions, deletions, and renames in the diff.
2. **Detect Languages:** Map file extensions to language references. Load only the relevant ones.
3. **Per-File Review:** For each changed file, evaluate against the checklist above plus the loaded language-specific rules.
4. **Cross-File Analysis:** Check for broken imports, missing migrations, orphaned dead code, inconsistent API contracts across the diff boundary.
5. **Synthesize:** Aggregate findings by severity. Emit verdict.

---

## 4. Verdict

- **APPROVE** — No CRITICAL or HIGH findings. MEDIUM findings may exist but are acknowledged.
- **CHANGES-REQUESTED** — One or more CRITICAL or HIGH findings that must be resolved before merge.

Each finding includes: severity, file:line, description, and a concrete suggestion (code snippet when applicable).

---

## 5. Activation Triggers

| Trigger Area | Indicators | Target Reference |
| :--- | :--- | :--- |
| **Go code** | `.go` files, `go.mod`, `go.sum` in diff | [Go Review Rules](references/go.md) |
| **TypeScript code** | `.ts`, `.tsx`, `.mts`, `.cts` files, `tsconfig.json` in diff | [TypeScript Review Rules](references/typescript.md) |
| **Rust code** | `.rs` files, `Cargo.toml`, `Cargo.lock` in diff | [Rust Review Rules](references/rust.md) |

---

## 6. Modular References Index

Detailed language-specific review checklists reside in the `references/` directory:

- 📄 **[Go Review Rules](references/go.md)** — Error handling discipline, goroutine leaks, interface design, sqlx patterns, concurrency safety.
- 📄 **[TypeScript Review Rules](references/typescript.md)** — Strict mode, type narrowing, async/await traps, React/Vue patterns, bundle safety.
- 📄 **[Rust Review Rules](references/rust.md)** — Ownership and borrowing, lifetime annotations, unsafe audit, error type design, panic boundaries.
