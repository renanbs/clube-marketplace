---
name: fullstack-performance-resilience
description: |
  Especialista em performance fullstack, otimização de runtime, resiliência de deploys e tuning de banco de dados.
  Agnóstica de provedor e de stack: cada seção declara o princípio e depois exemplifica numa linguagem concreta.
  Ative esta skill sempre que:
  - Configurar builds de frontend (Vite, Astro, Rollup, Webpack), code-splitting e lazy loading de rotas ou componentes.
  - Resolver ou prevenir erros de carregamento de módulos dinâmicos (chunks 404 em deploys de SPAs).
  - Configurar headers de CDN e políticas de cache HTTP (Cache-Control, immutable, ETag 304 com índices adequados).
  - Otimizar serviços em containers (GOMAXPROCS, pools de banco, concorrência).
  - Escrever consultas complexas ou criar migrations com índices (índices parciais, funcionais e CONCURRENTLY).
  - Implementar paralelismo com errgroup ou métricas de latência com Prometheus sem explosão de cardinalidade.
license: Apache-2.0
metadata:
  version: v2.0
  author: clubedepontos
---

# Fullstack Performance & Resilience Playbook

Práticas de desempenho, resiliência e estabilidade para frontends modernos, APIs em container e bancos relacionais.

> **Como ler esta skill:** cada seção declara primeiro o **princípio** (o que precisa ser verdade e por quê) e depois um **exemplo** numa stack concreta — Vue/Vite no frontend, Go/Gin no backend, PostgreSQL no banco. O princípio é o que viaja entre projetos; o exemplo se traduz para a stack em uso.

---

## 1. Resiliência de Deploys em SPAs: Chunk Recovery Global

**Princípio:** numa SPA com code-splitting servida por CDN, publicar uma nova versão remove os arquivos com hash da versão anterior. Usuários com o app já aberto recebem 404 ao navegar para uma rota lazy ou abrir um componente assíncrono. O app precisa detectar esse erro específico e recarregar a página uma vez, com trava contra loop infinito.

**Dois pontos de captura são necessários** — cobrir só um deixa metade dos casos de fora:
1. **Erro do roteador** (`router.onError`): cobre navegação para uma rota lazy.
2. **Erro de preload do bundler** (`vite:preloadError`): cobre componentes assíncronos filhos (`defineAsyncComponent`, `React.lazy`) carregados dentro de uma view já montada — um modal que falha ao abrir, por exemplo. Esse caso **não** passa pelo roteador.

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

  // Já recarregamos uma vez para este destino e falhou de novo: não insista.
  sessionStorage.removeItem(CHUNK_RELOAD_KEY);
  console.error('Falha persistente ao carregar módulo após atualização de versão:', reloadTarget);
}

export function installLazyRouteChunkRecovery(router) {
  // 1. Interceptador do bundler: cobre rotas E componentes assíncronos filhos.
  window.addEventListener('vite:preloadError', (event) => {
    event.preventDefault();
    triggerRecoveryReload(window.location.href);
  });

  // 2. Interceptador do roteador.
  if (router && typeof router.onError === 'function') {
    router.onError((error, to) => {
      if (!isLazyRouteChunkLoadError(error)) return;
      // Use fullPath, não pathname: pathname descarta a query string do destino.
      const target = to?.fullPath || window.location.href;
      triggerRecoveryReload(target);
    });

    router.afterEach(() => {
      sessionStorage.removeItem(CHUNK_RELOAD_KEY);
    });
  }
}
```

Instale junto da criação do router (`router/index.ts` ou `main.ts`):
```javascript
import { installLazyRouteChunkRecovery } from './lazyRouteChunkRecovery';
installLazyRouteChunkRecovery(router);
```

Cubra `isLazyRouteChunkLoadError` com teste unitário — é detecção por string de mensagem de erro, que muda entre versões de browser e bundler, e o teste é o que avisa quando parar de bater.

---

## 2. Política de Cache na Borda (CDN & HTTP Headers)

**Princípio:** existem duas classes de arquivo e elas precisam de políticas opostas.
* **Assets com hash no nome** (`Dashboard-a8f12.js`): o conteúdo nunca muda para aquele nome. Cache de 1 ano, `immutable`.
* **Arquivos de entrada sem hash** (`index.html`, `sw.js`, `manifest.webmanifest`, `robots.txt`, `sitemap.xml`): são o ponteiro para a versão atual. Precisam revalidar sempre, ou o usuário fica preso numa versão antiga apontando para chunks que já não existem — o que aciona a seção 1 desnecessariamente.

**Declare caminhos explícitos, não catch-all.** É tentador escrever uma regra `/(.*)` com `no-cache` e sobrescrevê-la com `/assets/(.*)` depois, confiando na ordem de precedência do provedor. Evite: a semântica de precedência varia entre CDNs, é fácil de quebrar com um reordenamento inocente, e faz a regra correta depender de um detalhe não-óbvio. Enumerar os arquivos de entrada é mais verboso e mais previsível.

*Exemplo em formato Vercel (`vercel.json`):*
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

*Equivalente em Nginx:*
```nginx
location /assets/ { add_header Cache-Control "public, max-age=31536000, immutable"; }
location = /index.html { add_header Cache-Control "no-cache, no-store, must-revalidate"; }
location = /sw.js     { add_header Cache-Control "no-cache, no-store, must-revalidate"; }
```
Na Cloudflare, o equivalente é Cache Rules por path; no CloudFront, Cache Policies por behavior.

> ⚠️ **Não empilhe Service Worker sobre isso sem necessidade.** Se o app não precisa funcionar offline de verdade, um SW que intercepta assets apenas para cacheá-los é redundante com o cache HTTP (que já é ótimo com hashes imutáveis) e adiciona uma camada a mais de invalidação para depurar quando algo fica velho. Só registre SW se houver requisito funcional de offline.

---

## 3. Runtime em Container

### A. Adequação à quota de CPU

**Princípio:** runtimes que dimensionam o pool de threads pelo número de núcleos leem os núcleos da **máquina host**, não a quota do container. Num container limitado a 1 vCPU rodando num host de 64 núcleos, o runtime cria 64 threads que disputam uma fatia de CPU, e o cgroup aplica *throttling* CFS — latência alta e errática sem que nenhuma métrica de uso pareça saturada.

*Em Go:* import anônimo que ajusta `GOMAXPROCS` pela quota do cgroup.
```go
import _ "go.uber.org/automaxprocs"
```
*Em outras runtimes:* Node respeita a quota para o event loop mas não para `UV_THREADPOOL_SIZE` (ajuste manual); JVM moderna lê cgroups com `-XX:+UseContainerSupport` (padrão desde o JDK 10); Python com Gunicorn exige definir `workers` explicitamente em vez de derivar de `os.cpu_count()`.

### B. Pool de conexões do banco

**Princípio:** o padrão de vários drivers é pool ilimitado. Com várias réplicas, o número total de conexões é `réplicas × pool`, e o Postgres aloca memória por conexão — é assim que se esgota o banco sem nenhum pico de tráfego real. Dimensione pensando no total, não na réplica isolada.

```go
db.SetMaxOpenConns(20)                 // teto por réplica: 20 × nº de réplicas ≤ max_connections do banco
db.SetMaxIdleConns(10)                 // conexões prontas para absorver picos
db.SetConnMaxLifetime(5 * time.Minute) // recicla conexões (evita conexões zumbis atrás de proxies)
db.SetConnMaxIdleTime(2 * time.Minute) // libera ociosas para poupar RAM do banco
```
Equivalentes: `pool_size` / `max_overflow` no SQLAlchemy, `max`/`idleTimeoutMillis` no `pg` do Node, `maximumPoolSize` no HikariCP.

---

## 4. Paralelismo de Consultas Independentes

**Princípio:** telas de dashboard agregam várias consultas que não dependem umas das outras. Executadas em série, a latência é a soma; em paralelo, é a maior delas. O paralelismo precisa propagar o contexto para que a falha de uma consulta cancele as demais em vez de deixá-las rodando à toa.

*Em Go, com `golang.org/x/sync/errgroup`:*
```go
g, gctx := errgroup.WithContext(ctx)

var (
    metrics StoreMetrics
    orders  []Order
)

g.Go(func() error {
    var err error
    // gctx: se outra goroutine falhar, esta query é cancelada no banco.
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
Equivalentes: `Promise.all` com `AbortController` no Node, `asyncio.gather` com `TaskGroup` no Python, `CompletableFuture.allOf` na JVM.

> Cuidado com o efeito no pool: N consultas paralelas por requisição consomem N conexões simultâneas. Um dashboard com 6 queries paralelas e 20 requisições concorrentes já estoura um pool de 20.

---

## 5. Cache Condicional HTTP via ETag (`304 Not Modified`)

**Princípio:** para endpoints sob polling frequente (agenda que atualiza sozinha, contador de notificações), calcule primeiro um *fingerprint* barato do resultado. Se bater com o `If-None-Match` do cliente, responda 304 sem executar a consulta pesada, sem instanciar structs e sem serializar JSON.

> ⚠️ **Requisito de banco:** o fingerprint exige índice composto cobrindo filtro e ordenação, ex: `(store_id, updated_at DESC)`. Sem ele, o `MAX(updated_at)` vira Sequential Scan a cada ciclo de polling — a "otimização" fica mais cara que a consulta original.

**Fingerprint:**
```sql
SELECT COUNT(*), COALESCE(MAX(updated_at), '1970-01-01'::timestamptz)
FROM appointments
WHERE store_id = $1;
```

### ⚠️ O ETag precisa incluir TODOS os parâmetros que mudam a resposta

Este é o erro mais fácil de cometer: gerar o ETag só com `count` e `max_updated_at`. Esses dois valores são **idênticos entre páginas e filtros diferentes da mesma tabela** — então o servidor devolve 304 quando o cliente pede a página 2, e o cliente continua exibindo a página 1. O bug é silencioso e parece "a paginação não funciona às vezes".

A chave do ETag deve conter o fingerprint **e** tudo que discrimina a resposta: view, limite, offset, filtros aplicados.

```go
func buildAppointmentListETag(viewKey string, f Filters, rev Revision) string {
    return fmt.Sprintf(
        `W/"appt-list-v=%s-lim=%d-off=%d-c=%d-m=%d"`,
        viewKey, f.Limit, f.Offset, rev.Count, rev.MaxUpdatedAt.UTC().UnixNano(),
    )
}
```

### ⚠️ `If-None-Match` é uma lista, não um valor único

O header pode legitimamente trazer vários validators separados por vírgula, ou `*`. Comparar com `==` direto faz o 304 simplesmente parar de acontecer nesses casos — a otimização se desliga sozinha sem erro nenhum.

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

**No handler:**
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

> **Quando NÃO usar este padrão.** O fingerprint prévio custa uma consulta extra: em cache miss, são 2 queries em vez de 1. Vale a pena só quando a taxa de acerto é alta — polling periódico sobre dados que mudam pouco. Em listagens navegadas manualmente ou dados que mudam a cada requisição, faça a consulta única e calcule o ETag a partir do payload já obtido.

---

## 6. Índices Estratégicos (exemplo em PostgreSQL)

### A. `CONCURRENTLY` em bases com tráfego

**Princípio:** `CREATE INDEX` comum toma lock exclusivo de escrita na tabela pelo tempo da construção. Numa tabela ativa, isso é uma janela de indisponibilidade. `CONCURRENTLY` constrói sem bloquear escritas.

> ⚠️ **`CREATE INDEX CONCURRENTLY` não roda dentro de um bloco de transação** — e a maioria dos migradores envolve cada migration numa transação por padrão. Sem desativar isso explicitamente, a migration falha com `CREATE INDEX CONCURRENTLY cannot run inside a transaction block`. É o erro nº 1 ao adotar este padrão.

*Com goose:*
```sql
-- +goose Up
-- +goose NO TRANSACTION

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_active_email
  ON users (email)
  WHERE active = true;

-- +goose Down
DROP INDEX CONCURRENTLY IF EXISTS idx_users_active_email;
```
*Equivalentes:* `disable_ddl_transaction!` no Rails; `atomic = False` na Migration do Django; `transaction := false` no golang-migrate (arquivo `.sql` sem wrapper); no Flyway, `CREATE INDEX CONCURRENTLY` exige script marcado como não-transacional.

> Uma criação com `CONCURRENTLY` que falha no meio deixa um índice **inválido** na tabela, que continua ocupando espaço e não é usado pelo planner. Depois de uma migration falha, verifique com `SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;` e dropar antes de tentar de novo.

### B. Índices parciais (`WHERE ...`)
Indexe só a fatia realmente consultada. O índice fica menor, cabe em memória e permanece lá.
```sql
-- Só agendamentos sem usuário registrado (convidados/avulsos)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_appointments_guest_phone
  ON appointments (customer_phone)
  WHERE customer_user_id IS NULL;
```
O planner só usa o índice parcial se o `WHERE` da consulta for **provavelmente implicado** pelo predicado do índice — a condição precisa aparecer na query.

### C. Índices funcionais / expression indexes
Aceleram buscas sobre valor normalizado sem coluna redundante. A expressão precisa ser estritamente `IMMUTABLE`.
```sql
-- Busca por telefone ignorando pontuação
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_phone_digits
  ON users (regexp_replace(phone, '\D', '', 'g'))
  WHERE phone IS NOT NULL;
```
A consulta precisa repetir a expressão **exatamente** como no índice para que o planner o utilize.

---

## 7. Observabilidade de Latência sem Explosão de Cardinalidade

**Princípio:** cada combinação distinta de labels num histograma Prometheus cria uma série temporal nova. Usar o caminho bruto da URL como label (`/stores/9a8b7c/appointments`) gera uma série por UUID — a cardinalidade cresce com o número de registros do produto até esgotar a memória do servidor de métricas. Use sempre o **template** da rota, não o caminho concretizado.

```go
// Em Gin, c.FullPath() retorna o template: "/stores/:store_id/appointments"
path := c.FullPath()
if path == "" {
    path = "unmatched" // requisições sem rota casada não viram label livre
}

httpRequestDuration.WithLabelValues(c.Request.Method, path, statusStr).Observe(duration.Seconds())
```
Equivalentes: `req.route.path` no Express, `request.url_rule.rule` no Flask, `route.path_format` no FastAPI/Starlette.

> O fallback `"unmatched"` não é detalhe: sem ele, requisições a rotas inexistentes (incluindo varredura automatizada por URLs aleatórias) viram labels de cardinalidade ilimitada — é um vetor de exaustão de memória acionável de fora.
