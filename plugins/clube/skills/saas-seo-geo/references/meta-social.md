# Meta Tags, Open Graph & Social Sharing

Technical guide for HTML head metadata, social link previews (Open Graph, Twitter Cards), canonical URLs, and indexing boundaries.

---

## 1. Mandatory Principles

1. **Absolute URLs for Canonical & Social Assets:** Tags like `<link rel="canonical">`, `og:url`, and `og:image` MUST use absolute HTTPS URLs with valid domains. Missing domains or relative paths break link previews on social platforms (WhatsApp, Slack, LinkedIn, Twitter/X).
2. **Dynamic Canonical Normalization:** The canonical tag must strip all campaign/tracking parameters (`utm_*`, `fbclid`, `gclid`, `ref`, etc.) to prevent duplicate content indexing.
3. **Noindex Boundary for Authenticated Routes:** Dashboards, settings, and login pages must declare `<meta name="robots" content="noindex, nofollow" />`.
4. **Never Canonicalize Noindex Pages:** Never place a canonical tag on a `noindex` page. The directives are mutually contradictory.

---

## 2. Production HTML Head Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="theme-color" content="#0F172A" />

  <!-- Primary Title and Meta Description -->
  <title>Actionable, Solution-Oriented Title (under 60 chars) | BrandName</title>
  <meta name="description" content="Concise value proposition detailing problems solved, target audience, and clear call to action (140-160 chars)." />

  <!-- Canonical URL: Dynamic and stripped of campaign parameters -->
  <link rel="canonical" href="https://www.domain.com/current-page" />

  <!-- Favicons and Touch Icons -->
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png" />
  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
  <link rel="manifest" href="/site.webmanifest" />

  <!-- Open Graph (WhatsApp, LinkedIn, Facebook, Slack, Discord) -->
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://www.domain.com/current-page" />
  <meta property="og:locale" content="en_US" />
  <meta property="og:site_name" content="BrandName" />
  <meta property="og:title" content="Product Value Proposition | BrandName" />
  <meta property="og:description" content="Engaging summary optimized for social conversions." />
  <meta property="og:image" content="https://www.domain.com/og-image.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="Visual overview or preview of BrandName" />

  <!-- Twitter / X Cards -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:site" content="@BrandHandle" />
  <meta name="twitter:title" content="Product Value Proposition | BrandName" />
  <meta name="twitter:description" content="Short overview for Twitter/X previews." />
  <meta name="twitter:image" content="https://www.domain.com/og-image.png" />
</head>
```

---

## 3. Dynamic Canonical Helper (TypeScript / JavaScript)

```typescript
/**
 * Strips tracking parameters and constructs the authoritative canonical URL.
 */
export function getCanonicalUrl(origin: string, pathname: string, allowedParams: string[] = []): string {
  const url = new URL(pathname, origin);
  const cleanParams = new URLSearchParams();

  for (const [key, value] of url.searchParams.entries()) {
    if (allowedParams.includes(key)) {
      cleanParams.set(key, value);
    }
  }

  const queryString = cleanParams.toString();
  return `${url.origin}${url.pathname}${queryString ? `?${queryString}` : ''}`;
}
```

---

## 4. Edge Cases & Common Traps

- ⚠️ **Staging/Local Leaks:** Ensure CI/CD builds for staging or PR previews do not bake production URLs into `og:image` or canonical tags. In staging, inject `<meta name="robots" content="noindex, nofollow" />`.
- ⚠️ **OG Image Dimensions:** Open Graph images should strictly measure `1200x630` px with an aspect ratio of `1.91:1`. Ensure critical text and logos sit inside the safe central zone (`1000x520` px).
- ⚠️ **Missing Trailing Slash Normalization:** Inconsistent trailing slashes (`/pricing` vs `/pricing/`) cause canonical divergence. Maintain a single standard across internal links and canonicals.

---

## 5. Cross-References

- [JSON-LD Schemas](json-ld-schemas.md) — Enrich metadata with Schema.org structured data.
- [Crawling & Sitemaps](crawling-sitemaps.md) — Indexing boundaries and `robots.txt` configuration.
- [Back to SaaS SEO Skill](../SKILL.md)
