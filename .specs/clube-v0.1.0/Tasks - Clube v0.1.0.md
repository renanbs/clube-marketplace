# Tasks - Clube v0.1.0

## Wave 1 (Async Implementation)

### Task 1: English Translation of Core Skills
- **ID:** T1
- **What:** Rewrite `fullstack-performance-resilience`, `saas-seo-geo`, `marketing-attribution-analytics`, and `data-privacy-observability` into authoritative, technical English.
- **Where:** `plugins/clube/skills/*/SKILL.md`
- **Depends On:** None
- **Async:** True
- **Goals:** G1
- **Done When:** All 4 skills contain English frontmatter and body with complete technical fidelity.
- **Tests:** `make check` confirms valid frontmatter and valid markdown.

### Task 2: Architecture Constitution Skill
- **ID:** T2
- **What:** Author `clube-architecture/SKILL.md` defining the 5 marketplace pillars.
- **Where:** `plugins/clube/skills/clube-architecture/SKILL.md`
- **Depends On:** None
- **Async:** True
- **Goals:** G2
- **Done When:** Skill is registered and documented.
- **Tests:** `make check` detects 6 valid modular skills.

### Task 3: Visual UI & Runlog Engine
- **ID:** T3
- **What:** Implement `plugins/clube/scripts/ui.py` and integrate it into all 5 audit scripts with `.clube/audit-last.json` persistence.
- **Where:** `plugins/clube/scripts/`
- **Depends On:** None
- **Async:** True
- **Goals:** G3
- **Done When:** `python3 plugins/clube/scripts/audit-all.py` outputs colored ASCII cards and creates `.clube/audit-last.json`.
- **Tests:** Run all 5 scripts and verify JSON file integrity.

---

## Wave 2 (Integration & Docs)

### Task 4: SemVer 0.1.0 Synchronization
- **ID:** T4
- **What:** Align all 9 manifest files to `"version": "0.1.0"` and update `bin/clube-config check` to verify version parity.
- **Where:** Root and plugin manifests, `bin/clube-config`
- **Depends On:** T1, T2, T3
- **Async:** False
- **Goals:** G4
- **Done When:** All manifests match `0.1.0`.
- **Tests:** `make check` verifies version parity.

### Task 5: Bilingual Documentation
- **ID:** T5
- **What:** Create `README.pt-BR.md`, `CHANGELOG.md`, `CHANGELOG.pt-BR.md`, and update `README.md` and `help.md`.
- **Where:** `README.md`, `README.pt-BR.md`, `CHANGELOG.md`, `CHANGELOG.pt-BR.md`, `plugins/clube/commands/help.md`
- **Depends On:** T4
- **Async:** False
- **Goals:** G5
- **Done When:** Documentation is 100% mirrored in English and Portuguese.
- **Tests:** Markdown files exist, link to each other, and pass formatting check.

---

## Wave 3 (Review & Verification)

### Task 6: Final Verification & PR
- **ID:** T6
- **What:** Run `make check`, `make audit`, perform `review` and `expert-security` review, commit, push, create PR, and merge.
- **Where:** Repository root
- **Depends On:** T5
- **Async:** False
- **Goals:** G6
- **Done When:** PR merged into `main`.
- **Tests:** `make check` and `make audit` pass.
