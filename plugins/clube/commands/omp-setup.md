---
name: omp-setup
description: omp-only. Configures task.agentModelOverrides for Clube agents to prevent "Error: No model selected" when custom agents declare model:inherit.
---

Run this once per Oh My Pi (OMP) installation (or whenever changing model providers).
This command applies exclusively to **omp** — abort if the active host is not omp.

## Purpose

Agents in this plugin ship `model: inherit` in their frontmatter.
Claude Code, Cursor, and Codex interpret this as "use the active model of the main session".
Oh My Pi requires explicit agent overrides for custom subagents, otherwise failing with `Error: No model selected`.

To fix this cleanly without touching shared agent definitions, configure OMP's native override table via `omp config set task.agentModelOverrides.<agent> <model-id>`.

## Steps

1. Confirm the host is OMP (`omp`). If not, inform the user and exit.
2. Resolve model IDs per class (`reasoning`, `code`, `critique`, `security`):
   - If the project profile (`AGENTS.md`) defines an `agents.omp` block, use those IDs.
   - Otherwise, list available models (`omp models`) and prompt the user to assign models per class.
3. Configure overrides using `omp config set task.agentModelOverrides.<agent> <model-id>`.
4. Verify configuration using `omp config get task.agentModelOverrides`.
5. Instruct the user to restart the session or run `/reload-plugins` to apply changes.
