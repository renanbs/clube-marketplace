# Spec - Clube v0.1.0

## 1. Skill Translations (G1)
The 4 Clube skills must be translated into authoritative, technical English:
- `fullstack-performance-resilience`: SPA chunk recovery (`vite:preloadError`, `router.onError`), CDN cache headers (`immutable`), container cgroups (`automaxprocs`), connection pools, and query tuning.
- `saas-seo-geo`: Strict LP vs App separation (`noindex`), metadata/OpenGraph, Schema.org JSON-LD, `/llms.txt` and `/llms-full.txt` specifications for LLM crawlers.
- `marketing-attribution-analytics`: First-touch UTM cookies on root domain, Meta CAPI deduplication via `event_id`, database persistence via `acquisition_context JSONB`.
- `data-privacy-observability`: "Log the shape, not the data", masking helpers, prohibiting blind struct serialization (`%+v`, `zap.Any`), Sentry scrubbing, metric label safety, and read-only impersonation audit.

## 2. Architecture Skill: `clube-architecture` (G2)
Location: `plugins/clube/skills/clube-architecture/SKILL.md`
Frontmatter: `name: clube-architecture`, description explaining its role as the marketplace constitution.
Defines:
- Pillar 1: Multi-Harness Modular Marketplace layout (`plugins/*`, root manifests).
- Pillar 2: Hybrid Architecture (deterministic Python script + LLM command).
- Pillar 3: 4-Phase Output Contract (`Plan`, `Execution`, `Summary`, `Recommended Actions`).
- Pillar 4: Structured State Logging (`.clube/audit-last.json`).
- Pillar 5: SemVer Parity & Bilingual Documentation.

## 3. Visual UI Module & Runlog (G3)
File: `plugins/clube/scripts/ui.py`
- Exposes:
  - ANSI colors and styling (`BOLD`, `GREEN`, `YELLOW`, `RED`, `CYAN`, `GRAY`, `RESET`).
  - `print_header(title, subtitle)`: ASCII box with centered title.
  - `format_badge(status, text)`: Colored badge `[PASS]`, `[WARN]`, `[FAIL]`.
  - `render_table(headers, rows)`: ASCII border table.
  - `render_health_bar(score)`: Visual graphical block bar `[██████░░]`.
  - `save_runlog(data, output_file=".clube/audit-last.json")`: JSON state saver.
- Integrated into `audit-privacy.py`, `audit-performance.py`, `audit-seo.py`, `audit-tracking.py`, and `audit-all.py`.

## 4. SemVer 0.1.0 Parity (G4)
Every manifest must declare `"version": "0.1.0"`:
- `package.json`
- `.claude-plugin/marketplace.json`
- `.omp-plugin/marketplace.json`
- `.cursor-plugin/marketplace.json`
- `.agents/plugins/marketplace.json`
- `plugins/clube/.claude-plugin/plugin.json`
- `plugins/clube/.cursor-plugin/plugin.json`
- `plugins/clube/.codex-plugin/plugin.json`
- `plugins/clube/.omp-plugin/plugin.json`

## 5. Bilingual Documentation (G5)
- `README.md`: English canonical showcase.
- `README.pt-BR.md`: Complete Brazilian Portuguese mirror.
- `CHANGELOG.md`: Keep a Changelog starting at `0.1.0`.
- `CHANGELOG.pt-BR.md`: Portuguese mirror of the changelog.
- `plugins/clube/commands/help.md`: Reflects all 6 skills and 8 commands.
