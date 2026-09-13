# SPA Rolling Deployment Resilience: Global Chunk Recovery

Technical guide for handling dynamic module loading errors (chunk 404s) during SPA rolling deployments, trapping router and bundler events, and guarding against infinite reload loops.

---

## 1. Mandatory Principles

1. **Dual Interception Points:** In code-split SPAs, releasing a new deployment removes or re-hashes old asset chunks on the CDN. Users on active sessions encounter 404s on route transitions OR when opening lazy child components (modals, tabs). You MUST trap:
   - **Router error hook** (`router.onError` in Vue Router, Next.js route change errors, SvelteKit error handlers).
   - **Bundler preload hook** (`vite:preloadError` in Vite, `__webpack_chunk_load__` rejection handlers).
2. **Reload-Loop Prevention Guard:** Automatic recovery must reload the current URL to fetch the new `index.html` with updated chunk hashes, but MUST record the target in `sessionStorage` to prevent infinite reload loops if the chunk is permanently broken.
3. **Query Parameter Preservation:** Use `to.fullPath` or `window.location.href` to avoid dropping query parameters and filters during the recovery reload.

---

## 2. Production Chunk Recovery Implementation (Vite + Vue Router / React / Vanilla)

```typescript
const CHUNK_RELOAD_KEY = 'app:lazy_chunk_reload';

/**
 * Detects whether an error is a dynamic module fetch failure across browser engines.
 */
export function isLazyRouteChunkLoadError(error: unknown): boolean {
  const message = error instanceof Error ? error.message : String(error ?? '');
  return (
    message.includes('Failed to fetch dynamically imported module') ||
    message.includes('Importing a module script failed') ||
    message.includes('error loading dynamically imported module') ||
    message.includes('Expected a JavaScript-or-Wasm module script') ||
    message.includes('Loading chunk') ||
    message.includes('Loading CSS chunk')
  );
}

function triggerRecoveryReload(targetUrl?: string): void {
  if (typeof window === 'undefined') return;
  const reloadTarget = targetUrl || window.location.href;
  const alreadyReloaded = sessionStorage.getItem(CHUNK_RELOAD_KEY) === reloadTarget;

  if (!alreadyReloaded) {
    sessionStorage.setItem(CHUNK_RELOAD_KEY, reloadTarget);
    window.location.assign(reloadTarget);
    return;
  }

  // Reload was already attempted once for this destination and failed again: do not loop.
  sessionStorage.removeItem(CHUNK_RELOAD_KEY);
  console.error('Persistent failure loading module after deployment update:', reloadTarget);
}

/**
 * Installs global error listeners on the bundler and router.
 */
export function installLazyRouteChunkRecovery(router?: { onError: (cb: (err: any, to: any) => void) => void; afterEach: (cb: () => void) => void }): void {
  if (typeof window === 'undefined') return;

  // 1. Bundler interceptor: covers route chunks AND async child components (modals, dialogs)
  window.addEventListener('vite:preloadError', (event: Event) => {
    event.preventDefault();
    triggerRecoveryReload(window.location.href);
  });

  // 2. Router interceptor
  if (router && typeof router.onError === 'function') {
    router.onError((error: any, to: any) => {
      if (!isLazyRouteChunkLoadError(error)) return;
      const target = to?.fullPath || window.location.href;
      triggerRecoveryReload(target);
    });

    if (typeof router.afterEach === 'function') {
      router.afterEach(() => {
        sessionStorage.removeItem(CHUNK_RELOAD_KEY);
      });
    }
  }
}
```

---

## 3. Webpack & Next.js Chunk Recovery Equivalents

### Webpack / Create React App / Custom React
```typescript
window.addEventListener('error', (event) => {
  if (isLazyRouteChunkLoadError(event.error)) {
    event.preventDefault();
    triggerRecoveryReload(window.location.href);
  }
});
```

### Next.js Pages / App Router
```typescript
import Router from 'next/router';

Router.events?.on('routeChangeError', (err, url) => {
  if (isLazyRouteChunkLoadError(err)) {
    triggerRecoveryReload(url);
  }
});
```

---

## 4. Edge Cases & Unit Testing

- ⚠️ **Unit Test String Signatures:** Ensure unit tests verify `isLazyRouteChunkLoadError` against Chrome, Firefox, Safari, and Webpack error string variations.
- ⚠️ **Preserve Auth Tokens:** Do not clear `localStorage` auth tokens during chunk recovery reloads; only clear the transient `CHUNK_RELOAD_KEY` in `sessionStorage`.

---

## 5. Cross-References

- [Edge Caching & Headers](caching-edge-headers.md) — HTTP caching policies preventing stale entrypoints.
- [Back to Fullstack Performance Skill](../SKILL.md)
