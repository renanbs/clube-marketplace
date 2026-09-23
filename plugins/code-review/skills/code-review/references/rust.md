# Rust — Code Review Reference

Language-specific review rules for Rust codebases. Loaded on demand when `.rs` files or `Cargo.toml` appear in the diff.

---

## 1. Ownership & Borrowing

- **Unnecessary clones.** `.clone()` on types that could be borrowed is MEDIUM. Each clone is a heap allocation. Ask: can this function take `&T` or `&str` instead of `T` or `String`?
- **Owned strings in function parameters.** `fn process(name: String)` forces callers to give up ownership or clone. Prefer `fn process(name: &str)` unless the function genuinely needs to store the owned value.
- **`Cow<'_, str>` for conditional ownership.** When a function sometimes needs to allocate and sometimes can borrow, `Cow` avoids unnecessary clones.
- **Avoid `Rc`/`Arc` as a reflex.** Reference counting has runtime cost. Restructure ownership first; reach for `Rc`/`Arc` only when shared ownership is genuinely required (graph structures, multi-threaded access).

---

## 2. Lifetime Annotations

- **Elision is preferred when unambiguous.** Don't annotate lifetimes the compiler can infer. Unnecessary `'a` annotations add noise.
- **Named lifetimes must be meaningful.** `'conn`, `'query`, `'input` over `'a`, `'b`, `'c` when multiple lifetimes coexist.
- **`'static` bounds sparingly.** `T: 'static` means the type contains no non-static references — it doesn't mean "lives forever". But requiring `'static` on trait objects that don't need it is overly restrictive (MEDIUM).
- **Lifetime in return types.** If a function returns a reference, the lifetime must tie to an input. Returning a reference to a local is a compile error, but returning a reference through complex indirection can hide bugs.

---

## 3. Error Handling

- **No `.unwrap()` / `.expect()` in library code.** Panics in libraries are CRITICAL — callers can't recover. Use `?` with a proper error type.
- **`.unwrap()` in `main()` or tests is acceptable** with a comment justifying why the value is guaranteed to be `Some`/`Ok`.
- **Custom error types with `thiserror`.** Library crates should define domain error enums. Use `#[from]` for automatic conversion from underlying errors.
- **`anyhow` for applications, `thiserror` for libraries.** `anyhow::Result` in a library crate forces callers into dynamic dispatch — MEDIUM.
- **Match all error variants.** `_ => ...` catch-all on error enums hides new variants added by dependencies. Use explicit matching unless the enum is `#[non_exhaustive]`.

---

## 4. Unsafe Audit

- **Every `unsafe` block must have a `// SAFETY:` comment.** The comment must state the invariant that makes the operation sound. Missing safety comments are HIGH.
- **Minimize unsafe scope.** The `unsafe` block should contain only the operation that requires it, not entire function bodies.
- **No raw pointer arithmetic without bounds checking.** Pointer offsets past allocation bounds are undefined behavior (CRITICAL).
- **FFI boundaries.** `extern "C"` functions are inherently unsafe at the boundary. Validate all inputs before passing to C code. Null pointers, dangling pointers, and buffer overflows are the caller's responsibility.
- **`unsafe impl Send/Sync`** must be justified. Incorrect `Send`/`Sync` implementations cause data races that Rust's type system would normally prevent (CRITICAL).

---

## 5. Performance & Allocation

- **`String` vs `&str` in struct fields.** If the struct borrows data with a known lifetime, `&'a str` avoids allocation. If it owns data, `String` or `Box<str>` (for immutable owned strings with less overhead).
- **`Vec::with_capacity` when size is known.** Pre-allocating avoids repeated reallocations. `Vec::new()` + loop of `.push()` with known count is MEDIUM.
- **Iterators over indexed loops.** `.iter().map().filter().collect()` is idiomatic and often optimized better than `for i in 0..len { vec[i] }`.
- **Avoid `collect()` into intermediate `Vec` when chaining.** `items.iter().map(f).collect::<Vec<_>>().iter().filter(g)` — skip the intermediate collection: `items.iter().map(f).filter(g)`.
- **`Box<dyn Trait>` vs generics.** Dynamic dispatch has indirection cost. Use generics (`impl Trait` or `<T: Trait>`) for hot paths. `Box<dyn Trait>` is fine for plugin systems, heterogeneous collections, or when binary size matters.

---

## 6. Concurrency

- **`Arc<Mutex<T>>` is often a sign of over-sharing.** Consider restructuring so each thread owns its data. Use channels (`mpsc`, `crossbeam`) for communication.
- **`Mutex` poisoning.** After a panic, `Mutex::lock()` returns `Err`. Decide on a policy: `.lock().unwrap()` (crash) or `.lock().unwrap_or_else(|e| e.into_inner())` (recover). The choice must be deliberate, not accidental.
- **`tokio::spawn` requires `'static + Send`.** Data moved into a spawned task must be owned. Accidentally capturing a reference is a compile error, but capturing a large clone is a performance trap.
- **Blocking in async context.** `std::fs`, `std::thread::sleep`, or CPU-heavy computation inside an async function blocks the executor. Use `tokio::fs`, `tokio::time::sleep`, or `spawn_blocking`.
- **Select fairness.** `tokio::select!` is pseudo-random among ready branches. If one branch is always ready, others starve. Use `biased;` only when intentional.

---

## 7. Common Traps

- ⚠️ **`to_string()` vs `to_owned()` vs `into()`.** For `&str → String`: all three work, but `to_owned()` is most idiomatic. `to_string()` goes through `Display` formatting (marginal overhead). `into()` is generic and can be ambiguous.
- ⚠️ **`impl Into<String>` parameters.** `fn new(name: impl Into<String>)` is ergonomic but hides the conversion cost from callers and complicates trait objects. Use for builder APIs, not hot paths.
- ⚠️ **Derive order matters for `PartialOrd`.** `#[derive(PartialOrd)]` compares fields in declaration order. Reordering struct fields silently changes sort behavior.
- ⚠️ **`drop` is not `defer`.** `drop(guard)` releases early, but `Drop::drop` is called in reverse declaration order at scope end. Relying on drop order for correctness (e.g., lock ordering) is fragile.
- ⚠️ **Cargo features are additive.** A feature that disables functionality violates Cargo's feature model. Features should only add capabilities. `default-features = false` in dependencies must be intentional.

---

## Cross-References

- [Back to Code Review Core](../SKILL.md)
- [Go Review Rules](go.md)
- [TypeScript Review Rules](typescript.md)
