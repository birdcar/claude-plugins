---
name: forge-skill
description: Create a production-grade Claude Code skill from a brain dump. Generates complete plugin scaffolding with optimized skills, agents, commands, and hooks.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, TodoWrite
argument-hint: [brain dump or description of the skill you want]
---

This command is a thin entry point into the `skill-forge:create-skill` workflow.

## Entry Point

If `$ARGUMENTS` is provided, treat the entire value as the brain dump.

If `$ARGUMENTS` is empty, use AskUserQuestion to ask:

> What skill do you want to build? Describe it in as much or as little detail as you like — a single sentence or a full brain dump both work.

## Delegation

Once you have the brain dump, follow the `skill-forge:create-skill` skill workflow exactly. That skill is the full orchestrator — this command only handles entry and hands off to it.

Do not duplicate the workflow logic here. Invoke `create-skill` by following its instructions with the brain dump text as the starting input.
