---
description: Initialize project AI configuration (AGENTS.md), handle non-standard skills/agents formats, and sync harness pointers (CLAUDE.md, GEMINI.md, .cursorrules).
---

# /init

Initializes the canonical `AGENTS.md` file for this project, resolves non-standard skill/agent formats, and ensures all supported harnesses point to `AGENTS.md` via `@AGENTS.md`:

```bash
./bin/clube-config init [DIR]
```

## Guided Flow for AI Agents
1. **Audit:** Scan for existing instructions in `CLAUDE.md`, `GEMINI.md`, `.cursorrules`, and non-standard skill/agent files.
2. **Prompt Options:** If non-standard formats or legacy instructions exist, ask the user:
   - **Option 1:** Move to standard format (migrate into canonical `AGENTS.md` and `skills/<name>/SKILL.md`).
   - **Option 2:** Leave as is (preserve without altering).
3. **Configure AGENTS.md:** Create or update `AGENTS.md` with project profile, stack details, and CI commands.
4. **Sync Harnesses:** Run `./scripts/sync-harness-configs.sh` to ensure pointer files contain `@AGENTS.md`.
5. **Report Output:** Always format output using the **Plan** → **Execution** → **Summary** → **Recommended Actions** contract.
