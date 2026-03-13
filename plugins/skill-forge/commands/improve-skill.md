---
name: improve-skill
description: Analyze and optimize an existing Claude Code skill for better trigger precision, structure, instruction quality, and agent efficiency. Works on any skill anywhere.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, TodoWrite
argument-hint: [path or name] [optional improvement notes]
---

Analyze and improve an existing Claude Code skill.

## Parse Arguments

`$ARGUMENTS` may contain a skill path/name followed by an optional braindump of improvement ideas.

Parse `$ARGUMENTS` as follows:

1. **First token** — if it contains `/` or ends in `.md`, treat it as a path. Otherwise treat it as a skill name.
2. **Remaining text** (everything after the first token) — treat as the user's braindump describing specific improvements they want. This is optional; many invocations will only have a path.

Examples:

- `/improve-skill plugins/my-plugin/` — path only, no braindump
- `/improve-skill my-skill` — name only, no braindump
- `/improve-skill plugins/my-plugin/ I want better error handling and clearer step names` — path + braindump
- `/improve-skill my-skill the description triggers on too many unrelated queries` — name + braindump

## Resolve Skill Path

Using the first token from above:

- If it looks like a path (contains `/` or ends in `.md`), use it directly as the skill path
- If it looks like a name, search these locations in order:
  1. `.claude/skills/{name}/SKILL.md`
  2. `~/.claude/skills/{name}/SKILL.md`
  3. `plugins/*/skills/{name}/SKILL.md`
  4. `**/skills/{name}/SKILL.md`

If no `$ARGUMENTS` provided:

- Use Glob to discover all `**/skills/*/SKILL.md` files in the working directory
- Use AskUserQuestion to present the list and ask which skill to improve
- Then use AskUserQuestion to ask: "Do you have specific improvements in mind? Describe them, or select 'No — just analyze and suggest improvements'."

If multiple matches are found for a name, use AskUserQuestion to ask the user to select one.

## Run the Workflow

Once the path is resolved, invoke the `skill-forge:improve-skill` skill with both the resolved path and any braindump text as context, then follow that skill's pipeline to completion.
