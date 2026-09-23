import { Plugin } from "@opencode/plugin"
import { readFileSync } from "node:fs"
import { join, dirname } from "node:path"
import { fileURLToPath } from "node:url"

const __dirname = dirname(fileURLToPath(import.meta.url))
const PLUGIN_ROOT = join(__dirname, "..", "..", "..", "plugins", "code-review")

// Skill definitions — single source of truth lives in
// plugins/code-review/skills/code-review/SKILL.md.
const SKILLS = [
  {
    id: "code-review",
    name: "Code Review",
    description: "Cross-project code review discipline: correctness, naming, error handling, performance, security surface, test quality, and project conventions. Language-agnostic core with on-demand references (Go, TypeScript, Rust). Activate whenever reviewing a diff, PR, branch, or staged changes.",
    file: "skills/code-review/SKILL.md",
  },
] as const

const COMMANDS = [
  { name: "code-review:review", file: "commands/review.md", skills: ["code-review"] },
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
  id: "code-review",
  name: "Code Review",
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