---
name: marketing-attribution-analytics
description: |
  Specialist in metric instrumentation, tracking, and end-to-end attribution for SaaS products.
  Domain skill: concrete for Meta and Google platforms, while infrastructure components
  (cookies, storage, deduplication, routing) are framework-agnostic.
  Activate this skill whenever configuring conversion tags, first-touch cookies, CAPI, or marketing persistence.
license: Apache-2.0
metadata:
  version: v0.3.0
  author: clubedepontos
---

# Marketing Attribution & Analytics Playbook

Standardized patterns for analytics tracking, paid traffic attribution, deduplication hygiene, and relational persistence from initial ad click through database modeling.

---

## 1. Core Principles

1. **First-Touch Preservation:** Capture first-touch campaign parameters (`utm_*`, `fbclid`, `gclid`, `gbraid`, `wbraid`) on first landing and scope shared cookies explicitly to verified root domains (`domain.com`).
2. **Deterministic Deduplication:** Share identical unique transaction IDs (`eventID` / `event_id` / `transaction_id`) across Meta Pixel, GA4, and backend Conversions API (CAPI).
3. **Relational Marketing Immutability:** Persist marketing attribution payloads in an immutable `acquisition_context JSONB` column upon user registration to decouple CAC/LTV queries from third-party dashboards.
4. **Privacy-First Server-Side Tracking:** Hash all PII (SHA-256 for email/phone) before dispatching to Meta CAPI, respect user consent, and never dump raw tracking bodies into application log streams.

---

## 2. Activation Triggers

| Trigger Area | Description & Indicators | Target Reference |
| :--- | :--- | :--- |
| **Cookies & Attribution** | Capturing UTMs, click IDs, Public Suffix List rules, `_fbc`/`_fbp` generation, `sessionStorage` fallback. | [First-Touch Cookies](references/first-touch-cookies.md) |
| **Deduplication & Hygiene** | Unique transaction ID deduplication, GA4 linker fail-safe timeout, admin route exclusion, funnel matrix. | [Deduplication & Hygiene](references/deduplication-hygiene.md) |
| **Server-Side Tracking** | Meta Conversions API (CAPI), payment webhook triggers, SHA-256 PII hashing, batching. | [Server-Side CAPI](references/server-side-capi.md) |
| **Database Persistence** | `acquisition_context JSONB` schema, PostgreSQL DDL, GIN indexing, pure SQL CAC/LTV queries. | [Database Attribution](references/database-attribution.md) |

---

## 3. Modular References Index

Detailed guides, DDLs, schemas, and framework configurations reside in the `references/` directory:

- 📄 **[First-Touch Attribution & Root Domain Cookies](references/first-touch-cookies.md)** — Scoping cookies across subdomains, handling PSL rules, and generating `_fbc`/`_fbp`.
- 📄 **[Attribution Deduplication & Frontend Hygiene](references/deduplication-hygiene.md)** — Conversion deduplication, GA4 linker with timeout, admin route exclusion, and testing.
- 📄 **[Server-Side Tracking: Meta Conversions API (CAPI)](references/server-side-capi.md)** — Webhook-driven CAPI dispatcher, SHA-256 PII normalization, and payload schemas.
- 📄 **[Database Attribution & Relational Modeling](references/database-attribution.md)** — PostgreSQL `acquisition_context JSONB` DDL, indexing, and SQL cohort analysis queries.
