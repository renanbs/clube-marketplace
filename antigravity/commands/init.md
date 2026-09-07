---
description: Initialize project AI configuration (AGENTS.md) and sync harness pointers (CLAUDE.md, GEMINI.md, .cursorrules).
---

# /init

Initializes the canonical `AGENTS.md` file for this project and ensures all supported harnesses point to it via `@AGENTS.md`:

```bash
./bin/clube-config init [DIR]
```

## Guided Flow for AI Agents
1. **Audit:** Scan for existing instructions in `CLAUDE.md`, `GEMINI.md`, `.cursorrules`, or `.cursor/rules/`.
2. **Report & Ask:** If custom/legacy content exists, report it and ask whether to migrate into `AGENTS.md`.
3. **Configure AGENTS.md:** Create or update `AGENTS.md` with project profile, stack details, and CI commands.
4. **Sync Harnesses:** Run `./scripts/sync-harness-configs.sh` to ensure pointer files contain `@AGENTS.md`.
5. **Report Output:** Always format output using the **Plan** → **Execution** → **Summary** → **Recommended Actions** contract.
