---
name: saas-seo-geo
description: |
  Specialist in technical SEO and Generative Engine Optimization (GEO) for SaaS applications and Landing Pages.
  Stack- and hosting-agnostic: principles apply across any modern frontend architecture.
  Activate this skill whenever:
  - Creating or refactoring Landing Pages, marketing websites, public showcases, blogs, or institutional pages.
  - Configuring metadata, Open Graph, Twitter Cards, canonical tags, robots.txt, sitemaps, llms.txt, or llms-full.txt.
  - Implementing structured data (Schema.org / JSON-LD) such as SoftwareApplication, FAQPage, Organization, or BreadcrumbList.
  - Developing pages with Astro, Vite, Next.js, Nuxt, SvelteKit, or static HTML.
  - Configuring indexing policies for SPAs or authenticated apps (preventing keyword cannibalization via noindex).
license: Apache-2.0
metadata:
  version: v2.0
  author: clubedepontos
---

# SaaS SEO & GEO (Search & AI Engine Optimization)

Architectural standards for traditional search engine optimization (SEO) and Generative Engine Optimization (GEO) in SaaS products.

> **How to read this skill:** Each section first declares the **principle** (what must hold true and why) followed by an **example** in a concrete stack. The principle is mandatory; the example is illustrative. When applying to a new project, adapt the example to the project's chosen stack and hosting provider.

---

## 1. Fundamental Principle: Strict Separation (Landing Page vs App)

Every SaaS architecture requires an explicit indexing boundary. Without one, login screens, authenticated views, and empty dashboard states compete with public marketing pages for the same domain keywords, diluting brand and domain authority.

1. **Landing Pages and Public Content:**
   * Publicly accessible, rendered via Static Site Generation (SSG) or Server-Side Rendering (SSR).
   * `robots.txt` configured with `Allow: /`.
   * Absolute, dynamic canonical tags stripped of tracking parameters (`utm_*`, `fbclid`, `gclid`, etc.).

2. **Authenticated Web App / Dashboard (SPA / PWA):**
   * **MUST NEVER** be indexed by search engines.
   * Mandatory tag inside the HTML entrypoint `<head>`:
     ```html
     <meta name="robots" content="noindex, nofollow" />
     ```
   * Enforce via HTTP response headers at the CDN, edge, or reverse proxy layer — ensuring non-HTML responses and crawlers that bypass JS execution are covered:
     ```http
     X-Robots-Tag: noindex, nofollow
     ```
     *Configuration target depends on provider: `headers` in `vercel.json`, Transform Rules in Cloudflare, `add_header` in Nginx, `Header set` in Apache, or CloudFront Response Headers Policies.*

   > ⚠️ **Never place `<link rel="canonical">` on a `noindex` page.** These directives conflict (`noindex` forbids indexing, whereas `canonical` designates the authoritative indexable URL). If a page is private, omit the canonical tag entirely.

   > ⚠️ **Validate absolute domains in social tags.** Tags such as `canonical`, `og:url`, and `og:image` require absolute URLs and are prone to domain typos (`.com` vs `.com.br`, missing subdomains, staging URLs). An invalid `og:image` URL silently breaks link previews in WhatsApp, Slack, and LinkedIn without triggering build or runtime errors. Always validate with the Facebook Sharing Debugger and Twitter Card Validator prior to release.

3. **Public Showcases inside SPAs (e.g., `/store/:slug`):**
   * If a dynamic entity page needs search indexing (public storefronts, appointment scheduling links, public professional profiles), it **CANNOT** be served under a `noindex` HTML shell.
   * Render these routes via SSR/SSG in a dedicated marketing service, or deploy dynamic server pre-rendering for verified crawler user agents.

---

## 2. Meta Tags and Social Sharing

Every public HTML document must contain standard head metadata:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="theme-color" content="#0F172A" />

  <!-- Primary Title and Meta Description -->
  <title>Actionable, Solution-Oriented Title (under 60 chars) | BrandName</title>
  <meta name="description" content="Concise value proposition detailing problems solved, target audience, and a clear call to action (140-160 characters)." />

  <!-- Absolute Canonical URL: Dynamic and stripped of campaign parameters -->
  <link rel="canonical" href="https://www.domain.com/current-page" />

  <!-- Favicons and Touch Icons -->
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png" />
  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />

  <!-- Open Graph (WhatsApp, LinkedIn, Facebook, Telegram, Slack) -->
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://www.domain.com/current-page" />
  <meta property="og:locale" content="en_US" />
  <meta property="og:site_name" content="BrandName" />
  <meta property="og:title" content="Product Value Proposition | BrandName" />
  <meta property="og:description" content="Engaging summary optimized for social conversions." />
  <meta property="og:image" content="https://www.domain.com/og-image.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="Visual overview or logo of BrandName" />

  <!-- Twitter Cards -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Product Value Proposition | BrandName" />
  <meta name="twitter:description" content="Short overview for Twitter/X previews." />
  <meta name="twitter:image" content="https://www.domain.com/og-image.png" />
</head>
```

---

## 3. Structured Data (Schema.org / JSON-LD)

Include corresponding JSON-LD structured data blocks inside `<head>` to assist traditional and generative search indexers.

### A. SoftwareApplication (for SaaS)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "SaaSProductName",
  "url": "https://www.domain.com/",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Web",
  "description": "Comprehensive description of software capabilities and key features.",
  "offers": {
    "@type": "Offer",
    "price": "49.00",
    "priceCurrency": "USD",
    "priceValidUntil": "2027-12-31",
    "description": "Starting at $49/mo on the annual plan."
  }
}
</script>
```

### B. FAQPage (GEO & Rich Snippets)
> **GEO Nuance:** While traditional search engines have reduced visible FAQ rich snippets for commercial websites, `FAQPage` structured data remains **the primary structured signal for Generative Engine Optimization (GEO)**. Large Language Models and AI search engines (Perplexity, ChatGPT Search, Claude, Gemini) consume these question-and-answer pairs directly to ground citations. Every visible FAQ item on the page MUST have an identical representation in JSON-LD — text divergence between UI and structured data risks search penalties.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Exact question text displayed in the accordion?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Complete answer text verbatim matching the visible UI answer."
      }
    }
  ]
}
</script>
```

### C. Organization (Brand Entity & Knowledge Graph)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "CompanyName",
  "url": "https://www.domain.com",
  "logo": "https://www.domain.com/logo.png",
  "sameAs": [
    "https://twitter.com/companyname",
    "https://www.linkedin.com/company/companyname",
    "https://github.com/companyname"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "customer support",
    "telephone": "+1-800-555-0199",
    "availableLanguage": ["English"]
  }
}
</script>
```

### D. BreadcrumbList (Subpages and Documentation/Blog)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.domain.com/" },
    { "@type": "ListItem", "position": 2, "name": "Features", "item": "https://www.domain.com/features" }
  ]
}
</script>
```

---

## 4. Generative Engine Optimization (GEO): `llms.txt` & `llms-full.txt`

In the public root directory (`/public` served at domain root), provide structured Markdown files specifically tailored for AI search agents and semantic web crawlers.

### A. `llms.txt` (Concise Index and Key Routes)

A dense summary of the product value proposition followed by categorized links. The first paragraph is critical: AI models extract this opening description when generating brand overviews.

```markdown
# ProductName

> One-line summary of the core value proposition, target customer segment, and business model.

Detailed product summary highlighting search-intent keywords, supported industries,
flagship capabilities, transparent pricing models (including exact numbers), and key market differentiators.

## Product

- [Website](https://www.domain.com/): Official marketing website
- [Pricing](https://www.domain.com/#pricing): Subscription plans and tiers
- [FAQ](https://www.domain.com/#faq): Frequently asked questions
- [Full Context](https://www.domain.com/llms-full.txt): Complete technical documentation for LLMs

## App / Access

- [Sign Up](https://app.domain.com/register): Free trial registration
- [Log In](https://app.domain.com/login): Customer dashboard authentication

## Support & Socials

- [Twitter](https://twitter.com/brand): Updates and product announcements
- [Support](https://help.domain.com/): Knowledge base and helpdesk

## Optional

- [Sitemap](https://www.domain.com/sitemap.xml): Indexable URL inventory
- [robots.txt](https://www.domain.com/robots.txt): Crawler access rules
```

> **State clear pricing and terms:** Include real numbers and plan specifics in plain text. Generative models directly quote these details when answering user queries such as "How much does X cost?". Omitting pricing hands the recommendation to competitors who disclose theirs.

### B. `llms-full.txt` (Comprehensive Context)
For models with large context windows, assemble a consolidated Markdown document containing:
1. Exhaustive breakdown of every product feature and workflow.
2. Complete questions and answers from all FAQ sections.
3. Feature comparison matrices against market alternatives.
4. Support policies, data security/privacy standards, and integration specifications.

Generate this file at build time from the single source of truth (content collections, FAQ data modules) rather than maintaining it manually to prevent outdated information.

---

## 5. Crawlability & Clean URLs

**1. `robots.txt`:**
```txt
User-agent: *
Allow: /

# Block internal API endpoints and private callbacks
Disallow: /api/

Sitemap: https://www.domain.com/sitemap.xml
```

**2. `sitemap.xml`:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.domain.com/</loc>
    <lastmod>2026-09-13</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
```
Generate sitemaps automatically during the build process using framework integrations (`@astrojs/sitemap`, `next-sitemap`, `nuxt/sitemap`). Manually maintained sitemaps drift out of sync immediately upon adding new pages.

**3. Single Canonical URL Structure (Clean URLs):**
Principle: Every piece of content must resolve to exactly **one** URL. Serving the same HTML from `/page`, `/page/`, and `/page.html` creates duplicate content and splits ranking signals. Select a canonical standard and issue permanent (301) redirects for all variants.

*Provider configurations:*
```json
// Vercel (vercel.json)
{ "cleanUrls": true, "trailingSlash": false }
```
```nginx
# Nginx
rewrite ^/(.*)\.html$ /$1 permanent;
rewrite ^/(.+)/$ /$1 permanent;
```
On Cloudflare Pages, enable URL Normalization; on Netlify, configure `pretty_urls`. In framework SSG, set options such as `trailingSlash: 'never'` in Astro, Next.js, or Nuxt.

---

## 6. Landing Page Stack Selection

**Principle:** Marketing landing pages must deliver fully rendered HTML on the very first byte with zero client-side JavaScript required for indexable content, while supporting component reusability (`<Header />`, `<Footer />`, `<SEO />`, `<FAQ />`) as the page count expands. Handcrafted static HTML meets the performance goal but fails at scale: past ~5 pages, shared headers, analytics snippets, and JSON-LD schemas inevitably diverge due to copy-pasting.

**Recommended Default:** If the project has no preexisting framework requirements, **Astro** is the optimal choice:
* Generates static HTML with 0 KB of client JavaScript by default.
* Provides full component composition (`<Header />`, `<Footer />`, `<SEO />`, `<FAQ />`).
* Markdown/MDX content collections enable scalable programmatic SEO (pages segmented by niche, city, or use case).
* Native sitemap and RSS generation via `@astrojs/sitemap`.

**When to choose alternatives:** If your team already operates a Next.js or Nuxt codebase and the landing page shares design systems, component libraries, or deployment pipelines, operational consistency outweighs a few kilobytes saved — use the existing framework. Likewise, a single, stable static page does not warrant migrating stacks.
