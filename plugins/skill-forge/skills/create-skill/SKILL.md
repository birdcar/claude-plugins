---
name: create-skill
description: >-
  Generates production-grade Claude Code skills from unstructured brain dumps.
  Creates complete plugin packages with optimized SKILL.md, agents, commands,
  and hooks. Use when the user asks to "create a skill", "build a skill",
  "make a skill that...", "write a skill for...", "generate a skill", or
  describes functionality they want as a reusable skill.
  Do NOT use for general code generation, documentation writing, or when
  the user wants to modify existing code that isn't a skill.
---

## Critical Rules

- ALWAYS use AskUserQuestion for decisions — never ask in plain text
- ALWAYS read shared knowledge base from `${CLAUDE_PLUGIN_ROOT}/shared/` before generating
- ALWAYS follow templates from `${CLAUDE_PLUGIN_ROOT}/shared/templates/`
- Generated SKILL.md files must be ≤500 lines with progressive disclosure
- Descriptions must be third-person with trigger phrases and negative cases
- Agent model assignments must be right-sized:
  - opus: complex generation, multi-step reasoning
  - sonnet: research, analysis, moderate tasks
  - haiku: scaffolding, validation, simple writes

## Step 1 — Intake & Analysis

Accept the brain dump from `$ARGUMENTS` or from the conversation context (if invoked from `forge-skill` command or by the user directly describing what they want).

Spawn the `skill-forge:intake-analyst` agent via the Agent tool, passing:

- The full brain dump text
- The current working directory path

The agent returns a structured classification containing:

- Skill type: `command-only` | `skill-only` | `command+skill` | `multi-skill-plugin`
- Workflow pattern (one of the 5 canonical types)
- Primitives needed
- Agent needs (count, roles, model assignments)
- Complexity estimate
- Similar/conflicting existing skills

Store this classification — it drives all subsequent steps.

## Step 2 — Target Selection

Use AskUserQuestion with the following options:

> Where should this skill be installed?
>
> 1. **Project skill** — `.claude/skills/` in the current working directory (available only in this project)
> 2. **Global skill** — `~/.claude/skills/` (available in all projects)
> 3. **Marketplace plugin** (Recommended) — published to a personal plugin marketplace repo

Include this context in the description:

> **Important limitations of project/global skills:**
>
> - No slash commands (`/command`) — commands only work in plugins
> - No custom agents — agent definitions require plugin.json
> - No hooks — hooks require `hooks/hooks.json` in a plugin directory
> - No shared files across skills — plugins provide `${CLAUDE_PLUGIN_ROOT}` for shared resources
>
> If the intake analysis identified commands, agents, hooks, or shared references, marketplace is the only viable target.

Based on selection:

- **Project** or **Global**: generate skill directory only (SKILL.md + `references/` subdirectory if needed). If the intake analysis requires commands, agents, or hooks, warn that these components will be omitted and recommend switching to marketplace.
- **Marketplace**: use AskUserQuestion to ask for the absolute path to the marketplace repo root (e.g. `~/Code/me/claude-plugins`). Store this as `$MARKETPLACE_ROOT`. Then generate full plugin scaffolding (plugin.json, package.json, tsconfig.json, all skill/agent/command/hook files) under `$MARKETPLACE_ROOT/plugins/`

## Step 3 — Confidence Gate

Score the current understanding across 5 dimensions (0–20 each):

| Dimension            | What it measures                           |
| -------------------- | ------------------------------------------ |
| Trigger Clarity      | Are the trigger phrases unambiguous?       |
| Workflow Definition  | Is the step-by-step process clear?         |
| Tool Requirements    | Are all needed tools identified?           |
| Output Specification | Is the expected output well-defined?       |
| Scope Boundaries     | Are in-scope and out-of-scope cases clear? |

**Threshold: ≥90 / 100 to proceed.**

If below threshold:

1. Identify which dimensions are under-scored
2. Use AskUserQuestion to ask 2–4 targeted clarifying questions per round
3. Re-score after each round
4. Loop until ≥90

Do not proceed to generation until the threshold is met.

## Step 4 — Codebase Research

If the target location already contains skills or related code:

Spawn the `skill-forge:skill-researcher` agent (Sonnet), passing:

- The target installation path
- The intake classification from Step 1

The agent examines:

- Existing SKILL.md files for naming and structural conventions
- Potential conflicts with the proposed skill name or trigger phrases
- Code patterns worth referencing in the new skill's instructions
- Related agent and command files

If the target is empty or greenfield (new directory), skip this step.

## Step 5 — Generation Plan

Read the following templates before generating:

- `${CLAUDE_PLUGIN_ROOT}/shared/templates/skill-template.md`
- `${CLAUDE_PLUGIN_ROOT}/shared/templates/agent-template.md`
- `${CLAUDE_PLUGIN_ROOT}/shared/templates/command-template.md`

Read relevant knowledge base docs as needed:

- `${CLAUDE_PLUGIN_ROOT}/shared/skill-anatomy.md` — structure rules
- `${CLAUDE_PLUGIN_ROOT}/shared/description-engineering.md` — description writing
- `${CLAUDE_PLUGIN_ROOT}/shared/anti-patterns.md` — what to avoid
- `${CLAUDE_PLUGIN_ROOT}/shared/agent-design.md` — agent definitions
- `${CLAUDE_PLUGIN_ROOT}/shared/workflow-patterns.md` — workflow structure
- `${CLAUDE_PLUGIN_ROOT}/shared/primitives-guide.md` — tool usage
- `${CLAUDE_PLUGIN_ROOT}/shared/local-config-pattern.md` — if intake flagged config needs (credentials, paths, PII)

Use AskUserQuestion to present the generation plan:

> Here's what I'll generate:
>
> **Skill name:** `{proposed-name}`
> **Description:** `{proposed-description}`
>
> **Components:**
>
> - SKILL.md ({estimated line count} lines)
> - {list of agents with models}
> - {command .md if applicable}
> - {hooks/hooks.json if applicable}
>
> **Workflow:** {1-sentence summary}
>
> Approve or adjust?
>
> 1. Approved — generate it
> 2. Adjust description
> 3. Change workflow
> 4. Add/remove components
> 5. Start over

Loop on adjustments until the user approves.

## Step 6 — Scaffolding & Writing

Use TodoWrite to track progress through this step.

**If target is Marketplace:**

1. Use AskUserQuestion to ask for the npm package scope (e.g. `@birdcar`, `@myorg`). Store as `$PACKAGE_SCOPE`.

2. Spawn `skill-forge:scaffold-writer` agent (Haiku) with:
   - Plugin name
   - Description
   - Version `"0.1.0"`
   - List of commands, agents, and skills to register
   - Marketplace repo root: `$MARKETPLACE_ROOT`
   - Package scope: `$PACKAGE_SCOPE`

   The scaffold-writer creates plugin.json, package.json, tsconfig.json, adds the tsconfig reference, and runs `bun run sync`.

3. Spawn `skill-forge:skill-generator` agent (Opus) with:
   - Intake classification
   - Research findings (if any)
   - Confidence-gate answers
   - Approved generation plan
   - Target path

   The skill-generator writes SKILL.md, agent .md files, command .md (if applicable), reference docs, and hooks/hooks.json (if applicable).

**If target is Project or Global:**

1. Create the skill directory at the target path
2. Spawn `skill-forge:skill-generator` agent (Opus) with the same inputs as above

## Step 7 — Validation

After all files are written, spawn the `skill-forge:skill-validator` agent (Haiku) via the Agent tool, passing the path to the newly created skill directory.

The validator performs:

1. **Structural checks** — frontmatter validity, naming, line count, progressive disclosure, tool restrictions
2. **Anti-pattern scan** — checks against `${CLAUDE_PLUGIN_ROOT}/shared/anti-patterns.md`
3. **Trigger test generation** — writes 20 test queries to `trigger-tests.md` alongside the SKILL.md

**If marketplace target**, also run:

```bash
bun run typecheck && bun run build && bun run format:check
```

Present the validator's report via AskUserQuestion:

- If CRITICAL failures exist: block delivery until fixed — loop back to fix and re-validate
- If HIGH failures exist: warn and recommend fixing before delivery
- Trigger tests are always generated regardless of pass/fail

Options:

1. "Looks good — finish" — proceed to delivery
2. "Fix the flagged issues" — address failures and re-validate

## Step 8 — Delivery

Summarize what was created:

- List all files written with their absolute paths
- Show the "getting started" invocation: the exact phrase or command to trigger the new skill
- If trigger tests were generated, remind the user to review `trigger-tests.md`
- If marketplace: remind to bump the version in plugin.json and run the marketplace's sync command before committing
- If marketplace: remind that `claude plugin marketplace update <marketplace-name>` must be run before `claude plugin update` will detect the new version
