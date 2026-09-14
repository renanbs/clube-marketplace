# Database Indexing, Query Optimization & ETag Caching

Technical guide for strategic PostgreSQL indexing (`CONCURRENTLY`, partial, functional), non-transactional migrations, query planning (`EXPLAIN ANALYZE`), zero `SELECT *` discipline, and conditional `ETag 304` query fingerprinting.

---

## 1. Mandatory Principles

1. **`CREATE INDEX CONCURRENTLY` in Production:** Standard index creation locks tables against writes. Always use `CONCURRENTLY` on live production databases.
2. **Non-Transactional Migrations for Concurrently:** `CREATE INDEX CONCURRENTLY` cannot run inside a transaction block. Migration tools must disable transaction wrapping for these files (e.g. `-- +goose NO TRANSACTION`).
3. **Partial & Expression Indexing:** Index only frequently filtered subsets (`WHERE active = true`) and deterministic immutable expressions (`regexp_replace(phone, '\D', '', 'g')`).
4. **Zero `SELECT *` in Persistence:** Explicitly name queried columns in SQL and ORM queries. Prevents unnecessary byte transmission, avoids invalidating covering indexes, and prevents unintended data leaks.
5. **Conditional HTTP `ETag` (304 Not Modified):** For high-frequency polling endpoints, compute a lightweight indexed query fingerprint (`COUNT(*)`, `MAX(updated_at)`). Return `304 Not Modified` if the client's `If-None-Match` header matches.

---

## 2. PostgreSQL Migration DDL Examples

### Non-Transactional Index Migration (Goose SQL format)
```sql
-- +goose Up
-- +goose NO TRANSACTION

-- 1. Partial index for active users
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_active_email
  ON users (email)
  WHERE active = true;

-- 2. Expression index for normalized phone lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_phone_digits
  ON users (regexp_replace(phone, '\D', '', 'g'))
  WHERE phone IS NOT NULL;

-- +goose Down
-- +goose NO TRANSACTION
DROP INDEX CONCURRENTLY IF EXISTS idx_users_active_email;
DROP INDEX CONCURRENTLY IF EXISTS idx_users_phone_digits;
```

---

## 3. High-Frequency Polling ETag Pattern (Go)

```go
package handler

import (
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

type ListRevision struct {
	Count        int64
	MaxUpdatedAt time.Time
}

func buildListETag(viewKey string, limit, offset int, rev ListRevision) string {
	return fmt.Sprintf(
		`W/"view=%s-lim=%d-off=%d-c=%d-m=%d"`,
		viewKey, limit, offset, rev.Count, rev.MaxUpdatedAt.UTC().UnixNano(),
	)
}

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

func (h *AppointmentHandler) ListAppointments(c *gin.Context) {
	storeID := c.Param("store_id")

	// 1. Lightweight fingerprint query backed by composite index (store_id, updated_at DESC)
	rev, err := h.repo.GetAppointmentsRevision(c.Request.Context(), storeID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to check revision"})
		return
	}

	etag := buildListETag("appointments", 50, 0, rev)
	c.Header("ETag", etag)
	c.Header("Cache-Control", "private, must-revalidate")

	if ifNoneMatchMatches(c.GetHeader("If-None-Match"), etag) {
		c.Status(http.StatusNotModified)
		return
	}

	// 2. Fetch full heavy dataset only on cache miss
	items, err := h.repo.ListAppointments(c.Request.Context(), storeID, 50, 0)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to list items"})
		return
	}

	c.JSON(http.StatusOK, items)
}
```

---

## 4. Edge Cases & Common Traps

- ⚠️ **Invalid Indexes from Failed Builds:** If `CREATE INDEX CONCURRENTLY` is interrupted or fails due to duplicate key violations, PostgreSQL leaves an **invalid** index on the table. Query invalid indexes with `SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;` and drop them before retrying.
- ⚠️ **Fingerprint Index Requirement:** The fingerprint query (`COUNT(*)`, `MAX(updated_at)`) MUST be backed by a covering composite index `(store_id, updated_at DESC)`. Otherwise, `MAX(updated_at)` performs a full table sequential scan, making the fingerprint check slower than the main query.

---

## 5. Cross-References

- [Runtime Tuning & Concurrency](runtime-tuning.md) — Database connection pool sizing.
- [Back to Fullstack Performance Skill](../SKILL.md)
