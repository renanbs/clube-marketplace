---
name: typesafe-jev
description: "Replace expensive LLM text generation with fast, calibrated, typed decisions using TypeSafe AI's Jev model. Offload classification, intent routing, and schema validation to cut token costs and latency across Python, TypeScript, Go, and Rust."
version: 0.1.1
topics:
  - system1-architecture
  - confidence-gating
  - python-pydantic
  - typescript-sdk
  - go-integration
  - rust-integration
---

# TypeSafe Jev — System 1 Decision Engine

This skill guides engineering teams on utilizing **Jev**, developed by **TypeSafe AI**, to replace traditional generative LLMs in deterministic decision-making pipelines.

Traditional LLMs generate text token-by-token, which introduces:
1. **High Latency:** 500ms to 4000ms per classification or routing decision.
2. **Token Inflation:** Hundreds of prompt and output tokens burned just to return an enum or boolean.
3. **Parsing Fragility:** Markdown wrappers, hallucinations, and uncalibrated confidence.

**Jev operates as a System 1 Model:** it evaluates program state and typed questions in a single parallel pass without conversational text generation. Decisions return in sub-20ms with mathematically calibrated probabilities.

---

## Core Pillars

### 1. System 1 vs System 2 Offloading
Never spend generative LLM tokens (System 2) where a structured decision (System 1) suffices:
- **Use Jev for:** Ticket categorization, intent triage, spam filtering, toxicity scoring, workflow routing, feature flag gating, PII detection, priority scoring.
- **Reserve Generative LLMs for:** Conversational prose, long-form synthesis, narrative explanation, creative ideation.

See `references/system1-architecture.md` for architectural patterns and latency/cost comparisons.

### 2. Confidence Gating & Safe Fallback
Every Jev judgment returns a calibrated confidence score (`0.0` to `1.0`). Always gate operational execution:
- **High Confidence ($\ge 0.85$):** Execute immediately (zero human or LLM intervention).
- **Ambiguous ($0.60 \le \text{score} < 0.85$):** Fallback to secondary check, domain-specific rule, or System 2 LLM.
- **Low Confidence ($< 0.60$):** Escalate to human operator / review queue.

### 3. Secure Credential Management (Linux Keyring)
Never commit or hardcode raw API keys. Under Linux, retrieve the API key dynamically from the system keyring:
```bash
# Using secret-tool (preferred):
export TYPESAFE_API_KEY=$(secret-tool lookup service typesafe account default 2>/dev/null || secret-tool lookup service typesafe-ai 2>/dev/null)

# Using pass fallback:
export TYPESAFE_API_KEY=$(pass show typesafe/api-key 2>/dev/null || pass show typesafe-ai/api-key 2>/dev/null)
```
Run `/clube:omp-setup` or `/clube:init` to preflight and store credentials in the keyring.

See `references/confidence-gating.md` for threshold policies and escalation matrices.

---

## Language Implementations

Load the relevant reference file for language-specific idioms, schemas, and client wrappers:

- **Python (Pydantic AI / FastAPI / Litestar):** `references/python-pydantic.md`
  - Integration with Pydantic AI (`TypeSafeModel`), Pydantic v2 schemas, strict enums, and FastAPI dependency injection.
- **TypeScript (Node / Bun / Edge):** `references/typescript-sdk.md`
  - TypeSafe JS/TS client, Zod schema validation, edge runtime compatibility (Cloudflare Workers, Vercel).
- **Go (sqlx / Ports & Adapters):** `references/go-integration.md`
  - Clean Go HTTP/gRPC client, strict struct unmarshaling, context timeouts, zero-allocation serialization.
- **Rust (Tokio / Serde):** `references/rust-integration.md`
  - Zero-overhead async client with `reqwest`/`tokio`, algebraic enum matching, strict deserialization with `serde`.

---

## Anti-Patterns to Avoid

- ❌ Calling `gpt-4o` or `claude-3-5-sonnet` with a 2000-token prompt just to ask: *"Is this ticket high priority? Answer YES or NO"*.
- ❌ Using regex to strip ` ```json ` markers from generative LLM outputs when strict schemas can be evaluated in parallel by Jev.
- ❌ Acting on uncalibrated LLM outputs without a confidence threshold check.
- ❌ Hardcoding confidence thresholds across different domains without calibration tests.
