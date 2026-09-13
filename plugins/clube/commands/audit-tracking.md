---
name: audit-tracking
description: Audits marketing attribution, root domain cookie persistence, Meta CAPI deduplication, and acquisition context.
---

# /audit-tracking — Marketing Attribution & Tracking Audit

Audit codebase against the `clube:marketing-attribution-analytics` playbook:
- Verifies that first-touch UTM cookies are saved on the root domain (`domain=.domain.com`) to persist across subdomains.
- Checks Meta Conversions API (CAPI) server-side event deduplication using matching `event_id`.
- Audits backend persistence of acquisition context (`acquisition_context` JSONB column on user/lead records).

## Execution Flow

1. Execute the deterministic tracking scanner:
   ```bash
   python3 "${CLUBE_PLUGIN_ROOT:-plugins/clube}/scripts/audit-tracking.py" --json
   ```
2. For identified opportunities:
   - Provide cookie setter helpers configured with the proper root domain scope.
   - Propose `event_id` generation logic for frontend and backend CAPI sync.
   - Propose database migration adding `acquisition_context JSONB`.
3. Report results using the **4-Phase Output Contract**:
   - `### 1. Plan`
   - `### 2. Execution`
   - `### 3. Summary` (Table of findings and severity)
   - `### 4. Recommended Actions` (Exact code patches ready to apply)
