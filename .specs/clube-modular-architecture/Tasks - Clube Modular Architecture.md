# Tasks - Clube Modular Architecture

This document decomposes the **Clube Modular Architecture Restructuring (v0.2.0)** into atomic, verifiable tasks across 4 execution waves.

---

## Task Summary Table

| ID | Title | Wave | Async | Depends On | Goals | Target Location |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **T1** | Implement 5 Named Specialist AI Agents | Wave 1 | `true` | None | **G1** | `plugins/clube/agents/*.md` |
| **T2** | Decompose 4 SaaS Skills into Modular `references/` | Wave 1 | `true` | None | **G2** | `plugins/clube/skills/*/` |
| **T3** | Upgrade Validator Engine & Bump 9 Manifests to v0.2.0 | Wave 2 | `false` | T1, T2 | **G3**, **G4** | `bin/clube-config`, `package.json`, manifests |
| **T4** | Update Architecture Constitution, Slash Help & Bilingual Docs | Wave 3 | `false` | T3 | **G5** | `SKILL.md`, `help.md`, `README*`, `CHANGELOG*` |
| **T5** | End-to-End Quality Gates & System Verification | Wave 4 | `false` | T4 | **G6** | Repository root (`make check`, `make audit`) |

---

## Wave 1 (Async Implementation)

### Task 1: Implement 5 Named Specialist AI Agents
- **ID:** `T1`
- **What:** Author 5 comprehensive, actionable specialist agent definition files in `plugins/clube/agents/` adhering to the standard YAML frontmatter specification (`name`, `description`, `tools`, `model`, `readonly`) and detailed domain instructions.
  - `expert-seo.md`: SEO/GEO specialist, Schema.org JSON-LD, `/llms.txt`, noindex boundaries, sitemaps.
  - `expert-tracking.md`: Marketing attribution, Meta Pixel & CAPI, GA4, root-domain cookies, `event_id` deduplication, DB persistence (`acquisition_context`).
  - `expert-privacy.md`: LGPD/GDPR compliance, PII masking, shape logging, Sentry scrubbing, retention policies.
  - `expert-performance.md`: SPA chunk recovery (`vite:preloadError`), edge cache headers, container cgroups runtime tuning, DB query optimization.
  - `clube-auditor.md`: 360° audit coordinator, Python script execution, `.clube/audit-last.json` parser, 4-phase remediation reporting (readonly).
- **Where:** `plugins/clube/agents/`
  - `plugins/clube/agents/expert-seo.md`
  - `plugins/clube/agents/expert-tracking.md`
  - `plugins/clube/agents/expert-privacy.md`
  - `plugins/clube/agents/expert-performance.md`
  - `plugins/clube/agents/clube-auditor.md`
- **Depends On:** None
- **Async:** `true`
- **Goals:** `G1`
- **Reuse:** LoopTech multi-harness agent patterns, existing skill domain knowledge, pure markdown structure.
- **Done When:** All 5 agent markdown files exist, have valid YAML frontmatter, specify correct tool permissions and model classes, and define comprehensive instructions.
- **Tests:**
  ```bash
  test -f plugins/clube/agents/expert-seo.md && \
  test -f plugins/clube/agents/expert-tracking.md && \
  test -f plugins/clube/agents/expert-privacy.md && \
  test -f plugins/clube/agents/expert-performance.md && \
  test -f plugins/clube/agents/clube-auditor.md
  ```
- **Commit Message:** `feat(agents): add 5 specialist AI agents for seo, tracking, privacy, performance, and audit coordination`

---

### Task 2: Decompose 4 SaaS Skills into Modular `references/`
- **ID:** `T2`
- **What:** Refactor the 4 dense SaaS skills into lean routing entrypoints (`SKILL.md` < 100 lines) and extract deep schemas, DDLs, regexes, and framework guides into 16 modular `references/*.md` topic documents.
  1. `plugins/clube/skills/saas-seo-geo/`:
     - `SKILL.md` (< 100 lines)
     - `references/meta-social.md`
     - `references/json-ld-schemas.md`
     - `references/geo-llmstxt.md`
     - `references/crawling-sitemaps.md`
  2. `plugins/clube/skills/marketing-attribution-analytics/`:
     - `SKILL.md` (< 100 lines)
     - `references/first-touch-cookies.md`
     - `references/deduplication-hygiene.md`
     - `references/server-side-capi.md`
     - `references/database-attribution.md`
  3. `plugins/clube/skills/fullstack-performance-resilience/`:
     - `SKILL.md` (< 100 lines)
     - `references/chunk-recovery.md`
     - `references/caching-edge-headers.md`
     - `references/runtime-tuning.md`
     - `references/db-indexing-queries.md`
  4. `plugins/clube/skills/data-privacy-observability/`:
     - `SKILL.md` (< 100 lines)
     - `references/pii-masking-shape.md`
     - `references/sentry-observability-scrubbing.md`
     - `references/compliance-retention.md`
- **Where:** `plugins/clube/skills/`
- **Depends On:** None
- **Async:** `true`
- **Goals:** `G2`
- **Reuse:** Existing `SKILL.md` content extracted and refined into modular reference files; relative linking patterns.
- **Done When:** All 4 SaaS skills have populated `references/` subdirectories with modular Markdown files, and each parent `SKILL.md` is under 100 lines and links to its references.
- **Tests:**
  ```bash
  test -d plugins/clube/skills/saas-seo-geo/references && \
  test -d plugins/clube/skills/marketing-attribution-analytics/references && \
  test -d plugins/clube/skills/fullstack-performance-resilience/references && \
  test -d plugins/clube/skills/data-privacy-observability/references
  ```
- **Commit Message:** `refactor(skills): decompose 4 saas skills into lean entrypoints and modular references`

---

## Wave 2 (Manifests & Validator Upgrade)

### Task 3: Upgrade Validator Engine & Bump 9 Manifests to v0.2.0
- **ID:** `T3`
- **What:**
  1. Upgrade `cmd_check` in `bin/clube-config` to:
     - Audit presence of `plugins/clube/agents/*.md` and validate YAML frontmatter properties (`name`, `description`, `tools`, `model`, `readonly`).
     - Audit `references/` subdirectories in all 4 vertical SaaS skills.
     - Validate SemVer parity target `0.2.0` across all 9 manifests.
  2. Bump version to `"0.2.0"` and ensure `"agents": "./agents/"` across all 9 manifest files:
     - `package.json`
     - `.claude-plugin/marketplace.json`
     - `.omp-plugin/marketplace.json`
     - `.cursor-plugin/marketplace.json`
     - `.agents/plugins/marketplace.json`
     - `plugins/clube/.claude-plugin/plugin.json`
     - `plugins/clube/.cursor-plugin/plugin.json`
     - `plugins/clube/.codex-plugin/plugin.json`
     - `plugins/clube/.omp-plugin/plugin.json`
- **Where:** `bin/clube-config`, `package.json`, `.claude-plugin/`, `.omp-plugin/`, `.cursor-plugin/`, `.agents/`, `plugins/clube/`
- **Depends On:** `T1`, `T2`
- **Async:** `false`
- **Goals:** `G3`, `G4`
- **Reuse:** Existing Python stdlib verification block in `bin/clube-config`.
- **Done When:** `./bin/clube-config check` executes without errors, confirms 5 valid agents, verifies modular references, and verifies 9/9 manifests aligned at v0.2.0.
- **Tests:**
  ```bash
  ./bin/clube-config check
  ```
- **Commit Message:** `feat(harness): upgrade bin/clube-config check to audit agents and bump manifests to v0.2.0`

---

## Wave 3 (Docs & Architecture Constitution)

### Task 4: Update Architecture Constitution, Slash Help & Bilingual Docs
- **ID:** `T4`
- **What:**
  1. Update `plugins/clube/skills/clube-architecture/SKILL.md` to define the 5 specialist agents standard and progressive disclosure reference architecture in Pillar 1.
  2. Update `plugins/clube/commands/help.md` to document the 5 specialist agents and modular skills.
  3. Update `README.md` (English) and `README.pt-BR.md` (Brazilian Portuguese) with the new agent roster, references layout, and v0.2.0 capabilities.
  4. Update `CHANGELOG.md` (English) and `CHANGELOG.pt-BR.md` (Portuguese) with v0.2.0 release notes in Keep a Changelog format.
- **Where:**
  - `plugins/clube/skills/clube-architecture/SKILL.md`
  - `plugins/clube/commands/help.md`
  - `README.md`
  - `README.pt-BR.md`
  - `CHANGELOG.md`
  - `CHANGELOG.pt-BR.md`
- **Depends On:** `T3`
- **Async:** `false`
- **Goals:** `G5`
- **Reuse:** Existing bilingual structure and Keep a Changelog format.
- **Done When:** All documentation files accurately reflect the v0.2.0 architecture and retain 100% bilingual parity.
- **Tests:**
  ```bash
  grep -q "expert-seo" plugins/clube/commands/help.md && \
  grep -q "0.2.0" CHANGELOG.md && \
  grep -q "0.2.0" CHANGELOG.pt-BR.md
  ```
- **Commit Message:** `docs: update architecture constitution, slash help, and bilingual docs for v0.2.0`

---

## Wave 4 (Verification & Quality Gates)

### Task 5: End-to-End Quality Gates & System Verification
- **ID:** `T5`
- **What:** Execute complete workspace validation via `make check` and `make audit`, ensuring 100% compliance, zero broken links, clean runlog generation (`.clube/audit-last.json`), and zero regressions across all slash commands and Python detector scripts.
- **Where:** Repository root
- **Depends On:** `T4`
- **Async:** `false`
- **Goals:** `G6`
- **Reuse:** `Makefile`, `bin/clube-config`, `plugins/clube/scripts/audit-all.py`.
- **Done When:** `make check` and `make audit` pass with exit code 0 and report 100% integrity.
- **Tests:**
  ```bash
  make check && make audit
  ```
- **Commit Message:** `chore(release): complete v0.2.0 modular architecture verification`
