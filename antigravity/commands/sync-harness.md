---
description: Synchronize @AGENTS.md pointer files across CLAUDE.md, GEMINI.md, and .cursorrules.
---

# /sync-harness

Ensures all sibling harness configuration files point to `@AGENTS.md` as the single source of truth:

```bash
./scripts/sync-harness-configs.sh [TARGET_DIR]
```

Or via CLI:
```bash
./bin/clube-config sync [TARGET_DIR]
```

- Safe to re-run: existing `@AGENTS.md` files remain untouched.
- Files with custom content are preserved and reported.
