---
name: init
description: Guided project onboarding for Clube projects. Use when the Clube plugin has just been installed, or when explicitly requested via "/clube:init", "/init", "$init", "setup project", "configure clube". Generates the canonical Project Profile in AGENTS.md and CLAUDE.md, audits database preflights, maps agent model roles, checks memory vault integration, and validates toolchain runtimes.
---

# clube:init — Guided Project Onboarding

## Overview

Guided, on-demand onboarding executed once per project repository. It prepares a newly installed project for standardized AI workflows. It follows a 6-step flow adhering to the **DETECT → REPORT → OFFER (with confirmation)** rhythm.

**Announce at start:** "I am using the `clube:init` skill to configure this repository."

### Core Principles
- **Never record secrets silently:** All credentials come directly from the developer; the agent never invents or persists credentials into files.
- **Production is strictly gated:** Production environments are never probed or touched without explicit human confirmation.
- **Idempotent:** Running `init` on an already-configured project audits and reports discrepancies without overwriting configurations unprompted.
- **Single Source of Truth:** The `AGENTS.md` file holds the authoritative Project Profile. Sibling files (`CLAUDE.md`, `GEMINI.md`, `.cursorrules`) reference `@AGENTS.md`.

---

## Step 1 — Project Profile Setup

AI workflows read the **Project Profile** from `AGENTS.md` and `CLAUDE.md` to resolve sub-projects, stacks, commands, and branch targets.

1. **DETECT:**
   - Inspect `./AGENTS.md` and `./CLAUDE.md`.
   - Check if a `## Project Profile` section already exists.
   - Scan repository root and subdirectories for stack manifests:
     - `go.mod` → Go stack (`expert-backend-go`)
     - `pyproject.toml` / `requirements.txt` → Python stack (`expert-backend-python`)
     - `package.json` with `react` → React stack (`expert-frontend-react`)
     - `package.json` with `vue` → Vue stack (`expert-frontend-vue`)
   - Infer UX orientations (e.g., admin panels → web-first, mobile apps → mobile-first).

2. **REPORT:**
   - Present detected sub-projects, infer stacks, and identify UX orientations per directory.

3. **OFFER:**
   - Build the canonical YAML block with the developer, confirming CI commands (`test`, `lint`, `build`) and base branches before writing:

```yaml
## Project Profile (clube:workflow-dev)
subprojects:
  - { path: backend/, stack: expert-backend-go }
  - path: frontend/
    stack: expert-frontend-react
    ux_default: expert-frontend-pwa
    ux_overrides:
      - { match: "src/**/admin/**", ux: expert-frontend-web }
vcs: { base: main, pr_target: main, prefixes: [feature, fix, hotfix] }
specs_dir: .specs/<feature>/
commands:
  expert-backend-go: { test: "go test ./...", lint: "golangci-lint run ./...", build: "go build ./..." }
  expert-frontend-react: { test: "npm test", lint: "npm run lint", build: "npm run build" }
database: { connections: { stage: stage-db, prod: prod-db }, dialect: postgres }
agents: { omp: { reasoning: { model: default }, code: { model: default }, critique: { model: default } } }
```

4. Ensure harness pointer files (`CLAUDE.md`, `GEMINI.md`, `.cursorrules`) strictly import `@AGENTS.md`.

---

## Step 2 — Database Connection Preflight (Optional)

If the project requires a relational database:
1. **DETECT:** Check if connection profiles exist in standard dialect locations (e.g., `~/.pgpass`, `~/.pg_service.conf`).
2. **REPORT:** State whether connections are registered and reachable.
3. **OFFER:** Ask user for connection identifiers. Test staging with a non-destructive query (`SELECT 1`). Never execute queries against production without explicit permission.

---

## Step 3 — Agent Role Mapping (Optional)

1. **DETECT:** Query active host model catalog (`omp models`, Claude models, Cursor models).
2. **REPORT:** List recommended models for `reasoning`, `code`, `critique`, and `security`.
3. **OFFER:** Write the host-specific model mapping into the Project Profile under `agents:`.

---

## Step 4 — Semantic Memory Vault (Optional)

1. **DETECT:** Check if an Obsidian vault or local documentation directory exists.
2. **OFFER:** Configure persistent project notes under `.specs/` or link to an existing vault.

---

## Step 5 — Runtime & Toolchain Validation

1. Run version checks for all detected runtimes (`go version`, `python3 --version`, `node -v`, `pnpm -v`, `docker -v`).
2. Report missing or outdated toolchains required by the project's CI commands.

---

## Step 6 — Summary & Hand-off

Print the final status using the standardized 4-phase format:
- `### 1. Plan`
- `### 2. Execution`
- `### 3. Summary` (Health table of subprojects, database, agent mappings, and runtimes)
- `### 4. Recommended Actions` (e.g., how to begin dev tasks or install missing CLI tools)
