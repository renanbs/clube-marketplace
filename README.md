<div align="center">

# Clube Marketplace

**Centralized multi-harness AI marketplace for skills, agents, commands, and workflows tailored for Clube SaaS products.**

[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Standards](https://img.shields.io/badge/standards-Keep%20a%20Changelog-orange.svg)](CHANGELOG.md)

[English](README.md) | [Português do Brasil](README.pt-BR.md)

</div>

---

## Overview

The **Clube AI Marketplace** provides a unified distribution model for AI coding skills, expert agents, and deterministic audit workflows across heterogeneous AI coding harnesses:
- **Claude Code** (`.claude-plugin/`)
- **Oh My Pi (OMP)** (`.omp-plugin/`)
- **Cursor** (`.cursor-plugin/`)
- **Codex / OpenAI Agents** (`.agents/plugins/`)

Each host reads its native marketplace catalog from the repository root, consuming modular plugins defined under `plugins/` (such as `plugins/clube`).

---

## Repository Structure

```
clube-marketplace/
├── .claude-plugin/marketplace.json     # Claude Code marketplace catalog (v0.2.0)
├── .omp-plugin/marketplace.json        # Oh My Pi marketplace catalog (v0.2.0)
├── .cursor-plugin/marketplace.json     # Cursor marketplace catalog (v0.2.0)
├── .agents/plugins/marketplace.json    # Codex marketplace catalog (v0.2.0)
├── Makefile                            # Operational targets (check, audit, sync, init)
├── AGENTS.md                           # Canonical instructions & Project Profile
├── CLAUDE.md                           # Pointer -> @AGENTS.md
├── GEMINI.md                           # Pointer -> @AGENTS.md
├── .cursorrules                        # Pointer -> @AGENTS.md
├── bin/
│   └── clube-config                    # Unified CLI tool & harness integrity checker
├── scripts/
│   ├── lib-harness.sh                  # Host harness detection engine
│   ├── lib-runlog.sh                   # Structured event logging utilities
│   └── sync-harness-configs.sh         # Pointer synchronizer (@AGENTS.md)
├── .clube/
│   └── audit-last.json                 # Structured audit runlog & persistent state
└── plugins/
    └── clube/                          # Core Clube plugin (v0.2.0)
        ├── .claude-plugin/plugin.json
        ├── .cursor-plugin/plugin.json
        ├── .codex-plugin/plugin.json
        ├── .omp-plugin/plugin.json
        ├── scripts/                    # Deterministic audit runners & ASCII UI engine
        │   ├── ui.py                   # ASCII box headers, badges, tables & health bars
        │   ├── audit-all.py            # Unified 360° audit runner
        │   ├── audit-privacy.py        # LGPD/PII static checker
        │   ├── audit-performance.py    # Chunk recovery & runtime resilience checker
        │   ├── audit-seo.py            # SEO & LLM discovery (/llms.txt) checker
        │   └── audit-tracking.py       # Cookies & Meta CAPI deduplication checker
        ├── commands/                   # Slash commands (/audit, /init, /help, etc.)
        ├── agents/                     # Named expert subagents
        │   ├── expert-seo.md           # Technical SEO, GEO & Schema.org JSON-LD
        │   ├── expert-tracking.md      # Attribution, Meta CAPI & root-domain cookies
        │   ├── expert-privacy.md       # LGPD/GDPR, PII masking & Sentry scrubbing
        │   ├── expert-performance.md   # SPA chunk recovery, caching & runtime tuning
        │   └── clube-auditor.md        # 360° audit coordinator (read-only)
        └── skills/                     # Progressive disclosure modular skills
            ├── clube-architecture/     # 5 core pillars & engineering constitution
            ├── init/                   # Project Profile onboarding
            ├── saas-seo-geo/           # Technical SEO, GEO & /llms.txt
            │   └── references/         # Deep schemas, DDLs & crawling guides
            ├── marketing-attribution-analytics/ # Attribution, CAPI & cookies
            │   └── references/         # CAPI payloads, cookie hygiene & DDLs
            ├── data-privacy-observability/      # LGPD/GDPR, PII & telemetry
            │   └── references/         # Masking helpers, Sentry scrubbing & DDLs
            └── fullstack-performance-resilience/# Chunk recovery, caching & tuning
                └── references/         # Vite recovery, edge headers & DB indexing
```

---

## Installation by AI Host

### Claude Code
```bash
/plugin marketplace add git@github.com:clubedepontos/clube-marketplace.git
/plugin install clube@clube
```

### Oh My Pi (OMP)
```bash
/marketplace add https://github.com/clubedepontos/clube-marketplace
/marketplace install --scope project clube@clube
```
*Note: If using custom agents on OMP, run `/clube:omp-setup` once to configure model overrides.*

### Cursor
Add as a Team marketplace via **Settings → Plugins**, or symlink for local development:
```bash
mkdir -p ~/.cursor/plugins/local
ln -s "$(pwd)/plugins/clube" ~/.cursor/plugins/local/clube
```

### Codex
```bash
codex plugin marketplace add clubedepontos/clube-marketplace --ref main
codex plugin install clube --source clube
```

---

## Specialist AI Agents (`plugins/clube/agents`)

Clube provides 5 first-class named specialist agents declared with strict YAML frontmatter contracts, abstract capability routing (`reasoning`, `code`, `critique`), and scoped tool permissions:

| Agent | Capability Class | Tools | Focus & Core Responsibilities |
| :--- | :--- | :--- | :--- |
| `expert-seo` | `reasoning` / `code` | Read, Write, Edit, Grep, Glob, Bash | Technical SEO, Generative Engine Optimization (GEO), Schema.org JSON-LD, `/llms.txt` and `/llms-full.txt` discovery, OpenGraph tags, and strict indexing boundaries (`noindex` on auth app). |
| `expert-tracking` | `code` / `reasoning` | Read, Write, Edit, Grep, Glob, Bash | Marketing attribution, browser Meta Pixel & server-side Conversions API (CAPI), `event_id` deduplication, root-domain first-party cookie hygiene, and `acquisition_context` JSONB database persistence. |
| `expert-privacy` | `reasoning` / `code` | Read, Write, Edit, Grep, Glob, Bash | LGPD/GDPR compliance, "Log the shape, not the data", deterministic PII masking (CPF, email, phone), Sentry error payload scrubbing, and audit logging. |
| `expert-performance` | `code` / `reasoning` | Read, Write, Edit, Grep, Glob, Bash | Fullstack performance, SPA chunk recovery (`vite:preloadError`, `router.onError` with infinite reload guard), CDN edge caching headers (`immutable`), container cgroups tuning (`automaxprocs`), and database query optimization. |
| `clube-auditor` | `reasoning` / `critique` | Read, Grep, Glob, Bash *(readonly)* | 360° production readiness coordinator (read-only), executing deterministic Python detector scripts, parsing `.clube/audit-last.json`, prioritizing findings, and synthesizing 4-phase remediation reports. |

---

## Included Skills (`plugins/clube`)

All vertical SaaS skills follow the **Progressive Disclosure Architecture**, featuring lean activation entrypoints (`SKILL.md` < 100 lines) supported by 15 comprehensive topic reference guides in `references/`:

| Skill | Topic References | Focus |
| :--- | :--- | :--- |
| `clube:init` | — | Guided project onboarding & `Project Profile` generation in `AGENTS.md` and `CLAUDE.md`. |
| `clube:clube-architecture` | — | Architectural constitution and engineering discipline (5 core pillars: multi-harness modular plugins, hybrid audit architecture, 4-phase output contract, runlog persistence, SemVer parity). |
| `clube:saas-seo-geo` | `meta-social.md`<br>`json-ld-schemas.md`<br>`geo-llmstxt.md`<br>`crawling-sitemaps.md` | Technical SEO and Generative Engine Optimization (GEO) for SaaS, strict LP vs App separation (`noindex`), metadata/OpenGraph, Schema.org JSON-LD, and `/llms.txt` specifications. |
| `clube:marketing-attribution-analytics` | `first-touch-cookies.md`<br>`deduplication-hygiene.md`<br>`server-side-capi.md`<br>`database-attribution.md` | End-to-end tracking, attribution models, root domain first-touch cookies, Meta CAPI deduplication via `event_id`, and `acquisition_context JSONB` persistence. |
| `clube:data-privacy-observability` | `pii-masking-shape.md`<br>`sentry-observability-scrubbing.md`<br>`compliance-retention.md` | PII/LGPD compliance in logs, APM, traces, telemetry, "log the shape, not the data", masking helpers, prohibiting blind struct serialization (`%+v`, `zap.Any`), and error scrubbing. |
| `clube:fullstack-performance-resilience` | `chunk-recovery.md`<br>`caching-edge-headers.md`<br>`runtime-tuning.md`<br>`db-indexing-queries.md` | Runtime optimization (Node/Bun/Go/Python), deploy resilience, chunk recovery (`vite:preloadError`, `router.onError`), CDN cache headers (`immutable`), container cgroups (`automaxprocs`), and database query tuning. |
---

## Slash Commands

| Slash Command | Focus |
| :--- | :--- |
| `/clube:audit` (or `/audit`) | Unified 360° SaaS production readiness audit across all 4 engineering pillars (Privacy, Performance, SEO/GEO, Tracking). |
| `/clube:audit-privacy` | Audits blind struct logging, PII in query strings, unmasked domain logs, and metric cardinality. |
| `/clube:audit-performance` | Audits SPA chunk recovery (404 prevention), CDN cache headers, connection pools, and container limits. |
| `/clube:audit-seo` | Audits `/llms.txt`, private route indexing protection (`noindex`), OpenGraph tags, and Schema.org structured data. |
| `/clube:audit-tracking` | Audits root domain cookies, Meta CAPI deduplication (`event_id`), and database acquisition context. |
| `/clube:init` (or `/init`, `$init`) | Guided project onboarding, database connection preflights, agent role mapping, and Project Profile generation. |
| `/clube:omp-setup` | (OMP only) Configures model overrides for plugin agents to ensure seamless subagent dispatch. |
| `/clube:help` (or `/help`) | Displays complete overview of commands, skills, and core engineering principles. |

---

## Operational CLI & Makefile Commands

The repository includes a dedicated CLI helper (`bin/clube-config`) and `Makefile` targets:

```bash
# Audit active harness detection, marketplace catalogs, and plugin integrity
make check
./bin/clube-config check

# Run deterministic 360° SaaS production readiness audit
make audit
./bin/clube-config audit [all|privacy|performance|seo|tracking]

# Synchronize harness pointer files (@AGENTS.md) across subdirectories
make sync
./bin/clube-config sync [DIR]

# Initialize project AI configuration and sync harness pointers
make init
./bin/clube-config init [DIR]

# Install clube-config CLI into ~/.local/bin
make install-cli
./bin/clube-config install
```

---

## Core Architectural Principles

The Clube AI Marketplace is governed by the **5 Mandatory Pillars** defined in `clube:clube-architecture`:

1. **Multi-Harness Modular Plugin Standard:** All AI harnesses (Claude Code, Cursor, Codex, Oh My Pi) consume modular plugins from `plugins/<name>/` via root marketplace catalogs.
2. **Hybrid Audit Architecture:** Deterministic Python static scripts (`plugins/clube/scripts/`) execute baseline checks fast, persist structured state in `.clube/audit-last.json`, and feed LLM slash commands with concrete evidence.
3. **4-Phase Output Contract:** Every command, skill, and AI workflow adheres to the strict 4-phase contract:
   - `### 1. Plan`
   - `### 2. Execution`
   - `### 3. Summary`
   - `### 4. Recommended Actions`
4. **Structured Runlog & State Persistence:** Automated audits record structured execution artifacts in `.clube/audit-last.json` with visual terminal rendering (ASCII tables, health bars, badges).
5. **SemVer Parity & Bilingual Documentation:** All 9 manifest files strictly declare identical SemVer versions (`0.2.0`), accompanied by complete bilingual documentation parity in English (`README.md`, `CHANGELOG.md`) and Brazilian Portuguese (`README.pt-BR.md`, `CHANGELOG.pt-BR.md`).
