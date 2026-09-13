# Clube Marketplace

Centralized multi-harness AI marketplace for skills, agents, commands, and workflows tailored for Clube projects.

Supported hosts include **Claude Code**, **Cursor**, **Codex**, and **Oh My Pi (OMP)**.
Each host reads its native marketplace catalog from the root (`.claude-plugin/`, `.cursor-plugin/`, `.agents/plugins/`, `.omp-plugin/`), consuming plugins defined directly under `plugins/`.

---

## Repository Structure

```
clube-marketplace/
├── .claude-plugin/marketplace.json     # Claude Code marketplace catalog
├── .omp-plugin/marketplace.json        # Oh My Pi marketplace catalog
├── .cursor-plugin/marketplace.json     # Cursor marketplace catalog
├── .agents/plugins/marketplace.json    # Codex / OpenAI Agents marketplace catalog
├── Makefile                            # Top-level operational targets (check, sync, init)
├── AGENTS.md                           # Authoritative AI instructions & project profile
├── CLAUDE.md                           # Pointer -> @AGENTS.md
├── GEMINI.md                           # Pointer -> @AGENTS.md
├── .cursorrules                        # Pointer -> @AGENTS.md
├── bin/
│   └── clube-config                    # Marketplace health check & CLI helper
├── scripts/
│   ├── lib-harness.sh                  # Host harness detection
│   ├── lib-runlog.sh                   # Structured event logging
│   └── sync-harness-configs.sh         # Pointer synchronizer (@AGENTS.md)
└── plugins/
    └── clube/                          # Core Clube plugin
        ├── .claude-plugin/plugin.json
        ├── .cursor-plugin/plugin.json
        ├── .codex-plugin/plugin.json
        ├── .omp-plugin/plugin.json
        ├── commands/                   # Slash commands (/init, /omp-setup, /help)
        ├── skills/                     # Modular skills (skills/<name>/SKILL.md)
        └── agents/                     # Named expert subagents
```

---

## Installation by AI Host

### Claude Code
```bash
/plugin marketplace add git@github.com:clubedepontos/clube-marketplace.git
/plugin install clube@clube
```

### Oh My Pi (OMP)
```bash
/marketplace add https://github.com/clubedepontos/clube-marketplace
/marketplace install --scope project clube@clube
```
*Note: If using custom agents on OMP, run `/clube:omp-setup` once to configure agent model overrides.*

### Cursor
Add as a Team marketplace via Dashboard → Plugins, or symlink for local development:
```bash
mkdir -p ~/.cursor/plugins/local
ln -s "$(pwd)/plugins/clube" ~/.cursor/plugins/local/clube
```

### Codex
```bash
codex plugin marketplace add clubedepontos/clube-marketplace --ref main
codex plugin install clube --source clube
```

---

## Core Principles

1. **Single Source of Truth (`AGENTS.md`):** Target projects declare their configuration once inside `AGENTS.md`. All other harness files (`CLAUDE.md`, `GEMINI.md`, `.cursorrules`) reference `@AGENTS.md`.
2. **Modular Directory Isolation:** Every skill is stored as `plugins/<plugin>/skills/<name>/SKILL.md`. Flat markdown skills are rejected by `make check`.
3. **Product-Agnostic Process:** Skills encapsulate process and discipline; repository-specific facts (paths, CI commands, branch conventions, connection profiles) are dynamically resolved from the target project's `Project Profile`.
4. **4-Phase Output Contract:** Every command and skill follows the standardized format:
   - `### 1. Plan`
   - `### 2. Execution`
   - `### 3. Summary`
   - `### 4. Recommended Actions`

---

## Operational Commands

- `make check` — Audits active harness, marketplace catalogs, and plugin integrity.
- `make sync` — Synchronizes harness pointer files (`@AGENTS.md`) across subdirectories.
- `make init` — Runs project AI onboarding and harness configuration.
