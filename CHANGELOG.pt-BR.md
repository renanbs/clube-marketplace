# Registro de Alterações (Changelog)

Todas as mudanças notáveis no Clube Marketplace serão documentadas neste arquivo.

O formato é baseado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/spec/v2.0.0.html).

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
