# Rust Backend Integration Guide

## Overview

In Rust microservices and high-throughput background workers, Jev delivers zero-compromise type safety and sub-millisecond serialization when paired with `serde` and `tokio`.

---

## Example 1: Serde Enums & Typed Deserialization

```rust
use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::time::Duration;
use thiserror::Error;

#[derive(Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum RiskTier {
    Low,
    Medium,
    High,
    Blocked,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TransactionRisk {
    pub tier: RiskTier,
    pub requires_mfa: bool,
    pub reason_code: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct JevResponse<T> {
    pub data: T,
    pub confidence: f64,
    pub latency_ms: u64,
}

#[derive(Error, Debug)]
pub enum JevError {
    #[error("network or http error: {0}")]
    Http(#[from] reqwest::Error),
    #[error("api returned status: {0}")]
    ApiStatus(u16),
}

pub struct JevClient {
    client: Client,
    api_key: String,
    base_url: String,
}

impl JevClient {
    pub fn new(api_key: impl Into<String>) -> Self {
        let client = Client::builder()
            .timeout(Duration::from_millis(300))
            .pool_idle_timeout(Duration::from_secs(90))
            .build()
            .expect("valid client config");

        Self {
            client,
            api_key: api_key.into(),
            base_url: "https://api.typesafe.ai/v1".to_string(),
        }
    }

    pub async fn evaluate_risk(&self, transaction_payload: &str) -> Result<TransactionRisk, JevError> {
        let resp = self
            .client
            .post(format!("{}/decide", self.base_url))
            .bearer_auth(&self.api_key)
            .json(&serde_json::json!({
                "input": transaction_payload,
                "schema_name": "TransactionRisk"
            }))
            .send()
            .await?;

        if !resp.status().is_success() {
            return Err(JevError::ApiStatus(resp.status().as_u16()));
        }

        let body: JevResponse<TransactionRisk> = resp.json().await?;

        // Calibrated confidence gating
        if body.confidence < 0.90 {
            // Safety threshold for financial transactions: require MFA on ambiguity
            return Ok(TransactionRisk {
                tier: RiskTier::High,
                requires_mfa: true,
                reason_code: Some("CONFIDENCE_THRESHOLD_UNMET".to_string()),
            });
        }

        Ok(body.data)
    }
}
```

---

## Best Practices in Rust

1. **Use `SCREAMING_SNAKE_CASE` or `snake_case` Serde renaming:** Enforce exact string matching on JSON serialization to guarantee clean alignment with Jev schemas.
2. **Connection Pooling:** Reuse the `reqwest::Client` across requests to avoid TLS re-handshakes.
3. **Algebraic Pattern Matching:** Use Rust's exhaustive `match` statements over the resulting enums to ensure all branches of the decision are handled at compile time.
