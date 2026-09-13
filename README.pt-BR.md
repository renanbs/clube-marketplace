<div align="center">

# Clube Marketplace

**Marketplace centralizado e multi-harness de IA para skills, agentes, comandos e fluxos de trabalho sob medida para os produtos SaaS do Clube.**

[![Versão](https://img.shields.io/badge/versão-0.1.0-blue.svg)](CHANGELOG.pt-BR.md)
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

Cada host lê seu catálogo nativo de marketplace a partir da raiz do repositório, consumindo plugins modulares definidos sob `plugins/` (como `plugins/clube`).

---

## Estrutura do Repositório

```
clube-marketplace/
├── .claude-plugin/marketplace.json     # Catálogo do marketplace para Claude Code (v0.1.0)
├── .omp-plugin/marketplace.json        # Catálogo do marketplace para Oh My Pi (v0.1.0)
├── .cursor-plugin/marketplace.json     # Catálogo do marketplace para Cursor (v0.1.0)
├── .agents/plugins/marketplace.json    # Catálogo do marketplace para Codex (v0.1.0)
├── Makefile                            # Alvos operacionais (check, audit, sync, init)
├── AGENTS.md                           # Instruções canônicas e Project Profile
├── CLAUDE.md                           # Ponteiro -> @AGENTS.md
├── GEMINI.md                           # Ponteiro -> @AGENTS.md
├── .cursorrules                        # Ponteiro -> @AGENTS.md
├── bin/
│   └── clube-config                    # Utilitário CLI e verificador de integridade
├── scripts/
│   ├── lib-harness.sh                  # Mecanismo de detecção do host ativo
│   ├── lib-runlog.sh                   # Utilitários para registro estruturado de eventos
│   └── sync-harness-configs.sh         # Sincronizador de ponteiros (@AGENTS.md)
├── .clube/
│   └── audit-last.json                 # Runlog estruturado de auditoria e estado persistente
└── plugins/
    └── clube/                          # Plugin principal do Clube (v0.1.0)
        ├── .claude-plugin/plugin.json
        ├── .cursor-plugin/plugin.json
        ├── .codex-plugin/plugin.json
        ├── .omp-plugin/plugin.json
        ├── scripts/                    # Scripts de auditoria estática e motor de UI ASCII
        │   ├── ui.py                   # Caixas ASCII, badges, tabelas e barras de saúde
        │   ├── audit-all.py            # Executor unificado de auditoria 360°
        │   ├── audit-privacy.py        # Verificador estático de LGPD/PII
        │   ├── audit-performance.py    # Verificador de chunk recovery e resiliência
        │   ├── audit-seo.py            # Verificador de SEO e LLM discovery (/llms.txt)
        │   └── audit-tracking.py       # Verificador de cookies e deduplicação Meta CAPI
        ├── commands/                   # Comandos slash (/audit, /init, /help, etc.)
        ├── skills/                     # Skills modulares (skills/<name>/SKILL.md)
        └── agents/                     # Subagentes especialistas nomeados
```

---

## Instalação por AI Host

### Claude Code
```bash
/plugin marketplace add git@github.com:clubedepontos/clube-marketplace.git
/plugin install clube@clube
```

### Oh My Pi (OMP)
```bash
/marketplace add https://github.com/clubedepontos/clube-marketplace
/marketplace install --scope project clube@clube
```
*Nota: Ao utilizar agentes customizados no OMP, execute `/clube:omp-setup` uma vez para configurar as sobreposições de modelo.*

### Cursor
Adicione como marketplace de equipe via **Configurações → Plugins**, ou crie um link simbólico para desenvolvimento local:
```bash
mkdir -p ~/.cursor/plugins/local
ln -s "$(pwd)/plugins/clube" ~/.cursor/plugins/local/clube
```

### Codex
```bash
codex plugin marketplace add clubedepontos/clube-marketplace --ref main
codex plugin install clube --source clube
```

---

## Skills Inclusas (`plugins/clube`)

| Skill | Foco |
| :--- | :--- |
| `clube:init` | Onboarding guiado de projetos e geração do `Project Profile` em `AGENTS.md` e `CLAUDE.md`. |
| `clube:clube-architecture` | Constituição de engenharia e disciplina arquitetural (5 pilares fundamentais: plugins modulares multi-harness, arquitetura híbrida de auditoria, contrato de saída em 4 fases, persistência de runlog, paridade SemVer). |
| `clube:fullstack-performance-resilience` | Otimização de runtime (Node/Bun/Go/Python), resiliência de deploy, recuperação de chunks SPA (`vite:preloadError`, `router.onError`), headers de cache CDN (`immutable`), cgroups em containers (`automaxprocs`) e tuning de queries de banco. |
| `clube:saas-seo-geo` | SEO técnico e Generative Engine Optimization (GEO) para SaaS, separação estrita de LP vs App (`noindex`), tags de metadados/OpenGraph, Schema.org JSON-LD e especificações de `/llms.txt`. |
| `clube:marketing-attribution-analytics` | Rastreamento ponta a ponta, modelos de atribuição, cookies primários de first-touch no domínio raiz, deduplicação Meta CAPI via `event_id` e persistência de `acquisition_context JSONB`. |
| `clube:data-privacy-observability` | Conformidade LGPD/PII em logs, APM, traces, telemetria, princípio de "log do formato, não do dado", funções auxiliares de mascaramento, proibição de serialização cega de structs (`%+v`, `zap.Any`) e higienização de erros. |

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

---

## Comandos Operacionais da CLI e Makefile

O repositório inclui um utilitário de linha de comando (`bin/clube-config`) e alvos correspondentes no `Makefile`:

```bash
# Audita detecção do harness ativo, catálogos de marketplace e integridade dos plugins
make check
./bin/clube-config check

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

1. **Padrão de Plugins Modulares Multi-Harness:** Todos os harnesses de IA (Claude Code, Cursor, Codex, Oh My Pi) consomem plugins modulares a partir de `plugins/<nome>/` através dos catálogos raiz de marketplace.
2. **Arquitetura Híbrida de Auditoria:** Scripts estáticos determinísticos em Python (`plugins/clube/scripts/`) executam verificações de base de forma rápida, persistem o estado estruturado em `.clube/audit-last.json` e alimentam os comandos slash dos LLMs com evidências concretas.
3. **Contrato de Saída em 4 Fases:** Cada comando, skill e fluxo de IA adere estritamente ao contrato de 4 fases:
   - `### 1. Plan`
   - `### 2. Execution`
   - `### 3. Summary`
   - `### 4. Recommended Actions`
4. **Persistência de Estado e Runlog Estruturado:** Auditorias automatizadas gravam artefatos estruturados de execução em `.clube/audit-last.json` com renderização visual no terminal (tabelas ASCII, barras de saúde gráfica, badges coloridos).
5. **Paridade SemVer e Documentação Bilíngue:** Todos os 9 arquivos de manifesto declaram estritamente versões SemVer idênticas (`0.1.0`), acompanhados por paridade completa de documentação bilíngue em Inglês (`README.md`, `CHANGELOG.md`) e Português do Brasil (`README.pt-BR.md`, `CHANGELOG.pt-BR.md`).
