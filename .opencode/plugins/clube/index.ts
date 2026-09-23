import { Plugin } from "@opencode/plugin"
import { readFileSync } from "node:fs"
import { join, dirname } from "node:path"
import { fileURLToPath } from "node:url"

const __dirname = dirname(fileURLToPath(import.meta.url))
const PLUGIN_ROOT = join(__dirname, "..", "..", "..", "plugins", "clube")

// Skill definitions — single source of truth lives in plugins/clube/skills/<id>/SKILL.md.
const SKILLS = [
  {
    id: "init",
    name: "Init",
    description: "Guided project onboarding for Clube projects — Project Profile in AGENTS.md/CLAUDE.md, database preflights, agent role mapping, memory vault check, and toolchain validation.",
    file: "skills/init/SKILL.md",
  },
  {
    id: "clube-architecture",
    name: "Clube Architecture",
    description: "Architectural constitution and engineering discipline for the Clube AI Marketplace. Defines the 5 core pillars: multi-harness modular plugins, hybrid audit architecture, 4-phase output contract, structured runlog persistence, and SemVer parity.",
    file: "skills/clube-architecture/SKILL.md",
  },
  {
    id: "saas-seo-geo",
    name: "SaaS SEO & GEO",
    description: "Specialist in technical SEO and Generative Engine Optimization (GEO) for SaaS applications and Landing Pages. Stack- and hosting-agnostic. Activate when configuring metadata, structured data, GEO (llms.txt), or crawler indexing.",
    file: "skills/saas-seo-geo/SKILL.md",
  },
  {
    id: "marketing-attribution-analytics",
    name: "Marketing Attribution & Analytics",
    description: "Specialist in metric instrumentation, tracking, and end-to-end attribution for SaaS products. Concrete for Meta and Google platforms while cookies, storage, deduplication, and routing are framework-agnostic.",
    file: "skills/marketing-attribution-analytics/SKILL.md",
  },
  {
    id: "data-privacy-observability",
    name: "Data Privacy & Observability",
    description: "Specialist in personal data handling across logs, telemetry, error tracking, and analytics. Activate when writing logs, configuring Sentry/tracing, handling PII, or auditing retention.",
    file: "skills/data-privacy-observability/SKILL.md",
  },
  {
    id: "fullstack-performance-resilience",
    name: "Fullstack Performance & Resilience",
    description: "Specialist in fullstack performance, runtime optimization, deployment resilience, and database tuning. Activate when configuring frontend builds, chunk recovery, edge caching, container runtimes, or database indexing.",
    file: "skills/fullstack-performance-resilience/SKILL.md",
  },
] as const

// Command definitions — every command reads its workflow body from
// plugins/clube/commands/<name>.md (frontmatter stripped), so the prompt templates
// never drift from the other harnesses. `omp-setup` is OMP-only and intentionally
// not registered.
const COMMANDS = [
  { name: "clube:init", file: "commands/init.md", skills: ["init"] },
  { name: "clube:help", file: "commands/help.md" },
  { name: "clube:audit", file: "commands/audit.md" },
  { name: "clube:audit-privacy", file: "commands/audit-privacy.md" },
  { name: "clube:audit-performance", file: "commands/audit-performance.md" },
  { name: "clube:audit-seo", file: "commands/audit-seo.md" },
  { name: "clube:audit-tracking", file: "commands/audit-tracking.md" },
] as const

function readSource(file: string): string {
  return readFileSync(join(PLUGIN_ROOT, file), "utf-8")
}

function stripFrontmatter(markdown: string): string {
  if (!markdown.startsWith("---")) return markdown.trim()
  const closing = markdown.indexOf("\n---")
  return closing === -1 ? markdown.trim() : markdown.slice(closing + 4).trim()
}

export default Plugin.define({
  id: "clube",
  name: "Clube AI Marketplace",
  version: "0.4.0",
  async setup(ctx) {
    // Register skills
    const skillRegistration = await ctx.skill.transform((editor) => {
      for (const skill of SKILLS) {
        editor.add({
          id: skill.id,
          name: skill.name,
          description: skill.description,
          path: join(PLUGIN_ROOT, skill.file),
          content: readSource(skill.file),
          autoinvoke: false,
        })
      }
    })

    // Register commands
    const commandRegistration = await ctx.command.transform((editor) => {
      for (const cmd of COMMANDS) {
        editor.add({
          name: cmd.name,
          description: readSource(cmd.file).match(/^description:\s*(.+)$/m)?.[1]?.trim() ?? cmd.name,
          execute: async ({ sessionID, prompt, delivery }) => {
            const body = stripFrontmatter(readSource(cmd.file))
            const args = prompt.text?.trim() ? `${prompt.text.trim()}\n\n` : ""
            await ctx.session.prompt({
              sessionID,
              text: `${args}Run the Clube command ${cmd.name}:\n\n${body}`,
              delivery,
              skills: cmd.skills,
            })
          },
        })
      }
    })

    // Return cleanup function
    return () => {
      skillRegistration.dispose()
      commandRegistration.dispose()
    }
  },
})