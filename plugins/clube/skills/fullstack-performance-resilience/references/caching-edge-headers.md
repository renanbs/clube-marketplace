# Edge Caching Policy & HTTP Headers

Technical reference for HTTP `Cache-Control` headers, CDN edge routing rules, immutable asset hashing, entrypoint revalidation, and service worker trade-offs.

---

## 1. Mandatory Principles

1. **Two Distinct Asset Classes:**
   - **Hashed Static Assets (`/assets/*-[hash].js`, `/assets/*-[hash].css`):** Immutable. Cache for 1 year with `public, max-age=31536000, immutable`.
   - **Unhashed Entrypoints (`index.html`, `sw.js`, `manifest.webmanifest`, `robots.txt`, `sitemap.xml`):** Pointers to the current release. Cache with `no-cache, no-store, must-revalidate`.
2. **Declare Explicit Paths:** Explicitly enumerate entrypoints in edge configs (`vercel.json`, Cloudflare Transform Rules, Nginx). Relying on ambiguous catch-all wildcards causes race conditions across CDN edge proxies.
3. **Avoid Redundant Service Workers:** If the application has no offline caching requirements, do not register a service worker. SW asset caches duplicate HTTP caching and introduce extra invalidation complexity.

---

## 2. Production Edge Configurations

### A. Vercel (`vercel.json`)
```json
{
  "headers": [
    {
      "source": "/",
      "headers": [{ "key": "Cache-Control", "value": "no-cache, no-store, must-revalidate" }]
    },
    {
      "source": "/index.html",
      "headers": [{ "key": "Cache-Control", "value": "no-cache, no-store, must-revalidate" }]
    },
    {
      "source": "/sw.js",
      "headers": [{ "key": "Cache-Control", "value": "no-cache, no-store, must-revalidate" }]
    },
    {
      "source": "/manifest.webmanifest",
      "headers": [{ "key": "Cache-Control", "value": "no-cache, no-store, must-revalidate" }]
    },
    {
      "source": "/assets/(.*)",
      "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }]
    }
  ]
}
```

### B. Nginx (`nginx.conf`)
```nginx
server {
    # 1. Immutable hashed bundles
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
        access_log off;
    }

    # 2. Never cache unhashed entrypoints
    location = /index.html {
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    location = /sw.js {
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    location = /manifest.webmanifest {
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }
}
```

### C. Cloudflare Rules
- **Cache Rule (Assets):** If URI path starts with `/assets/`, set Edge TTL to 1 month and Browser TTL to 1 year.
- **Cache Rule (HTML):** If URI path ends with `.html` or matches `/`, set Edge TTL to bypass and Browser TTL to respect server headers (`no-cache`).

---

## 3. Edge Cases & Common Traps

- ⚠️ **HTML Caching Disasters:** If `index.html` is cached for 1 hour, a user who loads the site 10 minutes before a deployment will request chunks that no longer exist for the remaining 50 minutes. Always revalidate HTML.
- ⚠️ **Font File MIME & CORS:** Web fonts (`.woff2`) served from CDNs require `Access-Control-Allow-Origin: *` to prevent CORS blocking across subdomains.

---

## 4. Cross-References

- [Chunk Recovery](chunk-recovery.md) — Mitigating chunk 404s when caching fails.
- [Back to Fullstack Performance Skill](../SKILL.md)
