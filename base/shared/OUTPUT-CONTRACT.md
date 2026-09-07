# Standard 4-Phase Output Contract

Every AI agent, command, and CLI execution across all harnesses (OMP, Claude Code, Cursor, Antigravity, OpenCode) must adhere to this structured reporting format.

---

## 1. Plan

Before modifying any state or executing actions:
- **Command / Target:** Exact command, file path, or operation being executed.
- **Action:** Clear, concise statement describing the intended change.
- **Reversible:** Strategy for rollback, or `read-only / not applicable`.

---

## 2. Execution

Step-by-step progress with explicit outcome indicators:
- `✅ <step>` — Completed and verified.
- `⏭️ <step>` — Skipped (state clear reason).
- `⚠️ <step>` — Completed with caveats/warnings (state exact reason).
- `❌ <step>` — Failed (include exact error output; never hallucinate or mask errors).

---

## 3. Summary

Objective snapshot of the operation outcome:

| Field | Content |
| :--- | :--- |
| **Status** | `success` \| `partial` \| `failed` \| `unchanged` |
| **Changed** | List of modified files/settings or `nothing — already compliant` |
| **Source of Truth** | `AGENTS.md` (or path to canonical configuration) |
| **Harnesses Synced** | List of synced harness pointers (`CLAUDE.md`, `GEMINI.md`, etc.) |
| **Backup / Snapshot** | Path to backup, or `none` |
| **How to Revert** | Exact command or steps to roll back |

---

## 4. Recommended Actions

*(Mandatory whenever any step produces `⚠️` (warning) or `❌` (failure))*

- `• <Issue description>`: `exact 1-line command or action to resolve`
