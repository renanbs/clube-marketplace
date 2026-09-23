---
name: release-marketplace
description: |
  Structured release ceremony for the Clube Marketplace and its independently versioned plugins.
  Use whenever preparing, executing, or auditing a marketplace release (SemVer parity, harness
  catalog synchronization, bilingual changelogs, GitHub tag + Release with changelog notes).
  Pairs with `/clube:release` expectations and follows the repository's Keep a Changelog /
  Semantic Versioning conventions.
---

# clube:release-marketplace — Marketplace Release Ceremony

Releases the Clube Marketplace and its independently versioned plugins in a deterministic,
repository-conventional way. Every step is enforced or documented so the ceremony stays the
same regardless of the AI harness running it.

**Announce at start:** "I am using the `clube:release-marketplace` skill to structure the marketplace release."

---

## When to use

- The project is doing a marketplace/plugin cut (SemVer target decided, feature frozen).
- You are following up after a feature merge that added skills, agents, commands, or plugins.
- You need to produce the version bump, bilingual changelog, GitHub tag, and GitHub Release
  with changelog notes.

## Goals

1. Bump **every** versioned manifest and catalog to the same target version (SemVer parity).
2. Keep the repository bilingual (EN + pt-BR) for changelog and docs.
3. Emit an annotated Git tag and a GitHub Release with bilingual changelog notes.
4. Leave `main` green: `make check` and `make test` must pass before merge.

## Flow

The full ceremony is detailed in the references. A one-shot checklist:

- [ ] Pre-flight: `main` clean, `make sync` run, GitHub CLI authenticated, target SemVer decided.
- [ ] Prepare the release worktree on a `chore/release-X.Y.Z` branch (do not cut on `main`).
- [ ] Bump all versioned manifests (see [Manifests](references/semver-manifests.md)) to the target.
  - Root `package.json`, the marketplace catalogs, the per-plugin manifests, the OpenCode
    adapter `package.json`/lock, and the vertical skill frontmatter.
  - Independently versioned plugins (e.g. `code-review` at its own `v0.1.0`) are **not** synced.
- [ ] Move the bilingual changelogs from `[Unreleased]`/`[Não lançado]` to `[X.Y.Z] - <date>`
  (see [Procedure](references/release-procedure.md)).
- [ ] Gate: `make check` (0 problems, SemVer parity + harness integration) and `make test` (all pass).
- [ ] Commit `chore(release): X.Y.Z`, push, open the PR (repo convention: merge commit).
- [ ] Merge, then create the annotated tag `vX.Y.Z` at the merge commit and push it.
- [ ] Create the GitHub Release with bilingual changelog notes (see
      [GitHub Release](references/github-release.md)).
- [ ] Cleanup: delete the release branch (local + remote), refresh the dev checkout.

## Rules

- **SemVer parity is non-negotiable:** every versioned manifest must declare the identical
  version, or `make check` reports a SemVer `Problem`. Never bump a single file in isolation.
- **Bilingual discipline:** CHANGELOG (EN) and CHANGELOG.pt-BR are both moved on release;
  release notes carry the same bilingual changelog content.
- **Merge commit, not squash:** the repository merges release PRs with `--merge` to keep
  the changelog/version history intact.
- **Independently versioned plugins stay put.** Only the "marketplace core" (Clube) is synced
  to the repo version; plugins like `code-review` ship their own version.
- **No silent bumps:** skill metadata.version follows the convention of the vertical frontmatter;
  when syncing, bump frontmatter consistently (e.g. `v0.4.0 → v0.5.0`) or justify the exemption.

## References

- [Release procedure](references/release-procedure.md) — step-by-step execution, exact commands.
- [SemVer manifests map](references/semver-manifests.md) — every versioned file and how `make check` validates it.
- [GitHub Release & changelog notes](references/github-release.md) — tag + `gh release create`, bilingual notes.
