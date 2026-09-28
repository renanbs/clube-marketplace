# Design: TypeSafe AI Plugin (`typesafe-ai`) with Jev Integration

- **Status:** Approved for Implementation Planning
- **Date:** 2026-09-27
- **Target Repository:** `clube-marketplace`
- **Plugin Name:** `typesafe-ai`
- **Initial Version:** `v0.1.0`

---

## 1. Context & Motivation

Traditional LLMs (ChatGPT, Claude, etc.) are often misused for operational classification, enum extraction, intent routing, and boolean verification. This leads to:
- Excessive latency (waiting for sequential token generation).
- Unnecessary token costs (spending hundreds of tokens to get a simple `"status": "APPROVED"`).
- Non-deterministic responses requiring retries and brittle prompt engineering.

**Jev**, developed by **TypeSafe AI**, is a specialized "System One" model that evaluates structured, typed questions over raw program state in a single parallel pass without generating conversational prose. It delivers sub-20ms typed decisions with calibrated confidence probabilities.

This plugin packages Jev architectural discipline, SDK integrations, an optimization auditor command, and specialist agent expertise into a standard, multi-harness marketplace plugin.

---

## 2. Architecture & Components

### 2.1 Plugin Structure
```text
plugins/typesafe-ai/
├── .claude-plugin/
│   └── plugin.json
├── .cursor-plugin/
│   └── plugin.json
├── .codex-plugin/
│   └── plugin.json
├── .omp-plugin/
│   └── plugin.json
├── .opencode-plugin/
│   └── plugin.json
├── agents/
│   └── expert-jev.md
├── commands/
│   └── optimize.md
└── skills/
    └── typesafe-jev/
        ├── SKILL.md
        └── references/
            ├── system1-architecture.md
            ├── confidence-gating.md
            ├── python-pydantic.md
            ├── typescript-sdk.md
            ├── go-integration.md
            └── rust-integration.md
```

### 2.2 Skill: `typesafe-jev`
- **Path:** `plugins/typesafe-ai/skills/typesafe-jev/SKILL.md`
- **Trigger:** When designing, optimizing, or implementing decision pipelines, classification, intent routing, or cost-cutting for LLM calls.
- **Content:**
  - System 1 (fast typed judgment) vs System 2 (slow generative reasoning) decomposition.
  - Confidence gating patterns (threshold tuning, human handoff, fallback cascade).
  - Code guides across 4 major languages:
    - **Python:** Pydantic AI (`TypeSafeModel`), Pydantic v2 schemas, FastAPI dependency injection.
    - **TypeScript:** Zod schemas, Node/Bun/Edge runtimes.
    - **Go:** Concrete structs, strict unmarshaling, context timeouts, concurrent parallel queries.
    - **Rust:** `serde` enums, algebraic data types, zero-copy parsing, `reqwest`/`tokio`.

### 2.3 Specialist Agent: `expert-jev`
- **Path:** `plugins/typesafe-ai/agents/expert-jev.md`
- **Role:** AI decision architecture specialist.
- **Capabilities:**
  - Audits code or specs to separate generative tasks from structured decisions.
  - Generates strict typed schemas for Jev queries.
  - Recommends calibrated probability thresholds based on domain criticality.

### 2.4 Command: `/typesafe-ai:optimize`
- **Path:** `plugins/typesafe-ai/commands/optimize.md`
- **Behavior (4-Phase Contract):**
  1. **Plan:** Scans repository for LLM SDK usages (`openai`, `anthropic`, `langchain`, `litellm`, etc.).
  2. **Execution:** Inspects prompts and schemas to detect LLMs used purely for classification, triage, or structured JSON.
  3. **Summary:** Lists optimization candidates with estimated token reduction and latency drop.
  4. **Recommended Actions:** Delivers copy-pasteable Jev integration diffs and confidence-gating implementations.

### 2.5 Marketplace Registration
The plugin will be registered in all 5 root marketplace manifests:
- `.claude-plugin/marketplace.json`
- `.omp-plugin/marketplace.json`
- `.cursor-plugin/marketplace.json`
- `.agents/plugins/marketplace.json`
- `.opencode-plugin/marketplace.json`
- `opencode.json`

---

## 3. Verification & Acceptance Criteria

1. `./bin/clube-config check` passes cleanly, recognizing `typesafe-ai` alongside `clube` and `code-review`.
2. `./bin/clube-config test` passes all tests (including new tests for the plugin).
3. All 5 harnesses recognize the new plugin, skills, commands, and agent.
4. All documentation and skill content adheres to English and repository standards.
