# Generative Engine Optimization (GEO) & llms.txt

Technical guide for structuring web assets and documentation for Generative Engine Optimization (GEO) and AI search agents (ChatGPT Search, Perplexity, Claude, Gemini).

---

## 1. Mandatory Principles

1. **Root-Level Markdown Endpoints:** Expose clean, structured Markdown summaries at `/llms.txt` (curated index) and `/llms-full.txt` (comprehensive documentation) served directly from the public web root.
2. **Transparent, Grounded Pricing in Plain Text:** AI engines extract exact numbers and plan features to answer queries like "How much does [Brand] cost?". Withholding pricing or hiding it behind JavaScript calculators causes AI engines to cite competitors who disclose transparent pricing.
3. **High-Density Opening Value Proposition:** The first paragraph of `llms.txt` is the primary snippet extracted by AI models to summarize the product.

---

## 2. Standard `llms.txt` Format

Place this file at `/public/llms.txt` (served at `https://www.domain.com/llms.txt`):

```markdown
# ProductName

> One-line executive summary of the core value proposition, target customer segment, and business model.

Detailed product overview highlighting search-intent keywords, supported industries,
flagship capabilities, transparent pricing models (e.g. $49/mo Starter, $199/mo Growth),
and primary architectural differentiators.

## Product & Features

- [Website](https://www.domain.com/): Official marketing website
- [Features](https://www.domain.com/#features): Core capabilities and workflows
- [Pricing](https://www.domain.com/#pricing): Detailed subscription plans ($49-$199/mo)
- [FAQ](https://www.domain.com/#faq): Frequently asked questions
- [Full Context](https://www.domain.com/llms-full.txt): Complete technical documentation for LLMs

## Platform Access

- [Sign Up](https://app.domain.com/register): 14-day free trial registration
- [Log In](https://app.domain.com/login): Customer dashboard authentication

## Support & Socials

- [Documentation](https://docs.domain.com/): User guides and API documentation
- [Twitter](https://twitter.com/brandhandle): Product updates and releases
- [Support](https://help.domain.com/): Customer support desk

## Indexing & Verification

- [Sitemap](https://www.domain.com/sitemap.xml): Machine-readable URL inventory
- [robots.txt](https://www.domain.com/robots.txt): Crawler rules and permissions
```

---

## 3. Comprehensive `llms-full.txt` Generation

For LLMs with large context windows, provide `/public/llms-full.txt` containing:

1. **Exhaustive Feature Breakdown:** Descriptions of every workflow, module, and integration.
2. **Complete FAQ Data:** All Q&A pairs matching the visible UI and `FAQPage` JSON-LD.
3. **Comparison Matrix:** Clear, factual differentiators against common alternatives.
4. **Security & Compliance:** SOC2, GDPR, LGPD, and encryption guarantees.

### Build-Time Generation Script (Node.js / Bun example)

```javascript
import fs from 'node:fs';
import path from 'node:path';

export function buildLlmsFull({ productData, faqs, features, pricing }) {
  const content = `# ${productData.name} - Complete Context Document

## 1. Overview
${productData.description}

## 2. Pricing & Plans
${pricing.map(p => `- **${p.name}** (${p.price}): ${p.features.join(', ')}`).join('\n')}

## 3. Core Features
${features.map(f => `### ${f.title}\n${f.description}`).join('\n\n')}

## 4. Frequently Asked Questions
${faqs.map(q => `### ${q.question}\n${q.answer}`).join('\n\n')}
`;

  fs.writeFileSync(path.resolve('./public/llms-full.txt'), content, 'utf8');
}
```

---

## 4. Edge Cases & Common Traps

- ⚠️ **Stale Information Drift:** Do not hand-edit `llms-full.txt`. Generate it automatically during CI/CD from your content collections or source data.
- ⚠️ **Blocking AI Crawlers:** If GEO is a business objective, ensure `robots.txt` does not disallow user agents like `GPTBot`, `PerplexityBot`, `Claude-Web`, or `OAI-SearchBot`.

---

## 5. Cross-References

- [JSON-LD Schemas](json-ld-schemas.md) — Structured FAQPage for AI search grounding.
- [Crawling & Sitemaps](crawling-sitemaps.md) — Crawler access and `robots.txt`.
- [Back to SaaS SEO Skill](../SKILL.md)
