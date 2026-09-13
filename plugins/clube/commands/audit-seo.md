---
name: audit-seo
description: Audits technical SEO and Generative Engine Optimization (GEO) for AI search engines (ChatGPT, Perplexity, Claude).
---

# /audit-seo — SaaS SEO & Generative Engine Optimization Audit

Audit codebase against the `clube:saas-seo-geo` playbook:
- Verifies existence of `/llms.txt` and `/llms-full.txt` for AI search engines.
- Checks strict separation between public landing pages and private app routes (`noindex`).
- Audits canonical URLs and Open Graph tags.
- Audits Schema.org structured data (`application/ld+json`).

## Execution Flow

1. Execute the deterministic SEO scanner:
   ```bash
   python3 "${CLUBE_PLUGIN_ROOT:-plugins/clube}/scripts/audit-seo.py" --json
   ```
2. For identified opportunities:
   - Generate high-quality `/llms.txt` containing the SaaS value proposition, pricing tiers, and capabilities.
   - Propose `noindex` guards for internal app routes to prevent search cannibalization.
   - Scaffold structured data (`SoftwareApplication` or `FAQPage`).
3. Report results using the **4-Phase Output Contract**:
   - `### 1. Plan`
   - `### 2. Execution`
   - `### 3. Summary` (Table of findings and severity)
   - `### 4. Recommended Actions` (Exact files to create or update)
