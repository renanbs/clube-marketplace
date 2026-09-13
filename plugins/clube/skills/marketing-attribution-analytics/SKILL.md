---
name: marketing-attribution-analytics
description: |
  Specialist in metric instrumentation, tracking, and end-to-end attribution for SaaS products.
  Domain skill: concrete for Meta and Google platforms, while infrastructure components
  (cookies, storage, deduplication, routing) are framework-agnostic.
  Activate this skill whenever:
  - Implementing or updating conversion tags (Meta Pixel, Google Ads, GA4, PostHog, Mixpanel).
  - Developing lead capture flows, signup/registration, onboarding, or checkout and payments.
  - Configuring campaign attribution (UTMs, fbclid, gclid, gbraid, wbraid, _fbc, _fbp).
  - Handling backend marketing persistence (acquisition_context JSONB column).
  - Implementing server-side tracking (Meta Conversions API - CAPI) or cross-domain tracking with event_id deduplication.
  - Configuring analytics trigger rules in client-side routers (Vue Router, React Router, SvelteKit, etc.).
license: Apache-2.0
metadata:
  version: v2.0
  author: clubedepontos
---

# Marketing Attribution & Analytics Playbook

Standardized patterns for analytics tracking and paid traffic attribution, from initial ad click through relational database persistence.

> **Scope of this skill:** Unlike general architecture skills, this is a **domain** skill. Platforms such as Meta Pixel, GA4, and Google Ads are referenced by name because this skill provides direct integration guidance. The universal, reusable infrastructure patterns reside in Sections 1 (cookies and storage), 4 (hygiene and deduplication), and 3B (data modeling).

---

## 1. First-Touch Attribution & Root Domain Cookies

### A. Parameters to Capture
Under a **first-touch** attribution model, campaign parameters that brought the user to the marketing site must never be lost during subsequent page navigation or the transition from landing page to application subdomain.

Capture: `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`, `fbclid`, `gclid`, `gbraid`, `wbraid`.

### B. Shared Cookie Between Landing Page and App Subdomain

For `domain.com` and `app.domain.com` to share attribution state, cookies must declare a `domain` attribute pointing to the shared root domain.

> ⚠️ **Never derive the root domain naively from hostname.** Taking "the last two host labels" fails in two critical scenarios:
> - **Compound Top-Level Domains:** `.com.br`, `.co.uk`, `.org.br` require three domain labels, not two.
> - **Public Suffix List (PSL):** Preview hosts such as `my-app-abc123.vercel.app`, `*.netlify.app`, `*.pages.dev`, and `*.github.io` are registered on the PSL. Setting `domain=.vercel.app` causes **the browser to silently reject the cookie** — without errors or exceptions, silently breaking attribution across all preview environments.
>
> The correct approach: **Only set `domain` when explicitly matching known production root domains; for any other host, omit the attribute** and allow the cookie to remain host-only. Preview environments and localhost do not require cross-subdomain sharing.

```javascript
const COOKIE_DAYS = 90;

// Single configuration point per project. List verified production root domains.
const PRODUCT_ROOT_DOMAINS = ['domain.com'];

/**
 * Returns the `; domain=...` suffix when the current host matches a recognized
 * production product domain. Otherwise returns an empty string (host-only cookie),
 * which is the correct behavior for localhost, raw IPs, and PSL preview hosts.
 */
export function cookieDomainSuffix() {
  if (typeof window === 'undefined') return '';
  const hostname = window.location.hostname;

  const root = PRODUCT_ROOT_DOMAINS.find(
    (domain) => hostname === domain || hostname.endsWith(`.${domain}`),
  );

  return root ? `; domain=.${root}` : '';
}

export function setAttributionCookie(name, value, days = COOKIE_DAYS) {
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  const secure = window.location.protocol === 'https:' ? '; Secure' : '';

  document.cookie =
    `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/` +
    `${cookieDomainSuffix()}; SameSite=Lax${secure}`;
}

export function getCookie(name) {
  const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const match = document.cookie.match(new RegExp(`(?:^|; )${escaped}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : '';
}
```

### C. Generation of `_fbc` and `_fbp`
* If `fbclid` is present in query parameters and no `_fbc` cookie exists, generate: `fb.1.${Date.now()}.${fbclid}`.
* If no `_fbp` cookie exists, generate a persistent identifier: `fb.1.${Date.now()}.${Math.floor(Math.random() * 2147483647)}`.
* If the landing page passes formed tracking parameters in query strings (e.g., `?pt_fbc=...&pt_fbp=...`), **always prefer the passed value** over regenerating a new ID — regenerating resets user continuity.

### D. Fallback in `sessionStorage`
Always store a parallel copy of the captured attribution context in `sessionStorage` to maintain tracking continuity when cookies are blocked or cleared.

---

## 2. Session Continuity: GA4 Cross-Domain Linker with Fail-Safe

Navigating from the landing page to an `app.` subdomain breaks Google Analytics 4 sessions unless the destination URL includes the GA linker parameter. URL decoration must occur at the moment of click because linker parameters are time-sensitive.

> ⚠️ **Critical UX Rule:** Never await `window.gtag` indefinitely. When users run adblockers (uBlock Origin, Brave Shields) or experience network hiccups, the `gtag` callback may **never fire** — locking the button and freezing the UI. A fail-safe timeout is mandatory: losing analytics session continuity is acceptable; blocking user signups is not.

```javascript
export function decorateWithGaLinker(targetUrl, timeoutMs = 600) {
  const gaId = import.meta.env.VITE_GOOGLE_ANALYTICS_ID;
  if (!gaId || typeof window.gtag !== 'function') {
    return Promise.resolve(targetUrl);
  }

  const linkerPromise = new Promise((resolve) => {
    window.gtag('get', gaId, 'linker_param', (linkerParam) => {
      if (!linkerParam) return resolve(targetUrl);
      try {
        const url = new URL(targetUrl);
        const [key, ...rest] = linkerParam.split('=');
        if (key && rest.length) {
          url.searchParams.set(key, rest.join('='));
        }
        resolve(url.toString());
      } catch {
        resolve(targetUrl);
      }
    });
  });

  const timeoutPromise = new Promise((resolve) => {
    setTimeout(() => resolve(targetUrl), timeoutMs);
  });

  return Promise.race([linkerPromise, timeoutPromise]);
}
```

On primary CTA click (Signup/Login):
1. Fire local click tracking events (`trackRegisterClick`).
2. Await linker decoration with timeout fail-safe: `const finalUrl = await decorateWithGaLinker(url);`
3. Redirect with `window.location.assign(finalUrl)`.

Also declare linked domains in your initial gtag configuration:
```javascript
gtag('config', GA_ID, { linker: { domains: ['domain.com', 'app.domain.com'] } });
```

---

## 3. Backend Persistence (`acquisition_context JSONB`)

Persisting marketing context as immutable relational data decouples CAC and LTV analytics from browser storage expiration, third-party cookie restrictions, and ad platform reporting delays.

### A. Frontend Signup Payload
```javascript
export function buildAcquisitionContextForSignup() {
  const ctx = readStoredCampaign();
  const out = {
    captured_at: new Date().toISOString(),
    referrer: document.referrer || null,
  };

  for (const key of [
    'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
    'fbclid', 'gclid', 'gbraid', 'wbraid',
  ]) {
    if (ctx[key]) out[key] = ctx[key];
  }

  out.landing_page = `${window.location.pathname}${window.location.search}`;
  return out;
}
```

### B. Relational Schema (PostgreSQL Example)
```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS acquisition_context JSONB;
COMMENT ON COLUMN users.acquisition_context IS
  'First-touch marketing attribution captured at signup (UTMs, fbclid, etc.). Immutable after creation.';
```

In databases without native JSON support, store serialized JSON in a text column or maintain a key-value relation — the core principle is that the acquisition context remains **immutable after account creation** and directly queryable alongside billing events.

* **Benefit:** Compute exact CAC, LTV, and cohort payback via pure SQL joining revenue to campaign source without external SaaS dependencies.

---

## 4. Frontend Hygiene and Routing

### A. Exclude Administrative Routes
Internal operators and support staff navigating the app pollute ad platform bidding algorithms — training optimization models on non-converting internal profiles.

```javascript
export function isAdminPath(path) {
  const p = (path || '').split('?')[0];
  return p === '/admin' || p.startsWith('/admin/');
}

export function shouldTrackRoute(path) {
  return trackingEnabled() && !isAdminPath(path);
}
```

### B. Conversion Resilience Across Asynchronous Redirects
In SPAs, immediate navigation to `/dashboard` upon form submission can abort pending network tracking requests. Use the **Pending / Flush** pattern: persist intent in storage prior to navigating, and flush tracking once the new route settles.

```javascript
// 1. On successful submission
sessionStorage.setItem('pt_pending_registration', JSON.stringify({ accountType, params }));

// 2. In router post-navigation hook
router.afterEach((to) => {
  flushPendingRegistrationTracking();
  if (shouldTrackRoute(to.fullPath)) {
    trackPageView(to.fullPath);
  }
});
```
*Equivalent hooks in other routers: `useEffect` listening to `location` in React Router, `afterNavigate` in SvelteKit, `router.events.on('routeChangeComplete')` in Next.js Pages Router.*

### C. Deduplication by Transaction Key
Always deduplicate conversion events by unique **transaction ID**, never with a global boolean flag — global flags prevent tracking recurring purchases, plan upgrades, and renewals.

```javascript
export function trackPurchaseOnce({ value, planId, transactionId }) {
  const dedupKey = `pt_purchase_fired_${transactionId || 'default'}`;
  if (sessionStorage.getItem(dedupKey) === '1') return;
  sessionStorage.setItem(dedupKey, '1');

  if (typeof window.fbq === 'function') {
    window.fbq(
      'track',
      'Purchase',
      { value, currency: 'USD', content_name: planId },
      { eventID: transactionId }, // Deduplication key shared with Meta CAPI
    );
  }

  if (typeof window.gtag === 'function') {
    window.gtag('event', 'purchase', {
      transaction_id: transactionId,
      value,
      currency: 'USD',
      items: [{ item_name: planId }],
    });
  }
}
```

### D. Automated Testing of Tracking Instrumentation

Analytics code is vulnerable to being left untested: it renders no UI, returns no visible feedback, and developers assume "we can verify in the dashboard later."

**When other system components break, errors surface** — console warnings, 500 status codes, broken layouts. When analytics breaks, **nothing visible happens**. The checkout completes, revenue arrives, but conversion events fail silently (or double-fire). Flawed data leads to misallocated ad budgets weeks before discovery.

Cover tracking pipelines with unit tests, mocking `window.fbq` and `window.gtag`:

1. **Deduplication Verification:** Invoking `trackPurchaseOnce` multiple times with the same `transactionId` fires exactly **once**.
2. **Per-Transaction Isolation:** Invoking with distinct `transactionId` values fires **again** — preventing regressions back to global boolean flags.
3. **Route Hygiene:** `shouldTrackRoute('/admin/stores')` evaluates to `false` and `shouldTrackRoute('/dashboard')` evaluates to `true`.
4. **Cross-Platform Key Parity:** The `eventID` passed to Meta Pixel is identical to `transaction_id` passed to GA4 — divergence breaks server-side CAPI deduplication without client-side errors.
5. **Graceful Degradation:** When `window.fbq` or `window.gtag` are undefined (adblockers), tracking methods resolve cleanly without throwing unhandled exceptions.
6. **Linker Fail-Safe:** `decorateWithGaLinker` resolves within the timeout deadline even when the GA callback fails to execute.

---

## 5. Standardized Funnel Events

| Funnel Step | Meta Pixel (`fbq`) | GA4 (`gtag`) | Google Ads |
| :--- | :--- | :--- | :--- |
| **Landing Page Visit** | `trackCustom('LpPageView')` | `event('lp_page_view')` | - |
| **Signup CTA Click** | `trackCustom('StartTrialClick')` | `event('register_click')` | - |
| **Registration Page View** | `trackCustom('RegisterPageView')` | `event('register_page_view')` | - |
| **Registration Completed** | `track('CompleteRegistration')` | `event('sign_up')` | `send_to: AW-xxx/signup` |
| **Onboarding Completed** | `trackCustom('OnboardingComplete')` | `event('onboarding_complete')` | `send_to: AW-xxx/onboard` |
| **Checkout Started** | `track('InitiateCheckout')` | `event('begin_checkout')` | `send_to: AW-xxx/checkout` |
| **Purchase / Subscription** | `track('Purchase', payload, { eventID })` | `event('purchase')` | `send_to: AW-xxx/purchase` |

> ⚠️ For `Purchase`, **ALWAYS** use the identical identifier (`transaction_id` / `eventID`) across client tags and server-side CAPI.

---

## 6. Server-Side Tracking: Meta Conversions API (CAPI)

Client-side adblockers and browser privacy protections (e.g., Safari ITP) drop between 25% and 45% of client conversion events. Server-side tracking guarantees reliable conversion delivery for revenue-critical events.

* **Trigger Point:** Execute inside the payment gateway webhook handler (Stripe, PagSeguro, Lemon Squeezy), not in the client checkout redirect — webhooks are the sole source of truth for payment settlement.
* **Automatic Deduplication:** Meta automatically deduplicates Pixel and CAPI events sharing the same `event_name` and `event_id` within a 48-hour window.

**Graph API Payload Structure:**
* `event_name`: `"Purchase"`
* `event_time`: Current Unix epoch timestamp
* `event_id`: Unique order UUID — **must** match the `transactionId` / `eventID` emitted by the client
* `action_source`: `"website"`
* `user_data`:
  * `em`: SHA256 hash of normalized email (lowercase, trimmed)
  * `ph`: SHA256 hash of normalized phone (digits only with country code — e.g., `15551234567`)
  * `fbc` / `fbp`: Cookie identifiers extracted from database or request headers
  * `client_ip_address`, `client_user_agent`
* `custom_data`: `currency`, `value`, `order_id`

> 🔒 **Privacy & Data Protection (LGPD / GDPR):**
> - **Hash PII Before Transmission:** Email and phone numbers must only leave your server as normalized SHA256 hashes. Never transmit raw plaintext PII to third-party ad networks.
> - **Never Log Assembled Payloads:** Avoid debugging with `log.Printf("%+v", payload)` in production. This leaks pseudonymized personal data into log aggregators where it persists for months. Log only `event_id` and response status codes.
> - **Respect User Consent:** Transmitting user data for advertising purposes requires legal basis and must respect user consent choices made in consent banners. Server-side dispatch must not bypass client opt-outs.
> - **Keep Access Tokens Secret:** Store Graph API tokens in secure server environment variables; never commit to repositories or expose to client bundles.
> - **Data Minimization:** Transmit only fields required for conversion matching (`em`, `ph`, `fbc`, `fbp`, IP, user-agent). Do not send extraneous user data.
