# Clube Marketplace

Centralized repository for AI skills, agents, commands, and harness configurations tailored for Clube projects.

## Supported AI Harnesses
- **Oh My Pi (OMP) / Orca Agent** (`.omp-plugin/`, `omp/`)
- **Claude Code CLI** (`.claude-plugin/`, `claude-code/`)
- **Cursor IDE / Agent** (`.cursor/`, `.cursorrules`, `cursor/`)
- **Google Antigravity** (`antigravity/`)
- **OpenCode** (`opencode/`)

## Architecture Principles
1. **Single Source of Truth:** `AGENTS.md` is the only canonical persistence file for project instructions and AI configuration.
2. **Harness Sync:** Supporting harness files (`CLAUDE.md`, `GEMINI.md`, `.cursorrules`) reference `@AGENTS.md` to avoid content divergence.
3. **No Blind Overwrites:** When initializing a project, existing configurations are detected, reported, and prompted for user confirmation before migrating.
4. **4-Phase Output Contract:** Every command and skill follows a structured output: **Plan** → **Execution** → **Summary** → **Recommended Actions**.

## Getting Started

### Building Distribution Bundles
To package and sync all skills and commands across all harness directories:
```bash
make build
```

### Initializing Project AI Configuration
```bash
make init
# or directly:
./bin/clube-config init
```

### Syncing Harness Pointers
```bash
make sync
# or directly:
./scripts/sync-harness-configs.sh
```

### Auditing Environment Status
```bash
make check
```

## Directory Structure
```
clube-marketplace/
├── .claude-plugin/          # Claude Code plugin manifests
├── .omp-plugin/             # Oh My Pi plugin manifests
├── .cursor/                 # Cursor IDE rules
├── base/                    # Shared core scripts and library definitions
├── bin/                     # Unified CLI entry points
├── commands/                # Canonical slash commands
├── skills/                  # Canonical AI skills
├── scripts/                 # Build & synchronization tooling
├── claude-code/             # Generated Claude Code distribution
├── omp/                     # Generated OMP distribution
├── cursor/                  # Generated Cursor distribution
├── antigravity/             # Generated Antigravity distribution
└── opencode/                # Generated OpenCode distribution
```
