# Attribution Deduplication & Frontend Hygiene

Technical guide for deduplicating conversion events across client tags and server APIs, GA4 cross-domain session linkers with fail-safe timeouts, admin route exclusion, pending/flush navigation patterns, and tracking test automation.

---

## 1. Mandatory Principles

1. **Transaction Key Deduplication:** Always deduplicate conversion events by a unique **transaction ID** / **event ID**, never with a global boolean flag (global flags break recurring purchases, plan upgrades, and renewals).
2. **Cross-Platform Key Parity:** The `eventID` passed to Meta Pixel must match the `event_id` dispatched via Meta CAPI and the `transaction_id` sent to GA4.
3. **Fail-Safe GA4 Linker Timeout:** Never await Google Analytics (`gtag`) callbacks indefinitely. Adblockers and network failures will lock primary signup buttons if not guarded with a fail-safe timeout race.
4. **Internal Traffic Exclusion:** Filter out internal operators and admin paths (`/admin/*`) from tracking pipelines to prevent polluting conversion bid algorithms.

---

## 2. GA4 Cross-Domain Linker with Timeout Guard

```typescript
export function decorateWithGaLinker(targetUrl: string, timeoutMs = 600): Promise<string> {
  const gaId = (import.meta as any).env?.VITE_GOOGLE_ANALYTICS_ID;
  if (!gaId || typeof (window as any).gtag !== 'function') {
    return Promise.resolve(targetUrl);
  }

  const linkerPromise = new Promise<string>((resolve) => {
    (window as any).gtag('get', gaId, 'linker_param', (linkerParam: string) => {
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

  const timeoutPromise = new Promise<string>((resolve) => {
    setTimeout(() => resolve(targetUrl), timeoutMs);
  });

  return Promise.race([linkerPromise, timeoutPromise]);
}
```

---

## 3. Conversion Deduplication & Hygiene

```typescript
export interface PurchaseEventParams {
  transactionId: string;
  value: number;
  currency: string;
  planId: string;
}

export function trackPurchaseOnce(params: PurchaseEventParams): void {
  const dedupKey = `tracking_purchase_${params.transactionId}`;
  if (sessionStorage.getItem(dedupKey) === '1') {
    return; // Already tracked this transaction in this browser session
  }
  sessionStorage.setItem(dedupKey, '1');

  // 1. Meta Pixel with eventID for server-side CAPI deduplication
  if (typeof (window as any).fbq === 'function') {
    (window as any).fbq(
      'track',
      'Purchase',
      { value: params.value, currency: params.currency, content_name: params.planId },
      { eventID: params.transactionId }
    );
  }

  // 2. Google Analytics 4
  if (typeof (window as any).gtag === 'function') {
    (window as any).gtag('event', 'purchase', {
      transaction_id: params.transactionId,
      value: params.value,
      currency: params.currency,
      items: [{ item_name: params.planId }]
    });
  }
}
```

---

## 4. Standard Funnel Matrix

| Funnel Step | Meta Pixel (`fbq`) | GA4 (`gtag`) | Google Ads |
| :--- | :--- | :--- | :--- |
| **Landing Page Visit** | `trackCustom('LpPageView')` | `event('lp_page_view')` | — |
| **Signup CTA Click** | `trackCustom('StartTrialClick')` | `event('register_click')` | — |
| **Registration Page View** | `trackCustom('RegisterPageView')` | `event('register_page_view')` | — |
| **Registration Completed** | `track('CompleteRegistration')` | `event('sign_up')` | `send_to: AW-xxx/signup` |
| **Onboarding Completed** | `trackCustom('OnboardingComplete')` | `event('onboarding_complete')` | `send_to: AW-xxx/onboard` |
| **Checkout Started** | `track('InitiateCheckout')` | `event('begin_checkout')` | `send_to: AW-xxx/checkout` |
| **Purchase / Subscription** | `track('Purchase', payload, { eventID })` | `event('purchase')` | `send_to: AW-xxx/purchase` |

---

## 5. Automated Testing Rules for Tracking

1. **Deduplication:** Calling `trackPurchaseOnce` multiple times with identical `transactionId` fires external tags exactly once.
2. **Per-Transaction Isolation:** Calling with distinct `transactionId` values fires tags for each unique transaction.
3. **Route Hygiene:** `isAdminPath('/admin/users')` returns `true`; `shouldTrackRoute('/admin/users')` returns `false`.
4. **Graceful Degradation:** When `fbq` or `gtag` are undefined (adblockers), tracking methods resolve without throwing unhandled exceptions.

---

## 6. Cross-References

- [First-Touch Cookies](first-touch-cookies.md) — Attribution parameters and cookie management.
- [Server-Side CAPI](server-side-capi.md) — Backend Meta Conversions API implementation.
- [Back to Marketing Attribution Skill](../SKILL.md)
