# Changelog

All notable changes to the Clube Marketplace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
