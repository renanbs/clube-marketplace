---
name: data-privacy-observability
description: |
  Specialist in personal data handling across logs, telemetry, error tracking, and analytics.
  Stack- and language-agnostic: declarations of core principles accompanied by concrete implementation examples.
  Activate this skill whenever:
  - Writing or reviewing logging, structured logging, tracing, or metrics touching user data.
  - Instrumenting error tracking with Sentry, Rollbar, Datadog, Grafana, or similar platforms.
  - Handling phone numbers, email addresses, tax IDs (SSN, CPF/CNPJ), addresses, payment cards, or any PII in backend or frontend code.
  - Debugging issues whose investigation requires inspecting production user data.
  - Building dashboards, analytics events, or data exports aggregating user data.
  - Implementing retention policies, data anonymization, account deletion, or subject access requests (GDPR/LGPD).
license: Apache-2.0
metadata:
  version: v1.0
  author: clubedepontos
---

# Data Privacy in Logging & Observability Playbook

How to instrument systems for maximum debuggability **without** turning log aggregators into parallel, unmanaged personal data repositories lacking retention limits, access controls, or governance.

> **How to read this skill:** Each section first declares the **principle** followed by an **example** in a concrete stack (Go on the backend, JavaScript on the frontend). The principle applies universally across stacks; the example translates directly to the target environment.

---

## 1. The Core Principle: Log the SHAPE of Data, Not the Data Itself

Engineers often assume the choice is between "logging raw customer PII" and "logging nothing at all." This false dichotomy is why teams inadvertently log plaintext PII — believing the alternative is total operational blindness.

**In production debugging, you rarely need the raw value.** What you need is the *shape* and properties of the value: Did the field arrive? Does it match the expected length? Is it formatted with an unexpected mask? Is it from the expected region/country? Does it match across multiple requests? All of these properties are observable without ever materializing raw personal data.

For each sensitive field, implement a dedicated helper exposing **the minimum information necessary to debug** and nothing more:

```go
package phonelog

// Mask displays country/area code + masked middle + last 4 digits (e.g., "11*****4321").
// Sufficient for customer support to verify "is this the number ending in 4321?"
// without the full phone number existing anywhere in log storage.
func Mask(phone string) string { /* ... */ }

// AreaCode returns the telephone area code. Enables detecting regional anomalies
// (e.g., an unexpected spike in signups from a single area code) without identifying users.
func AreaCode(phone string) string { /* ... */ }

// DigitCount returns the total count of digits after normalization.
// Directly answers the real debugging question: "Was the phone number truncated?"
func DigitCount(phone string) int { /* ... */ }
```

Usage in application handlers:
```go
logger.Log.Warn("failed to deliver confirmation",
    zap.String("phone", phonelog.Mask(customer.Phone)),
    zap.Int("phone_digits", phonelog.DigitCount(customer.Phone)),
    zap.String("appointment_id", appt.ID),
)
```

**Unit test all masking helpers.** Masking helpers are security controls disguised as string manipulation: an off-by-one error exposing an extra digit will not crash the build or trigger alarms in basic code review, but silently alters data retention in production. Test empty inputs, short strings, valid/invalid formats, with and without country codes, and international dial codes.

### Recommended Masking Formats by Data Type

| Data Type | Log This | Never Log |
| :--- | :--- | :--- |
| **Phone Number** | Area code + `*****` + last 4 digits | Full phone number |
| **Email Address** | Domain + first letter (`r***@domain.com`) or salted hash | Full email address |
| **National Tax ID / SSN / CPF** | Last 3 or 4 digits, or validation status (`valid/invalid`) | Full document ID, even with middle masking |
| **Payment Card (PCI-DSS)** | Card brand + last 4 digits | Full PAN, CVV, or expiration date under any circumstance |
| **Postal Address** | City / State, or truncated postal code (first 5 digits) | Street address, building number, apartment/unit |
| **Full Name** | First initial + last initial, or omit entirely | Full legal name |
| **Tokens / API Keys / Passwords** | Token length + first 4 prefix characters at most | Full secret value, even during local debugging |
| **Internal UUID / Entity ID** | Full UUID (pseudonymous identifier, not PII) | — |

> **Prefer Entity IDs Over Raw Data:** In almost every debugging scenario, `user_id` and `order_id` allow an authorized engineer to look up the authoritative database record under strict, audited access controls. Logs only require the correlation key, not the raw personal payload.

---

## 2. Salted Stable Hashing for User Correlation

When debugging requires answering "Did the same user initiate both requests?" rather than "Who is this user?", use SHA256 hashing with a secret, application-level salt. This enables `GROUP BY` aggregation and distributed cross-service correlation without writing reversible PII to logs.

```go
func StableHash(value string) string {
    sum := sha256.Sum256([]byte(appSalt + strings.ToLower(strings.TrimSpace(value))))
    return hex.EncodeToString(sum[:])[:12] // 12 characters provide sufficient correlation entropy
}
```

Two critical requirements:
* **Normalize values before hashing** (lowercase, trim whitespace, strip formatting characters). Otherwise identical inputs produce divergent hashes, breaking correlation silently.
* **Low-entropy data is vulnerable to dictionary and brute-force attacks.** National IDs and standard phone numbers have small search spaces easily enumerated in minutes. A high-entropy application salt (stored securely in environment variables, never hardcoded in code) is mandatory to prevent rainbow table reversal.

---

## 3. The Most Common Leak: Blind Struct Serialization

The vast majority of PII leaks in log storage stem from temporary debugging statements left in production code:

```go
log.Printf("payload: %+v", req)        // ❌ Dumps the entire request struct
logger.Info("user", zap.Any("u", user)) // ❌ Dumps all struct fields
console.log('checkout', payload)        // ❌ Dumps sensitive client payload to browser console
```

The underlying issue is structural drift: **struct fields expand over time without historical log statements being updated**. A log statement written when a struct had 3 non-sensitive fields later dumps 20 fields including tax IDs and home addresses after domain model refactoring.

**Mandatory Rules:**
1. **Never serialize entire domain models, request bodies, or response payloads into logs.** Explicitly enumerate logged fields. Apply the same discipline as `zero SELECT *` in persistence layers.
2. **Implement custom string and JSON marshallers on sensitive domain types** so that accidental dumps output masked representations by default:
   ```go
   type Phone string

   func (p Phone) String() string               { return phonelog.Mask(string(p)) }
   func (p Phone) MarshalJSON() ([]byte, error) { return json.Marshal(phonelog.Mask(string(p))) }
   ```
   Equivalents: `__repr__` in Python; `toString()` in Java; branded types with `toJSON()` in TypeScript.
3. **Treat database driver and constraint errors as sensitive.** Database constraint violation messages frequently echo the violating input value verbatim (e.g., `duplicate key value violates unique constraint ... Key (email)=(user@example.com)`). Logging raw errors leaks PII. Log the structured error code and constraint identifier, not the raw driver error message.

---

## 4. Frequently Overlooked Data Surfaces

Application log streams are only one surface. Audit and protect the following channels:

* **Error Tracking Platforms (Sentry / Rollbar):** Automatically capture local stack frame variables and HTTP request bodies. Configure `before_send` scrubbing hooks to redact sensitive keys and disable default request body capturing.
* **Distributed Tracing (OpenTelemetry):** Span attributes are indexed, searchable text. Never interpolate sensitive values directly into `db.statement` attributes; use parameterized query representations.
* **Prometheus Metric Labels:** Never use PII as Prometheus metric labels. In addition to leaking personal data, unbounded label cardinality exhausts metrics backend memory.
* **URLs and Query Strings:** Query parameters appear in CDN edge logs, reverse proxy access logs, HTTP `Referer` headers sent to third-party assets, and browser history. Never pass tokens, email addresses, or tax IDs in query parameters — use request bodies or Authorization headers.
* **Frontend `console.log`:** Output is visible to users, browser extensions, and captured by session replay scripts. Treat the production client console as a public broadcast channel.
* **Session Replay Tools (Hotjar, FullStory, Clarity):** Record DOM state including user input. Explicitly annotate input fields with exclusion attributes (`data-private`, `fs-mask`). Payment cards, passwords, and identity documents must be masked.
* **Webhook Bodies & Payment Gateway Callbacks:** Logging raw payment gateway payloads during checkout integration dumps customer credit card metadata into log aggregators.
* **Development Database Dumps:** Restoring raw production database dumps to local developer workstations or unhardened staging environments exposes personal data to uncontrolled environments. Always generate synthetic data or sanitize production dumps at the extraction point.

---

## 5. Auditing: What You MUST Record

Data privacy does not mean logging less — it means logging the right things. Privileged administrative access to customer data requires **more** comprehensive auditing, not less.

**Every impersonation session, administrative customer lookup, or bulk data export must generate an audit log** recording: who accessed, target user ID, timestamp, HTTP method, and route.

```go
func ImpersonationReadOnly() gin.HandlerFunc {
    return func(c *gin.Context) {
        impersonatorID, exists := c.Get("impersonatorID")
        if !exists {
            c.Next()
            return
        }

        // 1. Every impersonated request is audited — including successful GET reads.
        logger.Log.Info("impersonated request",
            zap.String("impersonator_id", impersonatorID.(string)),
            zap.String("target_user_id", c.GetString("userID")),
            zap.String("method", c.Request.Method),
            zap.String("path", c.Request.URL.Path),
        )

        // 2. Impersonation is strictly read-only: support staff can inspect but never mutate on behalf of customers.
        if c.Request.Method != http.MethodGet {
            c.AbortWithStatusJSON(http.StatusForbidden, gin.H{
                "error":      "read-only impersonation session",
                "error_code": "impersonation_readonly",
            })
            return
        }

        c.Next()
    }
}
```

Both controls are mandatory:
1. **Read-Only Enforcement:** Guarantees that support or administrative actions cannot be falsely attributed to the customer in billing or operational histories.
2. **Comprehensive Request Auditing:** Logging all requests (not merely rejected attempts) provides full traceability when responding to data subject access inquiries ("Who in the company accessed my records?").

Audit logs require distinct operational policies: longer retention, strictly segregated access permissions, and append-only immutability. Never mix audit logs into standard application stdout streams.

---

## 6. Retention Policies & Data Subject Rights

* **Define Retention per Log Category:** Configure automated lifecycle policies in log aggregators: short retention for application debug logs (7–30 days), extended retention for security audit logs according to statutory requirements.
* **Ensure Account Deletion Reaches Logs:** When logs contain only pseudonymous entity IDs (`user_id`, `order_id`) and masked strings, deleting the authoritative database record effectively satisfies Right to Erasure / GDPR Article 17 requests. Plaintext PII scattered across three months of unindexed logs makes compliant deletion impossible.
* **Data Minimization at the Source:** Never collect fields the product does not actively use. Every collected field increases the blast radius of data breaches and subject access compliance overhead.
* **Legal Basis for Third-Party Dispatches:** Forwarding customer data to advertising networks, CRMs, or analytics platforms constitutes personal data processing. It must be disclosed in privacy policies and respect user consent preferences — server-side tracking cannot be used to circumvent client cookie consent rejections.

---

## Verification Checklist

- [ ] Every sensitive field has a dedicated masking helper backed by unit tests?
- [ ] Logs reference entity IDs (`user_id`, `order_id`) instead of raw data wherever IDs suffice for database lookup?
- [ ] No log statement serializes full domain models, request bodies, or responses (`%+v`, `zap.Any`, `console.log(obj)`)?
- [ ] Sensitive domain types implement custom `String()` / `MarshalJSON()` methods with automatic masking?
- [ ] Database constraint errors are logged by structured error code and constraint name rather than raw driver error strings?
- [ ] Error tracking platforms (Sentry/Rollbar) have data scrubbing enabled and raw request body capture disabled?
- [ ] Zero PII exists in Prometheus metric labels, distributed tracing span attributes, URL paths, or query parameters?
- [ ] Session replay tools have sensitive DOM input fields explicitly annotated for masking/exclusion?
- [ ] User impersonation and administrative data access are strictly read-only and generate comprehensive audit logs?
- [ ] Audit logs are isolated from operational logs with append-only permissions and appropriate retention windows?
- [ ] Log aggregation backends enforce explicit TTL retention policies per log stream?
- [ ] Development and staging environments use synthetic data or anonymized extracts, never raw production database dumps?
