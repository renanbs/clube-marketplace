# Brainstorm - Clube v0.1.0 (codigo)

## 1. Lane & Sizing
- **Lane:** M (Medium scope, multi-file refactoring across skills, manifests, scripts, and bilingual documentation).
- **Mandate:** Orchestrator delegates implementation tasks to specialized subagents; coordinates git and verification gates.

## 2. Blast Radius & Affected Components
- `plugins/clube/skills/`:
  - `fullstack-performance-resilience/SKILL.md` (Translate PT -> EN)
  - `saas-seo-geo/SKILL.md` (Translate PT -> EN)
  - `marketing-attribution-analytics/SKILL.md` (Translate PT -> EN)
  - `data-privacy-observability/SKILL.md` (Translate PT -> EN)
  - `clube-architecture/SKILL.md` (New architecture constitution skill)
- Manifests (9 files bumped to SemVer `0.1.0`):
  - `package.json`
  - `.claude-plugin/marketplace.json`
  - `.omp-plugin/marketplace.json`
  - `.cursor-plugin/marketplace.json`
  - `.agents/plugins/marketplace.json`
  - `plugins/clube/.claude-plugin/plugin.json`
  - `plugins/clube/.cursor-plugin/plugin.json`
  - `plugins/clube/.codex-plugin/plugin.json`
  - `plugins/clube/.omp-plugin/plugin.json`
- Scripts & UI:
  - `plugins/clube/scripts/ui.py` (New ANSI color & ASCII card module)
  - `plugins/clube/scripts/audit-privacy.py` (Integrate ui.py & `.clube/audit-last.json`)
  - `plugins/clube/scripts/audit-performance.py` (Integrate ui.py & `.clube/audit-last.json`)
  - `plugins/clube/scripts/audit-seo.py` (Integrate ui.py & `.clube/audit-last.json`)
  - `plugins/clube/scripts/audit-tracking.py` (Integrate ui.py & `.clube/audit-last.json`)
  - `plugins/clube/scripts/audit-all.py` (Integrate ui.py & `.clube/audit-last.json`)
- Documentation:
  - `README.md` (EN - Updated with v0.1.0 & new skills)
  - `README.pt-BR.md` (PT - Complete Portuguese guide)
  - `CHANGELOG.md` (EN - Keep a Changelog standard)
  - `CHANGELOG.pt-BR.md` (PT - Changelog in Portuguese)
  - `plugins/clube/commands/help.md` (Reflect all 6 skills)

## 3. Key Architectural Decisions
- **Zero Third-Party Dependencies:** `ui.py` uses pure ANSI escape codes with TTY auto-detection (`sys.stdout.isatty()`) so colors degrade gracefully when redirected to CI logs or files.
- **Runlog Persistence:** Scripts create `.clube/` if missing and record the last execution in `.clube/audit-last.json` with a standard schema (timestamp, audit, verdict, score, findings).
- **SemVer Strictness:** All 9 manifests must declare exactly `0.1.0`. `bin/clube-config check` will verify version parity.

## 4. Async Dispatch Strategy
- **Wave 1:**
  - Task 1: English translation of the 4 SaaS skills (`fullstack-performance-resilience`, `saas-seo-geo`, `marketing-attribution-analytics`, `data-privacy-observability`).
  - Task 2: Creation of `clube-architecture/SKILL.md`.
  - Task 3: Implementation of `ui.py` and integration into all `audit-*.py` scripts.
- **Wave 2:**
  - Task 4: Manifests version alignment to `0.1.0` and `bin/clube-config` check enhancement.
  - Task 5: Bilingual documentation (`README.md`, `README.pt-BR.md`, `CHANGELOG.md`, `CHANGELOG.pt-BR.md`, `help.md`).
- **Wave 3:**
  - Verification & Code Review (`review` + `expert-security`).
