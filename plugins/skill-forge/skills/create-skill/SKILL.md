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
- ALWAYS write contract.md, spec.md, and learnings.md to {skill-dir}/docs/ before generating skill artifacts
- Generated SKILL.md files must be <=500 lines with progressive disclosure
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
- Retrospective recommendation: `full` | `lightweight` | `none`

Store this classification — it drives all subsequent steps.

## Step 2 — Target + Name Selection

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
- **Marketplace**: use AskUserQuestion to ask for the absolute path to the marketplace repo root (e.g. `~/Code/me/claude-plugins`). Store this as `$MARKETPLACE_ROOT`.

After target selection, present the skill name via AskUserQuestion:

> **Proposed skill name:** `{kebab-case-name-from-intake}`
>
> This name determines the skill directory path and all internal references.
>
> 1. Confirm this name
> 2. Use a different name (provide your preferred name)

Derive the skill name from the intake classification (converted to kebab-case). The user confirms or adjusts.

Establish the skill directory path now:

- **Project**: `{cwd}/.claude/skills/{skill-name}/`
- **Global**: `~/.claude/skills/{skill-name}/`
- **Marketplace**: `{$MARKETPLACE_ROOT}/plugins/{skill-name}/`

Store this as `$SKILL_DIR` — the spec and all artifacts write here.

## Step 3 — Spec Formation Loop

Score the current understanding across 5 dimensions (0-20 each):

| Dimension            | What it measures                           |
| -------------------- | ------------------------------------------ |
| Trigger Clarity      | Are the trigger phrases unambiguous?       |
| Workflow Definition  | Is the step-by-step process clear?         |
| Tool Requirements    | Are all needed tools identified?           |
| Output Specification | Is the expected output well-defined?       |
| Scope Boundaries     | Are in-scope and out-of-scope cases clear? |

**Threshold: >=90 / 100 to proceed.**

If below threshold:

1. Identify which dimensions are under-scored
2. Use AskUserQuestion to ask 2-4 targeted clarifying questions per round
3. Re-score after each round
4. Loop until >=90

### Codebase Research (during this loop)

If the target location already contains skills or related code, spawn the `skill-forge:skill-researcher` agent (Sonnet) during this loop, passing:

- The target installation path
- The intake classification from Step 1

Run the researcher while gathering clarifications so its findings inform the spec. If the target is empty or greenfield, skip the researcher.

### Spec Generation (when >=90)

Read templates from `${CLAUDE_PLUGIN_ROOT}/shared/templates/`:

- `contract-template.md`
- `spec-template.md`

Read relevant knowledge base docs from `${CLAUDE_PLUGIN_ROOT}/shared/`:

- `skill-anatomy.md` — structure rules
- `description-engineering.md` — description writing
- `anti-patterns.md` — what to avoid
- `agent-design.md` — agent definitions
- `workflow-patterns.md` — workflow structure
- `primitives-guide.md` — tool usage
- `local-config-pattern.md` — if intake flagged config needs

Write the following files to `{$SKILL_DIR}/docs/`:

1. **contract.md** — Design intent: problem statement, goals, success criteria, scope boundaries, design decisions. Follow `contract-template.md`.

2. **spec.md** — Execution plan containing:
   - Component manifest (every file to create with purpose and estimated size)
   - Skill architecture (workflow pattern, agent interactions, data flow)
   - Per-component details (for each file: sections, key decisions, dependencies)
   - Execution plan with phases and parallelization strategy
   - Retrospective configuration (based on intake analyst's recommendation: full/lightweight/none)
   - Validation strategy (structural checks, anti-pattern targets, build verification)

   Follow `spec-template.md`.

3. **learnings.md** — Start with a header explaining its purpose. The file begins empty and accumulates observations over time from retrospective runs.

### Spec Approval

Present the spec for approval via AskUserQuestion:

> **Spec is ready for review.**
>
> The contract and spec have been written to `{$SKILL_DIR}/docs/`.
> Review the spec's component manifest and execution plan.
>
> 1. **Approved** — proceed to generation
> 2. **Needs changes** — I'll edit the documents and re-present
> 3. **Missing scope** — the spec doesn't cover something important
> 4. **Start over** — discard and restart from intake

Handle responses:

- **Approved**: proceed to Step 4.
- **Needs changes**: use the Edit tool to update contract.md and/or spec.md based on user feedback. Re-present for approval. Loop until approved.
- **Missing scope**: ask targeted questions via AskUserQuestion, update the spec, re-present.
- **Start over**: discard the docs directory and return to Step 1.

This single approval replaces both the old confidence gate exit and the old generation plan approval.

## Step 4 — Execute Spec

Read the approved `{$SKILL_DIR}/docs/spec.md` — this is the primary input for generation.

**If target is Marketplace:**

1. Use AskUserQuestion to ask for the npm package scope (e.g. `@birdcar`, `@myorg`). Store as `$PACKAGE_SCOPE`.

2. Spawn `skill-forge:scaffold-writer` agent (Haiku) with:
   - Plugin name
   - Description
   - Version `"0.1.0"`
   - Scaffolding details from the spec's component manifest
   - Marketplace repo root: `$MARKETPLACE_ROOT`
   - Package scope: `$PACKAGE_SCOPE`

   The scaffold-writer creates plugin.json, package.json, tsconfig.json, adds the tsconfig reference, and runs `bun run sync`.

3. Spawn `skill-forge:skill-generator` agent (Opus) with:
   - The approved spec.md as PRIMARY input
   - Target path: `$SKILL_DIR`

   The generator reads shared/ reference docs for writing quality but follows the spec for WHAT to create. It executes the spec's execution plan for ordering and parallelization, and reports any deviations from the spec.

4. If the spec's retrospective configuration is `full`: generate a retrospective agent using `${CLAUDE_PLUGIN_ROOT}/shared/templates/retrospective-agent-template.md`, and a retrospective command if marketplace.

**If target is Project or Global:**

1. Create the skill directory at the target path
2. Spawn `skill-forge:skill-generator` agent (Opus) with the same spec-based inputs as above

## Step 4b — Eval Testing (Optional)

After generation completes, offer eval testing via AskUserQuestion:

- "Run eval loop (recommended for complex skills)" — runs execution-based evaluation comparing with-skill vs without-skill output
- "Skip to validation"

If the user selects eval testing:

1. Use the `/eval-skill` command flow in create mode (with_skill vs without_skill)
2. Auto-generate 2-3 test prompts from the skill's workflow steps and description
3. Run the full eval pipeline (parallel runs → grading → comparison → viewer)
4. After the user is satisfied with eval results, continue to validation

This step is most valuable for complex skills with multiple agents or intricate workflows. For simple skills, skipping is fine.

## Step 5 — Validate

Spawn the `skill-forge:skill-validator` agent (Haiku) via the Agent tool, passing:

- The path to the newly created skill directory
- The path to `{$SKILL_DIR}/docs/spec.md`

The validator performs:

1. **Structural checks** — frontmatter validity, naming, line count, progressive disclosure, tool restrictions
2. **Anti-pattern scan** — checks against `${CLAUDE_PLUGIN_ROOT}/shared/anti-patterns.md`
3. **Spec compliance check** — verify generated artifacts match the spec's component manifest. Flag files in the spec not created, or files created not in the spec.
4. **Trigger test generation** — write 20 test queries to `trigger-tests.md` alongside the SKILL.md

**If marketplace target**, also run:

```bash
bun run typecheck && bun run build && bun run format:check
```

Present the validator's report via AskUserQuestion:

- If CRITICAL failures exist: block delivery until fixed — loop back to fix and re-validate
- If HIGH failures exist: warn and recommend fixing before delivery
- Trigger tests are always generated regardless of pass/fail

Options:

1. "Looks good — finish" — proceed to retrospective and delivery
2. "Fix the flagged issues" — address failures and re-validate

## Step 6 — Retrospective & Delivery

### Retrospective

Spawn the `skill-forge:retrospective` agent (Sonnet) with:

- The approved spec (contract.md + spec.md)
- The validator report from Step 5
- Any user modifications made during the run (edits to spec, manual fixes after validation)

The agent:

1. Analyzes the run: Did intake classification match what was built? Did the validator catch things the spec should have prevented? Did the user manually change anything post-generation?
2. Appends timestamped observations to `${CLAUDE_PLUGIN_ROOT}/shared/learnings.md`
3. If a pattern appears 3+ times in learnings: proposes a concrete update to the relevant reference doc via AskUserQuestion (user approves before any modification)

### Delivery

Summarize what was created:

- List all files written with their absolute paths
- Show the "getting started" invocation: the exact phrase or command to trigger the new skill
- If trigger tests were generated, remind the user to review `trigger-tests.md`
- If marketplace: remind to bump the version in plugin.json and run the marketplace's sync command before committing
- If marketplace: remind that `claude plugin marketplace update <marketplace-name>` must be run before `claude plugin update` will detect the new version
