import { Plugin } from "@opencode/plugin"
import { readFileSync } from "node:fs"
import { join, dirname } from "node:path"
import { fileURLToPath } from "node:url"

const __dirname = dirname(fileURLToPath(import.meta.url))
const PLUGIN_ROOT = join(__dirname, "..", "..", "..", "plugins", "typesafe-ai")

// Skill definitions — single source of truth lives in
// plugins/typesafe-ai/skills/typesafe-jev/SKILL.md.
const SKILLS = [
  {
    id: "typesafe-jev",
    name: "TypeSafe Jev Decision Engine",
    description: "Replace expensive LLM text generation with fast, calibrated, typed decisions using TypeSafe AI's Jev model. Offload classification, intent routing, and schema validation to cut token costs and latency across Python, TypeScript, Go, and Rust.",
    file: "skills/typesafe-jev/SKILL.md",
  },
] as const

const COMMANDS = [
  { name: "typesafe-ai:optimize", file: "commands/optimize.md", skills: ["typesafe-jev"] },
] as const

function readSource(file: string): string {
  try {
    return readFileSync(join(PLUGIN_ROOT, file), "utf-8")
  } catch {
    return ""
  }
}

function stripFrontmatter(markdown: string): string {
  if (!markdown.startsWith("---")) return markdown.trim()
  const closing = markdown.indexOf("\n---")
  return closing === -1 ? markdown.trim() : markdown.slice(closing + 4).trim()
}

export default Plugin.define({
  id: "typesafe-ai",
  name: "TypeSafe AI (Jev)",
  version: "0.1.0",
  async setup(ctx) {
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

    return () => {
      skillRegistration.dispose()
      commandRegistration.dispose()
    }
  },
})
