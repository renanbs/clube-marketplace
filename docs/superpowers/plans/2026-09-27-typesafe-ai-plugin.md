# TypeSafe AI Plugin (`typesafe-ai`) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create and integrate the `typesafe-ai` plugin (v0.1.0) into the marketplace, providing the `typesafe-jev` skill (System 1 decision routing, confidence gating, and integrations for Python, TypeScript, Go, and Rust), the `expert-jev` specialist agent, the `/typesafe-ai:optimize` slash command, and multi-harness distribution across all 5 platforms.

**Architecture:** A self-contained plugin living under `plugins/typesafe-ai/` with standard manifests for Claude Code, Cursor, Codex, Oh My Pi, and OpenCode V2. Verified via `./bin/clube-config check` and `pytest`.

**Tech Stack:** Python, TypeScript (OpenCode adapter), Markdown/YAML frontmatter (Skills, Agents, Commands), JSON (harness manifests).

**Spec:** `docs/superpowers/specs/2026-09-27-typesafe-ai-plugin-design.md`

## Global Constraints

- All skills, agents, commands, documentation, and manifests must remain in **English**.
- Skill files reside at `plugins/<plugin>/skills/<skill_name>/SKILL.md` with topic references in `references/`.
- Slash commands adhere to the 4-phase contract: Plan → Execution → Summary → Recommended Actions.
- Plugin version starts at `v0.1.0` and must be strictly aligned across all its manifests (`.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.omp-plugin/plugin.json`, `.opencode-plugin/plugin.json`).
- OpenCode V2 wiring requires `.opencode/plugins/typesafe-ai/index.ts` and registration in `opencode.json` and `.opencode/opencode.json`.
- The repository validator (`./bin/clube-config check`) and tests (`./bin/clube-config test`) must pass cleanly with 0 problems.

## Review Focus

1. **Manifest version mismatch:** All 5 harness manifests for `typesafe-ai` must declare `0.1.0` matching the marketplace catalog entries.
2. **Missing OpenCode adapter:** `check_opencode_integration` requires `.opencode/plugins/typesafe-ai/index.ts` and valid wiring in `opencode.json`.
3. **Agent frontmatter compliance:** `plugins/typesafe-ai/agents/expert-jev.md` must contain valid frontmatter (`name`, `description`, `tools`, `model`).
4. **Command frontmatter & phase contract:** `plugins/typesafe-ai/commands/optimize.md` must have valid frontmatter (`name`, `description`) and document all 4 phases.
5. **Skill structure:** `plugins/typesafe-ai/skills/typesafe-jev/SKILL.md` must reference all 6 technical documents in `references/` (`system1-architecture.md`, `confidence-gating.md`, `python-pydantic.md`, `typescript-sdk.md`, `go-integration.md`, `rust-integration.md`).

---

### Task 1: Scaffolding Manifests & Marketplace Catalog Registration

**Files:**
- Create: `plugins/typesafe-ai/.claude-plugin/plugin.json`
- Create: `plugins/typesafe-ai/.cursor-plugin/plugin.json`
- Create: `plugins/typesafe-ai/.codex-plugin/plugin.json`
- Create: `plugins/typesafe-ai/.omp-plugin/plugin.json`
- Create: `plugins/typesafe-ai/.opencode-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `.cursor-plugin/marketplace.json`
- Modify: `.agents/plugins/marketplace.json`
- Modify: `.omp-plugin/marketplace.json`
- Modify: `.opencode-plugin/marketplace.json`

**Interfaces:**
- Produces: Catalog and plugin manifests for `typesafe-ai` version `0.1.0`.

- [ ] **Step 1: Write test asserting `typesafe-ai` plugin is cataloged and validated**
Add a test in `tests/test_cli_check.py` validating that when `typesafe-ai` is registered in marketplace catalogs with its 5 manifests, `check_repo` recognizes it as valid.

- [ ] **Step 2: Run test to verify it fails**
Run: `uv run pytest tests/test_cli_check.py -k typesafe -v`
Expected: FAIL (plugin not found / not registered)

- [ ] **Step 3: Create the 5 plugin manifests and update marketplace catalogs**
Create manifests in `plugins/typesafe-ai/` with version `0.1.0`.
Update the 5 root `marketplace.json` files with the `typesafe-ai` entry:
```json
{
  "name": "typesafe-ai",
  "version": "0.1.0",
  "description": "TypeSafe AI integration for Jev System 1 decision engine, calibrated confidence gating, and token optimization",
  "author": "clubedepontos",
  "path": "plugins/typesafe-ai"
}
```

- [ ] **Step 4: Run test to verify it passes**
Run: `uv run pytest tests/test_cli_check.py -k typesafe -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add plugins/typesafe-ai/ .claude-plugin/marketplace.json .cursor-plugin/marketplace.json .agents/plugins/marketplace.json .omp-plugin/marketplace.json .opencode-plugin/marketplace.json tests/test_cli_check.py
git commit -m "feat(typesafe-ai): scaffold plugin manifests and register in marketplace catalogs"
```

---

### Task 2: OpenCode V2 Integration

**Files:**
- Create: `.opencode/plugins/typesafe-ai/package.json`
- Create: `.opencode/plugins/typesafe-ai/index.ts`
- Modify: `opencode.json`
- Modify: `.opencode/opencode.json`

**Interfaces:**
- Consumes: `plugins/typesafe-ai`
- Produces: OpenCode adapter package enabling `/typesafe-ai:optimize` command, `expert-jev` agent, and `typesafe-jev` skill in OpenCode V2.

- [ ] **Step 1: Write test checking OpenCode adapter validation for `typesafe-ai`**
Add test in `tests/test_cli_check.py` ensuring `check_opencode_integration` passes with `typesafe-ai`.

- [ ] **Step 2: Run test to verify it fails**
Run: `uv run pytest tests/test_cli_check.py -k opencode_typesafe -v`
Expected: FAIL (missing `.opencode/plugins/typesafe-ai/index.ts`)

- [ ] **Step 3: Implement OpenCode adapter and wire `opencode.json`**
Create `.opencode/plugins/typesafe-ai/package.json` and `index.ts`.
Wire agent and plugin in `opencode.json` and `.opencode/opencode.json`.

- [ ] **Step 4: Run test to verify it passes**
Run: `uv run pytest tests/test_cli_check.py -k opencode_typesafe -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add .opencode/plugins/typesafe-ai/ opencode.json .opencode/opencode.json tests/test_cli_check.py
git commit -m "feat(typesafe-ai): add OpenCode V2 adapter and configuration"
```

---

### Task 3: Skill `typesafe-jev` and References (Python, TypeScript, Go, Rust)

**Files:**
- Create: `plugins/typesafe-ai/skills/typesafe-jev/SKILL.md`
- Create: `plugins/typesafe-ai/skills/typesafe-jev/references/system1-architecture.md`
- Create: `plugins/typesafe-ai/skills/typesafe-jev/references/confidence-gating.md`
- Create: `plugins/typesafe-ai/skills/typesafe-jev/references/python-pydantic.md`
- Create: `plugins/typesafe-ai/skills/typesafe-jev/references/typescript-sdk.md`
- Create: `plugins/typesafe-ai/skills/typesafe-jev/references/go-integration.md`
- Create: `plugins/typesafe-ai/skills/typesafe-jev/references/rust-integration.md`

**Interfaces:**
- Produces: Complete technical documentation, guides, and architectural rules for Jev.

- [ ] **Step 1: Write test verifying skill frontmatter, sections, and references**
Add test asserting that `typesafe-jev` has valid frontmatter, a description, and that all 6 references exist and are valid markdown.

- [ ] **Step 2: Run test to verify it fails**
Run: `uv run pytest tests/test_cli_check.py -k typesafe_skill -v`
Expected: FAIL

- [ ] **Step 3: Write `SKILL.md` and all 6 reference guides**
Create `SKILL.md` detailing:
- Intent: System 1 decision engine replacing LLMs for classification, triage, routing.
- Principles: Parallel sampling, zero token generation for choices, calibrated probability.
- Write each reference with production-ready code examples:
  - `system1-architecture.md`: Architecture comparison, latency benchmarks, token economics.
  - `confidence-gating.md`: Confidence scoring, fallback triggers, human review loop.
  - `python-pydantic.md`: FastAPI, Pydantic AI `TypeSafeModel`, Pydantic v2 enums.
  - `typescript-sdk.md`: Node/Bun/Edge, Zod schemas, type inference.
  - `go-integration.md`: Standard library HTTP client, JSON unmarshal into strict structs, context timeouts.
  - `rust-integration.md`: `reqwest`, `serde` enums, strict error handling.

- [ ] **Step 4: Run test to verify it passes**
Run: `uv run pytest tests/test_cli_check.py -k typesafe_skill -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add plugins/typesafe-ai/skills/ tests/test_cli_check.py
git commit -m "feat(typesafe-ai): add typesafe-jev skill and multilingual reference guides"
```

---

### Task 4: Specialist Agent `expert-jev` & Slash Command `/typesafe-ai:optimize`

**Files:**
- Create: `plugins/typesafe-ai/agents/expert-jev.md`
- Create: `plugins/typesafe-ai/commands/optimize.md`

**Interfaces:**
- Produces: Invokable agent `expert-jev` and slash command `/typesafe-ai:optimize`.

- [ ] **Step 1: Write test verifying agent and command validation**
Add test in `tests/test_cli_check.py` ensuring `check_agents` and `check_commands` validate `expert-jev` and `optimize`.

- [ ] **Step 2: Run test to verify it fails**
Run: `uv run pytest tests/test_cli_check.py -k typesafe_agent_command -v`
Expected: FAIL

- [ ] **Step 3: Implement `expert-jev.md` and `optimize.md`**
- `expert-jev.md`: Model class `reasoning` / `code`, specialized in System 1 design, schemas, and token optimization.
- `optimize.md`: 4-phase contract command (`/typesafe-ai:optimize`) auditing projects for LLM token waste.

- [ ] **Step 4: Run test to verify it passes**
Run: `uv run pytest tests/test_cli_check.py -k typesafe_agent_command -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add plugins/typesafe-ai/agents/ plugins/typesafe-ai/commands/ tests/test_cli_check.py
git commit -m "feat(typesafe-ai): add expert-jev agent and optimize command"
```

---

### Task 5: End-to-End Validation & CLI Integration

**Files:**
- Test: Full repository check via `./bin/clube-config check` and `make check`
- Test: Full test suite via `./bin/clube-config test` and `make test`

- [ ] **Step 1: Run full check**
Run: `./bin/clube-config check`
Expected: Output showing `[Plugin: typesafe-ai]` with 1 valid modular skill (6 topic references), 1 valid specialist agent, 1 slash command, and 0 problems.

- [ ] **Step 2: Run full test suite**
Run: `./bin/clube-config test`
Expected: 100% tests passing.

- [ ] **Step 3: Commit any final sync adjustments**
```bash
git commit -am "chore(typesafe-ai): verify full repository check and test suite"
```
