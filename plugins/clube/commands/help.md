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

## Available Skills

- `clube:init` — Guided onboarding and Project Profile setup in `AGENTS.md` and `CLAUDE.md`.
- `clube:clube-architecture` — Architectural constitution and engineering discipline (5 core pillars: multi-harness modular plugins, hybrid audit architecture, 4-phase output contract, runlog persistence, SemVer parity).
- `clube:fullstack-performance-resilience` — Runtime optimization (Node/Bun/Go/Python), deploy resilience, chunk recovery (`vite:preloadError`), CDN cache headers, and database query tuning.
- `clube:saas-seo-geo` — Technical SEO and Generative Engine Optimization (GEO) for SaaS, LLM discoverability (`/llms.txt`), structured data (Schema.org), and landing pages.
- `clube:marketing-attribution-analytics` — End-to-end tracking, attribution models, Meta CAPI deduplication via `event_id`, and `acquisition_context` database persistence.
- `clube:data-privacy-observability` — PII/LGPD compliance in logs, APM, traces, telemetry, blind struct logging elimination, and error tracking.

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
