---
name: saas-seo-geo
description: |
  Especialista em SEO técnico e GEO (Generative Engine Optimization) para aplicações SaaS e Landing Pages.
  Agnóstica de stack e de provedor de hospedagem: os exemplos usam uma stack concreta, mas o princípio vale para qualquer uma.
  Ative esta skill sempre que:
  - Criar ou refatorar Landing Pages, páginas de marketing, vitrines públicas, blogs ou telas institucionais.
  - Configurar metadados, Open Graph, Twitter Cards, tags canônicas, robots.txt, sitemaps, llms.txt ou llms-full.txt.
  - Implementar dados estruturados (Schema.org / JSON-LD) como FAQPage, SoftwareApplication, Organization ou Breadcrumbs.
  - Desenvolver páginas com Astro, Vite, Next.js, Nuxt, SvelteKit ou HTML estático.
  - Configurar políticas de indexação para SPAs ou aplicações logadas (proteção contra canibalização via noindex).
license: Apache-2.0
metadata:
  version: v2.0
  author: clubedepontos
---

# SaaS SEO & GEO (Search & AI Engine Optimization)

Padrão arquitetural de SEO tradicional e otimização para motores de IA (GEO) em projetos SaaS.

> **Como ler esta skill:** cada seção declara primeiro o **princípio** (o que precisa ser verdade e por quê) e depois um **exemplo** numa stack concreta. O princípio é obrigatório; o exemplo é ilustrativo. Ao aplicar num projeto novo, traduza o exemplo para a stack e o provedor de hospedagem daquele projeto.

---

## 1. Princípio Fundamental: Separação Estrita (LP vs App)

Toda arquitetura SaaS precisa de uma fronteira explícita de indexação. Sem ela, telas de login, rotas privadas e estados vazios de dashboard competem com a Landing Page pelas mesmas palavras-chave e diluem a autoridade do domínio.

1. **Landing Page e páginas públicas:**
   * Públicas, estáticas ou renderizadas no servidor (SSR/SSG).
   * `robots.txt` com `Allow: /`.
   * Tags canônicas absolutas, dinâmicas e sem parâmetros de campanha (`utm_*`, `fbclid`, etc.).

2. **Web App logado / Dashboard (SPA / PWA):**
   * **NUNCA** deve ser indexado.
   * Obrigatório no `<head>` do HTML de entrada:
     ```html
     <meta name="robots" content="noindex, nofollow" />
     ```
   * Reforce também via header HTTP na camada de CDN/edge/proxy do projeto — o header cobre respostas não-HTML e crawlers que não executam JS:
     ```http
     X-Robots-Tag: noindex, nofollow
     ```
     *Onde configurar depende do provedor: `headers` no `vercel.json`, Transform Rules na Cloudflare, `add_header` no Nginx, `Header set` no Apache, regra de CDN no CloudFront.*

   > ⚠️ **Não coloque `<link rel="canonical">` numa página `noindex`.** Os dois sinais são contraditórios (um diz "não me indexe", o outro diz "este é o endereço oficial para indexar") e o canonical é ignorado de qualquer forma. Se a página é privada, remova a canonical em vez de apontá-la para lugar nenhum.

   > ⚠️ **Confira o domínio nas tags absolutas.** `canonical`, `og:url` e `og:image` usam URL absoluta e por isso são o ponto mais comum de erro de digitação de domínio (`.com` no lugar de `.com.br`, faltar o subdomínio, apontar para staging). Um `og:image` com domínio errado quebra silenciosamente o preview em WhatsApp e LinkedIn sem nenhum erro em build ou runtime — valide sempre no Facebook Sharing Debugger antes de publicar.

3. **Vitrines públicas dentro de SPAs (ex: `/loja/:slug`):**
   * Se a vitrine precisa ranquear (perfil de estabelecimento, link público de agendamento, página de profissional), ela **NÃO** pode viver sob um HTML de entrada com `noindex` — o `noindex` vale para todas as rotas servidas por aquele arquivo.
   * Renderize via SSR/SSG num projeto separado, ou adicione pré-renderização dinâmica no servidor para user-agents de crawler.

---

## 2. Meta Tags e Social Sharing

Todo documento HTML público deve incluir:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="theme-color" content="#0F172A" />

  <!-- Título e descrição primários -->
  <title>Título Claro e Focado na Solução (até 60 chars) | NomeDaMarca</title>
  <meta name="description" content="Descrição concisa com proposta de valor, dores resolvidas e chamada para ação (140 a 160 caracteres)." />

  <!-- URL canônica absoluta: dinâmica e limpa de parâmetros de tracking -->
  <link rel="canonical" href="https://www.dominio.com.br/pagina-atual" />

  <!-- Favicons e touch icons -->
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png" />
  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />

  <!-- Open Graph (WhatsApp, LinkedIn, Facebook, Telegram) -->
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://www.dominio.com.br/pagina-atual" />
  <meta property="og:locale" content="pt_BR" />
  <meta property="og:site_name" content="NomeDaMarca" />
  <meta property="og:title" content="Título do Produto | NomeDaMarca" />
  <meta property="og:description" content="Descrição idêntica ou complementar com foco em conversão social." />
  <meta property="og:image" content="https://www.dominio.com.br/og-image.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="Demonstração visual ou logotipo do NomeDaMarca" />

  <!-- Twitter Cards -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Título do Produto | NomeDaMarca" />
  <meta name="twitter:description" content="Descrição curta para Twitter/X." />
  <meta name="twitter:image" content="https://www.dominio.com.br/og-image.png" />
```

---

## 3. Dados Estruturados (Schema.org / JSON-LD)

Sempre que a página tiver conteúdo correspondente, adicione os blocos JSON-LD no `<head>`.

### A. SoftwareApplication (para SaaS)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "NomeDoSaaS",
  "url": "https://www.dominio.com.br/",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Web",
  "description": "Descrição detalhada do software e suas funcionalidades.",
  "offers": {
    "@type": "Offer",
    "price": "149.00",
    "priceCurrency": "BRL",
    "priceValidUntil": "2027-12-31",
    "description": "A partir de R$ XX/mês no plano anual."
  }
}
</script>
```

### B. FAQPage (GEO & Rich Snippets)
> **Regra e nuance GEO:** embora o Google tenha reduzido em 2023 os rich snippets visuais de FAQ na SERP para sites comerciais, o `FAQPage` é hoje **o sinal estruturado mais relevante para GEO**. Modelos como Perplexity, ChatGPT Search, Claude e Gemini consomem esses pares de pergunta/resposta para fundamentar respostas e citar a marca como fonte. Todo FAQ visível na página DEVE ter espelho exato em JSON-LD — texto divergente entre o visível e o estruturado é motivo de penalização.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Pergunta exata do acordeão?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Resposta completa e idêntica à exibida visualmente para o usuário."
      }
    }
  ]
}
</script>
```

### C. Organization (entidade da marca e Knowledge Graph)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "NomeDaEmpresa",
  "url": "https://www.dominio.com.br",
  "logo": "https://www.dominio.com.br/logo.png",
  "sameAs": [
    "https://www.instagram.com/nomedaempresa",
    "https://www.linkedin.com/company/nomedaempresa"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "customer support",
    "telephone": "+55-11-99999-9999",
    "availableLanguage": ["Portuguese"]
  }
}
</script>
```

### D. BreadcrumbList (páginas secundárias e blog)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Início", "item": "https://www.dominio.com.br/" },
    { "@type": "ListItem", "position": 2, "name": "Nome da Subpágina", "item": "https://www.dominio.com.br/subpagina" }
  ]
}
</script>
```

---

## 4. Otimização para Motores de IA: `llms.txt` & `llms-full.txt` (GEO)

Na pasta pública servida na raiz do domínio, forneça arquivos Markdown estruturados para consumo por agentes de IA e crawlers semânticos.

### A. `llms.txt` (índice conciso e rotas)

Um resumo denso da proposta de valor seguido de links rotulados. O primeiro parágrafo é o que mais importa: é dele que os modelos extraem a descrição da marca ao citá-la.

```markdown
# NomeDoProduto

> Resumo em uma linha da proposta de valor, público-alvo e modelo de negócio.

Descrição detalhada com palavras-chave de intenção de busca, público atendido, funcionalidades
principais, modelos de precificação (com valores reais) e diferenciais competitivos.

## Produto

- [Site](https://www.dominio.com.br/): Landing page oficial
- [Preços](https://www.dominio.com.br/#precos): Valores e planos
- [FAQ](https://www.dominio.com.br/#faq): Perguntas frequentes
- [Documentação completa](https://www.dominio.com.br/llms-full.txt): Contexto integral para LLMs

## App / Acesso

- [Criar conta](https://app.dominio.com.br/register): Teste grátis
- [Entrar](https://app.dominio.com.br/login): Login de clientes

## Contato

- [Instagram](https://instagram.com/marca): Conteúdo e novidades
- [Suporte](https://ig.me/m/marca): Atendimento

## Optional

- [Sitemap](https://www.dominio.com.br/sitemap.xml): URLs indexáveis
- [robots.txt](https://www.dominio.com.br/robots.txt): Regras de robôs
```

> Inclua preços, cupons e condições comerciais reais em texto corrido. Modelos generativos citam esses números diretamente ao responder "quanto custa X" — deixar isso de fora entrega a resposta para um concorrente que incluiu.

### B. `llms-full.txt` (contexto completo)
Para modelos com janelas de contexto amplas, compile uma versão agregada em Markdown com:
1. Detalhamento completo de cada funcionalidade.
2. Todas as perguntas e respostas do FAQ.
3. Tabelas comparativas com alternativas de mercado.
4. Políticas de suporte, segurança de dados e integrações suportadas.

Gere esse arquivo no build a partir das mesmas fontes do site (coleções de conteúdo, JSON de FAQ) em vez de mantê-lo à mão — arquivo duplicado manualmente desatualiza e passa a mentir sobre o produto.

---

## 5. Rastreabilidade & Clean URLs

**1. `robots.txt`:**
```txt
User-agent: *
Allow: /

# Bloqueia rotas de API interna ou callbacks
Disallow: /api/

Sitemap: https://www.dominio.com.br/sitemap.xml
```

**2. `sitemap.xml`:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.dominio.com.br/</loc>
    <lastmod>2026-09-13</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
```
Gere o sitemap no build sempre que o framework permitir (`@astrojs/sitemap`, `next-sitemap`, `nuxt/sitemap`). Sitemap escrito à mão desatualiza no primeiro deploy que adiciona uma página.

**3. URL canônica única (clean URLs):**
Princípio: cada conteúdo deve responder em **um** endereço só. `/pagina`, `/pagina/` e `/pagina.html` servindo o mesmo HTML é conteúdo duplicado e divide sinais de ranqueamento. Escolha uma forma e redirecione (301) as demais.

*Como declarar, por provedor:*
```json
// Vercel (vercel.json)
{ "cleanUrls": true, "trailingSlash": false }
```
```nginx
# Nginx
rewrite ^/(.*)\.html$ /$1 permanent;
rewrite ^/(.+)/$ /$1 permanent;
```
Na Cloudflare Pages, equivale a habilitar as regras de normalização de URL; no Netlify, `pretty_urls`. Em SSG com framework, normalmente é opção de config (`trailingSlash` no Astro/Next/Nuxt).

---

## 6. Escolha de Stack para Landing Pages

**Princípio:** a LP deve entregar HTML completo no primeiro byte, sem depender de JavaScript para renderizar conteúdo indexável, e permitir reuso de componentes (header, footer, bloco de SEO, FAQ) conforme o número de páginas cresce. HTML estático escrito à mão atende o primeiro requisito e falha no segundo: a partir de ~5 páginas, cabeçalhos, scripts de analytics e blocos JSON-LD passam a ser copiados e colados, e divergem.

**Default recomendado:** se o projeto não tem stack definida por outro motivo, **Astro** é o melhor ponto de partida:
* Gera HTML estático com 0kb de JavaScript cliente por padrão.
* Componentiza `<Header />`, `<Footer />`, `<SEO />`, `<FAQ />`.
* Coleções de conteúdo em Markdown/MDX habilitam SEO programático (páginas por nicho, cidade, caso de uso) de forma escalável.
* Integração nativa de `sitemap.xml` e RSS via `@astrojs/sitemap`.

**Quando escolher outra coisa:** se o time já opera Next.js ou Nuxt em outro produto e a LP vai compartilhar componentes, design system ou pipeline de deploy com ele, a consistência operacional vale mais do que os kilobytes economizados — use a stack que já existe. Da mesma forma, uma LP de página única e estável não justifica migrar nada.
