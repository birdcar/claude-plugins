---
name: forge-harness
description: Scaffold or audit an agentic harness in a target repository — AGENTS.md/CLAUDE.md, feature_list.json, progress.md, init.sh, session-handoff.md. Stack-aware verification commands.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Agent
  - AskUserQuestion
  - TaskCreate
  - TaskUpdate
  - TaskList
argument-hint: '[target path] [optional: create | audit | report]'
---

This command is a thin entry point into the `skill-forge:forge-harness` workflow.

## Entry Point

If `$ARGUMENTS` is provided, the first token is the target path and the optional second token is the intent (`create`, `audit`, or `report`).

If `$ARGUMENTS` is empty, use AskUserQuestion to ask:

> Which repository should I work on? (Provide an absolute path.)

Then:

> What's the intent?
>
> 1. **Create** — scaffold a new harness from scratch
> 2. **Audit** — score the existing harness across the 5 subsystems
> 3. **Report** — produce a shareable HTML assessment

## Delegation

Once you have the target path and intent, follow the `skill-forge:forge-harness` skill workflow exactly. That skill is the full orchestrator — this command only handles entry and hands off to it.

Do not duplicate the workflow logic here. Invoke `forge-harness` by following its instructions with the target path and intent as the starting input.
