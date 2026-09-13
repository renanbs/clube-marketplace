---
name: clube-marketplace-architecture
description: Architectural constitution and engineering discipline for the Clube AI Marketplace. Defines the multi-harness plugin standard, root marketplace manifests, 4-phase output contract, and directory conventions.
---

# Architecture & Engineering Discipline — Clube Marketplace

This document defines the **Architectural Constitution** of the `clube-marketplace` repository.
Every skill, agent, command, or plugin added to this marketplace must adhere to the principles outlined below.

---

## 1. Multi-Harness Marketplace Architecture

The repository operates as a **Universal AI Marketplace** supporting Claude Code, Cursor, Codex, and Oh My Pi (OMP).
It follows the standard marketplace model:

```
clube-marketplace/
├── .claude-plugin/marketplace.json     # Claude Code marketplace catalog
├── .omp-plugin/marketplace.json        # Oh My Pi marketplace catalog
├── .cursor-plugin/marketplace.json     # Cursor marketplace catalog
├── .agents/plugins/marketplace.json    # Codex marketplace catalog
├── Makefile                            # Developer commands (check, init, help)
├── AGENTS.md                           # Authoritative repository instructions
├── CLAUDE.md                           # Pointer -> @AGENTS.md
├── GEMINI.md                           # Pointer -> @AGENTS.md
├── .cursorrules                        # Pointer -> @AGENTS.md
└── plugins/
    └── clube/                          # Core Clube plugin
        ├── .claude-plugin/plugin.json
        ├── .cursor-plugin/plugin.json
        ├── .codex-plugin/plugin.json
        ├── .omp-plugin/plugin.json
        ├── commands/                   # Slash commands
        ├── skills/                     # Modular skills (skills/<name>/SKILL.md)
        └── agents/                     # Named expert subagents
```

### Zero-Duplication Rule
Harnesses read directly from `plugins/<plugin_name>/` using their native plugin manifests.
Never replicate skills or commands across separate distribution folders (e.g., `omp/`, `claude-code/`).
All skills and commands live inside their respective plugin directory.

---

## 2. Inviolable Architectural Principles

1. **Single Source of Truth (`AGENTS.md`):**
   - In target projects, `AGENTS.md` is the only authoritative file for AI configuration and instructions.
   - All sibling harness files (`CLAUDE.md`, `GEMINI.md`, `.cursorrules`) must strictly import `@AGENTS.md`.

2. **Standard Skill Layout:**
   - Every skill must reside in its own subdirectory with an isolated `SKILL.md`:
     `plugins/<plugin>/skills/<skill-name>/SKILL.md`
   - Flat markdown files directly inside `skills/` are prohibited.

3. **Canonical English:**
   - All skills, agents, commands, manifests, and documentation must remain in standard **English**.

4. **The 4-Phase Output Contract:**
   - Every interactive command and AI workflow must report in four standardized phases:
     1. `### 1. Plan` (Command, Action, Reversibility)
     2. `### 2. Execution` (Detailed step-by-step progress with status badges: `✅`, `⏭️`, `⚠️`, `❌`)
     3. `### 3. Summary` (Markdown table with ground truth state, source of truth, and changes)
     4. `### 4. Recommended Actions` (Actionable next steps, mandatory when manual steps, `⚠️`, or `❌` occur)

5. **Product-Agnostic Plugins:**
   - Marketplace skills must never hardcode product names, private database URLs, or repository-specific paths.
   - All concrete facts must be loaded dynamically from the target project's `Project Profile`.
