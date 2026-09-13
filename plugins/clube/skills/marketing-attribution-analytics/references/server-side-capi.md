# Server-Side Tracking: Meta Conversions API (CAPI)

Technical reference for implementing backend server-side conversion tracking via the Meta Conversions API (CAPI) with SHA-256 PII hashing normalization, webhook trigger architecture, and privacy compliance.

---

## 1. Mandatory Principles

1. **Webhook-Driven Execution:** Execute CAPI dispatches inside verified payment gateway webhook handlers (e.g. Stripe, Lemon Squeezy, PagSeguro), never in client-side redirect handlers. Webhooks represent the authoritative source of payment truth.
2. **Deterministic Deduplication:** The `event_id` sent to Meta CAPI must match the `transaction_id` / `eventID` emitted by client-side Meta Pixel and GA4 tags. Meta deduplicates matching events within a 48-hour window.
3. **Normalize and Hash PII Prior to Dispatch:** All personal customer data (`em` for email, `ph` for phone) MUST be normalized (trimmed, lowercase, non-digit removal) and hashed via SHA-256 before leaving your servers.
4. **Zero Raw Payload Logging:** Never dump full CAPI request bodies into production log streams (`log.Printf("%+v", payload)`). Log only `event_id`, HTTP status, and error codes.
5. **Consent Compliance (LGPD / GDPR):** Server-side tracking cannot be used to bypass client cookie banner consent rejections. Respect stored user consent preferences.

---

## 2. PII Normalization & Hashing Helper (Go Example)

```go
package tracking

import (
	"crypto/sha256"
	"encoding/hex"
	"regexp"
	"strings"
)

var nonDigitsRegex = regexp.MustCompile(`\D`)

// HashEmail normalizes email (lowercase, trim) and computes SHA-256.
func HashEmail(email string) string {
	clean := strings.ToLower(strings.TrimSpace(email))
	if clean == "" {
		return ""
	}
	hash := sha256.Sum256([]byte(clean))
	return hex.EncodeToString(hash[:])
}

// HashPhone normalizes phone to digits-only with country code and computes SHA-256.
func HashPhone(phone string) string {
	digits := nonDigitsRegex.ReplaceAllString(phone, "")
	if digits == "" {
		return ""
	}
	hash := sha256.Sum256([]byte(digits))
	return hex.EncodeToString(hash[:])
}
```

---

## 3. Meta Conversions API Payload Schema

```json
{
  "data": [
    {
      "event_name": "Purchase",
      "event_time": 1773489600,
      "event_id": "ord_9a8b7c6d-1234-5678-9abc-def012345678",
      "event_source_url": "https://www.domain.com/checkout",
      "action_source": "website",
      "user_data": {
        "em": ["f660ab912ec121d1b1e928a0bb4bc61b15f5ad44d5efdc4e1c92a25e99b8e44a"],
        "ph": ["9a8b1c4d5e..."],
        "fbc": "fb.1.1773489600.IwAR123...",
        "fbp": "fb.1.1773489600.2147483647",
        "client_ip_address": "203.0.113.195",
        "client_user_agent": "Mozilla/5.0 ..."
      },
      "custom_data": {
        "currency": "USD",
        "value": 49.00,
        "order_id": "ord_9a8b7c6d"
      }
    }
  ]
}
```

---

## 4. Backend Webhook Dispatcher (Go)

```go
package tracking

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

type CAPIClient struct {
	pixelID     string
	accessToken string
	httpClient  *http.Client
}

func NewCAPIClient(pixelID, token string) *CAPIClient {
	return &CAPIClient{
		pixelID:     pixelID,
		accessToken: token,
		httpClient:  &http.Client{Timeout: 5 * time.Second},
	}
}

func (c *CAPIClient) SendPurchaseEvent(ctx context.Context, orderID string, amount float64, email, phone, fbc, fbp, ip, ua string) error {
	payload := map[string]interface{}{
		"data": []map[string]interface{}{
			{
				"event_name":    "Purchase",
				"event_time":    time.Now().Unix(),
				"event_id":      orderID,
				"action_source": "website",
				"user_data": map[string]interface{}{
					"em":                []string{HashEmail(email)},
					"ph":                []string{HashPhone(phone)},
					"fbc":               fbc,
					"fbp":               fbp,
					"client_ip_address": ip,
					"client_user_agent": ua,
				},
				"custom_data": map[string]interface{}{
					"currency": "USD",
					"value":    amount,
					"order_id": orderID,
				},
			},
		},
	}

	body, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("marshal capi payload: %w", err)
	}

	url := fmt.Sprintf("https://graph.facebook.com/v19.0/%s/events?access_token=%s", c.pixelID, c.accessToken)
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("dispatch capi request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		return fmt.Errorf("capi returned error status: %d", resp.StatusCode)
	}
	return nil
}
```

---

## 5. Cross-References

- [Deduplication & Hygiene](deduplication-hygiene.md) — Event key parity rules.
- [Database Attribution](database-attribution.md) — Storing marketing context for CAPI matching.
- [Back to Marketing Attribution Skill](../SKILL.md)
