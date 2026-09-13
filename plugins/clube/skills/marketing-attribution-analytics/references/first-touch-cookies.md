# First-Touch Attribution & Root Domain Cookies

Technical guide for capturing first-touch marketing attribution parameters, managing root domain cookies across subdomains, handling Public Suffix List (PSL) rules, and generating ad platform continuity tokens.

---

## 1. Mandatory Principles

1. **First-Touch Preservation:** Campaign parameters that drove the initial user visit (`utm_*`, `fbclid`, `gclid`, `gbraid`, `wbraid`) must be captured immediately on first landing and preserved across cross-page navigations and transitions to the application subdomain.
2. **Explicit Root Domain Scoping:** Cookies shared across subdomains (`domain.com` and `app.domain.com`) must declare `; domain=.domain.com`.
3. **Never Naively Derive Root Domains:** Naively splitting hostnames by `.` breaks on:
   - **Compound TLDs:** `.com.br`, `.co.uk`, `.org.br` (requires 3 labels).
   - **Public Suffix List (PSL):** Setting cookies on `*.vercel.app`, `*.netlify.app`, `*.pages.dev`, or `*.github.io` causes browsers to silently reject the cookie without throwing errors.
   - **Rule:** Only set the `domain` attribute for explicit, known production root domains. For localhost and preview environments, omit the `domain` attribute (host-only cookie).
4. **SessionStorage Parallel Fallback:** Always persist a mirror of captured attribution in `sessionStorage` to retain continuity if cookies are cleared or restricted.

---

## 2. Production Cookie & Attribution Manager (TypeScript / JavaScript)

```typescript
const COOKIE_DAYS = 90;

// Explicit production root domains list
const PRODUCT_ROOT_DOMAINS = ['domain.com', 'brand.com.br'];

/**
 * Returns the `; domain=.root` string only when matching known production domains.
 * Returns empty string for localhost, raw IPs, and preview platforms (Vercel, Netlify).
 */
export function getCookieDomainSuffix(): string {
  if (typeof window === 'undefined') return '';
  const hostname = window.location.hostname;

  const root = PRODUCT_ROOT_DOMAINS.find(
    (domain) => hostname === domain || hostname.endsWith(`.${domain}`)
  );

  return root ? `; domain=.${root}` : '';
}

export function setAttributionCookie(name: string, value: string, days = COOKIE_DAYS): void {
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  const secure = window.location.protocol === 'https:' ? '; Secure' : '';

  document.cookie =
    `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/` +
    `${getCookieDomainSuffix()}; SameSite=Lax${secure}`;
}

export function getCookie(name: string): string {
  if (typeof document === 'undefined') return '';
  const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const match = document.cookie.match(new RegExp(`(?:^|; )${escaped}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : '';
}
```

---

## 3. Ad Platform Token Generation (`_fbc` & `_fbp`)

Meta Pixel and Conversions API require `_fbc` and `_fbp` for event match quality:

```typescript
export function initializeMetaCookies(): { fbc: string; fbp: string } {
  const urlParams = new URLSearchParams(window.location.search);
  const fbclid = urlParams.get('fbclid');

  // 1. Handle _fbc (Click ID)
  let fbc = getCookie('_fbc');
  if (fbclid && !fbc) {
    fbc = `fb.1.${Date.now()}.${fbclid}`;
    setAttributionCookie('_fbc', fbc);
  }

  // 2. Handle _fbp (Browser ID)
  let fbp = getCookie('_fbp');
  if (!fbp) {
    const randomInt = Math.floor(Math.random() * 2147483647);
    fbp = `fb.1.${Date.now()}.${randomInt}`;
    setAttributionCookie('_fbp', fbp);
  }

  return { fbc, fbp };
}
```

---

## 4. Edge Cases & Common Traps

- ⚠️ **Preserve Passed Query Parameters:** If your landing page passes formed tracking parameters in query strings (e.g., `?pt_fbc=...&pt_fbp=...`), always prefer the passed value over generating new IDs. Regenerating resets user attribution continuity.
- ⚠️ **Safari ITP / 7-Day Cap:** JavaScript `document.cookie` is capped at 7 days (or 24 hours with link decoration) on Safari. Transitioning attribution data to server-side `Set-Cookie` headers or persisting into `acquisition_context` on signup mitigates this limitation.

---

## 5. Cross-References

- [Deduplication & Hygiene](deduplication-hygiene.md) — Event deduplication and route filtering.
- [Database Attribution](database-attribution.md) — Relational schema for `acquisition_context`.
- [Back to Marketing Attribution Skill](../SKILL.md)
