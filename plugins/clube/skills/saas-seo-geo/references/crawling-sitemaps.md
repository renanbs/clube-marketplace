# Crawling, Sitemaps & Clean URLs

Technical guide for crawler indexing controls, `robots.txt`, dynamic XML sitemaps, HTTP headers, and URL normalization.

---

## 1. Mandatory Principles

1. **Explicit Indexing Boundary:** Public marketing and documentation pages must be indexable (`Allow: /`), while authenticated web apps, SPAs, and admin panels must explicitly forbid indexing (`noindex, nofollow`).
2. **HTTP Header Enforcement (`X-Robots-Tag`):** In addition to HTML `<meta name="robots">`, configure `X-Robots-Tag: noindex, nofollow` on backend APIs, private subdomains, and CDN edge layers to protect non-HTML assets.
3. **Single Canonical URL Normalization:** Content must resolve to exactly one URL standard (e.g. no trailing slashes, clean paths without `.html`). Duplicate paths must 301-redirect to the canonical URL.

---

## 2. Crawler Configuration Templates

### A. Production `robots.txt`

```txt
User-agent: *
Allow: /

# Disallow private dashboards, internal APIs, and auth callbacks
Disallow: /api/
Disallow: /auth/
Disallow: /app/
Disallow: /admin/

Sitemap: https://www.domain.com/sitemap.xml
```

### B. Dynamic XML Sitemap (`sitemap.xml`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.domain.com/</loc>
    <lastmod>2026-09-13</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://www.domain.com/features</loc>
    <lastmod>2026-09-13</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://www.domain.com/pricing</loc>
    <lastmod>2026-09-13</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
```

---

## 3. Server & Edge URL Normalization

### Vercel (`vercel.json`)
```json
{
  "cleanUrls": true,
  "trailingSlash": false,
  "headers": [
    {
      "source": "/app/(.*)",
      "headers": [
        { "key": "X-Robots-Tag", "value": "noindex, nofollow" }
      ]
    }
  ]
}
```

### Nginx Configuration
```nginx
# Strip trailing slashes and .html extensions to enforce clean canonical URLs
rewrite ^/(.*)\.html$ /$1 permanent;
rewrite ^/(.+)/$ /$1 permanent;

location /app/ {
    add_header X-Robots-Tag "noindex, nofollow" always;
    try_files $uri $uri/ /app/index.html;
}
```

---

## 4. Edge Cases & Common Traps

- ⚠️ **Public Entities in SPAs:** If an application includes public storefronts or profiles under dynamic routes (e.g. `/store/:slug`), do not serve them under a global `noindex` SPA shell. Use SSR/SSG or edge prerendering for verified crawler user agents.
- ⚠️ **Sitemap Staleness:** Never maintain sitemaps manually. Integrate automated build-time sitemap generators (e.g., `@astrojs/sitemap`, `next-sitemap`).

---

## 5. Cross-References

- [Meta & Social Metadata](meta-social.md) — HTML meta tags and canonical configuration.
- [GEO & llms.txt](geo-llmstxt.md) — AI crawler guidance.
- [Back to SaaS SEO Skill](../SKILL.md)
