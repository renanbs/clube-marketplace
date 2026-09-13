# Compliance, Audit Trails & Data Retention

Technical guide for LGPD/GDPR compliance, access audit logging, read-only user impersonation middleware, log lifecycle TTLs, data minimization, and right-to-erasure workflows.

---

## 1. Mandatory Principles

1. **Audit Privileged Access:** Every administrative customer lookup, data export, or user impersonation MUST emit an audit log recording: who accessed, target customer ID, timestamp, HTTP method, and route.
2. **Read-Only Impersonation Enforcement:** Customer support staff impersonating a user must be restricted to strictly read-only (`GET`/`HEAD`) permissions at the middleware layer to prevent fraudulent mutation on behalf of customers.
3. **Log Stream Segregation & Retention TTLs:** Segregate operational debug logs (7–30 day retention) from security audit logs (1–5 year statutory retention). Audit logs must be append-only and immutable.
4. **Data Subject Rights & Erasure (GDPR Art. 17 / LGPD):** When application logs reference only pseudonymous entity IDs (`user_id`, `order_id`), deleting the database record satisfies the Right to Erasure without needing to re-index months of compressed log files.

---

## 2. Read-Only Impersonation Middleware (Go / Gin Example)

```go
package middleware

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

type AuditLogger interface {
	Info(msg string, fields ...zap.Field)
}

func ImpersonationAuditMiddleware(logger AuditLogger) gin.HandlerFunc {
	return func(c *gin.Context) {
		impersonatorID, exists := c.Get("impersonator_id")
		if !exists {
			c.Next()
			return
		}

		// 1. Audit every impersonated request (including reads)
		logger.Info("impersonated_access",
			zap.String("impersonator_id", impersonatorID.(string)),
			zap.String("target_user_id", c.GetString("user_id")),
			zap.String("method", c.Request.Method),
			zap.String("path", c.Request.URL.Path),
			zap.String("ip", c.ClientIP()),
		)

		// 2. Strict read-only enforcement
		if c.Request.Method != http.MethodGet && c.Request.Method != http.MethodHead {
			c.AbortWithStatusJSON(http.StatusForbidden, gin.H{
				"error":      "impersonation sessions are strictly read-only",
				"error_code": "impersonation_mutation_forbidden",
			})
			return
		}

		c.Next()
	}
}
```

---

## 3. Log Stream Segregation & Retention Policies

| Log Stream | Intended Audience | Retention TTL | Storage Policy |
| :--- | :--- | :--- | :--- |
| **Operational Debug** | Developers, On-call | 7–14 days | Standard log aggregator (Datadog, Grafana Loki, CloudWatch) |
| **HTTP Access Logs** | DevOps, SRE | 30 days | Edge CDN / Load Balancer S3 bucket with lifecycle transition to Glacier |
| **Security Audit Logs** | Security, Compliance | 1–5 years | Dedicated append-only bucket with object lock (WORM) |
| **Financial / Billing** | Finance, Audit | 5–10 years | Encrypted cold storage (PostgreSQL audited audit table) |

---

## 4. Edge Cases & Common Traps

- ⚠️ **Development DB Dumps:** Never restore raw production database dumps to local developer laptops or staging environments. Extract sanitized/anonymized database fixtures using automated data scrubbing scripts.
- ⚠️ **Data Minimization:** Never collect fields the product does not actively use. Unused PII fields needlessly expand the blast radius of data breaches.

---

## 5. Cross-References

- [PII Masking & Shape](pii-masking-shape.md) — Masking rules for operational logs.
- [Sentry & Observability Scrubbing](sentry-observability-scrubbing.md) — Sanitizing error payloads.
- [Back to Data Privacy Skill](../SKILL.md)
