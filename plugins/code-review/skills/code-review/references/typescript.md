# TypeScript — Code Review Reference

Language-specific review rules for TypeScript codebases. Loaded on demand when `.ts`, `.tsx`, `.mts`, or `.cts` files appear in the diff.

---

## 1. Type Safety & Strict Mode

- **`strict: true` in `tsconfig.json` is non-negotiable.** PRs disabling `strictNullChecks`, `noImplicitAny`, or `strictFunctionTypes` are HIGH.
- **No `any`.** Use `unknown` when the type is genuinely unknown, then narrow. `any` disables the compiler — every `any` must justify itself with a comment. Unjustified `any` is MEDIUM.
- **No `@ts-ignore` / `@ts-expect-error` without explanation.** If suppressing, the comment must state why and link a tracking issue.
- **No non-null assertion (`!`) on uncertain values.** `user!.name` is a runtime crash waiting to happen. Narrow with `if`, optional chaining, or a guard.
- **Prefer discriminated unions over boolean flags.** `type State = { status: 'loading' } | { status: 'ok'; data: T } | { status: 'error'; error: Error }` over `{ loading: boolean; data?: T; error?: Error }`.

---

## 2. Async & Promises

- **No floating promises.** Every `async` call must be `await`ed, returned, or explicitly voided with `void promise` and a comment explaining why. Unhandled rejections crash Node and silently fail in browsers.
- **No `async` on a function that doesn't `await`.** Wrapping a synchronous return in a promise adds overhead and misleads readers.
- **Error handling in `async`.** `try/catch` around `await`, or `.catch()` on the promise. Unhandled errors in `Promise.all` abort the entire batch — use `Promise.allSettled` when partial failure is acceptable.
- **No `await` inside loops when parallelizable.** `for (const x of items) { await fetch(x) }` is N sequential round-trips. Use `Promise.all(items.map(...))` unless ordering or rate-limiting requires serial execution.
- **AbortController for cancellable fetches.** Long-running requests without abort signals leak connections and ignore component unmounts.

---

## 3. React Patterns (when applicable)

- **Hooks rules.** No hooks inside conditions, loops, or nested functions. Violations are CRITICAL (runtime crash on re-render).
- **Dependency arrays.** Missing deps in `useEffect`/`useMemo`/`useCallback` cause stale closures (HIGH). Suppressing the lint rule with `// eslint-disable` requires justification.
- **No inline object/array/function literals in JSX props.** `<Comp style={{ color: 'red' }} />` creates a new reference every render, defeating `React.memo`. Extract to constants, `useMemo`, or module-level.
- **Keys in lists.** Array index as key is MEDIUM when the list is reordered, filtered, or items are added/removed. Use a stable unique identifier.
- **No direct DOM manipulation.** `document.getElementById` inside a React component bypasses the virtual DOM. Use `useRef`.
- **Component size.** Components over ~150 lines or with more than 3 responsibilities should be decomposed.

---

## 4. Vue Patterns (when applicable)

- **`<script setup>` with TypeScript.** New components should use `<script setup lang="ts">`. Options API only when extending legacy.
- **Typed refs.** `ref<string>('')` not bare `ref('')`. Template refs: `ref<HTMLInputElement | null>(null)`.
- **Reactive destructuring.** `const { x } = reactive(obj)` loses reactivity. Use `toRefs()` or access `obj.x` directly.
- **`v-for` keys.** Same rules as React keys — stable unique identifier, not array index for dynamic lists.
- **Composable return types.** Composables (`use*`) should return typed objects, not tuples. Explicit return type annotation for public composables.

---

## 5. Module & Bundle Safety

- **No side effects at import time.** Top-level code that mutates global state, starts timers, or fetches data breaks tree-shaking and causes surprises in tests.
- **Barrel files (`index.ts`) with caution.** Re-exporting everything defeats tree-shaking in some bundlers. Only re-export the public API.
- **Dynamic imports for heavy deps.** Libraries >50KB gzipped should be `import()`ed lazily on the code path that uses them.
- **No secrets in client code.** API keys, tokens, or internal URLs in client-side code are CRITICAL. Use environment variables resolved at build time with `VITE_`/`NEXT_PUBLIC_` prefix, and only for public-facing keys.

---

## 6. Error Handling

- **Typed error responses.** API call error handling should discriminate between network errors, 4xx, and 5xx — not a single `catch` that shows "Something went wrong".
- **Error boundaries (React).** Pages/routes should have error boundaries. A thrown error in a child should not white-screen the entire app.
- **Global unhandled rejection handler.** `window.addEventListener('unhandledrejection', ...)` with telemetry reporting.
- **Zod/Valibot at API boundaries.** External data (API responses, URL params, form inputs) should be validated at the boundary with a schema validator, not trusted as `T`.

---

## 7. Common Traps

- ⚠️ **`===` vs `==`.** Always `===` and `!==`. Loose equality with coercion is a correctness trap.
- ⚠️ **Optional chaining + nullish coalescing.** `user?.address?.city ?? 'Unknown'` — but beware: `??` only catches `null`/`undefined`, not `''` or `0`. Use `||` only when falsy fallback is intended.
- ⚠️ **Enums at runtime.** TypeScript `enum` emits JavaScript objects. Prefer `as const` objects + `typeof` for zero-runtime overhead: `const Status = { Active: 'active', Inactive: 'inactive' } as const`.
- ⚠️ **`Array.prototype.sort` mutates.** `arr.sort()` modifies the original array. Use `[...arr].sort()` or `arr.toSorted()` (ES2023+) to avoid side effects.
- ⚠️ **`JSON.parse` returns `any`.** Always validate or cast the result: `const data: unknown = JSON.parse(raw)` then narrow.

---

## Cross-References

- [Back to Code Review Core](../SKILL.md)
- [Go Review Rules](go.md)
- [Rust Review Rules](rust.md)
