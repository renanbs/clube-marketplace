# Container Runtime Tuning & Concurrency

Technical guide for container CPU quota alignment, database connection pool sizing across replicas, parallel independent query execution with context cancellation, and Prometheus metric cardinality protection.

---

## 1. Mandatory Principles

1. **cgroup CPU Quota Alignment:** In containerized environments (Kubernetes, ECS, Docker), runtimes often inspect the **host's** physical CPU cores rather than the container's cgroup CPU quota. This causes thread pool over-allocation and severe kernel CFS throttling.
2. **Replica-Aware Connection Pool Sizing:** Total database connections equal `replicas × max_connections_per_replica`. Relational databases allocate substantial RAM per connection. Size connection pools globally across all horizontal replicas.
3. **Context-Aware Parallel Queries:** Execute independent queries in parallel using concurrency groups (`errgroup` in Go, `Promise.all` with `AbortController` in JS/TS, `asyncio.gather` with `TaskGroup` in Python). Failure in one query must immediately cancel sibling queries.
4. **Zero Metric Label Cardinality Explosion:** Never record unbounded dynamic values (UUIDs, raw URLs, emails) in Prometheus histogram labels. Always map paths to parameterized route templates (`/stores/:id/items`).

---

## 2. Runtime CPU Quota Tuning

### Go (automaxprocs)
Add an anonymous import in `main.go` to automatically adjust `GOMAXPROCS` to match the container's CPU quota:
```go
package main

import (
	_ "go.uber.org/automaxprocs"
)
```

### Node.js / Bun
Set `UV_THREADPOOL_SIZE` equal to the assigned container vCPU count (or `4` for light I/O):
```bash
export UV_THREADPOOL_SIZE=4
export NODE_OPTIONS="--max-old-space-size=1536"
```

### Python / Gunicorn
Explicitly calculate worker count from container quotas, not `os.cpu_count()`:
```python
# gunicorn.conf.py
import os

cpu_limit = float(os.getenv("CONTAINER_CPU_LIMIT", "2"))
workers = max(int(cpu_limit * 2) + 1, 2)
```

---

## 3. Database Connection Pool Sizing (Go Example)

```go
package db

import (
	"database/sql"
	"time"
)

func ConfigurePool(db *sql.DB, replicaCount int, maxDbConns int) {
	// Allocate fair share per replica, reserving headroom for migrations
	connsPerReplica := (maxDbConns - 10) / replicaCount
	if connsPerReplica < 5 {
		connsPerReplica = 5
	}

	db.SetMaxOpenConns(connsPerReplica)
	db.SetMaxIdleConns(connsPerReplica / 2)
	db.SetConnMaxLifetime(5 * time.Minute) // Cycle connections to drop dead TCP proxies
	db.SetConnMaxIdleTime(2 * time.Minute) // Free idle memory during low traffic
}
```

---

## 4. Parallel Queries with Context Cancellation (Go `errgroup`)

```go
package service

import (
	"context"
	"golang.org/x/sync/errgroup"
)

type DashboardData struct {
	Metrics StoreMetrics
	Orders  []Order
}

func (s *DashboardService) GetDashboard(ctx context.Context, storeID string) (*DashboardData, error) {
	g, gctx := errgroup.WithContext(ctx)

	var (
		metrics StoreMetrics
		orders  []Order
	)

	// 1. Fetch metrics
	g.Go(func() error {
		var err error
		metrics, err = s.repo.GetMetrics(gctx, storeID)
		return err
	})

	// 2. Fetch recent orders
	g.Go(func() error {
		var err error
		orders, err = s.repo.GetRecentOrders(gctx, storeID)
		return err
	})

	if err := g.Wait(); err != nil {
		return nil, err
	}

	return &DashboardData{Metrics: metrics, Orders: orders}, nil
}
```

---

## 5. Metric Label Cardinality Protection (Go / Gin)

```go
package middleware

import (
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus"
)

var httpRequestDuration = prometheus.NewHistogramVec(
	prometheus.HistogramOpts{
		Name: "http_request_duration_seconds",
		Help: "Duration of HTTP requests in seconds.",
	},
	[]string{"method", "route", "status"},
)

func MetricsMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		c.Next()

		duration := time.Since(start)
		
		// Use c.FullPath() to obtain the route template ("/stores/:id"), never c.Request.URL.Path
		route := c.FullPath()
		if route == "" {
			route = "unmatched" // Prevent external bot scans from exploding cardinality
		}

		status := strconv.Itoa(c.Writer.Status())
		httpRequestDuration.WithLabelValues(c.Request.Method, route, status).Observe(duration.Seconds())
	}
}
```

---

## 6. Cross-References

- [Database Indexing & Queries](db-indexing-queries.md) — Indexing and query planning.
- [Back to Fullstack Performance Skill](../SKILL.md)
