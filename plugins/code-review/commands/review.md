---
name: review
description: Structured code review of staged changes, the current branch, or a pull request. Loads language-specific rules (Go, TypeScript, Rust) only for languages present in the diff and returns an APPROVE or CHANGES-REQUESTED verdict.
---

# /review — Structured Code Review

Delegates to the `reviewer` agent using the `code-review` skill.

## Usage

- `/code-review:review` — Staged changes; falls back to the current branch vs. its base when nothing is staged.
- `/code-review:review <branch>` — Diff of `<branch>` against the base branch.
- `/code-review:review #<number>` or a PR URL — Pull request diff via `gh pr diff`.

## Execution Flow

1. Resolve the review target and collect the diff:
   ```bash
   git diff --staged
   git diff "$(git merge-base HEAD <base>)"...HEAD
   gh pr diff <number>
   ```
   The base branch comes from the Project Profile in `AGENTS.md` (`vcs.base`), defaulting to `main`.
2. List changed files and detect languages by extension.
3. Load `skills/code-review/SKILL.md`, then only the matching `references/*.md`.
4. Review each file against the core checklist and loaded language rules, reading surrounding code as needed.
5. Report following the **4-Phase Output Contract**:
   - `### 1. Plan`
   - `### 2. Execution`
   - `### 3. Summary` (findings table + verdict)
   - `### 4. Recommended Actions` (findings ordered by severity with concrete suggestions)
