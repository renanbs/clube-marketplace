---
name: audit
description: 360° SaaS production readiness audit. Runs deterministic static checks across Privacy, Performance, SEO/GEO, and Tracking, then provides LLM contextual analysis and concrete code fixes.
---

# /audit — 360° SaaS Production Readiness Audit

Runs a unified audit across all four Clube engineering pillars:
1. Data Privacy & Observability (`clube:data-privacy-observability`)
2. Fullstack Performance & Resilience (`clube:fullstack-performance-resilience`)
3. SaaS SEO & Generative Engine Optimization (`clube:saas-seo-geo`)
4. Marketing Attribution & Tracking (`clube:marketing-attribution-analytics`)

## Execution Flow

1. Execute the deterministic audit script to collect baseline facts:
   ```bash
   python3 "${CLUBE_PLUGIN_ROOT:-plugins/clube}/scripts/audit-all.py" --json
   ```
2. Parse the output. If issues are identified:
   - For **Privacy** issues: Read affected files, eliminate false positives, and propose masked domain helpers.
   - For **Performance** issues: Inspect frontend bundler / backend setup and propose chunk recovery or concurrency bounds.
   - For **SEO & GEO** issues: Check public routes and generate missing `llms.txt` or structured data.
   - For **Tracking** issues: Inspect cookie setting logic and propose root domain cookies or `acquisition_context` migrations.
3. Present the verdict adhering strictly to the **4-Phase Output Contract**:
   - `### 1. Plan`
   - `### 2. Execution`
   - `### 3. Summary` (Consolidated table across all 4 pillars)
   - `### 4. Recommended Actions` (Numbered concrete patches ready to apply)
