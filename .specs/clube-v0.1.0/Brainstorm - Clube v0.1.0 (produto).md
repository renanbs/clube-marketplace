# Brainstorm - Clube v0.1.0 (produto)

## 1. Problem Statement
The `clube-marketplace` repository has successfully transitioned to a multi-harness modular plugin architecture. However, several production-grade standards are pending to reach release `v0.1.0`:
1. **Language Inconsistency:** Core skills (`fullstack-performance-resilience`, `saas-seo-geo`, `marketing-attribution-analytics`, `data-privacy-observability`) are currently in Portuguese. They must be in canonical English to ensure maximum AI model prompt adherence, token efficiency, and international standards.
2. **Missing Repository Architecture Skill:** Developers and AI assistants need an explicit architectural constitution (`clube-architecture`) defining the pillars for adding new skills, commands, and scripts without breaking cross-harness compatibility.
3. **Version Alignment (SemVer 0.1.0):** The marketplace needs a clean, uniform version reset to `0.1.0` across all 9 manifest files.
4. **Bilingual Documentation:** While internal instructions remain English, user-facing team documentation needs Portuguese mirrors (`README.pt-BR.md`, `CHANGELOG.pt-BR.md`).
5. **Visual Terminal UI & AI Runlog:** Audit scripts must render colored ASCII reports for developers while writing persistent `.clube/audit-last.json` for AI tools.

## 2. Target Users & Beneficiaries
- **Clube Engineering Team:** Quick CLI auditing (`make audit`, `clube-config audit`) and clear Portuguese guides.
- **AI Coding Harnesses (Claude Code, Cursor, Codex, OMP):** Canonical English skills for high token density and zero instruction drift; structured JSON files for deterministic facts.

## 3. Success Criteria (Goals)
- **G1:** All 4 Clube SaaS skills translated to rich, canonical English.
- **G2:** `clube-architecture` skill created and registered in `plugins/clube/skills/clube-architecture/SKILL.md`.
- **G3:** All 9 manifest files synchronized to version `0.1.0`.
- **G4:** Bilingual documentation complete: `README.md`, `README.pt-BR.md`, `CHANGELOG.md`, `CHANGELOG.pt-BR.md`.
- **G5:** Shared UI module (`plugins/clube/scripts/ui.py`) integrated into all audit scripts with colored output and `.clube/audit-last.json` persistence.
- **G6:** `make check` and `make audit` pass with 100% compliance.

## 4. Constraints & Invariants
- Zero external Python pip dependencies (standard library only).
- All audit operations remain 100% read-only on inspected project files.
- Single Source of Truth (`AGENTS.md`) preserved.

## 5. Non-Goals
- Adding third-party or BigQuery/GCP skills (kept out of scope).
- Automated mutation / auto-fixing of user code without explicit interactive prompts.
