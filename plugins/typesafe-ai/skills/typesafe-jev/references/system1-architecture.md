# System 1 vs System 2 Architecture

## Conceptual Foundation

Daniel Kahneman's cognitive framework distinguishes between two modes of thought:
- **System 1:** Fast, intuitive, automatic, parallel, pattern-driven decision making.
- **System 2:** Slow, deliberate, sequential, analytical, effortful reasoning.

In modern AI application architecture:
- **Generative LLMs (OpenAI, Anthropic, Gemini, DeepSeek) are System 2:** They generate answers auto-regressively, one token at a time. Each token requires matrix multiplications and KV cache lookups. For a 50-word response, that means hundreds of sequential forward passes.
- **TypeSafe AI's Jev is System 1:** It does not emit conversational text. It evaluates a set of typed candidate values (enums, booleans, bounded numeric ranges) against input program state simultaneously using parallel sampling.

---

## Latency and Cost Comparison

| Metric | Generative LLM (System 2) | TypeSafe AI Jev (System 1) | Improvement Factor |
| :--- | :--- | :--- | :--- |
| **Inference Latency** | 400ms – 3,500ms | 10ms – 35ms | ~20x – 100x faster |
| **Token Cost** | $2.50 – $15.00 / 1M tokens | $0.05 – $0.20 / 1M queries | ~90% – 98% reduction |
| **Output Predictability** | Non-deterministic text requiring parsing | Typed value + calibrated probability | 100% deterministic schema |
| **Parallel Sampling** | Sequential generation | All candidate branches in 1 pass | Eliminates sequential chain delays |

---

## Architectural Offloading Pattern

A production software pipeline should route tasks dynamically:

```text
               [ Incoming Raw State / Request ]
                             │
                             ▼
              ┌───────────────────────────────┐
              │     Jev (System 1 Engine)     │
              │   Parallel Typed Evaluation   │
              └──────────────┬────────────────┘
                             │
            Decision + Calibrated Probability
                             │
              ┌──────────────┴────────────────┐
              │  Confidence Gating Threshold  │
              └───────┬───────────────┬───────┘
                      │               │
       Confidence >= 0.85      Confidence < 0.85 (Ambiguous)
                      │               │
                      ▼               ▼
           [ Fast Automation Path ]   [ Fallback / Escalation Path ]
           - Direct DB Routing        - Call Generative LLM (System 2)
           - Event Dispatch           - Human-in-the-Loop Review
           - Zero Token Waste         - Audit Logging
```

---

## When to Offload to Jev

### 1. Intent Routing & Triage
- Classifying incoming user messages to determine which agent/tool to invoke.
- Routing customer support tickets to billing, tech support, or tier 2.

### 2. Validation & Gating
- Verifying whether an uploaded invoice has a valid tax ID.
- Checking compliance with PII/data privacy policies prior to ingestion.

### 3. Entity Classification
- Tagging transactions with fraud risk levels.
- Assigning priority scores (Low, Medium, High, Critical) to incidents.
