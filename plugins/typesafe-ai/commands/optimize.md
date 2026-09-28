---
name: optimize
description: Audit project codebase for expensive LLM calls (classification, routing, structured JSON) that can be offloaded to TypeSafe AI's Jev System 1 engine to drastically reduce token costs and latency.
---

# /optimize — LLM Token & Latency Optimization Audit

Delegates to the `expert-jev` agent using the `typesafe-jev` skill.

## Usage

- `/typesafe-ai:optimize` — Scans the current repository for generative LLM API calls (OpenAI, Anthropic, LangChain, LiteLLM, Ollama) and analyzes opportunities for offloading to Jev.

## Execution Flow (4-Phase Output Contract)

Execute the audit following the standard 4-phase contract:

### 1. Plan
- Identify repository scope and target directory.
- Prepare deterministic execution of the TypeSafe AI detector:
  `python3 plugins/typesafe-ai/scripts/detect-llm-hotspots.py [--target <dir>]`

### 2. Execution
- Execute `python3 plugins/typesafe-ai/scripts/detect-llm-hotspots.py --target <dir>`.
- Read authoritative runlog from `.typesafe/optimize-last.json` (never parse ANSI terminal stdout).
- For each candidate hotspot, inspect the source file to evaluate:
  - The prompt asking for an enum, boolean, category, or fixed schema without requiring long-form prose.
  - Generative tokens wasted on formatting or markdown codeblocks (` ```json `).
  - Endpoints suffering from multi-second latency where <20ms is desirable.
### 3. Summary
- Present a structured markdown table of optimization candidates:

| File:Line | Current LLM Provider | Task / Intent | Est. Tokens Saved / Call | Est. Latency Drop | Offload Viability |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `src/triage.py:42` | `openai (gpt-4o)` | Ticket Priority Triage | ~650 prompt + 50 output | 1,800ms -> 18ms | High (Jev System 1) |

- Summarize total potential cost and latency reduction.

### 4. Recommended Actions
- Provide copy-pasteable refactoring patches replacing the identified LLM calls with Jev:
  1. Define the strictly typed schema (Pydantic / Zod / Go struct / Serde).
  2. Implement the parallel Jev decision call.
  3. Wire the calibrated confidence gate with safe fallback.
