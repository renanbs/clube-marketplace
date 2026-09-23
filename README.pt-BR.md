<div align="center">

# Clube Marketplace

**Marketplace centralizado e multi-harness de IA para skills, agentes, comandos e fluxos de trabalho sob medida para os produtos SaaS do Clube.**

[![Versão](https://img.shields.io/badge/versão-0.5.0-blue.svg)](CHANGELOG.pt-BR.md)
[![Licença](https://img.shields.io/badge/licença-MIT-green.svg)](LICENSE)
[![Padrões](https://img.shields.io/badge/padrões-Keep%20a%20Changelog-orange.svg)](CHANGELOG.pt-BR.md)

[English](README.md) | [Português do Brasil](README.pt-BR.md)

</div>

---

## Visão Geral

O **Clube AI Marketplace** fornece um modelo de distribuição unificado para skills de codificação em IA, agentes especialistas e fluxos determinísticos de auditoria através de múltiplos harnesses heterogêneos de IA:
- **Claude Code** (`.claude-plugin/`)
- **Oh My Pi (OMP)** (`.omp-plugin/`)
- **Cursor** (`.cursor-plugin/`)
- **Codex / OpenAI Agents** (`.agents/plugins/`)
- **OpenCode V2** (`.opencode-plugin/` + adaptadores `.opencode/`)

Cada host lê seu catálogo nativo de marketplace a partir da raiz do repositório, consumindo plugins modulares definidos sob `plugins/` (como `plugins/clube`). O OpenCode V2 não tem marketplace nativo — ele consome `opencode.json` além dos adaptadores TypeScript em `.opencode/plugins/`.

---

## Estrutura do Repositório

```
clube-marketplace/
├── .claude-plugin/marketplace.json     # Catálogo do marketplace para Claude Code
├── .omp-plugin/marketplace.json        # Catálogo do marketplace para Oh My Pi
├── .cursor-plugin/marketplace.json     # Catálogo do marketplace para Cursor
├── .agents/plugins/marketplace.json    # Catálogo do marketplace para Codex
├── .opencode-plugin/marketplace.json   # Catálogo do marketplace para OpenCode V2
├── opencode.json                       # Configuração do OpenCode V2 (plugins + agentes)
├── .opencode/
│   ├── opencode.json                   # Configuração do OpenCode V2 (paths relativos portáveis)
│   └── plugins/                        # Adaptadores de plugin para OpenCode
│       ├── clube/index.ts              # Adaptador Clube: 7 skills + 6 comandos
│       └── code-review/index.ts        # Adaptador code review: 1 skill + 1 comando
├── Makefile                            # Alvos operacionais (check, audit, sync, init)
├── AGENTS.md                           # Instruções canônicas e Project Profile
├── CLAUDE.md                           # Ponteiro -> @AGENTS.md
├── GEMINI.md                           # Ponteiro -> @AGENTS.md
├── .cursorrules                        # Ponteiro -> @AGENTS.md
├── bin/
│   └── clube-config                    # Lançador enxuto para a CLI em Python
├── clube_cli/                          # Implementação da CLI (coberta por testes)
│   ├── cli.py                          # Despacho de comandos
│   ├── check.py                        # Validador de integridade do repositório
│   ├── harness.py                      # Mecanismo de detecção do host ativo
│   ├── runlog.py                       # Utilitários para registro estruturado de eventos
│   └── sync.py                         # Sincronizador de ponteiros (@AGENTS.md)
├── tests/                              # Suíte pytest (rode com `make test`)
├── .clube/
│   └── audit-last.json                 # Runlog estruturado de auditoria e estado persistente
└── plugins/
    └── clube/                          # Plugin principal do Clube (v0.5.0)
        ├── .claude-plugin/plugin.json
        ├── .cursor-plugin/plugin.json
        ├── .codex-plugin/plugin.json
        ├── .omp-plugin/plugin.json
        ├── .opencode-plugin/plugin.json
        ├── scripts/                    # Scripts de auditoria estática e motor de UI ASCII
        │   ├── ui.py                   # Caixas ASCII, badges, tabelas e barras de saúde
        │   ├── audit-all.py            # Executor unificado de auditoria 360°
        │   ├── audit-privacy.py        # Verificador estático de LGPD/PII
        │   ├── audit-performance.py    # Verificador de chunk recovery e resiliência
        │   ├── audit-seo.py            # Verificador de SEO e LLM discovery (/llms.txt)
        │   └── audit-tracking.py       # Verificador de cookies e deduplicação Meta CAPI
        ├── commands/                   # Comandos slash (/audit, /init, /help, etc.)
        ├── agents/                     # Subagentes especialistas nomeados
        │   ├── expert-seo.md           # SEO técnico, GEO e Schema.org JSON-LD
        │   ├── expert-tracking.md      # Atribuição, Meta CAPI e cookies no domínio raiz
        │   ├── expert-privacy.md       # LGPD/GDPR, máscara de PII e higienização Sentry
        │   ├── expert-performance.md   # Recuperação de chunks SPA, cache e tuning
        │   └── clube-auditor.md        # Coordenador de auditoria 360° (somente leitura)
        └── skills/                     # Skills modulares de divulgação progressiva
            ├── clube-architecture/     # 5 pilares fundamentais e constituição de engenharia
            ├── init/                   # Onboarding e Project Profile
            ├── saas-seo-geo/           # SEO técnico, GEO e /llms.txt
            │   └── references/         # Schemas profundos, DDLs e guias de crawling
            ├── marketing-attribution-analytics/ # Atribuição, CAPI e cookies
            │   └── references/         # Payloads CAPI, higiene de cookies e DDLs
            ├── data-privacy-observability/      # LGPD/GDPR, PII e telemetria
            │   └── references/         # Funções de máscara, higienização Sentry e DDLs
            └── fullstack-performance-resilience/# Recuperação de chunks, cache e tuning
                └── references/         # Recuperação Vite, headers de borda e índices DB
    └── code-review/                    # Plugin de code review (v0.1.0, versionado à parte)
        ├── .{claude,cursor,codex,omp,opencode}-plugin/plugin.json
        ├── commands/review.md          # /code-review:review
        ├── agents/reviewer.md          # Revisor somente leitura (classe critique)
        └── skills/code-review/
            ├── SKILL.md                # Checklist geral, escala de severidade e veredito
            └── references/             # go.md, typescript.md, rust.md (carregados sob demanda)
```

---

## Instalação por AI Host

### Claude Code
```bash
/plugin marketplace add git@github.com:clubedepontos/clube-marketplace.git
/plugin install clube@clube
/plugin install code-review@clube
```

### Oh My Pi (OMP)
```bash
/marketplace add https://github.com/clubedepontos/clube-marketplace
/marketplace install --scope project clube@clube
/marketplace install --scope project code-review@clube
```
*Nota: Ao utilizar agentes customizados no OMP, execute `/clube:omp-setup` uma vez para configurar as sobreposições de modelo.*

### Cursor
Adicione como marketplace de equipe via **Configurações → Plugins**, ou crie um link simbólico para desenvolvimento local:
```bash
mkdir -p ~/.cursor/plugins/local
ln -s "$(pwd)/plugins/clube" ~/.cursor/plugins/local/clube
ln -s "$(pwd)/plugins/code-review" ~/.cursor/plugins/local/code-review
```

### Codex
```bash
codex plugin marketplace add clubedepontos/clube-marketplace --ref main
codex plugin install clube --source clube
codex plugin install code-review --source clube
```

### OpenCode V2

O OpenCode V2 não tem marketplace nativo — os plugins são conectados via `opencode.json`.
Cada adaptador vive em `.opencode/plugins/<plugin>/` com um `package.json` (apontando para
`@opencode/plugin`); rode `npm install` (ou `bun install`) lá uma vez e depois referencie
o adaptador no `opencode.json` do seu projeto:

```bash
# A partir deste repositório (desenvolvimento local)
cd .opencode/plugins/clube && npm install
cd ../code-review && npm install
```

Depois adicione ao `opencode.json` do seu projeto:

```json
{
  "plugins": [
    "/caminho/para/clube-marketplace/.opencode/plugins/clube",
    "/caminho/para/clube-marketplace/.opencode/plugins/code-review"
  ],
  "agents": {
    "expert-seo": { "mode": "subagent", "system": "/caminho/para/clube-marketplace/plugins/clube/agents/expert-seo.md" },
    "expert-tracking": { "mode": "subagent", "system": "/caminho/para/clube-marketplace/plugins/clube/agents/expert-tracking.md" },
    "expert-privacy": { "mode": "subagent", "system": "/caminho/para/clube-marketplace/plugins/clube/agents/expert-privacy.md" },
    "expert-performance": { "mode": "subagent", "system": "/caminho/para/clube-marketplace/plugins/clube/agents/expert-performance.md" },
    "clube-auditor": { "mode": "subagent", "system": "/caminho/para/clube-marketplace/plugins/clube/agents/clube-auditor.md" },
    "reviewer": { "mode": "subagent", "system": "/caminho/para/clube-marketplace/plugins/code-review/agents/reviewer.md" }
  }
}
```

Os sinais são os mesmos em todos os harnesses: skills (`/skill init`, `/skill clube-architecture`, …),
comandos slash (`/clube:init`, `/clube:audit`, `/clube:audit-seo`, `/code-review:review`, …) e
subagentes nomeados (`expert-seo`, `reviewer`, …). Os agentes não carregam `model` — herdam o
modelo da sessão — mantendo o marketplace independente de provedor. Este repositório já entrega
um `opencode.json` e `.opencode/opencode.json` prontos para uso (paths relativos portáveis,
resolvidos quando o OpenCode roda dentro do checkout).

---

## Agentes Especialistas de IA (`plugins/clube/agents`)

O Clube fornece 5 agentes especialistas de primeira classe declarados com contratos estritos de frontmatter YAML, roteamento de capacidades abstratas (`reasoning`, `code`, `critique`) e permissões de ferramentas escopadas:

| Agente | Classe de Capacidade | Ferramentas | Foco e Responsabilidades Principais |
| :--- | :--- | :--- | :--- |
| `expert-seo` | `reasoning` / `code` | Read, Write, Edit, Grep, Glob, Bash | SEO técnico, Generative Engine Optimization (GEO), Schema.org JSON-LD, descoberta via `/llms.txt` e `/llms-full.txt`, tags OpenGraph e limites estritos de indexação (`noindex` na aplicação autenticada). |
| `expert-tracking` | `code` / `reasoning` | Read, Write, Edit, Grep, Glob, Bash | Atribuição de marketing, Meta Pixel no navegador e Conversions API (CAPI) no servidor, deduplicação via `event_id`, higiene de cookies primários no domínio raiz e persistência de `acquisition_context` JSONB no banco de dados. |
| `expert-privacy` | `reasoning` / `code` | Read, Write, Edit, Grep, Glob, Bash | Conformidade LGPD/GDPR, princípio de "log do formato, não do dado", mascaramento determinístico de PII (CPF, e-mail, telefone), higienização de payloads de erro no Sentry e logs de auditoria. |
| `expert-performance` | `code` / `reasoning` | Read, Write, Edit, Grep, Glob, Bash | Performance fullstack, recuperação de chunks SPA (`vite:preloadError`, `router.onError` com proteção contra loop infinito de recarga), headers de cache CDN (`immutable`), tuning de cgroups em containers (`automaxprocs`) e otimização de queries de banco. |
| `clube-auditor` | `reasoning` / `critique` | Read, Grep, Glob, Bash *(somente leitura)* | Coordenador de prontidão para produção 360° (somente leitura), executando scripts detectores determinísticos em Python, analisando `.clube/audit-last.json`, priorizando achados e sintetizando relatórios de correção em 4 fases. |

---

## Skills Inclusas (`plugins/clube`)

Todas as skills verticais de SaaS seguem a **Arquitetura de Divulgação Progressiva**, apresentando pontos de entrada de ativação enxutos (`SKILL.md` < 100 linhas) suportados por 15 guias de referência temática abrangentes em `references/`:

| Skill | Guias de Referência | Foco |
| :--- | :--- | :--- |
| `clube:init` | — | Onboarding guiado de projetos e geração do `Project Profile` em `AGENTS.md` e `CLAUDE.md`. |
| `clube:clube-architecture` | — | Constituição de engenharia e disciplina arquitetural (5 pilares fundamentais: plugins modulares multi-harness, arquitetura híbrida de auditoria, contrato de saída em 4 fases, persistência de runlog, paridade SemVer). |
| `clube:saas-seo-geo` | `meta-social.md`<br>`json-ld-schemas.md`<br>`geo-llmstxt.md`<br>`crawling-sitemaps.md` | SEO técnico e Generative Engine Optimization (GEO) para SaaS, separação estrita de LP vs App (`noindex`), tags de metadados/OpenGraph, Schema.org JSON-LD e especificações de `/llms.txt`. |
| `clube:marketing-attribution-analytics` | `first-touch-cookies.md`<br>`deduplication-hygiene.md`<br>`server-side-capi.md`<br>`database-attribution.md` | Rastreamento ponta a ponta, modelos de atribuição, cookies primários de first-touch no domínio raiz, deduplicação Meta CAPI via `event_id` e persistência de `acquisition_context JSONB`. |
| `clube:data-privacy-observability` | `pii-masking-shape.md`<br>`sentry-observability-scrubbing.md`<br>`compliance-retention.md` | Conformidade LGPD/PII em logs, APM, traces, telemetria, princípio de "log do formato, não do dado", funções auxiliares de mascaramento, proibição de serialização cega de structs (`%+v`, `zap.Any`) e higienização de erros. |
| `clube:fullstack-performance-resilience` | `chunk-recovery.md`<br>`caching-edge-headers.md`<br>`runtime-tuning.md`<br>`db-indexing-queries.md` | Otimização de runtime (Node/Bun/Go/Python), resiliência de deploy, recuperação de chunks SPA (`vite:preloadError`, `router.onError`), headers de cache CDN (`immutable`), cgroups em containers (`automaxprocs`) e tuning de queries de banco. |
---

## Comandos Slash

| Comando Slash | Foco |
| :--- | :--- |
| `/clube:audit` (ou `/audit`) | Auditoria unificada 360° de prontidão para produção em SaaS cobrindo todos os 4 pilares de engenharia (Privacidade, Performance, SEO/GEO, Rastreamento). |
| `/clube:audit-privacy` | Audita logging cego de structs, PII em query strings, logs de domínios sem máscara e cardinalidade de métricas. |
| `/clube:audit-performance` | Audita recuperação de chunks SPA (prevenção de 404), headers de cache CDN, pools de conexão e limites de container. |
| `/clube:audit-seo` | Audita `/llms.txt`, proteção contra indexação de rotas privadas (`noindex`), tags OpenGraph e dados estruturados Schema.org. |
| `/clube:audit-tracking` | Audita cookies no domínio raiz, deduplicação no Meta CAPI (`event_id`) e contexto de aquisição no banco de dados. |
| `/clube:init` (or `/init`, `$init`) | Onboarding guiado do projeto, pré-validação de conexões de banco de dados, mapeamento de papéis de agentes e geração do Project Profile. |
| `/clube:omp-setup` | (Exclusivo OMP) Configura sobreposições de modelo para agentes do plugin, garantindo despacho suave de subagentes. |
| `/clube:help` (ou `/help`) | Exibe visão geral completa dos comandos, skills e princípios fundamentais de engenharia. |

## Plugin de Code Review (`plugins/code-review`)

Um plugin separado, versionado de forma independente do `clube` (atualmente `v0.1.0`), para code review estruturado e baseado em evidências em qualquer projeto.

| Componente | Nome | Foco |
| :--- | :--- | :--- |
| Comando | `/code-review:review` | Revisa as mudanças staged (ou, na falta delas, a branch atual), uma branch (`<branch>`) ou um pull request (`#<número>`). |
| Agente | `reviewer` | Somente leitura, classe `critique`. Carrega só as regras das linguagens presentes no diff, aplica as convenções do `AGENTS.md` do projeto e responde `APPROVE` ou `CHANGES-REQUESTED`. |
| Skill | `code-review:code-review` | Checklist geral (corretude, tratamento de erros, nomes, performance, segurança, testes, contratos de API, convenções) e escala de severidade, com `references/go.md`, `references/typescript.md` e `references/rust.md`. |

---

## Comandos Operacionais da CLI e Makefile

O repositório inclui um utilitário de linha de comando (`bin/clube-config`) e alvos correspondentes no `Makefile`:

```bash
# Audita detecção do harness ativo, catálogos de marketplace e integridade dos plugins
make check
./bin/clube-config check

# Roda a suíte de testes em Python (pytest via uv)
make test
./bin/clube-config test

# Verifica dependências obrigatórias e opcionais da toolchain (python3, uv, pytest, make, git)
make doctor
./bin/clube-config doctor

# Executa auditoria determinística 360° de prontidão para produção em SaaS
make audit
./bin/clube-config audit [all|privacy|performance|seo|tracking]

# Sincroniza arquivos ponteiro de harness (@AGENTS.md) entre subdiretórios
make sync
./bin/clube-config sync [DIR]

# Inicializa configuração de IA do projeto e sincroniza ponteiros de harness
make init
./bin/clube-config init [DIR]

# Instala a CLI clube-config em ~/.local/bin
make install-cli
./bin/clube-config install
```

---

## Princípios Fundamentais de Arquitetura

O Clube AI Marketplace é regido pelos **5 Pilares Obrigatórios** definidos na skill `clube:clube-architecture`:

1. **Padrão de Plugins Modulares Multi-Harness:** Todos os harnesses de IA (Claude Code, Cursor, Codex, Oh My Pi, OpenCode V2) consomem plugins modulares a partir de `plugins/<nome>/` através dos catálogos raiz de marketplace.
2. **Arquitetura Híbrida de Auditoria:** Scripts estáticos determinísticos em Python (`plugins/clube/scripts/`) executam verificações de base de forma rápida, persistem o estado estruturado em `.clube/audit-last.json` e alimentam os comandos slash dos LLMs com evidências concretas.
3. **Contrato de Saída em 4 Fases:** Cada comando, skill e fluxo de IA adere estritamente ao contrato de 4 fases:
   - `### 1. Plan`
   - `### 2. Execution`
   - `### 3. Summary`
   - `### 4. Recommended Actions`
4. **Persistência de Estado e Runlog Estruturado:** Auditorias automatizadas gravam artefatos estruturados de execução em `.clube/audit-last.json` com renderização visual no terminal (tabelas ASCII, barras de saúde gráfica, badges coloridos).
5. **Paridade SemVer e Documentação Bilíngue:** Todos os manifests versionados (`package.json` raiz, 5 catálogos de marketplace, 5 manifests do plugin `clube`) declaram estritamente versões SemVer idênticas (`0.5.0`), enquanto plugins adicionais como o `code-review` têm versão própria, mantida consistente entre seus manifests e entradas de catálogo. Toda a documentação mantém paridade bilíngue completa em Inglês (`README.md`, `CHANGELOG.md`) e Português do Brasil (`README.pt-BR.md`, `CHANGELOG.pt-BR.md`).
