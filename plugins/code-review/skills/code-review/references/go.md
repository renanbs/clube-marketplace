# Go — Code Review Reference

Language-specific review rules for Go codebases. Loaded on demand when `.go` files appear in the diff.

---

## 1. Error Handling

- **Every error must be handled.** `_ = fn()` on an error-returning function is a finding (HIGH) unless explicitly justified with a comment.
- **Wrap with context.** Bare `return err` loses call-site context. Use `fmt.Errorf("operation: %w", err)` to preserve the chain.
- **Never `log.Fatal` / `os.Exit` in library code.** Fatal exits belong only in `main()` or CLI entrypoints.
- **Sentinel errors use `errors.New` at package level.** Check with `errors.Is()`, not string comparison.
- **Custom error types implement `Error()` and unwrap.** If wrapping, implement `Unwrap() error`.

---

## 2. Concurrency Safety

- **Goroutine lifecycle.** Every `go func()` must have a clear shutdown path. Look for: context cancellation, `sync.WaitGroup`, or channel signaling. Orphaned goroutines are HIGH.
- **Shared state.** Mutable state accessed from multiple goroutines needs explicit synchronization (`sync.Mutex`, `sync.RWMutex`, atomic, or channel). Race conditions are CRITICAL.
- **Channel direction.** Function signatures should declare `chan<-` or `<-chan` when the function only sends or receives.
- **`sync.Once` for initialization.** Lazy singletons without `sync.Once` race on first access.
- **Context propagation.** Functions doing I/O or calling downstream services must accept `context.Context` as the first parameter. Bare `context.Background()` deep in the call stack is a smell.

---

## 3. Interface Design

- **Accept interfaces, return structs.** Concrete return types give callers full access; interface parameters give callers flexibility.
- **Small interfaces.** Prefer 1–3 method interfaces. The `io.Reader` / `io.Writer` pattern over monolith interfaces.
- **Define interfaces at the consumer, not the implementor.** Avoids import cycles and unnecessary coupling.
- **No interface pollution.** If only one implementation exists and no testing boundary is needed, a concrete type is simpler.

---

## 4. Database & sqlx Patterns

- **Named query constants.** SQL lives in `const` blocks, never inline string literals scattered across functions.
- **Zero `SELECT *`.** Enumerate columns explicitly. Schema changes silently break `SELECT *` scans.
- **Parameterized queries only.** `$1`/`:param` placeholders. String concatenation into SQL is CRITICAL (injection).
- **`sql.Null*` / `null.*` for nullable columns.** Scanning nullable columns into non-pointer types panics or silently zeroes.
- **Connection pool tuning.** `SetMaxOpenConns`, `SetMaxIdleConns`, `SetConnMaxLifetime` must be set explicitly — defaults are unbounded or zero, causing connection exhaustion.

---

## 5. Code Organization & Style

- **Package naming.** Lowercase, single-word, no underscores. `package httputil` not `package http_util`.
- **Exported names.** Exported functions, types, and constants must have doc comments starting with the name.
- **No `init()` side effects.** `init()` should register, not execute I/O, open connections, or panic.
- **Avoid `any` / `interface{}` in public APIs.** Generics (`[T any]`) are preferred when the type set is bounded.
- **Struct field ordering.** Group by purpose, not alphabetically. Consider memory alignment for hot structs.

---

## 6. Testing

- **Table-driven tests.** Use `[]struct{ name string; ... }` with `t.Run(tc.name, ...)` for parameterized cases.
- **`testify` assertions if already in the project.** Don't introduce `testify` into a project using stdlib `testing` only.
- **`t.Helper()` in test helpers.** Ensures error line numbers point to the caller, not the helper.
- **No sleeping.** Use channels, `sync.WaitGroup`, or `time.After` in `select`. Flaky `time.Sleep` in tests is MEDIUM.
- **`t.Parallel()` where safe.** Tests that don't share mutable state should opt in.

---

## 7. Common Traps

- ⚠️ **Loop variable capture in goroutines.** Pre-Go 1.22: `go func() { use(v) }()` captures the loop variable by reference. Fix: `go func(v T) { use(v) }(v)`. Go 1.22+ fixes this, but flag if the module targets earlier versions.
- ⚠️ **Deferred close on writable files.** `defer f.Close()` discards the error on `Close()`. For writes, check: `if err := f.Close(); err != nil { ... }`.
- ⚠️ **Slice append aliasing.** Appending to a slice received as a parameter may mutate the caller's underlying array if capacity allows. Copy first if the slice is shared.
- ⚠️ **`http.DefaultClient` has no timeout.** Always create `&http.Client{Timeout: ...}`. Unbounded requests hang goroutines.

---

## Cross-References

- [Back to Code Review Core](../SKILL.md)
- [TypeScript Review Rules](typescript.md)
- [Rust Review Rules](rust.md)
