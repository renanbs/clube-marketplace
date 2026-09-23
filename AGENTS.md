# Clube Marketplace — AI Instructions

## Project Profile
- **Project Name:** Clube Marketplace
- **Description:** Centralized AI marketplace, skills, agents, and multi-harness distribution suite for Clube projects.
- **Primary Architecture:** Multi-Harness Plugin Marketplace Architecture (Claude Code, Cursor, Codex, Oh My Pi, OpenCode V2).
- **Single Source of Truth:** This `AGENTS.md` file is authoritative across all AI coding harnesses.

## Development Conventions
- All skills, agents, commands, documentation, and manifests must remain in **English**.
- Plugins reside under `plugins/<plugin_name>/` (e.g. `plugins/clube/`).
- Each skill resides in its isolated directory: `plugins/<plugin>/skills/<skill_name>/SKILL.md`.
- Each slash command resides in `plugins/<plugin>/commands/<command_name>.md`.
- Named agents reside in `plugins/<plugin>/agents/<agent_name>.md`.
- Run `make check` to audit active harness detection, marketplace catalogs, and plugin integrity.
- Run `make sync` whenever new subdirectories or projects are added.
- All AI workflows adhere to the 4-phase output contract: Plan → Execution → Summary → Recommended Actions.
