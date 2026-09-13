---
name: audit-privacy
description: Audits data privacy and PII compliance in logs, APM, Sentry, query strings, and metrics. Runs deterministic scan and generates masked models.
---

# /audit-privacy — Data Privacy & Observability Audit

Audit codebase against the `clube:data-privacy-observability` playbook:
- Detects blind struct/object logging (`console.log(req.body)`, `log.Printf("%+v")`, `zap.Any`).
- Detects PII in query parameters (`?cpf=`, `?email=`, `?phone=`).
- Checks high-cardinality metric labels in Prometheus.
- Audits Sentry scrubbing and error tracking.

## Execution Flow

1. Execute the deterministic privacy scanner:
   ```bash
   python3 "${CLUBE_PLUGIN_ROOT:-plugins/clube}/scripts/audit-privacy.py" --json
   ```
2. For each flagged file:
   - Verify if the object actually contains sensitive user data or static system config.
   - Propose custom masking functions (e.g. `MaskPhone`, `MaskEmail`, or branded types with `MarshalJSON()`).
3. Report results using the **4-Phase Output Contract**:
   - `### 1. Plan`
   - `### 2. Execution`
   - `### 3. Summary` (Table of findings and severity)
   - `### 4. Recommended Actions` (Exact code patches implementing masked logging)
