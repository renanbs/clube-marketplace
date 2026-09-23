---
name: saas-seo-geo
description: |
  Specialist in technical SEO and Generative Engine Optimization (GEO) for SaaS applications and Landing Pages.
  Stack- and hosting-agnostic: principles apply across any modern frontend architecture.
  Activate this skill whenever configuring metadata, structured data, GEO (llms.txt), or crawler indexing.
license: Apache-2.0
metadata:
  version: v0.6.0
  author: clubedepontos
---

# SaaS SEO & GEO (Search & AI Engine Optimization)

Architectural standards for search engine optimization (SEO) and Generative Engine Optimization (GEO) across SaaS marketing pages, documentation, and web applications.

---

## 1. Core Principles

1. **Strict Indexing Separation:** Public marketing pages must be statically indexed with dynamic canonicals, while authenticated dashboards and private web applications must strictly enforce `noindex, nofollow` in HTML and edge headers.
2. **Generative Grounding (GEO):** Maintain high-density structured contexts (`/llms.txt`, `FAQPage` JSON-LD) with explicit pricing and feature details to ground LLM-driven search engines (Perplexity, ChatGPT Search, Claude).
3. **Structured Entity Schema:** Implement valid Schema.org JSON-LD matching visible UI text verbatim.
4. **URL Normalization:** Enforce a single canonical URL structure (clean URLs, normalized slashes) with 301 redirects.

---

## 2. Activation Triggers

| Trigger Area | Description & Indicators | Target Reference |
| :--- | :--- | :--- |
| **Meta & Social** | Open Graph, Twitter Cards, canonical tags, theme colors, touch icons, link preview debugging. | [Meta & Social Sharing](references/meta-social.md) |
| **Structured Data** | `SoftwareApplication`, `FAQPage`, `Organization`, `BreadcrumbList` JSON-LD schemas. | [JSON-LD Schemas](references/json-ld-schemas.md) |
| **GEO & LLMs** | AI search optimization, `/llms.txt` and `/llms-full.txt` generation, transparent pricing context. | [GEO & llms.txt](references/geo-llmstxt.md) |
| **Crawling & Indexing** | `robots.txt`, dynamic `sitemap.xml`, clean URL redirects, edge `X-Robots-Tag` headers. | [Crawling & Sitemaps](references/crawling-sitemaps.md) |

---

## 3. Modular References Index

Detailed guides, DDLs, schemas, and framework configurations reside in the `references/` directory:

- 📄 **[Meta Tags, Open Graph & Social Sharing](references/meta-social.md)** — Production `<head>` template, dynamic canonical helpers, and social preview optimization.
- 📄 **[Schema.org Structured Data (JSON-LD)](references/json-ld-schemas.md)** — Ready-to-use JSON-LD templates for SaaS products, FAQs, organizations, and breadcrumbs.
- 📄 **[Generative Engine Optimization (GEO) & llms.txt](references/geo-llmstxt.md)** — Markdown standards and build-time context generation for AI search agents.
- 📄 **[Crawling, Sitemaps & Clean URLs](references/crawling-sitemaps.md)** — `robots.txt` configuration, dynamic sitemaps, clean URL redirects, and SPA indexing boundaries.

---

## 4. Stack Recommendation

For standalone marketing pages, **Astro** is the recommended default (0 KB client JavaScript by default, component composition, native sitemaps). For existing fullstack apps, reuse the existing framework (Next.js, Nuxt, SvelteKit) to maintain operational consistency.
