# Database Attribution & Relational Modeling

Technical guide for modeling first-touch marketing attribution in PostgreSQL databases via immutable `acquisition_context JSONB` columns, schema DDL, GIN indexing, and direct SQL CAC/LTV reporting queries.

---

## 1. Mandatory Principles

1. **Relational Immutability:** Marketing attribution captured at user registration must be stored immutably alongside the primary user record. It must never be overwritten on subsequent logins or profile updates.
2. **Decoupled from Ad Networks:** Storing first-touch attribution directly in PostgreSQL decouples CAC, LTV, and cohort payback analysis from third-party dashboard reporting delays, cookie expiration, and ad network attribution window changes.
3. **Structured Payload Schema:** Store UTM parameters, click IDs (`fbclid`, `gclid`, `gbraid`, `wbraid`), referrer, and landing page URL in a normalized JSONB structure.

---

## 2. PostgreSQL DDL & Indexing

```sql
-- 1. Add acquisition_context column to primary users table
ALTER TABLE users 
  ADD COLUMN IF NOT EXISTS acquisition_context JSONB;

COMMENT ON COLUMN users.acquisition_context IS
  'First-touch marketing attribution captured at signup (UTMs, fbclid, gclid, referrer). Immutable after user creation.';

-- 2. GIN index for rapid campaign filtering and aggregation
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_acquisition_context_gin
  ON users USING GIN (acquisition_context);

-- 3. Expression indexes for high-frequency source/campaign aggregation
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_acquisition_source
  ON users ((acquisition_context->>'utm_source'))
  WHERE acquisition_context IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_acquisition_campaign
  ON users ((acquisition_context->>'utm_campaign'))
  WHERE acquisition_context IS NOT NULL;
```

---

## 3. Frontend Signup Payload Construction (TypeScript)

```typescript
export interface StoredAttributionContext {
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  utm_content?: string;
  utm_term?: string;
  fbclid?: string;
  gclid?: string;
  gbraid?: string;
  wbraid?: string;
}

export function buildAcquisitionContextForSignup(stored: StoredAttributionContext) {
  const out: Record<string, any> = {
    captured_at: new Date().toISOString(),
    referrer: typeof document !== 'undefined' ? document.referrer || null : null,
    landing_page: typeof window !== 'undefined' ? `${window.location.pathname}${window.location.search}` : null,
  };

  const allowedKeys: (keyof StoredAttributionContext)[] = [
    'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
    'fbclid', 'gclid', 'gbraid', 'wbraid',
  ];

  for (const key of allowedKeys) {
    if (stored[key]) {
      out[key] = stored[key];
    }
  }

  return out;
}
```

---

## 4. Production SQL Analytics Queries

### A. Customer Acquisition Count by Campaign Source
```sql
SELECT
  COALESCE(acquisition_context->>'utm_source', 'direct / organic') AS source,
  COALESCE(acquisition_context->>'utm_campaign', 'none') AS campaign,
  COUNT(*) AS total_signups,
  COUNT(CASE WHEN u.subscription_status = 'active' THEN 1 END) AS paying_customers
FROM users u
WHERE u.created_at >= NOW() - INTERVAL '30 days'
GROUP BY 1, 2
ORDER BY paying_customers DESC, total_signups DESC;
```

### B. Cohort Revenue & LTV by Paid Channel
```sql
SELECT
  COALESCE(u.acquisition_context->>'utm_source', 'organic') AS channel,
  COUNT(DISTINCT u.id) AS total_users,
  SUM(p.amount_cents) / 100.0 AS total_revenue_usd,
  ROUND((SUM(p.amount_cents) / 100.0) / COUNT(DISTINCT u.id), 2) AS arpu_usd
FROM users u
JOIN payments p ON p.user_id = u.id AND p.status = 'succeeded'
WHERE u.created_at >= '2026-01-01'
GROUP BY 1
ORDER BY total_revenue_usd DESC;
```

---

## 5. Cross-References

- [First-Touch Cookies](first-touch-cookies.md) — Cookie capturing logic.
- [Server-Side CAPI](server-side-capi.md) — Replaying stored marketing context to ad networks.
- [Back to Marketing Attribution Skill](../SKILL.md)
