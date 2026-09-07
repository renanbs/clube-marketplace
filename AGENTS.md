# Clube Marketplace — AI Instructions

## Project Profile
- **Project Name:** Clube Marketplace
- **Description:** Centralized AI marketplace, skills, agents, and multi-harness distribution suite for Clube projects.
- **Primary Architecture:** Multi-Harness Plugin Architecture (OMP, Claude Code, Cursor, Antigravity, OpenCode).
- **Single Source of Truth:** This `AGENTS.md` file is authoritative across all AI coding harnesses.

## Development Conventions
- All skills, agents, commands, documentation, and manifests must remain in **English**.
- Changes to canonical skills or commands should be made under `base/` and built via `make build`.
- Execute `make sync` whenever new subdirectories or projects are added.
- All AI workflows adhere to the 4-phase output contract: Plan → Execution → Summary → Recommended Actions.
