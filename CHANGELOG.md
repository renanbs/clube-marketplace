# Changelog

All notable changes to the Clube Marketplace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **OpenCode V2 support:** first-class OpenCode harness distribution.
  - `.opencode-plugin/marketplace.json` catalog plus per-plugin `.opencode-plugin/plugin.json` manifests (SemVer parity enforced by `make check`).
  - `.opencode/plugins/clube/index.ts` and `.opencode/plugins/code-review/index.ts` OpenCode plugin adapters registering 7 skills and 7 slash commands (`/clube:init`, `/clube:help`, `/clube:audit`, `/clube:audit-privacy`, `/clube:audit-performance`, `/clube:audit-seo`, `/clube:audit-tracking`, `/code-review:review`). `clube:omp-setup` stays OMP-only.
  - Root `opencode.json` and `.opencode/opencode.json` wiring the adapters plus 6 named subagents (`expert-seo`, `expert-tracking`, `expert-privacy`, `expert-performance`, `clube-auditor`, `reviewer`) whose `system` resolves to the canonical `plugins/` agent files. Agents omit `model` to inherit the session model (provider-agnostic).
  - `make check` now audits the OpenCode integration: both configs parse, every catalog plugin ships an adapter `index.ts`, and every agent `system` path resolves.
- Bilingual docs updated: README/README.pt-BR installation sections, `clube:help`, and `AGENTS.md`.

## [0.4.0] - 2026-09-23

### Added
- **`code-review` plugin (`plugins/code-review/`, v0.1.0):** A separate, independently versioned plugin for structured code review.
  - `/code-review:review` command for staged changes, branches, and pull requests.
  - `reviewer` read-only agent (`critique` class) returning `APPROVE` or `CHANGES-REQUESTED`.
  - `code-review` skill with a language-agnostic core and on-demand references for Go, TypeScript, and Rust.
- Registered `code-review` in all four root marketplace catalogs.

### Changed
- **Per-plugin version validation:** `make check` validates each plugin's version against its own manifests and its entry in every catalog, so plugins can be versioned independently.
- Repository-wide SemVer parity now reads the `clube` catalog entry by name instead of the first entry, so catalog order no longer matters.
- `make check` output lists each problem only under the plugin it belongs to.
- Synchronized `package.json`, the `clube` catalog entries, the 4 `clube` plugin manifests, and the vertical skill frontmatter to `v0.4.0`. `code-review` ships at its own `v0.1.0`.

## [0.3.0] - 2026-09-13

### Added
- **Python CLI (`clube_cli/`):** `bin/clube-config` is now a thin launcher; command logic (`check`, `audit`, `sync`, `init`, `install`) lives in a unit-tested Python package using only the standard library at runtime.
- **pytest suite (`tests/`, `make test`):** Covers the four auditors (including calibrated false positives), the validator's failure scenarios, severity scoring, harness detection, and pointer sync. Runs via `uv`; `uv.lock` is versioned.
- **Dependency preflight (`make doctor`):** Checks `python3` (minimum read from `pyproject.toml`), `uv`, `pytest`, `make`, and `git`. `init` runs it before writing any file and aborts when a required dependency is missing.
- `make test` fails with an actionable message when neither `uv` nor `pytest` is available.
- **Validator link integrity:** `make check` flags broken reference links and orphaned references in skills.

### Changed
- **`make check` can now fail:** The exit code is derived from the number of problems found. Previously it exited `0` in every state.
- Vertical skills are required to ship `references/` by default, with an exemption list (`init`, `clube-architecture`), so a new skill can no longer escape the check.
- Agent frontmatter is parsed only inside the `---` block, and missing fields are named.
- **Single source of truth for the version:** The SemVer parity target comes from `package.json`, and `clube_cli.__version__` is derived from it instead of being hardcoded.
- **Architectural constitution:** Added rules 2.3 (Gates Must Be Able To Fail) and 5.1 (Single Source of Truth), clarified that the stdlib-only rule applies at runtime, and added new anti-patterns.
- Synchronized all 9 manifests and the vertical skill frontmatter to `v0.3.0`.

### Fixed
- Runlog entries are serialized with `json.dumps`, so `details` containing quotes no longer produce invalid JSON.
- Parent-process harness detection is depth-limited and no longer loops when `ps` fails.
- A corrupt or missing profile falls back to defaults instead of raising.

### Removed
- `scripts/*.sh` (`lib-harness.sh`, `lib-runlog.sh`, `sync-harness-configs.sh`), replaced by the Python CLI.

## [0.2.0] - 2026-09-13

### Added
- **5 Named Specialist AI Agents (`plugins/clube/agents/`):**
  - `expert-seo`: Technical SEO, Generative Engine Optimization (GEO), Schema.org JSON-LD, and `/llms.txt`.
  - `expert-tracking`: Marketing attribution, Meta Pixel & CAPI, `event_id` deduplication, and root-domain cookie hygiene.
  - `expert-privacy`: LGPD/GDPR compliance, PII masking, shape logging, Sentry scrubbing, and audit trails.
  - `expert-performance`: Fullstack performance, SPA chunk recovery, CDN edge caching headers, and database query optimization.
  - `clube-auditor`: 360° production readiness coordinator executing deterministic Python detectors and synthesizing 4-phase remediation reports.
- **15 Topic Reference Guides:** Decomposed vertical SaaS skills into deep-dive reference guides in `references/` subdirectories (`meta-social.md`, `json-ld-schemas.md`, `geo-llmstxt.md`, `crawling-sitemaps.md`, `first-touch-cookies.md`, `deduplication-hygiene.md`, `server-side-capi.md`, `database-attribution.md`, `pii-masking-shape.md`, `sentry-observability-scrubbing.md`, `compliance-retention.md`, `chunk-recovery.md`, `caching-edge-headers.md`, `runtime-tuning.md`, `db-indexing-queries.md`).
- **Automated Manifest & Agent Validator:** Upgraded `bin/clube-config check` and `make check` to validate agent YAML frontmatter, skill reference directories, and 9-manifest version alignment in pure Python 3 stdlib.

### Changed
- **Progressive Disclosure Skill Refactoring:** Refactored 4 monolithic SaaS skills (`saas-seo-geo`, `marketing-attribution-analytics`, `data-privacy-observability`, `fullstack-performance-resilience`) into lean trigger routing entrypoints (`SKILL.md` < 100 lines).
- **Synchronized 9-Manifest Version Alignment:** Synchronized `package.json`, 4 root marketplace catalogs, and 4 plugin manifests to `v0.2.0`.
- **Architectural Constitution Update:** Formally added Section 1.2 (Named Specialist Agents Standard) and Section 1.3 (Progressive Disclosure Skill Architecture) to `clube:clube-architecture`.

### Improved
- **Multi-Harness Agent Registration:** Standardized agent discovery and registration across Claude Code, Cursor, Codex, and Oh My Pi.

## [0.1.0] - 2026-09-13

### Added
- **Multi-Harness Marketplace Architecture:** Unified distribution catalogs for Claude Code (`.claude-plugin/`), Cursor (`.cursor-plugin/`), Codex (`.agents/plugins/`), and Oh My Pi (`.omp-plugin/`).
- **6 Modular Skills:**
  - `clube:init`: Guided onboarding and `Project Profile` generator in `AGENTS.md` and `CLAUDE.md`.
  - `clube:clube-architecture`: Engineering constitution, 5 core pillars, and quality standards.
  - `clube:fullstack-performance-resilience`: Chunk recovery (`vite:preloadError`), CDN cache headers (`immutable`), container cgroups (`automaxprocs`), and database query tuning.
  - `clube:saas-seo-geo`: Strict LP vs App isolation (`noindex`), OpenGraph metadata, Schema.org JSON-LD, and `/llms.txt` / `/llms-full.txt` specifications.
  - `clube:marketing-attribution-analytics`: Root-domain first-touch UTM cookies, Meta CAPI deduplication via `event_id`, and `acquisition_context JSONB` persistence.
  - `clube:data-privacy-observability`: PII/LGPD protection in logs/telemetry, blind struct logging elimination (`%+v`, `zap.Any`), Sentry scrubbing, and metric label cardinality safety.
- **8 Slash Commands:**
  - `/clube:audit` (or `/audit`): Unified 360° SaaS production readiness audit across all 4 pillars.
  - `/clube:audit-privacy`: Static and contextual audit for PII in logs, queries, and metric cardinality.
  - `/clube:audit-performance`: SPA chunk recovery, CDN caching, and container resource limits.
  - `/clube:audit-seo`: Public route discoverability, `/llms.txt`, and structured data.
  - `/clube:audit-tracking`: Root domain cookies, Meta CAPI deduplication, and database acquisition context.
  - `/clube:init` (or `/init`, `$init`): Guided onboarding, DB connection preflights, and agent role mapping.
  - `/clube:omp-setup`: OMP model override configuration for subagent dispatch.
  - `/clube:help`: Centralized command and skill directory.
- **Hybrid Audit Suite:** Deterministic static Python runners (`audit-all.py`, `audit-privacy.py`, `audit-performance.py`, `audit-seo.py`, `audit-tracking.py`, `ui.py`) with rich ASCII table rendering, health bars, and JSON state persistence at `.clube/audit-last.json`.
- **Operational CLI & Makefile:** `clube-config` CLI and `Makefile` targets (`make check`, `make audit`, `make sync`, `make init`, `make install-cli`).
- **4-Phase Output Contract:** Standardized format across all commands: `### 1. Plan`, `### 2. Execution`, `### 3. Summary`, `### 4. Recommended Actions`.
- **Bilingual Documentation:** Canonical English documentation (`README.md`, `CHANGELOG.md`) mirrored in Brazilian Portuguese (`README.pt-BR.md`, `CHANGELOG.pt-BR.md`).

### Removed
- Legacy flat distribution bundles and monolithic single-file marketplace definitions.
