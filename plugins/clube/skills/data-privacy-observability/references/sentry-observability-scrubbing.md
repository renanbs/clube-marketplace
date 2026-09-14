# Sentry, Tracing & Observability Data Scrubbing

Technical guide for sanitizing error tracking platforms (Sentry, Rollbar), distributed tracing spans (OpenTelemetry), APM telemetry, URL query parameters, and session replay masking.

---

## 1. Mandatory Principles

1. **Scrub Before Ingestion:** Instrument client and server SDKs with `beforeSend` scrubbing hooks that strip sensitive headers (Authorization, Cookie), redact PII keys from stack frame local variables, and sanitize HTTP request bodies.
2. **Disable Raw Request Body Capture:** Never capture full HTTP request bodies by default in error tracking platforms. Opt into capturing structured metadata or sanitized parameters explicitly.
3. **Trace Parameterization:** In OpenTelemetry spans, never interpolate raw user IDs, emails, or SQL parameters into `db.statement` or span attribute strings. Use parameterized queries.
4. **Zero PII in URLs & Metric Labels:** Query strings appear in CDN edge logs, proxy logs, and browser history. Never pass tokens, CPF, or email addresses in query parameters. Never use personal data in Prometheus labels.
5. **Session Replay DOM Masking:** In session replay tools (Hotjar, FullStory, Clarity), explicitly annotate password fields, credit card inputs, and identity documents with masking classes (`data-private`, `fs-mask`).

---

## 2. Sentry Configuration with `beforeSend` Scrubbing

### JavaScript / TypeScript (Frontend / Node.js)
```typescript
import * as Sentry from '@sentry/browser';

const SENSITIVE_KEYS = new Set([
  'password', 'token', 'access_token', 'authorization', 'secret',
  'cpf', 'cnpj', 'ssn', 'credit_card', 'card_number', 'cvv', 'cvc',
  'email', 'phone', 'telephone', 'cellphone'
]);

function scrubObject(obj: any): any {
  if (!obj || typeof obj !== 'object') return obj;
  if (Array.isArray(obj)) return obj.map(scrubObject);

  const clean: Record<string, any> = {};
  for (const [key, value] of Object.entries(obj)) {
    if (SENSITIVE_KEYS.has(key.toLowerCase())) {
      clean[key] = '[REDACTED]';
    } else if (typeof value === 'object') {
      clean[key] = scrubObject(value);
    } else {
      clean[key] = value;
    }
  }
  return clean;
}

Sentry.init({
  dsn: (import.meta as any).env?.VITE_SENTRY_DSN,
  sendDefaultPii: false, // Strictly disable automatic PII collection
  beforeSend(event) {
    // 1. Scrub request headers
    if (event.request?.headers) {
      delete event.request.headers['Authorization'];
      delete event.request.headers['Cookie'];
      delete event.request.headers['X-Auth-Token'];
    }

    // 2. Scrub request data / body
    if (event.request?.data) {
      event.request.data = scrubObject(event.request.data);
    }

    // 3. Scrub extra context
    if (event.extra) {
      event.extra = scrubObject(event.extra);
    }

    return event;
  }
});
```

### Go (Sentry SDK)
```go
package observability

import (
	"strings"

	"github.com/getsentry/sentry-go"
)

var sensitiveKeys = map[string]bool{
	"password": true, "authorization": true, "cookie": true,
	"token": true, "cpf": true, "email": true, "phone": true,
}

func InitSentry(dsn string, env string) error {
	return sentry.Init(sentry.ClientOptions{
		Dsn:              dsn,
		Environment:      env,
		AttachStacktrace: true,
		BeforeSend: func(event *sentry.Event, hint *sentry.EventHint) *sentry.Event {
			if event.Request != nil {
				// Strip auth headers
				cleanedHeaders := make(map[string]string)
				for k, v := range event.Request.Headers {
					if sensitiveKeys[strings.ToLower(k)] {
						cleanedHeaders[k] = "[REDACTED]"
					} else {
						cleanedHeaders[k] = v
					}
				}
				event.Request.Headers = cleanedHeaders
				// Remove raw request body
				event.Request.Data = "[REDACTED]"
			}
			return event
		},
	})
}
```

---

## 3. Session Replay DOM Privacy Masking (HTML)

```html
<!-- Explicitly mask private inputs in session recording tools -->
<form>
  <label for="cpf">Tax ID (CPF)</label>
  <input type="text" id="cpf" name="cpf" class="data-private fs-mask" data-clarity-mask="true" />

  <label for="card">Credit Card</label>
  <input type="text" id="card" name="card" class="data-private fs-mask" data-clarity-mask="true" />
</form>
```

---

## 4. Edge Cases & Overlooked Surfaces

- ⚠️ **Webhook Payloads:** Payment gateway webhook bodies contain customer credit card metadata, billing addresses, and emails. Never log raw webhook request bodies during checkout debugging.
- ⚠️ **Database Driver Constraint Messages:** Duplicate key constraint errors echo input values verbatim (e.g. `Key (email)=(john@domain.com) already exists`). Strip driver messages or capture only the constraint name.

---

## 5. Cross-References

- [PII Masking & Shape](pii-masking-shape.md) — Logging format rules.
- [Compliance & Retention](compliance-retention.md) — Retention policies and access audit trails.
- [Back to Data Privacy Skill](../SKILL.md)
