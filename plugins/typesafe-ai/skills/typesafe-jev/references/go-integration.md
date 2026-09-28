# Go Backend Integration Guide

## Overview

In Go microservices and backends (`expert-backend-go`), Jev is integrated via standard HTTP or gRPC clients with zero dynamic reflection overhead.

Because Go values explicit errors, compile-time types, and strict concurrency controls, Jev decisions map directly into Go structs with `json` unmarshaling and context cancellation.

---

## Example 1: Typed Decision with Context & HTTP Client

```go
package typesafe

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

type Priority string

const (
	PriorityLow      Priority = "LOW"
	PriorityMedium   Priority = "MEDIUM"
	PriorityHigh     Priority = "HIGH"
	PriorityCritical Priority = "CRITICAL"
)

type IncidentDecision struct {
	Priority   Priority `json:"priority"`
	PageOnCall bool     `json:"page_on_call"`
}

type JevResponse[T any] struct {
	Data       T       `json:"data"`
	Confidence float64 `json:"confidence"`
	LatencyMs  int     `json:"latency_ms"`
}

type Client struct {
	httpClient *http.Client
	apiKey     string
	baseURL    string
}

func NewClient(apiKey string) *Client {
	return &Client{
		httpClient: &http.Client{Timeout: 500 * time.Millisecond},
		apiKey:     apiKey,
		baseURL:    "https://api.typesafe.ai/v1",
	}
}

func EvaluateIncident(ctx context.Context, client *Client, logText string) (*IncidentDecision, error) {
	reqBody, err := json.Marshal(map[string]any{
		"input":        logText,
		"schema_name": "IncidentDecision",
	})
	if err != nil {
		return nil, fmt.Errorf("marshal request: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, client.baseURL+"/decide", bytes.NewReader(reqBody))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}
	req.Header.Set("Authorization", "Bearer "+client.apiKey)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("execute request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("jev api error: status %d", resp.StatusCode)
	}

	var res JevResponse[IncidentDecision]
	if err := json.NewDecoder(resp.Body).Decode(&res); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}

	// Calibrated confidence gating in Go
	if res.Confidence < 0.85 {
		// Log and fallback to default safety procedure
		return &IncidentDecision{Priority: PriorityHigh, PageOnCall: true}, nil
	}

	return &res.Data, nil
}
```

---

## Best Practices in Go

1. **Strict Context Timeouts:** Always enforce `context.WithTimeout(ctx, 200*time.Millisecond)`. Jev responds in ~20ms, so 200ms is more than enough headroom.
2. **Re-use HTTP Client Transport:** Maintain a single `*http.Client` with `MaxIdleConnsPerHost` tuned to keep connections warm.
3. **Decouple via Ports:** In Clean Architecture, expose an interface `type DecisionEngine interface { ... }` in your domain layer and place the HTTP client in `internal/infrastructure/typesafe/`.
