---
name: data-privacy-observability
description: |
  Specialist in personal data handling across logs, telemetry, error tracking, and analytics.
  Stack- and language-agnostic: declarations of core principles accompanied by concrete implementation examples.
  Activate this skill whenever writing logs, configuring Sentry/tracing, handling PII, or auditing retention.
license: Apache-2.0
metadata:
  version: v0.2.0
  author: clubedepontos
---

# Data Privacy in Logging & Observability Playbook

How to instrument systems for maximum operational debuggability without turning log aggregators into unmanaged personal data repositories lacking retention limits, access controls, or governance.

---

## 1. Core Principles

1. **Log the Shape, Not the Data:** Expose the minimum information necessary to debug (digit counts, area codes, email domains, validation status) and reference database entity IDs (`user_id`, `order_id`) rather than logging raw PII.
2. **Zero Blind Struct Logging:** Enumerate logged fields explicitly. Never serialize entire request structs, responses, or models into logs (`%+v`, `zap.Any`, `console.log(obj)`).
3. **Scrub Before Ingestion:** Sanitize error tracking payloads (Sentry `beforeSend` hooks), strip authorization headers, parameterize tracing statements, and mask sensitive session replay DOM elements.
4. **Audit Privileged Access:** Enforce strictly read-only user impersonation with comprehensive access auditing, and configure automated TTL lifecycle policies per log stream.

---

## 2. Activation Triggers

| Trigger Area | Description & Indicators | Target Reference |
| :--- | :--- | :--- |
| **PII Masking & Shape** | Masking helpers (phone, email, CPF/SSN, card), salted hashing, zero blind struct logging, custom type marshallers. | [PII Masking & Shape](references/pii-masking-shape.md) |
| **Sentry & Tracing** | Sentry `beforeSend` scrubbing, OpenTelemetry span parameterization, URL query strings, session replay. | [Sentry & Tracing Scrubbing](references/sentry-observability-scrubbing.md) |
| **Audit & Compliance** | Read-only impersonation middleware, audit logs, log stream TTL retention, GDPR Article 17 / LGPD erasure. | [Compliance & Retention](references/compliance-retention.md) |

---

## 3. Modular References Index

Detailed guides, DDLs, schemas, and framework configurations reside in the `references/` directory:

- 📄 **[PII Masking & "Log the Shape" Paradigm](references/pii-masking-shape.md)** — Data masking standards by type, Go custom type marshallers, and salted correlation hashing.
- 📄 **[Sentry, Tracing & Observability Data Scrubbing](references/sentry-observability-scrubbing.md)** — Sentry `beforeSend` sanitization, OpenTelemetry attribute masking, and DOM replay masking.
- 📄 **[Compliance, Audit Trails & Data Retention](references/compliance-retention.md)** — Read-only user impersonation middleware, log stream segregation, and retention policies.
