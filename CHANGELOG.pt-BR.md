# Registro de Alterações (Changelog)

Todas as mudanças notáveis no Clube Marketplace serão documentadas neste arquivo.

O formato é baseado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/spec/v2.0.0.html).

## [0.5.0] - 2026-09-23

### Adicionado
- **Suporte ao OpenCode V2:** distribuição de primeira classe para o harness OpenCode.
  - Catálogo `.opencode-plugin/marketplace.json` e manifests `.opencode-plugin/plugin.json` por plugin (paridade SemVer garantida pelo `make check`).
  - Adaptadores de plugin OpenCode `.opencode/plugins/clube/index.ts` e `.opencode/plugins/code-review/index.ts` registrando 7 skills e 7 comandos slash (`/clube:init`, `/clube:help`, `/clube:audit`, `/clube:audit-privacy`, `/clube:audit-performance`, `/clube:audit-seo`, `/clube:audit-tracking`, `/code-review:review`). O `clube:omp-setup` permanece exclusivo do OMP.
  - `opencode.json` raiz e `.opencode/opencode.json` conectando os adaptadores e 6 subagentes nomeados (`expert-seo`, `expert-tracking`, `expert-privacy`, `expert-performance`, `clube-auditor`, `reviewer`) cujo `system` resolve para os arquivos canônicos de agente em `plugins/`. Os agentes omitem `model` para herdar o modelo da sessão (independente de provedor).
  - O `make check` agora audita a integração OpenCode: ambos os configs precisam fazer parse, cada plugin do catálogo precisa ter um adaptador `index.ts` e cada `system` de agente precisa resolver.
- Documentação bilíngue atualizada: seções de instalação do README/README.pt-BR, `clube:help` e `AGENTS.md`.
- `package.json`, as entradas do `clube` nos catálogos, os 5 manifests do plugin `clube`, o frontmatter das skills verticais e o adaptador OpenCode sincronizados em `v0.5.0`. O `code-review` permanece com a própria versão, `v0.1.0`.

## [0.4.0] - 2026-09-23

### Adicionado
- **Plugin `code-review` (`plugins/code-review/`, v0.1.0):** Plugin separado, com versão independente, para code review estruturado.
  - Comando `/code-review:review` para mudanças staged, branches e pull requests.
  - Agente `reviewer` somente leitura (classe `critique`) que responde `APPROVE` ou `CHANGES-REQUESTED`.
  - Skill `code-review` com núcleo independente de linguagem e referências sob demanda para Go, TypeScript e Rust.
- `code-review` registrado nos quatro catálogos de marketplace da raiz.

### Alterado
- **Validação de versão por plugin:** `make check` valida a versão de cada plugin contra os próprios manifests e contra a entrada dele em cada catálogo, permitindo versões independentes.
- A paridade SemVer geral agora lê a entrada do `clube` no catálogo pelo nome, e não a primeira entrada, então a ordem dos catálogos deixou de importar.
- A saída do `make check` mostra cada problema só embaixo do plugin a que pertence.
- `package.json`, as entradas do `clube` nos catálogos, os 4 manifests do plugin `clube` e o frontmatter das skills verticais sincronizados em `v0.4.0`. O `code-review` sai com a própria versão, `v0.1.0`.

## [0.3.0] - 2026-09-13

### Adicionado
- **CLI em Python (`clube_cli/`):** `bin/clube-config` virou um lançador fino; a lógica dos comandos (`check`, `audit`, `sync`, `init`, `install`) fica num pacote Python testado, usando só a biblioteca padrão em tempo de execução.
- **Suíte pytest (`tests/`, `make test`):** Cobre os quatro auditores (incluindo falsos positivos calibrados), os cenários de falha do validador, a pontuação por severidade, a detecção de harness e o sync de ponteiros. Roda via `uv`; o `uv.lock` é versionado.
- **Preflight de dependências (`make doctor`):** Verifica `python3` (versão mínima lida do `pyproject.toml`), `uv`, `pytest`, `make` e `git`. O `init` roda o preflight antes de escrever qualquer arquivo e aborta se faltar uma dependência obrigatória.
- `make test` falha com uma mensagem acionável quando não há `uv` nem `pytest` disponíveis.
- **Integridade de links no validador:** `make check` acusa links quebrados para references e references órfãs nas skills.

### Alterado
- **`make check` agora pode falhar:** O exit code vem da quantidade de problemas encontrados. Antes ele saía `0` em qualquer estado.
- Skills verticais passam a exigir `references/` por padrão, com lista de isenção (`init`, `clube-architecture`), então uma skill nova não escapa mais da checagem.
- O frontmatter dos agentes é lido só dentro do bloco `---`, e os campos faltantes são nomeados.
- **Fonte única de versão:** O alvo da paridade SemVer vem do `package.json`, e `clube_cli.__version__` é derivado dele em vez de ficar fixo no código.
- **Constituição de arquitetura:** Novas regras 2.3 (Gates Must Be Able To Fail) e 5.1 (Single Source of Truth), esclarecimento de que a regra de só usar stdlib vale em tempo de execução, e novos anti-padrões.
- Os 9 manifests e o frontmatter das skills verticais sincronizados em `v0.3.0`.

### Corrigido
- Entradas do runlog são serializadas com `json.dumps`, então `details` com aspas não geram mais JSON inválido.
- A detecção de harness pelo processo pai tem limite de profundidade e não entra mais em loop quando o `ps` falha.
- Um profile corrompido ou ausente cai no padrão em vez de gerar erro.

### Removido
- `scripts/*.sh` (`lib-harness.sh`, `lib-runlog.sh`, `sync-harness-configs.sh`), substituídos pelo CLI em Python.

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
