---
name: audit-performance
description: Audits fullstack performance, deploy resilience (chunk recovery 404), CDN cache headers, and container concurrency.
---

# /audit-performance — Fullstack Performance & Resilience Audit

Audit codebase against the `clube:fullstack-performance-resilience` playbook:
- Verifies SPA chunk recovery against 404 errors during rolling deployments (`vite:preloadError`, `router.onError`).
- Audits CDN cache headers (`immutable` for hashed assets, `no-cache` for entrypoints).
- Checks container cgroup CPU limits (`automaxprocs` in Go).
- Checks database connection pool sizing (`SetMaxOpenConns`, `pool_size`).

## Execution Flow

1. Execute the deterministic performance scanner:
   ```bash
   python3 "${CLUBE_PLUGIN_ROOT:-plugins/clube}/scripts/audit-performance.py" --json
   ```
2. For identified opportunities:
   - Provide the exact `installLazyRouteChunkRecovery` listener tailored to the project's router.
   - Propose CDN rules (`vercel.json` or `nginx.conf`).
   - Suggest connection pool sizing based on replica count.
3. Report results using the **4-Phase Output Contract**:
   - `### 1. Plan`
   - `### 2. Execution`
   - `### 3. Summary` (Table of findings and severity)
   - `### 4. Recommended Actions` (Exact code patches ready to paste)
