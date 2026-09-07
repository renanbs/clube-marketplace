---
name: init
description: Generic AI project initialization and harness onboarding skill for Clube projects. Sets up AGENTS.md as the single source of truth, detects legacy instruction files and prompts for migration, and synchronizes harness pointer files (CLAUDE.md, GEMINI.md, .cursorrules) with @AGENTS.md.
---

# init — Generic Project AI Onboarding & Harness Setup

## Overview

Sets up or aligns a repository for multi-harness AI development (Oh My Pi, Claude Code, Cursor, Antigravity, OpenCode).

**Announce at start:** `"Using init skill to configure AI harness and AGENTS.md for this project."`

### Core Principles
1. **Single Source of Truth:** All project instructions, conventions, and profiles persist **strictly in `AGENTS.md`**.
2. **Never Overwrite Silently:** If existing configurations or custom instructions exist (`CLAUDE.md`, `GEMINI.md`, `.cursorrules`, etc.), report them and ask the user whether to migrate their content into `AGENTS.md` or follow specific custom instructions.
3. **Multi-Harness Pointer Alignment:** Supporting harnesses resolve `@AGENTS.md` imports. The sync script (`scripts/sync-harness-configs.sh`) sets up `@AGENTS.md` pointers without duplicating content.
4. **Product Agnostic:** Does not make rigid assumptions about language, framework, or tooling. The user confirms or supplies the project specifics.

---

## Step 1 — Audit Existing Project Instructions

Check for any pre-existing instruction or prompt files in the repository root and subdirectories:
- `CLAUDE.md`
- `GEMINI.md`
- `.cursorrules`
- `.cursor/rules/`
- Custom prompt files (`.prompt`, `PROMPT.md`, `INSTRUCTIONS.md`, etc.)

### Behavior:
- **Case A: No existing files found.**
  - Proceed directly to **Step 2** to initialize a clean `AGENTS.md`.
- **Case B: Files exist and already contain only `@AGENTS.md`.**
  - Report that harness pointers are already aligned. Check if `AGENTS.md` exists and contains required sections.
- **Case C: Legacy / custom content detected.**
  - **STOP and REPORT:** List all detected files and summarize their contents.
  - **ASK USER:** Ask whether to:
    1. Migrate and consolidate legacy content into the canonical `AGENTS.md`.
    2. Keep existing files separate and request manual guidance.
    3. Overwrite/replace with a fresh `AGENTS.md` template (after user confirmation).

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

Any file that already contains custom instructions is **preserved** and reported, never overwritten without explicit user approval.

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
- ✅ Checked repository root for legacy instruction files
- ✅ Configured canonical AGENTS.md
- ✅ Synchronized CLAUDE.md, GEMINI.md, and .cursorrules pointers

### 3. Summary
| Field | Content |
| :--- | :--- |
| **Status** | success |
| **Source of Truth** | AGENTS.md |
| **Harness Pointers** | CLAUDE.md, GEMINI.md, .cursorrules (@AGENTS.md) |
| **Legacy Files Migrated** | None (fresh setup) |

### 4. Recommended Actions
- Review and refine project-specific build/test commands in AGENTS.md as needed.
```

---

## Red Flags — STOP Immediately If:
- Writing project instructions to `CLAUDE.md`, `GEMINI.md`, or `.cursorrules` directly instead of `AGENTS.md`.
- Overwriting or deleting existing legacy instruction files without presenting their contents and getting explicit user confirmation.
- Hardcoding speculative environment assumptions without user input.
