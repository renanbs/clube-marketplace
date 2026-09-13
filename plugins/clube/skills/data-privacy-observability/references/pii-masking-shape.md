# PII Masking & "Log the Shape" Paradigm

Technical guide for masking personal data in logging streams, structured logging discipline, salted stable hashing for distributed correlation, zero blind struct logging, and custom type marshallers.

---

## 1. Mandatory Principles

1. **Log the Shape, Not the Data:** For operational debugging, logs rarely require raw PII. Instead, log the *shape* and properties: did the field arrive? What is its digit count? What is the telephone area code? What is the email domain?
2. **Zero Blind Struct Logging:** Never serialize entire request structs, database entities, or payload objects (`log.Printf("%+v", req)`, `zap.Any("u", user)`, `console.log(obj)`). Struct fields expand over time; historic log calls will silently dump newly added PII fields.
3. **Dedicated, Unit-Tested Masking Helpers:** Masking helpers are security controls. Off-by-one errors in masking code will leak PII to log aggregators. Back every helper with unit tests covering empty strings, invalid inputs, international formatting, and edge cases.
4. **Salted Stable Hashing for Correlation:** When debugging needs to answer "Did the same user initiate both requests?", compute a SHA-256 hash using a high-entropy secret application salt (`appSalt`).
5. **Custom Type Marshallers:** Implement custom `String()` and `MarshalJSON()` methods on domain types (`type Phone string`, `type CPF string`) so that unintended dumps output masked representations by default.

---

## 2. Masking Standards by Data Type

| Data Type | Log This Format | Never Log |
| :--- | :--- | :--- |
| **Phone Number** | Area code + `*****` + last 4 digits (`11*****4321`) | Full phone number |
| **Email Address** | First char + `***@` + domain (`r***@domain.com`) or salted hash | Full email address |
| **National Tax ID / CPF / SSN** | Last 3 or 4 digits, or validation status (`valid/invalid`) | Full tax ID |
| **Credit / Debit Card** | Brand + last 4 digits (`Visa ... 4242`) | Full PAN, CVV, or expiration date |
| **Postal Address** | City / State, or truncated postal code | Full street address, apartment/unit |
| **Full Name** | First initial + last initial (`J. D.`), or omit | Full legal name |
| **Tokens / API Keys** | Token length + first 4 prefix characters | Secret token value |
| **Internal UUID** | Full UUID (pseudonymous identifier, safe to log) | — |

---

## 3. Masking Helpers & Custom Types (Go Example)

```go
package phonelog

import (
	"encoding/json"
	"regexp"
	"strings"
)

var nonDigitsRegex = regexp.MustCompile(`\D`)

// Mask returns area code + masked middle + last 4 digits (e.g., "11*****4321").
func Mask(phone string) string {
	digits := nonDigitsRegex.ReplaceAllString(phone, "")
	if len(digits) < 4 {
		return "****"
	}
	if len(digits) <= 7 {
		return "****" + digits[len(digits)-4:]
	}
	areaCode := digits[:2]
	last4 := digits[len(digits)-4:]
	return areaCode + strings.Repeat("*", len(digits)-6) + last4
}

// DigitCount returns normalized digit length to debug truncation issues.
func DigitCount(phone string) int {
	return len(nonDigitsRegex.ReplaceAllString(phone, ""))
}

// Phone domain type with automatic masking marshallers
type Phone string

func (p Phone) String() string {
	return Mask(string(p))
}

func (p Phone) MarshalJSON() ([]byte, error) {
	return json.Marshal(Mask(string(p)))
}
```

---

## 4. Salted Stable Hashing for User Correlation

```go
package correlation

import (
	"crypto/sha256"
	"encoding/hex"
	"os"
	"strings"
)

var appSalt = os.Getenv("LOG_CORRELATION_SALT") // High-entropy secret from environment

// StableHash produces a 12-char pseudonymous correlation identifier.
func StableHash(value string) string {
	if value == "" || appSalt == "" {
		return "anonymous"
	}
	normalized := strings.ToLower(strings.TrimSpace(value))
	sum := sha256.Sum256([]byte(appSalt + ":" + normalized))
	return hex.EncodeToString(sum[:])[:12]
}
```

---

## 5. Edge Cases & Common Traps

- ⚠️ **Database Constraint Errors:** Database constraint violations often echo raw input in the error message (e.g., `duplicate key value violates unique constraint "users_email_key" Key (email)=(user@example.com)`). Always log the structured SQLState error code and constraint name, not the raw driver error message.
- ⚠️ **Unsalted Hashes:** Low-entropy data (phone numbers, tax IDs) can be easily reversed via rainbow tables in seconds if hashed without a high-entropy secret salt.

---

## 6. Cross-References

- [Sentry & APM Observability Scrubbing](sentry-observability-scrubbing.md) — Scrubbing Sentry error frames, OpenTelemetry, and APM headers.
- [Compliance & Retention](compliance-retention.md) — Audit trails and retention windows.
- [Back to Data Privacy Skill](../SKILL.md)
