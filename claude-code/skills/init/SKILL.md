---
name: init
description: Generic AI project initialization and harness onboarding skill for Clube projects. Sets up AGENTS.md as the single source of truth, detects legacy instruction files and non-standard skills/agents formats, prompts the user to migrate or keep them, and synchronizes harness pointer files (CLAUDE.md, GEMINI.md, .cursorrules) with @AGENTS.md.
---

# init — Generic Project AI Onboarding & Harness Setup

## Overview

Sets up or aligns a repository for multi-harness AI development (Oh My Pi, Claude Code, Cursor, Antigravity, OpenCode).

**Announce at start:** `"Using init skill to configure AI harness and AGENTS.md for this project."`

### Core Principles
1. **Single Source of Truth:** All project instructions, conventions, and profiles persist **strictly in `AGENTS.md`**.
2. **Never Overwrite Silently:** If existing configurations, legacy instructions, or non-standard skills/agents are detected, report them and ask the user how to handle them.
3. **Multi-Harness Pointer Alignment:** Supporting harnesses resolve `@AGENTS.md` imports. The sync script (`scripts/sync-harness-configs.sh`) sets up `@AGENTS.md` pointers without duplicating content.
4. **Product Agnostic:** Does not make rigid assumptions about language, framework, or tooling. The user confirms or supplies the project specifics.

---

## Step 1 — Audit Existing Instructions, Skills, and Agents

Check the repository root and subdirectories for:
1. **Instruction & Prompt Files:**
   - `CLAUDE.md`
   - `GEMINI.md`
   - `.cursorrules`
   - `.cursor/rules/`
   - Custom prompt files (`.prompt`, `PROMPT.md`, `INSTRUCTIONS.md`, etc.)

2. **Skills & Agents in Non-Standard Formats:**
   - Skills placed in flat files (e.g. `skills/foo.md` or `.claude/skills/foo.md` instead of `skills/foo/SKILL.md`).
   - Legacy agent definitions or directories (`.omp/skills/`, `.cursor/agents/`, `agents/` in non-standard layout).

### Decision Flow When Non-Standard Formats or Legacy Files Are Found:

If any legacy instructions, non-standard skills, or non-standard agent files are found, **STOP and ask the user:**

```
Found existing instructions / skills / agents in non-standard format:
  • <list of detected files and paths>

How would you like to proceed?
  [1] Move to standard format (Recommended)
      - Migrate instructions into canonical AGENTS.md
      - Reorganize skills into standard skills/<name>/SKILL.md
      - Replace sibling harness configs with @AGENTS.md pointer
  [2] Leave as is
      - Keep existing files intact without moving or altering them
```

- **If User Chooses Option 1 (Move to standard):**
  - Migrate and consolidate the content into `AGENTS.md` and `skills/<name>/SKILL.md`.
  - Replace the harness config files with `@AGENTS.md`.
- **If User Chooses Option 2 (Leave as is):**
  - Preserve all existing files as they are.
  - Do not overwrite or move them.

---

## Step 2 — Configure Canonical `AGENTS.md`

Persist project configuration **exclusively in `AGENTS.md`**.

If creating a new `AGENTS.md` or updating an existing one, use this standard structure:

```markdown
# Project AI Instructions

## Project Profile
- **Project Name:** <Name>
- **Description:** <Brief description of the service/application>
- **Primary Stack:** <e.g., Go, Python, React, Vue, TypeScript, Node.js>
- **Architecture:** <e.g., Clean Architecture, Hexagonal, Monorepo, Microservice>

## Build & Test Commands
- **Test:** `<test command, e.g. go test ./... or pnpm test>`
- **Lint:** `<lint command, e.g. golangci-lint run or pnpm lint>`
- **Build:** `<build command, e.g. go build or pnpm build>`

## Development Conventions
- **Code Style:** <conventions or formatter rules>
- **Testing Standard:** <unit, integration, e2e expectations>
- **Single Source of Truth:** This `AGENTS.md` file is authoritative across all AI tools.
```

---

## Step 3 — Synchronize Harness Pointers

Ensure all supported AI coding harnesses resolve instructions from `AGENTS.md` via the `@AGENTS.md` import line.

Run the sync script or execute:
```bash
./scripts/sync-harness-configs.sh . CLAUDE.md GEMINI.md .cursorrules
```

This creates or verifies:
- `CLAUDE.md` -> containing `@AGENTS.md`
- `GEMINI.md` -> containing `@AGENTS.md`
- `.cursorrules` -> containing `@AGENTS.md`

Any file that already contains custom instructions and was selected to stay as-is (Option 2) is **preserved** and not overwritten.

---

## Step 4 — Verification & Summary

Validate the final state and present the outcome using the **Standard 4-Phase Output Contract**:

### Example Summary:
```markdown
### 1. Plan
- **Command:** init
- **Action:** Initialized AGENTS.md and synchronized harness pointers
- **Reversible:** Yes (files can be edited or restored)

### 2. Execution
- ✅ Checked repository root for legacy instruction files and non-standard skills/agents
- ✅ User selected migration strategy: [Option 1: Move to standard | Option 2: Leave as is]
- ✅ Configured canonical AGENTS.md
- ✅ Synchronized CLAUDE.md, GEMINI.md, and .cursorrules pointers

### 3. Summary
| Field | Content |
| :--- | :--- |
| **Status** | success |
| **Source of Truth** | AGENTS.md |
| **Harness Pointers** | CLAUDE.md, GEMINI.md, .cursorrules (@AGENTS.md) |
| **Migration Decision** | Moved to standard / Kept as-is |

### 4. Recommended Actions
- Review and refine project-specific build/test commands in AGENTS.md as needed.
```

---

## Red Flags — STOP Immediately If:
- Writing project instructions to `CLAUDE.md`, `GEMINI.md`, or `.cursorrules` directly instead of `AGENTS.md`.
- Overwriting, moving, or deleting existing legacy files/skills without prompting the user with the two options (Option 1: Move to standard, Option 2: Leave as is).
- Hardcoding speculative environment assumptions without user input.
