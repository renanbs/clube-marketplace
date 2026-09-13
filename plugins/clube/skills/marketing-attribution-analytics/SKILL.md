---
name: marketing-attribution-analytics
description: |
  Especialista em instrumentação de métricas, tracking e atribuição ponta a ponta para SaaS.
  Skill de domínio: é intencionalmente concreta sobre Meta/Google, mas os blocos de infraestrutura
  (cookies, storage, deduplicação, roteamento) são agnósticos de framework.
  Ative esta skill sempre que:
  - Implementar ou modificar tags de conversão (Meta Pixel, Google Ads, GA4, PostHog, Mixpanel).
  - Desenvolver fluxos de captura de leads, registro/signup, onboarding ou checkout e pagamentos.
  - Configurar atribuição de campanhas (UTMs, fbclid, gclid, gbraid, wbraid, _fbc, _fbp).
  - Lidar com persistência de dados de marketing no backend (coluna acquisition_context JSONB).
  - Implementar tracking server-side (Meta Conversions API - CAPI) ou rastreamento cross-domain com deduplicação via event_id.
  - Configurar regras de disparo de analytics no roteador (Vue Router, React Router, SvelteKit, etc.).
license: Apache-2.0
metadata:
  version: v2.0
  author: clubedepontos
---

# Marketing Attribution & Analytics Playbook

Padrão de rastreamento analítico e atribuição de tráfego pago, do clique no anúncio até a persistência no banco relacional.

> **Escopo desta skill:** diferente das skills de arquitetura, esta é uma skill de **domínio**. Meta Pixel, GA4 e Google Ads aparecem por nome porque a skill é justamente sobre integrar com eles — generalizar isso destruiria o valor prático. O que é genérico e reaproveitável em qualquer stack são as seções 1 (cookies e storage), 4 (higiene e deduplicação) e 3B (modelo de dados).

---

## 1. Atribuição First-Touch & Cookies de Domínio Raiz

### A. Parâmetros a capturar
Modelo de **primeiro toque**: os dados da campanha que trouxe o usuário não podem se perder em navegações subsequentes nem no salto da LP para o app.

`utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`, `fbclid`, `gclid`, `gbraid`, `wbraid`.

### B. Cookie compartilhado entre LP e subdomínio do app

Para que `dominio.com.br` e `app.dominio.com.br` leiam o mesmo cookie, ele precisa do atributo `domain` apontando para o domínio raiz.

> ⚠️ **Nunca derive o domínio raiz genericamente a partir do hostname.** A tentação é "pegar os dois últimos rótulos do host", mas isso quebra em dois cenários comuns:
> - **Sufixos compostos:** `.com.br`, `.co.uk`, `.org.br` precisam de três rótulos, não dois.
> - **Public Suffix List:** hosts de preview como `meu-app-abc123.vercel.app`, `*.netlify.app`, `*.pages.dev` e `*.github.io` têm o sufixo registrado na PSL. Setar `domain=.vercel.app` faz o **browser rejeitar o cookie silenciosamente** — sem erro, sem exceção, só atribuição sumindo em todo ambiente de preview.
>
> A regra correta é a inversa: **declare `domain` apenas quando reconhecer explicitamente o domínio do produto; em qualquer outro host, omita o atributo** e deixe o cookie ser host-only. Preview e localhost não precisam de compartilhamento cross-subdomain mesmo.

```javascript
const COOKIE_DAYS = 90;

// Único ponto de configuração por projeto. Liste os domínios raiz reais do produto.
const PRODUCT_ROOT_DOMAINS = ['dominio.com.br'];

/**
 * Retorna o sufixo `; domain=...` quando o host atual pertence a um domínio
 * conhecido do produto. Caso contrário retorna string vazia (cookie host-only),
 * o que é o comportamento correto em localhost, IP bruto e domínios de preview
 * cobertos pela Public Suffix List.
 */
export function cookieDomainSuffix() {
  if (typeof window === 'undefined') return '';
  const hostname = window.location.hostname;

  const root = PRODUCT_ROOT_DOMAINS.find(
    (domain) => hostname === domain || hostname.endsWith(`.${domain}`),
  );

  return root ? `; domain=.${root}` : '';
}

export function setAttributionCookie(name, value, days = COOKIE_DAYS) {
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  const secure = window.location.protocol === 'https:' ? '; Secure' : '';

  document.cookie =
    `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/` +
    `${cookieDomainSuffix()}; SameSite=Lax${secure}`;
}

export function getCookie(name) {
  const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const match = document.cookie.match(new RegExp(`(?:^|; )${escaped}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : '';
}
```

### C. Geração de `_fbc` e `_fbp`
* Se houver `fbclid` na query e não existir `_fbc`, gere: `fb.1.${Date.now()}.${fbclid}`.
* Se não existir `_fbp`, gere um ID persistente: `fb.1.${Date.now()}.${Math.floor(Math.random() * 2147483647)}`.
* Se a LP repassar os valores já formados na query (ex: `?pt_fbc=...&pt_fbp=...`), **prefira o valor repassado** ao regerar — regerar cria um identificador novo e quebra a continuidade da atribuição.

### D. Fallback em `sessionStorage`
Armazene sempre uma cópia do contexto capturado em `sessionStorage`, para sobreviver a cookies rejeitados, bloqueados por extensão ou limpos durante a sessão.

---

## 2. Continuidade de Sessão: Linker GA4 Cross-Domain com Fail-Safe

Navegar da LP para o subdomínio `app.` quebra a sessão no GA4 a menos que a URL de destino carregue o parâmetro do linker. A decoração precisa acontecer no momento do clique, porque o parâmetro é sensível ao tempo.

> ⚠️ **Regra crítica de UX:** nunca espere o `window.gtag` indefinidamente. Com adblockers (uBlock, Brave Shields) ou conexão instável, o callback do `gtag` pode **nunca** responder — e o usuário fica com o botão travado. Timeout fail-safe é obrigatório: perder a continuidade de sessão é aceitável, perder o clique não é.

```javascript
export function decorateWithGaLinker(targetUrl, timeoutMs = 600) {
  const gaId = import.meta.env.VITE_GOOGLE_ANALYTICS_ID;
  if (!gaId || typeof window.gtag !== 'function') {
    return Promise.resolve(targetUrl);
  }

  const linkerPromise = new Promise((resolve) => {
    window.gtag('get', gaId, 'linker_param', (linkerParam) => {
      if (!linkerParam) return resolve(targetUrl);
      try {
        const url = new URL(targetUrl);
        const [key, ...rest] = linkerParam.split('=');
        if (key && rest.length) {
          url.searchParams.set(key, rest.join('='));
        }
        resolve(url.toString());
      } catch {
        resolve(targetUrl);
      }
    });
  });

  const timeoutPromise = new Promise((resolve) => {
    setTimeout(() => resolve(targetUrl), timeoutMs);
  });

  return Promise.race([linkerPromise, timeoutPromise]);
}
```

No clique do CTA de cadastro/login:
1. Dispare os eventos locais de clique (`trackRegisterClick`).
2. Aguarde a decoração com timeout seguro: `const finalUrl = await decorateWithGaLinker(url);`
3. Redirecione com `window.location.assign(finalUrl)`.

Declare também os domínios no config do gtag, para o linker automático cobrir links normais:
```javascript
gtag('config', GA_ID, { linker: { domains: ['dominio.com.br', 'app.dominio.com.br'] } });
```

---

## 3. Persistência no Backend (`acquisition_context JSONB`)

Dado de marketing vira dado relacional permanente. É o que torna a análise de CAC e LTV imune a restrições de navegador, expiração de cookie e mudança de política das plataformas.

### A. Frontend (payload de signup)
```javascript
export function buildAcquisitionContextForSignup() {
  const ctx = readStoredCampaign();
  const out = {
    captured_at: new Date().toISOString(),
    referrer: document.referrer || null,
  };

  for (const key of [
    'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
    'fbclid', 'gclid', 'gbraid', 'wbraid',
  ]) {
    if (ctx[key]) out[key] = ctx[key];
  }

  out.landing_page = `${window.location.pathname}${window.location.search}`;
  return out;
}
```

### B. Banco de dados (exemplo em PostgreSQL)
```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS acquisition_context JSONB;
COMMENT ON COLUMN users.acquisition_context IS
  'First-touch marketing attribution captured at signup (UTMs, fbclid, etc.). Immutable after create.';
```

Em bancos sem tipo JSON nativo, use uma coluna texto com o JSON serializado ou uma tabela lateral chave/valor — o princípio é que o contexto de aquisição seja **imutável após a criação** e consultável junto com faturamento, não que seja JSONB especificamente.

* **Benefício:** CAC, LTV e cohort reais com SQL direto entre faturamento e campanha, sem depender de relatório externo de plataforma.

---

## 4. Higiene e Roteamento no Frontend

### A. Bloqueio em rotas administrativas
Eventos disparados por operadores e equipe interna contaminam o algoritmo de lances das plataformas de anúncio — o modelo passa a otimizar para um perfil de usuário que nunca vai comprar.

```javascript
export function isAdminPath(path) {
  const p = (path || '').split('?')[0];
  return p === '/admin' || p.startsWith('/admin/');
}

export function shouldTrackRoute(path) {
  return trackingEnabled() && !isAdminPath(path);
}
```

### B. Resiliência de conversão em redirects assíncronos
Em SPAs, navegar para `/dashboard` logo após o submit cancela requisições de tracking pendentes. Use o padrão **Pending / Flush**: grave a intenção antes de navegar, dispare depois que a rota assentou.

```javascript
// 1. No submit bem-sucedido
sessionStorage.setItem('pt_pending_registration', JSON.stringify({ accountType, params }));

// 2. No hook pós-navegação do roteador
router.afterEach((to) => {
  flushPendingRegistrationTracking();
  if (shouldTrackRoute(to.fullPath)) {
    trackPageView(to.fullPath);
  }
});
```
*O hook equivalente em outros roteadores: `useEffect` sobre `location` no React Router, `afterNavigate` no SvelteKit, `router.events.on('routeChangeComplete')` no Next.js Pages Router.*

### C. Deduplicação por chave de transação
Deduplique por **transação**, nunca por flag booleana global — flag global impede registrar a segunda compra do mesmo cliente, upgrades de plano e renovações.

```javascript
export function trackPurchaseOnce({ value, planId, transactionId }) {
  const dedupKey = `pt_purchase_fired_${transactionId || 'default'}`;
  if (sessionStorage.getItem(dedupKey) === '1') return;
  sessionStorage.setItem(dedupKey, '1');

  if (typeof window.fbq === 'function') {
    window.fbq(
      'track',
      'Purchase',
      { value, currency: 'BRL', content_name: planId },
      { eventID: transactionId }, // chave de deduplicação com CAPI
    );
  }

  if (typeof window.gtag === 'function') {
    window.gtag('event', 'purchase', {
      transaction_id: transactionId,
      value,
      currency: 'BRL',
      items: [{ item_name: planId }],
    });
  }
}
```

### D. Teste a instrumentação — ela é a única parte do sistema que falha em silêncio

Código de tracking é o candidato natural a ficar sem teste: não tem tela, não tem retorno para o usuário, e "dá para conferir no painel depois". É exatamente por isso que precisa de teste.

**Quando qualquer outra parte do sistema quebra, alguma coisa reclama** — erro no console, tela em branco, requisição 500, alerta. Quando o tracking quebra, **nada acontece**. A aplicação continua perfeita, o usuário completa a compra, e o evento simplesmente não sai (ou sai duplicado). Você descobre semanas depois reconciliando faturamento — e, no intervalo, otimizou campanha e decidiu orçamento em cima de número errado. O custo do bug não é o bug: é a decisão tomada com o dado que ele corrompeu.

Cubra com teste unitário, mockando `window.fbq` e `window.gtag`:

1. **Deduplicação funciona:** chamar `trackPurchaseOnce` duas vezes com o mesmo `transactionId` dispara **uma** vez.
2. **Deduplicação não é global:** chamar com `transactionId` diferente dispara **de novo** — é o teste que pega a regressão de "voltaram a usar flag booleana" e mata a receita de recompra e upgrade.
3. **Higiene de rota:** `shouldTrackRoute('/admin/lojas')` é `false` e `shouldTrackRoute('/dashboard')` é `true`.
4. **Chave de deduplicação cruzada:** o `eventID` passado ao Pixel é idêntico ao `transaction_id` enviado ao GA4 — se divergirem, a deduplicação com o CAPI para de funcionar sem nenhum sintoma local.
5. **Degradação segura:** com `window.fbq` e `window.gtag` indefinidos (adblocker), as funções de tracking não lançam exceção nem interrompem o fluxo de checkout.
6. **Fail-safe do linker:** `decorateWithGaLinker` resolve dentro do timeout mesmo quando o callback do `gtag` nunca é chamado.

Os itens 4 e 5 são os que mais pegam bug real: o primeiro quebra atribuição sem quebrar nada visível, o segundo transforma um adblocker em falha de checkout.

---

## 5. Eventos Padronizados de Funil

| Etapa | Meta Pixel (`fbq`) | GA4 (`gtag`) | Google Ads |
| :--- | :--- | :--- | :--- |
| **Visita LP** | `trackCustom('LpPageView')` | `event('lp_page_view')` | - |
| **Clique CTA cadastro** | `trackCustom('StartTrialClick')` | `event('register_click')` | - |
| **Página de registro** | `trackCustom('RegisterPageView')` | `event('register_page_view')` | - |
| **Cadastro concluído** | `track('CompleteRegistration')` | `event('sign_up')` | `send_to: AW-xxx/signup` |
| **Onboarding finalizado** | `trackCustom('OnboardingComplete')` | `event('onboarding_complete')` | `send_to: AW-xxx/onboard` |
| **Início do checkout** | `track('InitiateCheckout')` | `event('begin_checkout')` | `send_to: AW-xxx/checkout` |
| **Compra / assinatura** | `track('Purchase', payload, { eventID })` | `event('purchase')` | `send_to: AW-xxx/purchase` |

> ⚠️ Para `Purchase`, **SEMPRE** use o mesmo identificador (`transaction_id` / `eventID`) no client e no server (CAPI).

---

## 6. Server-Side Tracking: Meta Conversions API (CAPI)

Adblockers, ITP no Safari e navegadores focados em privacidade bloqueiam entre 25% e 45% dos eventos de conversão no cliente. Para eventos de receita, o disparo server-side é o que garante entrega.

* **Quando disparar:** no handler do webhook de confirmação de pagamento do gateway (Stripe, PagSeguro, InfinitePay), não no retorno do checkout — o webhook é a única fonte confiável de que o pagamento aconteceu.
* **Deduplicação automática:** a Meta deduplica eventos do Pixel e do CAPI que compartilhem o mesmo `event_name` + `event_id` dentro de uma janela de 48 horas.

**Payload para a Graph API:**
* `event_name`: `"Purchase"`
* `event_time`: timestamp Unix atual
* `event_id`: UUID único do pedido — **deve** ser idêntico ao `transactionId` usado no `eventID` do frontend
* `action_source`: `"website"`
* `user_data`:
  * `em`: hash SHA256 do e-mail (normalizado: minúsculas, sem espaços nas pontas)
  * `ph`: hash SHA256 do telefone (só dígitos, com DDI — ex: `5511999999999`)
  * `fbc` / `fbp`: cookies recuperados do banco ou da requisição
  * `client_ip_address`, `client_user_agent`
* `custom_data`: `currency`, `value`, `order_id`

> 🔒 **Tratamento de dados pessoais (LGPD/GDPR).** `user_data` transporta PII de cliente real. Requisitos não-negociáveis:
> - **Hash antes de sair do seu domínio.** E-mail e telefone vão para a Meta apenas como SHA256 da forma normalizada. Nunca envie valor em claro.
> - **Nunca logue o payload montado.** É o vazamento mais comum: um `log.Printf("%+v", payload)` de debug em produção despeja PII (mesmo hasheada, é dado pessoal pseudonimizado) no agregador de logs, onde fica retido por meses e acessível a quem não deveria. Logue no máximo `event_id` e status da resposta.
> - **Base legal e consentimento.** O envio de dados de cliente a terceiro para fins publicitários precisa estar coberto na política de privacidade e respeitar a escolha do usuário quando houver banner de consentimento — se o usuário recusou cookies de marketing, o disparo server-side não é uma brecha para ignorar isso.
> - **Token de acesso é segredo.** O token da Graph API fica em variável de ambiente do backend, nunca em repositório, nunca exposto ao client.
> - **Minimize.** Envie apenas os campos que melhoram o match (`em`, `ph`, `fbc`, `fbp`, IP, user-agent). Não inclua nome, endereço, CPF ou qualquer campo que a plataforma não exija.
