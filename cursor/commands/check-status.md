---
description: Audit active AI harness alignment and repository AGENTS.md integrity.
---

# /check-status

Runs a non-destructive audit of the active host harness, canonical `AGENTS.md` presence, and pointer alignment:

```bash
./bin/clube-config check
```

Reports:
- Active detected harness (OMP, Claude Code, Cursor, Antigravity, OpenCode).
- Presence and status of `AGENTS.md`.
- Alignment status of pointer files (`CLAUDE.md`, `GEMINI.md`, `.cursorrules`).
