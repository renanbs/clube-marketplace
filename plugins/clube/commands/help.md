---
name: help
description: Displays overview of Clube AI Marketplace commands, skills, and engineering workflows.
---

# Clube AI Marketplace — Help & Overview

The **Clube AI Marketplace** provides standardized AI workflows, stack-expert skills, and multi-harness distribution across Claude Code, Cursor, Codex, and Oh My Pi.

## Available Slash Commands

- `/clube:init` (or `/init`, `$init`) — Guided onboarding for target projects: sets up `Project Profile` in `CLAUDE.md` & `AGENTS.md`, checks database preflights, maps agent roles, and audits runtimes.
- `/clube:omp-setup` — (OMP only) Configures model overrides for plugin agents.
- `/clube:help` — Shows this overview.
- `/clube:audit` (or `/audit`) — Unified 360° SaaS production readiness audit across all 4 engineering pillars (Privacy, Performance, SEO/GEO, Tracking).
- `/clube:audit-privacy` — Audits blind struct logging, PII in query strings, and metric cardinality.
- `/clube:audit-performance` — Audits SPA chunk recovery (404 prevention), CDN cache headers, and container limits.
- `/clube:audit-seo` — Audits `/llms.txt`, private route indexing protection, and Schema.org structured data.
- `/clube:audit-tracking` — Audits root domain cookies, Meta CAPI deduplication, and acquisition context.

## Available Specialist Agents

| Agent | Capability Class | Scope & Responsibilities |
| :--- | :--- | :--- |
| `expert-seo` | `reasoning` / `code` | Technical SEO, Generative Engine Optimization (GEO), Schema.org JSON-LD, `/llms.txt` and `/llms-full.txt` discovery, OpenGraph tags, and strict indexing boundaries (`noindex` on auth app). |
| `expert-tracking` | `code` / `reasoning` | Marketing attribution, browser Meta Pixel & server-side Conversions API (CAPI), `event_id` deduplication, root-domain first-party cookie hygiene, and `acquisition_context` JSONB database persistence. |
| `expert-privacy` | `reasoning` / `code` | LGPD/GDPR compliance, "Log the shape, not the data", deterministic PII masking (CPF, email, phone), Sentry error payload scrubbing, and audit logging. |
| `expert-performance` | `code` / `reasoning` | Fullstack performance, SPA chunk recovery (`vite:preloadError`, `router.onError` with infinite reload guard), CDN edge caching headers (`immutable`), container cgroups tuning (`automaxprocs`), and database query optimization. |
| `clube-auditor` | `reasoning` / `critique` | 360° production readiness coordinator (read-only), executing deterministic Python detector scripts, parsing `.clube/audit-last.json`, prioritizing findings, and synthesizing 4-phase remediation reports. |

## Available Skills

Skills follow the **Progressive Disclosure Architecture**, featuring lean activation entrypoints (`SKILL.md` < 100 lines) supported by comprehensive topic guides under `references/`:

| Skill | References Guides | Focus |
| :--- | :--- | :--- |
| `clube:init` | — | Guided onboarding and `Project Profile` setup in `AGENTS.md` and `CLAUDE.md`. |
| `clube:clube-architecture` | — | Architectural constitution and engineering discipline (5 core pillars: multi-harness modular plugins, hybrid audit architecture, 4-phase output contract, runlog persistence, SemVer parity). |
| `clube:saas-seo-geo` | `meta-social.md`, `json-ld-schemas.md`, `geo-llmstxt.md`, `crawling-sitemaps.md` | Technical SEO, GEO for AI engine discovery (`/llms.txt`), structured data (Schema.org JSON-LD), robots.txt rules, and dynamic XML sitemaps. |
| `clube:marketing-attribution-analytics` | `first-touch-cookies.md`, `deduplication-hygiene.md`, `server-side-capi.md`, `database-attribution.md` | End-to-end marketing attribution, root-domain first-touch cookies, client/server Meta CAPI deduplication via `event_id`, and `acquisition_context` JSONB persistence. |
| `clube:data-privacy-observability` | `pii-masking-shape.md`, `sentry-observability-scrubbing.md`, `compliance-retention.md` | LGPD/GDPR compliance, PII masking, shape logging ("log the shape, not the data"), Sentry `beforeSend` scrubbing, and retention policies. |
| `clube:fullstack-performance-resilience` | `chunk-recovery.md`, `caching-edge-headers.md`, `runtime-tuning.md`, `db-indexing-queries.md` | Deploy resilience, SPA chunk recovery (`vite:preloadError`), CDN cache headers (`immutable`), container tuning (`automaxprocs`), and database query indexing. |

## Other Plugins in This Marketplace

- **`code-review`** (versioned independently) — `/code-review:review` runs a structured, read-only code review of staged changes, a branch, or a pull request, with language-specific rules for Go, TypeScript, and Rust. Install it separately (e.g. `code-review@clube`).

## Core Principles

1. **Single Source of Truth (`AGENTS.md`):** Every project declares its Project Profile inside `AGENTS.md` and imports it into `CLAUDE.md`, `GEMINI.md`, and `.cursorrules` using `@AGENTS.md`.
2. **Hybrid Audit Architecture:** Deterministic Python static scripts (`plugins/clube/scripts/`) execute baseline checks fast, persist structured state in `.clube/audit-last.json`, and feed LLM slash commands with factual evidence.
3. **4-Phase Output Contract:** Commands and agents report progress following:
   - `### 1. Plan`
   - `### 2. Execution`
   - `### 3. Summary`
   - `### 4. Recommended Actions`
4. **Product-Agnostic Skills:** Skills encapsulate transferable engineering disciplines; concrete project facts (paths, CI commands, connections) live strictly in each project's Project Profile.
5. **SemVer & Bilingual Docs:** Full SemVer parity across all harness catalogs and 100% mirrored bilingual documentation (English and Brazilian Portuguese).
