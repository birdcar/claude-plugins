---
name: improve-skill
description: Analyze and optimize an existing Claude Code skill for better trigger precision, structure, instruction quality, and agent efficiency. Works on any skill anywhere.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, TodoWrite
argument-hint: [path to SKILL.md or skill name]
---

Analyze and improve an existing Claude Code skill.

## Resolve Skill Path

If `$ARGUMENTS` is provided:

- If it looks like a path (contains `/` or ends in `.md`), use it directly as the skill path
- If it looks like a name, search these locations in order:
  1. `.claude/skills/{name}/SKILL.md`
  2. `~/.claude/skills/{name}/SKILL.md`
  3. `plugins/*/skills/{name}/SKILL.md`
  4. `**/skills/{name}/SKILL.md`

If no `$ARGUMENTS` provided:

- Use Glob to discover all `**/skills/*/SKILL.md` files in the working directory
- Use AskUserQuestion to present the list and ask which skill to improve

If multiple matches are found for a name, use AskUserQuestion to ask the user to select one.

## Run the Workflow

Once the path is resolved, invoke the `skill-forge:improve-skill` skill with the resolved path as context, then follow that skill's pipeline to completion.
