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


## Available Skills

- `clube:init` — Guided onboarding and Project Profile setup.
- `clube:fullstack-performance-resilience` — Runtime optimization (Node/Bun/Go/Python), deploy resilience, chunk recovery, and database query tuning.
- `clube:saas-seo-geo` — Technical SEO and Generative Engine Optimization (GEO) for SaaS and landing pages.
- `clube:marketing-attribution-analytics` — End-to-end tracking, attribution models, and marketing metric instrumentation.
- `clube:data-privacy-observability` — PII/LGPD compliance in logs, APM, traces, telemetry, and error tracking.
## Core Principles

1. **Single Source of Truth (`AGENTS.md`):** Every project declares its Project Profile inside `AGENTS.md` and imports it into `CLAUDE.md`, `GEMINI.md`, and `.cursorrules` using `@AGENTS.md`.
2. **4-Phase Output Contract:** Commands and agents report progress following:
   - `### 1. Plan`
   - `### 2. Execution`
   - `### 3. Summary`
   - `### 4. Recommended Actions`
3. **Product-Agnostic Skills:** Skills encapsulate transferrable engineering disciplines; concrete project facts (paths, CI commands, connections) live strictly in each project's Project Profile.
