---
name: fullstack-performance-resilience
description: |
  Specialist in fullstack performance, runtime optimization, deployment resilience, and database tuning.
  Stack- and provider-agnostic: each section establishes the core architectural principle followed by concrete implementation examples.
  Activate this skill whenever:
  - Configuring frontend builds (Vite, Astro, Rollup, Webpack), code-splitting, and lazy loading for routes or components.
  - Resolving or preventing dynamic module loading errors (chunk 404s during SPA rolling deployments).
  - Configuring CDN edge headers and HTTP caching policies (Cache-Control, immutable, ETag 304 with proper indexes).
  - Tuning containerized runtimes (GOMAXPROCS/automaxprocs, database connection pooling, concurrency).
  - Authoring complex queries or migrations with indexes (partial, functional, and CONCURRENTLY).
  - Implementing parallel queries via errgroup/Promise.all or Prometheus latency metrics without cardinality explosion.
license: Apache-2.0
metadata:
  version: v2.0
  author: clubedepontos
---

# Fullstack Performance & Resilience Playbook

Performance, resilience, and stability engineering practices for modern frontends, containerized APIs, and relational databases.

> **How to read this skill:** Each section first declares the **principle** (what must hold true and why) followed by an **example** in a concrete stack — Vue/Vite on the frontend, Go/Gin on the backend, PostgreSQL for the database. The principle is what transfers across projects; the example translates to the active stack.

---

## 1. SPA Rolling Deployment Resilience: Global Chunk Recovery

**Principle:** In a code-split SPA served via CDN, deploying a new release removes or invalidates the hashed asset chunks of the previous release. Users with the application already open encounter HTTP 404 errors when navigating to a lazy-loaded route or opening an asynchronous component. The application must detect this specific error and trigger a single page reload with a guard against infinite reload loops.

**Two capture points are strictly required** — covering only one leaves half of all failure modes unhandled:
1. **Router error hook** (`router.onError`): Catches route transitions to lazy-loaded page components.
2. **Bundler preload error hook** (`vite:preloadError`): Catches asynchronous child components (`defineAsyncComponent`, `React.lazy`) dynamically mounted inside an already active view — such as a modal dialog that fails upon opening. This case **does not** trigger router navigation hooks.

```javascript
const CHUNK_RELOAD_KEY = 'app:lazy_chunk_reload';

export function isLazyRouteChunkLoadError(error) {
  const message = error instanceof Error ? error.message : String(error ?? '');
  return (
    message.includes('Failed to fetch dynamically imported module') ||
    message.includes('Importing a module script failed') ||
    message.includes('error loading dynamically imported module') ||
    message.includes('Expected a JavaScript-or-Wasm module script')
  );
}

function triggerRecoveryReload(targetUrl) {
  const reloadTarget = targetUrl || window.location.href;
  const alreadyReloaded = sessionStorage.getItem(CHUNK_RELOAD_KEY) === reloadTarget;

  if (!alreadyReloaded) {
    sessionStorage.setItem(CHUNK_RELOAD_KEY, reloadTarget);
    window.location.assign(reloadTarget);
    return;
  }

  // Reload was already attempted once for this destination and failed again: do not loop.
  sessionStorage.removeItem(CHUNK_RELOAD_KEY);
  console.error('Persistent failure loading module after version update:', reloadTarget);
}

export function installLazyRouteChunkRecovery(router) {
  // 1. Bundler interceptor: covers route chunks AND async child components.
  window.addEventListener('vite:preloadError', (event) => {
    event.preventDefault();
    triggerRecoveryReload(window.location.href);
  });

  // 2. Router interceptor.
  if (router && typeof router.onError === 'function') {
    router.onError((error, to) => {
      if (!isLazyRouteChunkLoadError(error)) return;
      // Use fullPath instead of pathname to preserve target query parameters.
      const target = to?.fullPath || window.location.href;
      triggerRecoveryReload(target);
    });

    router.afterEach(() => {
      sessionStorage.removeItem(CHUNK_RELOAD_KEY);
    });
  }
}
```

Install during router initialization (`router/index.ts` or `main.ts`):
```javascript
import { installLazyRouteChunkRecovery } from './lazyRouteChunkRecovery';
installLazyRouteChunkRecovery(router);
```

Always cover `isLazyRouteChunkLoadError` with unit tests — error message strings can shift across browser engines and bundler releases, and automated tests are your safeguard against regressions.

---

## 2. Edge Caching Policy (CDN & HTTP Headers)

**Principle:** Assets fall into two distinct classes requiring opposing caching strategies:
* **Hashed static assets** (`Dashboard-a8f12.js`): The content is immutable for a given file name. Cache for 1 year with `immutable`.
* **Unhashed entrypoints** (`index.html`, `sw.js`, `manifest.webmanifest`, `robots.txt`, `sitemap.xml`): These serve as pointers to the current deployment version. They must be revalidated on every request, otherwise users remain locked to outdated entrypoints referencing nonexistent chunks — needlessly triggering chunk recovery.

**Declare explicit paths rather than relying on catch-all overrides.** Relying on a root `/(.*)` catch-all with `no-cache` overridden by `/assets/(.*)` depends on provider-specific precedence rules. Precedence semantics vary across CDNs, break easily upon reordering, and create subtle edge bugs. Explicitly enumerating entrypoint paths is more predictable.

*Vercel configuration example (`vercel.json`):*
```json
{
  "headers": [
    { "source": "/",           "headers": [{ "key": "Cache-Control", "value": "no-cache, no-store, must-revalidate" }] },
    { "source": "/index.html", "headers": [{ "key": "Cache-Control", "value": "no-cache, no-store, must-revalidate" }] },
    { "source": "/sw.js",      "headers": [{ "key": "Cache-Control", "value": "no-cache, no-store, must-revalidate" }] },
    { "source": "/manifest.webmanifest", "headers": [{ "key": "Cache-Control", "value": "no-cache, no-store, must-revalidate" }] },
    { "source": "/assets/(.*)", "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }] }
  ]
}
```

*Nginx equivalent:*
```nginx
location /assets/ { add_header Cache-Control "public, max-age=31536000, immutable"; }
location = /index.html { add_header Cache-Control "no-cache, no-store, must-revalidate"; }
location = /sw.js     { add_header Cache-Control "no-cache, no-store, must-revalidate"; }
```
On Cloudflare, configure Cache Rules by path; on AWS CloudFront, configure Cache Policies per behavior.

> ⚠️ **Avoid unnecessary Service Workers.** If the application has no genuine offline functional requirements, a Service Worker that merely caches static assets is redundant with HTTP caching (which is already optimal with immutable hashes) and introduces an extra invalidation layer to debug. Only register a Service Worker when offline operation is a required feature.

---

## 3. Containerized Runtime Optimization

### A. CPU Quota Alignment

**Principle:** Runtimes that size their internal thread pools or worker counts based on available CPU cores read the **host machine's** physical cores, not the container's cgroup CPU quota. In a container restricted to 1 vCPU running on a 64-core host, the runtime spawns 64 threads competing for CPU slices. The kernel cgroup applies CFS throttling, producing erratic high latency without visible CPU saturation in standard metrics.

*In Go:* Add an anonymous import that dynamically adjusts `GOMAXPROCS` to match the cgroup quota:
```go
import _ "go.uber.org/automaxprocs"
```
*In other runtimes:* Node.js respects container quotas for its main event loop but requires manual tuning of `UV_THREADPOOL_SIZE`; modern JVMs read cgroups automatically via `-XX:+UseContainerSupport` (default since JDK 10); Python with Gunicorn requires explicitly setting `workers` rather than deriving from `os.cpu_count()`.

### B. Database Connection Pool Sizing

**Principle:** Many database drivers default to unbounded connection pools. With multiple service replicas, the total connection count is `replicas × pool_size`. Relational databases like PostgreSQL allocate significant memory per active connection — easily exhausting backend resources without any actual traffic spike. Always size connection pools globally across all replicas.

```go
db.SetMaxOpenConns(20)                 // Per-replica ceiling: 20 × replica_count <= database max_connections
db.SetMaxIdleConns(10)                 // Warm idle connections to absorb traffic bursts
db.SetConnMaxLifetime(5 * time.Minute) // Periodically recycles connections to prevent stale proxies/zombies
db.SetConnMaxIdleTime(2 * time.Minute) // Releases idle connections to preserve database RAM
```
Equivalents: `pool_size` / `max_overflow` in SQLAlchemy, `max` / `idleTimeoutMillis` in Node `pg`, `maximumPoolSize` in HikariCP.

---

## 4. Parallel Independent Queries

**Principle:** Dashboard endpoints frequently aggregate multiple queries that have no mutual data dependencies. Executed sequentially, total endpoint latency is the sum of all queries; executed in parallel, latency equals the single slowest query. Parallel execution must propagate request context so that failure or client cancellation in one query immediately aborts the remaining running queries.

*In Go, utilizing `golang.org/x/sync/errgroup`:*
```go
g, gctx := errgroup.WithContext(ctx)

var (
    metrics StoreMetrics
    orders  []Order
)

g.Go(func() error {
    var err error
    // gctx: if another goroutine in the group fails, this database query is cancelled immediately.
    metrics, err = s.repo.GetMetrics(gctx, storeID)
    return err
})

g.Go(func() error {
    var err error
    orders, err = s.repo.GetRecentOrders(gctx, storeID)
    return err
})

if err := g.Wait(); err != nil {
    return nil, err
}
```
Equivalents: `Promise.all` with `AbortController` in Node.js/TypeScript, `asyncio.gather` with `TaskGroup` in Python, `CompletableFuture.allOf` on the JVM.

> ⚠️ **Connection Pool Impact:** Executing $N$ parallel queries per incoming HTTP request consumes $N$ simultaneous database connections. A dashboard firing 6 parallel queries under 20 concurrent requests will instantly saturate a connection pool of 20. Ensure pool sizes and query concurrency are balanced.

---

## 5. HTTP Conditional Caching via ETag (`304 Not Modified`)

**Principle:** For high-frequency polling endpoints (e.g., auto-refreshing schedules, notification badges), compute a lightweight query fingerprint first. If the computed fingerprint matches the client's `If-None-Match` header, respond immediately with `304 Not Modified` without executing the full heavy query, instantiating domain models, or serializing JSON payloads.

> ⚠️ **Database Index Requirement:** The fingerprint query requires a composite index covering filters and timestamp ordering, e.g., `(store_id, updated_at DESC)`. Without this index, `MAX(updated_at)` performs a full sequential scan on every polling interval — making the "optimization" more expensive than the original query.

**Fingerprint Query:**
```sql
SELECT COUNT(*), COALESCE(MAX(updated_at), '1970-01-01'::timestamptz)
FROM appointments
WHERE store_id = $1;
```

### ⚠️ The ETag Must Include All Response Discriminators

A critical pitfall is generating the ETag solely from `count` and `max_updated_at`. Those two metrics are **identical across different pagination offsets and filter parameters for the same dataset** — causing the server to return 304 when the client requests page 2, leaving the user viewing page 1 data.

The ETag key must concatenate the revision fingerprint **plus** every parameter that discriminates the response payload (view mode, limit, offset, active filters):

```go
func buildAppointmentListETag(viewKey string, f Filters, rev Revision) string {
    return fmt.Sprintf(
        `W/"appt-list-v=%s-lim=%d-off=%d-c=%d-m=%d"`,
        viewKey, f.Limit, f.Offset, rev.Count, rev.MaxUpdatedAt.UTC().UnixNano(),
    )
}
```

### ⚠️ `If-None-Match` Is a List, Not a Single Scalar

HTTP specifications allow clients and proxies to provide comma-separated validator lists or `*`. Direct equality comparison (`==`) causes 304 responses to fail silently in these scenarios.

```go
func ifNoneMatchMatches(ifNoneMatch, etag string) bool {
    if ifNoneMatch == "" || etag == "" {
        return false
    }
    if ifNoneMatch == "*" {
        return true
    }
    for _, part := range strings.Split(ifNoneMatch, ",") {
        if strings.TrimSpace(part) == etag {
            return true
        }
    }
    return false
}
```

**Handler Implementation:**
```go
etag := buildAppointmentListETag(viewKey, filters, rev)
c.Header("ETag", etag)
c.Header("Cache-Control", "private, must-revalidate")

if ifNoneMatchMatches(c.GetHeader("If-None-Match"), etag) {
    c.Status(http.StatusNotModified)
    return
}

data, err := h.service.GetAppointments(c.Request.Context(), filters)
// ...
c.JSON(http.StatusOK, data)
```

> **When NOT to use this pattern:** Computing a prior fingerprint incurs an extra database query: on a cache miss, 2 queries execute instead of 1. This pattern is only beneficial when the cache hit ratio is high (periodic background polling on slowly changing data). For user-navigated listings or rapidly changing datasets, execute the single query and derive the ETag from the retrieved payload.

---

## 6. Strategic Indexing (PostgreSQL Example)

### A. `CONCURRENTLY` on Production Databases

**Principle:** Standard `CREATE INDEX` acquires an exclusive `SHARE` lock on the target table, blocking all concurrent write operations for the duration of the build. On active production tables, this causes downtime. `CONCURRENTLY` builds the index without blocking writes.

> ⚠️ **`CREATE INDEX CONCURRENTLY` cannot run inside a transaction block** — yet most database migration runners wrap each migration file in a transaction by default. Unless explicitly disabled, the migration fails with: `CREATE INDEX CONCURRENTLY cannot run inside a transaction block`.

*Using goose:*
```sql
-- +goose Up
-- +goose NO TRANSACTION

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_active_email
  ON users (email)
  WHERE active = true;

-- +goose Down
DROP INDEX CONCURRENTLY IF EXISTS idx_users_active_email;
```
*Equivalents:* `disable_ddl_transaction!` in Ruby on Rails; `atomic = False` in Django migrations; `transaction := false` in golang-migrate; Flyway requires migrations using `CONCURRENTLY` to be configured as non-transactional.

> A failed `CONCURRENTLY` build leaves an **invalid** index on the table, consuming disk space while remaining unused by the query planner. Clean up failed indexes before retrying: `SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;`.

### B. Partial Indexes (`WHERE ...`)
Index only the specific subset of rows frequently queried. Partial indexes remain smaller, fit in memory buffers, and reduce write overhead.
```sql
-- Index only appointments from guest/unregistered users
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_appointments_guest_phone
  ON appointments (customer_phone)
  WHERE customer_user_id IS NULL;
```
The query planner only utilizes a partial index if the query's `WHERE` clause logically implies the index predicate.

### C. Functional / Expression Indexes
Accelerate searches over normalized values without adding redundant table columns. The indexed expression must be strictly `IMMUTABLE`.
```sql
-- Search users by digits-only phone numbers ignoring formatting
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_phone_digits
  ON users (regexp_replace(phone, '\D', '', 'g'))
  WHERE phone IS NOT NULL;
```
The querying SQL statement must reproduce the exact expression used in the index definition for the planner to utilize it.

---

## 7. Latency Observability Without Cardinality Explosion

**Principle:** Every unique combination of label values in a Prometheus histogram instantiates a new time series. Using raw URL paths (`/stores/9a8b7c/appointments`) as metric labels creates a time series for every UUID — causing memory consumption to grow linearly with database records until the metrics server runs out of memory. Always record the **route template**, never the parameterized raw path.

```go
// In Gin, c.FullPath() returns the parameterized route template: "/stores/:store_id/appointments"
path := c.FullPath()
if path == "" {
    path = "unmatched" // Unmatched 404 requests must not generate unbounded arbitrary labels
}

httpRequestDuration.WithLabelValues(c.Request.Method, path, statusStr).Observe(duration.Seconds())
```
Equivalents: `req.route.path` in Express, `request.url_rule.rule` in Flask, `route.path_format` in FastAPI/Starlette.

> The `"unmatched"` fallback is essential: without it, requests to non-existent endpoints (including vulnerability scanners and bot probes hitting random URLs) generate unbounded label cardinality — exposing an external memory exhaustion attack vector.
