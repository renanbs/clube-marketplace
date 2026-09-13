# Brainstorm - Clube Modular Architecture (produto)

```yaml
problem:
  what: "A estrutura de plugins do Clube Marketplace está monolítica e sub-modularizada em comparação com o padrão de referência do LoopTech. Atualmente o plugin 'clube' não possui nenhum agente nomeado em 'plugins/clube/agents/' (apenas um .gitkeep vazio), suas 4 skills verticais densas (SEO, Tracking, Performance, Privacidade) acumulam centenas de linhas de schemas SQL, regexes e regras sem subpastas 'references/', e os manifestos de host e o validador 'clube-config check' não auditam agentes."
  why: "Sem agentes nomeados, hosts como Claude Code, Cursor, Codex e OMP não conseguem instanciar subagentes especialistas com restrições de ferramentas e modelos dedicados. Sem a decomposição em 'references/', os LLMs sofrem de 'token bloating' carregando centenas de linhas irrelevantes para o passo ativo, degradando a aderência a instruções."

users:
  - role: "Desenvolvedor / Usuário de IA em projetos Clube"
    job: "Invocar e despachar subagentes especialistas de domínio (SEO, Tracking, Performance, Privacidade) nos hosts suportados (Claude Code, Codex, Cursor, OMP)."
  - role: "Engenheiro de Plataforma Clube"
    job: "Manter e expandir skills e auditorias do marketplace com separação estrita de conceitos, alta manutenibilidade e verificação determinística via 'make check'."

success_criteria:
  - id: SC1
    statement: "Plugins do Clube contêm 5 agentes nomeados funcionais com frontmatter YAML (name, description, tools, model, readonly) e instruções de execução em 'plugins/clube/agents/'."
    evidence: "Arquivos 'expert-seo.md', 'expert-tracking.md', 'expert-privacy.md', 'expert-performance.md' e 'clube-auditor.md' criados e validados por 'bin/clube-config check'."
  - id: SC2
    statement: "As 4 skills verticais de SaaS possuem diretórios 'references/' com especificações profundas, schemas e padrões desacoplados do 'SKILL.md' principal."
    evidence: "Presença de subpastas 'references/' em 'saas-seo-geo', 'marketing-attribution-analytics', 'fullstack-performance-resilience' e 'data-privacy-observability', com seus respectivos 'SKILL.md' referenciando-as."
  - id: SC3
    statement: "Todos os manifestos de plugins e de marketplace (.claude-plugin, .cursor-plugin, .codex-plugin, .omp-plugin) registram explicitamente a lista de agentes."
    evidence: "make check passa com 100% de integridade confirmando registro dos agentes em todos os 4 hosts."
  - id: SC4
    statement: "O comando 'bin/clube-config check' e 'make check' validam a existência e integridade dos agentes declarados nos manifestos."
    evidence: "'make check' exibe contagem de agentes válidos e passa sem erros."
  - id: SC5
    statement: "A constituição arquitetural 'clube-architecture/SKILL.md' e a documentação bilíngue (README, CHANGELOG) documentam a nova modularidade e os agentes especialistas."
    evidence: "'clube-architecture/SKILL.md', 'README.md' e 'README.pt-BR.md' atualizados e consistentes."

constraints:
  - "Todos os agentes, skills, referências e documentação do repositório devem permanecer em inglês estrito (exceto README.pt-BR.md e CHANGELOG.pt-BR.md)."
  - "Manter paridade estrita de SemVer em todos os 9 manifestos (versão bumped para 0.2.0)."
  - "Zero dependências externas pip: scripts e validadores continuam executando sob Python 3 standard library pura."
  - "Não quebrar nenhum dos comandos existentes (/audit, /audit-seo, /audit-tracking, /audit-performance, /audit-privacy, /init, /help, /omp-setup)."

non_goals:
  - "Não vamos reescrever os scripts de auditoria em Python (audit-*.py) nesta tarefa, pois eles já foram calibrados e estão funcionando perfeitamente."
  - "Não vamos introduzir um servidor MCP de banco vetorial externo nesta fase (isso seria um plugin separado futuro caso necessário)."

invariants:
  - "make check e make audit devem continuar passando sem regressão."
  - "Todos os comandos slash e links entre arquivos devem ser válidos e funcionais."
  - "Contrato de 4 fases (Plan -> Execution -> Summary -> Recommended Actions) preservado em todos os comandos."

unknowns:
  - item: "Devemos bump de versão para 0.2.0 ou manter 0.1.0?"
    resolution: "Bump para 0.2.0 é a prática canônica do SemVer (Minor bump) já que adiciona novas capacidades (agentes nomeados e módulos de referências) sem quebrar compatibilidade reversa."

risks:
  - "Divergência entre a lista de agentes declarada nos manifestos de cada host."
    mitigation: "Atualizar 'bin/clube-config check' para auditar a paridade dos agentes em todos os hosts durante 'make check'."
```
