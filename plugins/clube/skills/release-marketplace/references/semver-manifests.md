# SemVer Manifests Map

Every file that carries the marketplace version, how `make check` treats it, and the
parity rule. This is the Single Source of Truth for "what must be bumped on release".

## The 11 versioned manifests (clube core)

| # | Path | Kind | Notes |
|---|------|------|-------|
| 1 | `package.json` (root) | root | canonical target for `make check` |
| 2 | `.claude-plugin/marketplace.json` | marketplace | Clube catalog entry |
| 3 | `.comp-plugin/marketplace.json` | marketplace | Clube catalog entry |
| 4 | `.cursor-plugin/marketplace.json` | marketplace | Clube catalog entry |
| 5 | `.agents/plugins/marketplace.json` | marketplace | Clube catalog entry |
| 6 | `.opencode-plugin/marketplace.json` | marketplace | Clube catalog entry |
| 7 | `plugins/clube/.claude-plugin/plugin.json` | plugin | per-harness manifest |
| 8 | `plugins/clube/.cursor-plugin/plugin.json` | plugin | per-harness manifest |
| 9 | `plugins/clube/.codex-plugin/plugin.json` | plugin | per-harness manifest |
| 10 | `plugins/clube/.omp-plugin/plugin.json` | plugin | per-harness manifest |
| 11 | `plugins/clube/.opencode-plugin/plugin.json` | plugin | per-harness manifest |

Plus the OpenCode adapter packages (versioned to match for the marketplace-adjacent
distribution):

- `.opencode/plugins/clube/package.json` (+ `package-lock.json` top-level `version`
  fields only).
- `.opencode/plugins/code-review/package.json` — ships at its **own** independent version
  (e.g. `v0.1.0`), not synced with the clube core.

## Independently versioned plugins

- `code-review` (and any future plugin) is **not** synchronized to the clube core version.
  Its `plugin.json` manifests + catalog entries + adapter package carry their own SemVer
  and only need internal parity (checked independently by `make check`).

## `make check` semantics

- **SemVer parity:** every manifest above must declare the identical version as the root
  `package.json`. Mismatch → `Problem("semver", …)` per file; verified by
  `check_semver_parity` iterating the `VERSIONED_MANIFESTS` tuple.
- **Independent plugins:** parity validated per-plugin against its own manifests (and
  against its catalog entry) via `check_catalog_parity` + `check_plugin_parity`.
- **OpenCode integration:** both `opencode.json` configs parse, every catalog plugin ships
  an adapter `index.ts`, and every agent `system` path resolves (see `check_opencode_integration`).
- **Skills:** each vertical skill needs a `references/` directory with every reference
  linked from `SKILL.md` (orphaned/unreachable references are flagged); `init` and
  `clube-architecture` are the documented exemptions. Skill `metadata.version` frontmatter
  is synchronized to the release version by convention (not gated).

## Bilingual changelog

`CHANGELOG.md` (EN) and `CHANGELOG.pt-BR.md` carry `[Unreleased]`/`[Não lançado]`
sections and get the same release bump. Release notes are published bilingually
(EN section + pt-BR section) — see [github-release.md](github-release.md).
