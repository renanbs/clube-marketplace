# Brainstorm - Clube Modular Architecture (codigo)

```yaml
lane: M

subprojects:
  - name: "plugins/clube"
    path: "plugins/clube"
    stack: "markdown/yaml/python"
    responsibility: "Modular marketplace plugin containing specialized AI agents, decomposed domain skills, references subdirectories, slash commands, and deterministic Python audit scripts."
  - name: "clube-marketplace"
    path: "."
    stack: "bash/python/json"
    responsibility: "Marketplace root catalogs (.claude-plugin, .cursor-plugin, .codex-plugin, .omp-plugin, .agents), Makefile, harness pointers, and CLI distribution via bin/clube-config."

blast_radius:
  direct:
    - "plugins/clube/agents/expert-seo.md (New: technical SEO & GEO specialist agent)"
    - "plugins/clube/agents/expert-tracking.md (New: attribution & analytics instrumentation agent)"
    - "plugins/clube/agents/expert-privacy.md (New: data privacy, PII masking & telemetry agent)"
    - "plugins/clube/agents/expert-performance.md (New: fullstack performance & resilience agent)"
    - "plugins/clube/agents/clube-auditor.md (New: 360-degree audit coordinator & advisor agent)"
    - "plugins/clube/skills/saas-seo-geo/SKILL.md (Decomposed into core rules + references)"
    - "plugins/clube/skills/saas-seo-geo/references/ (New: meta-social.md, json-ld-schemas.md, geo-llmstxt.md, crawling-sitemaps.md)"
    - "plugins/clube/skills/marketing-attribution-analytics/SKILL.md (Decomposed into core rules + references)"
    - "plugins/clube/skills/marketing-attribution-analytics/references/ (New: first-touch-cookies.md, deduplication-hygiene.md, server-side-capi.md, database-attribution.md)"
    - "plugins/clube/skills/fullstack-performance-resilience/SKILL.md (Decomposed into core rules + references)"
    - "plugins/clube/skills/fullstack-performance-resilience/references/ (New: chunk-recovery.md, caching-edge-headers.md, runtime-tuning.md, db-indexing-queries.md)"
    - "plugins/clube/skills/data-privacy-observability/SKILL.md (Decomposed into core rules + references)"
    - "plugins/clube/skills/data-privacy-observability/references/ (New: pii-masking-shape.md, sentry-observability-scrubbing.md, compliance-retention.md)"
    - "plugins/clube/skills/clube-architecture/SKILL.md (Updated: 5 pillars, agent standards, references decomposition)"
    - "bin/clube-config (Updated: cmd_check auditing agents/*.md, frontmatter validity, and 0.2.0 SemVer parity)"
    - "package.json (Bumped to version 0.2.0)"
    - ".claude-plugin/marketplace.json (Bumped to version 0.2.0)"
    - ".omp-plugin/marketplace.json (Bumped to version 0.2.0)"
    - ".cursor-plugin/marketplace.json (Bumped to version 0.2.0)"
    - ".agents/plugins/marketplace.json (Bumped to version 0.2.0)"
    - "plugins/clube/.claude-plugin/plugin.json (Bumped to 0.2.0 with agents pointer)"
    - "plugins/clube/.cursor-plugin/plugin.json (Bumped to 0.2.0 with agents pointer)"
    - "plugins/clube/.codex-plugin/plugin.json (Bumped to 0.2.0 with agents pointer)"
    - "plugins/clube/.omp-plugin/plugin.json (Bumped to 0.2.0 with agents pointer)"
    - "plugins/clube/commands/help.md (Updated: reflect 5 agents and modular skills)"
    - "README.md (Updated: document agents, references architecture, and v0.2.0 capabilities in EN)"
    - "README.pt-BR.md (Updated: document agents, references architecture, and v0.2.0 capabilities in PT-BR)"
    - "CHANGELOG.md (Updated: v0.2.0 release notes in Keep a Changelog standard)"
    - "CHANGELOG.pt-BR.md (Updated: v0.2.0 release notes in Portuguese)"
  indirect:
    - "Slash command invocations (/audit, /audit-seo, /audit-tracking, /audit-performance, /audit-privacy, /init, /help, /omp-setup)"
    - "AI host subagent orchestrators (Claude Code Task/Agent, OMP hub subagents, Cursor Composer, Codex CLI)"
  risks:
    - risk: "Inconsistent or malformed YAML frontmatter in agent files causing parser failure in strict harnesses (e.g. OMP or Claude Code)."
      mitigation: "Enforce strict frontmatter schema (name, description, tools, model, readonly) and validate via bin/clube-config check."
    - risk: "Dangling or broken relative markdown links between SKILL.md and references/*.md files."
      mitigation: "Verify cross-links using relative filesystem paths and validate during skill decomposition."
    - risk: "SemVer mismatch or forgotten manifest when bumping 9 separate manifest files."
      mitigation: "Automate validation via bin/clube-config check, asserting that all 9 manifests declare exactly 0.2.0."

construction:
  approach:
    - "Phase 1: Implement 5 named specialist agents in plugins/clube/agents/ with complete frontmatter and actionable domain instructions."
    - "Phase 2: Refactor the 4 dense SaaS skills by extracting in-depth schemas, code snippets, and deep rules into references/ subdirectories, retaining lean high-level activation triggers in SKILL.md."
    - "Phase 3: Upgrade bin/clube-config check to audit agent definitions, frontmatter properties, skill references, and verify 0.2.0 SemVer parity across all 9 manifests."
    - "Phase 4: Synchronize all 9 manifests (.claude-plugin, .cursor-plugin, .codex-plugin, .omp-plugin, .agents, package.json) to version 0.2.0."
    - "Phase 5: Update the architectural constitution (clube-architecture/SKILL.md), slash command help, and bilingual documentation (README.md, README.pt-BR.md, CHANGELOG.md, CHANGELOG.pt-BR.md)."
  patterns_to_reuse:
    - "LoopTech/Expo Multi-Harness Plugin Standard: Unified distribution via host-specific plugin.json pointing to canonical plugins/clube/ directory."
    - "Pure Python 3 Standard Library: Zero-dependency inspection in bin/clube-config check using json, os, and re."
    - "Progressive Disclosure Documentation Pattern: Compact SKILL.md for primary routing and references/*.md for specialized reference material."
    - "Standardized 4-Phase Output Contract: Plan -> Execution -> Summary -> Recommended Actions across all commands."
    - "Strict SemVer Parity: Synchronous version bumping across all 9 manifest files."
  components:
    - component: "plugins/clube/agents/"
      role: "Specialist subagent definition files for domain-specific AI delegation."
      details:
        - "expert-seo.md: Specialist in technical SEO, Generative Engine Optimization (GEO), metadata, JSON-LD schemas, and indexing boundaries."
        - "expert-tracking.md: Specialist in marketing attribution, Meta Pixel, GA4, CAPI server-side tracking, cookie domain hygiene, and DB persistence."
        - "expert-performance.md: Specialist in fullstack performance, SPA chunk recovery, HTTP edge caching headers, database indexing, and runtime tuning."
        - "expert-privacy.md: Specialist in LGPD/GDPR compliance, PII masking, shape logging, Sentry scrubbing, and data retention policies."
        - "clube-auditor.md: 360-degree audit coordinator executing python scripts and formatting structured 4-phase remediation plans."
    - component: "plugins/clube/skills/*/references/"
      role: "Modular domain deep-dives decoupled from the main skill activation files."
      details:
        - "saas-seo-geo/references/: meta-social.md, json-ld-schemas.md, geo-llmstxt.md, crawling-sitemaps.md"
        - "marketing-attribution-analytics/references/: first-touch-cookies.md, deduplication-hygiene.md, server-side-capi.md, database-attribution.md"
        - "fullstack-performance-resilience/references/: chunk-recovery.md, caching-edge-headers.md, runtime-tuning.md, db-indexing-queries.md"
        - "data-privacy-observability/references/: pii-masking-shape.md, sentry-observability-scrubbing.md, compliance-retention.md"
    - component: "bin/clube-config (cmd_check)"
      role: "Deterministic test and validation harness for repository and plugin integrity."
      details:
        - "Verifies presence of 5 agents in plugins/clube/agents/ with valid YAML frontmatter."
        - "Verifies modular references/ directories in all 4 SaaS skills."
        - "Verifies SemVer parity target 0.2.0 across all 9 manifests."
        - "Ensures zero regressions in existing harness and pointer checks."

decisions:
  - id: D1
    title: "Agent Definitions and Model Class Routing"
    context: "AI harnesses (OMP, Claude Code, Cursor, Codex) require agent definitions in plugins/clube/agents/. How should agent frontmatter specify model classes and tool restrictions?"
    options:
      - id: opt1
        name: "Generic Capability Classes (reasoning, code, inherit) with Standard Tool Allocations"
        pros:
          - "Host-agnostic: Works across OMP, Claude Code, Cursor, and Codex without proprietary lock-in."
          - "Graceful fallback when specific proprietary models are unavailable."
          - "Complies with LoopTech multi-harness agent standards."
        cons:
          - "Requires harness-level mapping to resolve abstract capability classes into concrete provider models."
      - id: opt2
        name: "Vendor-Specific Hardcoded Model Strings (e.g. claude-3-5-sonnet-20241022, gpt-4o)"
        pros:
          - "Direct binding on specific single-vendor setups."
        cons:
          - "Breaks across heterogeneous harnesses and local/offline AI environments."
          - "High maintenance overhead as vendor model IDs deprecate."
    decision: opt1
    rationale: "Clube Marketplace distributes across multiple AI hosts. Using abstract capability classes (e.g. reasoning for audit/analysis, code for implementation) paired with explicit tool boundaries guarantees full portability and longevity."

  - id: D2
    title: "Skill Decomposition Pattern into references/ Subdirectories"
    context: "Currently, the 4 SaaS skills are dense monolithic documents (200-350 lines) combining introductory principles, edge-case rules, extensive JSON-LD schemas, SQL DDLs, and multi-framework code blocks. How should they be structured?"
    options:
      - id: opt1
        name: "Progressive Disclosure: Lean SKILL.md (<100 lines) + references/*.md Topic Files"
        pros:
          - "Prevents token bloating: AI agents load the core skill for routing and only fetch specific references when executing a subtask."
          - "Greatly improves maintainability: Individual reference guides (e.g. JSON-LD schemas, CAPI integration) can be updated in isolation."
          - "Aligns with LoopTech modular architecture constitution."
        cons:
          - "Increases file count across the plugins directory."
      - id: opt2
        name: "Monolithic Single-File SKILL.md per Domain (Status Quo)"
        pros:
          - "Fewer files in the filesystem."
        cons:
          - "LLMs incur massive prompt overhead on simple tasks."
          - "Risk of context truncation and degraded instruction adherence."
    decision: opt1
    rationale: "Progressive disclosure optimizes token economy and LLM reasoning accuracy. Decomposing deep schemas and implementation guides into references/ subdirectories allows subagents to load only the relevant domain slices on demand."

  - id: D3
    title: "SemVer Release Strategy (Minor Bump 0.2.0 vs Patch 0.1.1 vs Pin 0.1.0)"
    context: "This restructuring introduces 5 first-class named agents, modular reference sub-specifications, and agent integrity auditing in bin/clube-config. What version increment is appropriate?"
    options:
      - id: opt1
        name: "Minor Version Bump to 0.2.0"
        pros:
          - "Strictly complies with Semantic Versioning 2.0 (adding new functional capabilities—agents, references—in a backward-compatible manner)."
          - "Clearly signals the architectural modularity milestone to marketplace users."
        cons:
          - "Requires updating all 9 manifest files simultaneously."
      - id: opt2
        name: "Patch Version Bump to 0.1.1"
        pros:
          - "Minimal version change."
        cons:
          - "Misleading: 5 new agents and structural decomposition are substantial features, not mere bug fixes."
      - id: opt3
        name: "Retain 0.1.0"
        pros:
          - "Zero manifest changes."
        cons:
          - "Violates release hygiene and obscures significant architectural additions."
    decision: opt1
    rationale: "Bumping to 0.2.0 accurately reflects the introduction of new architectural capabilities (named agents, references hierarchy, agent validation) while preserving 100% backward compatibility for all existing slash commands and scripts."

code_success_criteria:
  - id: CC1
    statement: "Plugins directory contains 5 valid named agent files in plugins/clube/agents/ with standard YAML frontmatter (name, description, tools, model, readonly) and actionable instructions."
    verification: "test -f plugins/clube/agents/expert-seo.md && test -f plugins/clube/agents/expert-tracking.md && test -f plugins/clube/agents/expert-privacy.md && test -f plugins/clube/agents/expert-performance.md && test -f plugins/clube/agents/clube-auditor.md"
  - id: CC2
    statement: "All 4 SaaS skills are decomposed into lean SKILL.md files accompanied by modular references/ subdirectories containing deep-dive guides and schemas."
    verification: "test -d plugins/clube/skills/saas-seo-geo/references && test -d plugins/clube/skills/marketing-attribution-analytics/references && test -d plugins/clube/skills/fullstack-performance-resilience/references && test -d plugins/clube/skills/data-privacy-observability/references"
  - id: CC3
    statement: "SemVer parity is strictly verified across all 9 manifest files aligned at version 0.2.0."
    verification: "./bin/clube-config check | grep 'SemVer parity: all manifests aligned at v0.2.0'"
  - id: CC4
    statement: "The check routine in bin/clube-config audits agents and skill references, and make check passes with 100% integrity across all checks."
    verification: "make check && make audit"

async_hint:
  waves:
    - wave: 1
      tasks:
        - name: "Task 1: Create 5 Named Specialist Agents"
          target: "plugins/clube/agents/"
          files:
            - "expert-seo.md"
            - "expert-tracking.md"
            - "expert-privacy.md"
            - "expert-performance.md"
            - "clube-auditor.md"
        - name: "Task 2: Decompose 4 SaaS Skills into Modular references/"
          target: "plugins/clube/skills/"
          files:
            - "saas-seo-geo/SKILL.md & references/"
            - "marketing-attribution-analytics/SKILL.md & references/"
            - "fullstack-performance-resilience/SKILL.md & references/"
            - "data-privacy-observability/SKILL.md & references/"
    - wave: 2
      tasks:
        - name: "Task 3: Upgrade bin/clube-config Check Engine & Bump 9 Manifests to 0.2.0"
          target: "bin/clube-config & manifest files"
          files:
            - "bin/clube-config"
            - "package.json"
            - ".claude-plugin/marketplace.json"
            - ".omp-plugin/marketplace.json"
            - ".cursor-plugin/marketplace.json"
            - ".agents/plugins/marketplace.json"
            - "plugins/clube/.claude-plugin/plugin.json"
            - "plugins/clube/.cursor-plugin/plugin.json"
            - "plugins/clube/.codex-plugin/plugin.json"
            - "plugins/clube/.omp-plugin/plugin.json"
        - name: "Task 4: Update Architecture Constitution, Slash Command Help & Bilingual Documentation"
          target: "Documentation & Architecture Skill"
          files:
            - "plugins/clube/skills/clube-architecture/SKILL.md"
            - "plugins/clube/commands/help.md"
            - "README.md"
            - "README.pt-BR.md"
            - "CHANGELOG.md"
            - "CHANGELOG.pt-BR.md"
    - wave: 3
      tasks:
        - name: "Task 5: End-to-End Validation & Verification Gate"
          target: "Workspace verification"
          command: "make check && make audit"
```
