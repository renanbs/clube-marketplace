---
name: fullstack-performance-resilience
description: |
  Specialist in fullstack performance, runtime optimization, deployment resilience, and database tuning.
  Stack- and provider-agnostic: declarations of core architectural principles accompanied by concrete implementations.
  Activate this skill whenever configuring frontend builds, chunk recovery, edge caching, container runtimes, or database indexing.
license: Apache-2.0
metadata:
  version: v0.4.0
  author: clubedepontos
---

# Fullstack Performance & Resilience Playbook

Performance engineering and operational resilience practices for modern single-page applications, containerized APIs, and relational databases.

---

## 1. Core Principles

1. **SPA Rolling Deployment Resilience:** Capture chunk 404s via both router error hooks and bundler preload error listeners (`vite:preloadError`), triggering recovery reloads with anti-loop guards.
2. **Deterministic Edge Caching:** Distinguish immutable hashed static assets (`/assets/*-[hash].js`, 1-year cache) from unhashed entrypoints (`index.html`, `sw.js`, `manifest`, revalidated on every request).
3. **Container cgroup CPU & Pool Alignment:** Set runtime concurrency based on container cgroups (`automaxprocs`), size database connection pools globally across horizontal replicas, and execute parallel queries with context cancellation.
4. **Non-Blocking Database Migrations:** Always create indexes `CONCURRENTLY` in non-transactional migration blocks on live production tables, utilize partial/functional indexes, and apply conditional HTTP `ETag` (304) polling patterns.

---

## 2. Activation Triggers

| Trigger Area | Description & Indicators | Target Reference |
| :--- | :--- | :--- |
| **SPA Chunk Recovery** | Dynamic module load errors, Vite preload errors, rolling deployment 404s, reload loops. | [Chunk Recovery](references/chunk-recovery.md) |
| **Edge Caching & CDN** | `Cache-Control` headers, immutable hashed assets, unhashed entrypoints, Cloudflare/Nginx rules. | [Edge Caching & Headers](references/caching-edge-headers.md) |
| **Container & Runtime** | `automaxprocs`, CPU quotas, DB pool sizing, `errgroup`/`Promise.all` parallel queries, metric cardinality. | [Runtime Tuning](references/runtime-tuning.md) |
| **Database Indexing** | `CREATE INDEX CONCURRENTLY`, partial/expression indexes, zero `SELECT *`, ETag 304 fingerprint queries. | [Database Indexing](references/db-indexing-queries.md) |

---

## 3. Modular References Index

Detailed guides, DDLs, schemas, and framework configurations reside in the `references/` directory:

- 📄 **[SPA Rolling Deployment Resilience: Global Chunk Recovery](references/chunk-recovery.md)** — Trapping Vite and router module errors, session anti-loop guards, and multi-framework hooks.
- 📄 **[Edge Caching Policy & HTTP Headers](references/caching-edge-headers.md)** — Immutable asset caching, entrypoint revalidation, and Nginx/Vercel/Cloudflare configs.
- 📄 **[Container Runtime Tuning & Concurrency](references/runtime-tuning.md)** — cgroup CPU quota alignment, database connection pooling, parallel query cancellation, and Prometheus label protection.
- 📄 **[Database Indexing, Query Optimization & ETag Caching](references/db-indexing-queries.md)** — Non-transactional `CONCURRENTLY` migrations, partial/functional indexes, and ETag fingerprinting.
