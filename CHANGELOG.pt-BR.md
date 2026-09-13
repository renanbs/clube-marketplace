# Registro de Alterações (Changelog)

Todas as mudanças notáveis no Clube Marketplace serão documentadas neste arquivo.

O formato é baseado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/spec/v2.0.0.html).

## [0.2.0] - 2026-09-13

### Adicionado
- **5 Agentes Especialistas de IA Nomeados (`plugins/clube/agents/`):**
  - `expert-seo`: SEO técnico, Generative Engine Optimization (GEO), Schema.org JSON-LD e `/llms.txt`.
  - `expert-tracking`: Atribuição de marketing, Meta Pixel & CAPI, deduplicação via `event_id` e higiene de cookies no domínio raiz.
  - `expert-privacy`: Conformidade LGPD/GDPR, máscara de PII, logging de formato, higienização Sentry e trilhas de auditoria.
  - `expert-performance`: Performance fullstack, recuperação de chunks SPA, headers de cache CDN e otimização de queries de banco.
  - `clube-auditor`: Coordenador de prontidão para produção 360° executando detectores determinísticos em Python e sintetizando relatórios em 4 fases.
- **15 Guias de Referência Temática:** Decomposição das skills verticais de SaaS em guias profundos em subdiretórios `references/` (`meta-social.md`, `json-ld-schemas.md`, `geo-llmstxt.md`, `crawling-sitemaps.md`, `first-touch-cookies.md`, `deduplication-hygiene.md`, `server-side-capi.md`, `database-attribution.md`, `pii-masking-shape.md`, `sentry-observability-scrubbing.md`, `compliance-retention.md`, `chunk-recovery.md`, `caching-edge-headers.md`, `runtime-tuning.md`, `db-indexing-queries.md`).
- **Validador Automatizado de Agentes e Manifestos:** Atualização de `bin/clube-config check` e `make check` para validar frontmatter YAML de agentes, diretórios de referências de skills e alinhamento de versão dos 9 manifestos em Python 3 stdlib puro.

### Alterado
- **Refatoração de Skills em Divulgação Progressiva:** Refatoração de 4 skills monolíticas de SaaS (`saas-seo-geo`, `marketing-attribution-analytics`, `data-privacy-observability`, `fullstack-performance-resilience`) em pontos de entrada enxutos de roteamento (`SKILL.md` < 100 linhas).
- **Alinhamento Sincronizado de Versão em 9 Manifestos:** Sincronização de `package.json`, 4 catálogos raiz de marketplace e 4 manifestos de plugin para `v0.2.0`.
- **Atualização da Constituição de Arquitetura:** Adição formal da Seção 1.2 (Padrão de Agentes Especialistas Nomeados) e Seção 1.3 (Arquitetura de Divulgação Progressiva de Skills) na skill `clube:clube-architecture`.

### Melhorado
- **Registro Multi-Harness de Agentes:** Descoberta e registro padronizados de agentes no Claude Code, Cursor, Codex e Oh My Pi.

## [0.1.0] - 2026-09-13

### Adicionado
- **Arquitetura Multi-Harness de Marketplace:** Catálogos unificados de distribuição para Claude Code (`.claude-plugin/`), Cursor (`.cursor-plugin/`), Codex (`.agents/plugins/`) e Oh My Pi (`.omp-plugin/`).
- **6 Skills Modulares:**
  - `clube:init`: Onboarding guiado e gerador de `Project Profile` em `AGENTS.md` e `CLAUDE.md`.
  - `clube:clube-architecture`: Constituição de engenharia, 5 pilares fundamentais e padrões de qualidade.
  - `clube:fullstack-performance-resilience`: Recuperação de chunks SPA (`vite:preloadError`), headers de cache CDN (`immutable`), cgroups em containers (`automaxprocs`) e tuning de queries de banco.
  - `clube:saas-seo-geo`: Separação estrita de LP vs App (`noindex`), metadados OpenGraph, Schema.org JSON-LD e especificações `/llms.txt` / `/llms-full.txt`.
  - `clube:marketing-attribution-analytics`: Cookies primários de first-touch UTM no domínio raiz, deduplicação Meta CAPI via `event_id` e persistência de `acquisition_context JSONB`.
  - `clube:data-privacy-observability`: Conformidade LGPD/PII em logs/telemetria, eliminação de serialização cega de structs (`%+v`, `zap.Any`), higienização de Sentry e segurança de cardinalidade em métricas.
- **8 Comandos Slash:**
  - `/clube:audit` (ou `/audit`): Auditoria unificada 360° de prontidão para produção em SaaS cobrindo todos os 4 pilares.
  - `/clube:audit-privacy`: Auditoria estática e contextual para PII em logs, query strings e cardinalidade de métricas.
  - `/clube:audit-performance`: Recuperação de chunks SPA, cache de CDN e limites de recursos em containers.
  - `/clube:audit-seo`: Descobrabilidade de rotas públicas, `/llms.txt` e dados estruturados.
  - `/clube:audit-tracking`: Cookies no domínio raiz, deduplicação Meta CAPI e contexto de aquisição no banco de dados.
  - `/clube:init` (ou `/init`, `$init`): Onboarding guiado, validação de conexões de banco e mapeamento de papéis de agentes.
  - `/clube:omp-setup`: Configuração de sobreposições de modelo no OMP para despacho de subagentes.
  - `/clube:help`: Diretório centralizado de comandos e skills.
- **Suite de Auditoria Híbrida:** Scripts estáticos determinísticos em Python (`audit-all.py`, `audit-privacy.py`, `audit-performance.py`, `audit-seo.py`, `audit-tracking.py`, `ui.py`) com renderização rica em tabelas ASCII, barras de saúde gráfica e persistência de estado em `.clube/audit-last.json`.
- **CLI Operacional e Makefile:** CLI `clube-config` e alvos do `Makefile` (`make check`, `make audit`, `make sync`, `make init`, `make install-cli`).
- **Contrato de Saída em 4 Fases:** Formato padronizado em todos os comandos: `### 1. Plan`, `### 2. Execution`, `### 3. Summary`, `### 4. Recommended Actions`.
- **Documentação Bilíngue:** Documentação canônica em inglês (`README.md`, `CHANGELOG.md`) espelhada em português do Brasil (`README.pt-BR.md`, `CHANGELOG.pt-BR.md`).

### Removido
- Pacotes monolíticos legados de distribuição em arquivo único e declarações planas de skills.
