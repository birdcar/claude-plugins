---
name: improve-skill
description: >-
  Analyzes and optimizes existing Claude Code skills for better trigger precision,
  structural compliance, instruction quality, and agent efficiency. Produces
  measurable before/after scorecards. Use when the user asks to "improve a skill",
  "optimize a skill", "review a skill", "audit skill quality", "fix skill triggers",
  or points to an existing SKILL.md that needs work.
  Do NOT use for creating new skills (use create-skill instead) or for general
  code review.
---

## Critical Rules

- ALWAYS use AskUserQuestion for decisions and approvals — never plain text questions
- ALWAYS use Edit for applying changes — surgical modifications, never full rewrites
- ALWAYS present before/after diffs via AskUserQuestion with preview before applying
- ALWAYS update the spec before modifying skill artifacts when design intent has shifted
- Read shared knowledge base from `${CLAUDE_PLUGIN_ROOT}/shared/` for scoring criteria
- Non-destructive: every individual change must be approved before applying

## Step 1 — Locate Skill & Gather Context

Accept a skill path and an optional braindump from the command or conversation context.

- **Path**: provided directly or discovered via search
- **Braindump** (optional): the user's own improvement ideas, specific complaints, or desired changes

If a path was provided, read the SKILL.md at that path.

If a name was provided (no `/`, does not end in `.md`), search these locations in order and use the first match:

1. `.claude/skills/{name}/SKILL.md` (project-local)
2. `~/.claude/skills/{name}/SKILL.md` (global)
3. `plugins/*/skills/{name}/SKILL.md` (marketplace)
4. `**/skills/{name}/SKILL.md` (anywhere in working directory)

If multiple matches exist, use AskUserQuestion to ask the user to select one.

After locating SKILL.md, also read:

- All other files in the same skill directory
- `plugin.json` in the parent plugin directory (if it exists)
- Any agent `.md` files referenced by or co-located with the plugin
- Any command `.md` files in the plugin's `commands/` directory
- `hooks/hooks.json` (if it exists)
- All files under `references/` in the skill directory (if it exists)

### Spec Context

Determine the skill's root directory (the directory containing `skills/`, `agents/`, etc.). Check whether `{skill-root}/docs/` exists, and if so, read:

- `{skill-root}/docs/contract.md` — design intent document
- `{skill-root}/docs/spec.md` — execution plan document
- `{skill-root}/docs/learnings.md` — accumulated observations

Record whether a spec exists or not — this determines Step 2's behavior.

If a braindump was provided, hold it for Step 2 — the user's ideas are passed to the optimizer alongside the skill content so the analysis addresses both systematic quality issues and the user's specific concerns.

## Step 2 — Analysis & Scoring

### When a spec exists

Spawn the `skill-forge:skill-optimizer` agent (Sonnet) with all collected skill content AND spec content provided in the prompt. Include spec files under a `## Spec Context` section containing the full text of contract.md and spec.md.

If the user provided a braindump, include it under a `## User-Requested Improvements` section.

The optimizer performs a three-way analysis:

1. **Spec vs reality drift**: has the skill diverged from its spec? Are there components in the spec that don't exist, or components that exist but aren't in the spec?
2. **Braindump vs spec alignment**: is the user's request consistent with the original design intent?
3. **Braindump vs spec conflict**: does the user want something the spec explicitly excluded or scoped out?

After the three-way analysis, the optimizer scores the standard four dimensions (0-25 each):

- Description Quality
- Structural Compliance
- Instruction Quality
- Agent/Tool Optimization

Each braindump item is mapped to the most relevant dimension. Braindump items that conflict with best practices are flagged with trade-off explanations.

### When no spec exists

Before running the optimizer, offer retroactive spec generation via AskUserQuestion:

- **Option A**: "Generate spec from current skill state"
- **Option B**: "Skip, improve without spec"

If the user selects **Option A**:

1. Spawn the `skill-forge:skill-optimizer` agent with skill content and a directive to reverse-engineer a contract.md and spec.md from the current skill state
2. The optimizer generates both documents using the templates in `${CLAUDE_PLUGIN_ROOT}/shared/templates/`
3. Create `{skill-root}/docs/` if it doesn't exist
4. Write the generated contract.md and spec.md to `{skill-root}/docs/`
5. Create an empty learnings.md with a header explaining its purpose
6. Present the generated spec to the user via AskUserQuestion for approval
7. Once approved, proceed with the full three-way analysis as if a spec had existed

If the user selects **Option B**:

Spawn the `skill-forge:skill-optimizer` agent with skill content only (no spec context). The optimizer performs the standard scored analysis — four dimensions scored 0-25 each. This is the current behavior with no regression.

Wait for the agent to return the full scored analysis before proceeding.

## Step 3 — Recommendations

Present the scorecard via AskUserQuestion. Show each dimension score and the most impactful improvement for that dimension. If braindump items were provided, show how they map to dimensions.

### When spec alignment findings exist

Present spec alignment issues alongside the scorecard:

- **Spec drift**: list each divergence between spec and current skill state
- **Braindump conflicts**: list any user requests that conflict with the spec's scope boundaries
- **Braindump alignment**: confirm which user requests are consistent with the spec

If spec updates are needed (due to drift or intentional design changes), present the proposed spec changes FIRST, before skill improvements. The spec is the source of truth — it must be updated before downstream artifacts change.

### User selection

Ask the user which improvements to apply. Options:

- "Improve all"
- "Description only"
- "Structure only"
- "Instructions only"
- "Agents/Tools only"
- "Update spec only"
- "I'm satisfied"

If the user selects "I'm satisfied", stop here and summarize the scores.

For each selected dimension, generate specific improvements with concrete before/after examples drawn from the agent's recommendations.

## Step 4 — Apply Changes

### Spec-first updates

If spec updates were approved (either from drift findings or design intent changes):

1. Edit contract.md first — update problem statement, goals, scope boundaries, or design decisions as needed
2. Edit spec.md second — update component manifest, architecture, or execution plan as needed
3. Present each spec change via AskUserQuestion with before/after text before applying

### Skill improvements

For each improvement identified in the selected dimensions:

1. Use AskUserQuestion to show the user the old text vs the proposed new text
2. Options: "Apply", "Skip", "Modify"
3. If "Apply": use Edit to make the surgical change
4. If "Modify": use AskUserQuestion to collect the desired modification, then apply
5. If "Skip": record it as skipped
6. Use TodoWrite to track which improvements have been applied and which were skipped

Never rewrite entire files. Every Edit must be the minimum change needed for the improvement.

## Step 5 — Re-validate & Report

After all approved changes are applied:

1. Re-read all modified files
2. Re-score all four dimensions (you may do this inline, no need to re-spawn the agent unless the changes are extensive)
3. Present a before/after scorecard:

```
Dimension          Before  After  Change
-----------------  ------  -----  ------
Description           12     22    +10
Structure             15     21     +6
Instructions          18     23     +5
Agents/Tools           8     19    +11
-----------------  ------  -----  ------
TOTAL                 53     85    +32
```

4. Append a score history entry to `{skill-root}/docs/learnings.md`. Create the file if it does not exist.

```markdown
## YYYY-MM-DD — Improvement Run

- **Trigger:** <braindump summary or "systematic improvement">
- **Before:** Description X/25, Structure X/25, Instructions X/25, Agents X/25 (Total: X/100)
- **After:** Description X/25, Structure X/25, Instructions X/25, Agents X/25 (Total: X/100)
- **Changes applied:** <list>
- **Changes skipped:** <list>
```

Use the actual date (from the system) and real scores. This creates an audit trail of improvement runs over time.

5. If the skill is inside a marketplace plugin (a `package.json` exists in the plugin directory with `bun` scripts), run:

   ```bash
   bun run typecheck && bun run build
   ```

   Report the result.

6. If the description field was changed, spawn the `skill-forge:skill-validator` agent (Haiku) with the skill directory path. The validator generates 20 trigger test queries and writes them to `trigger-tests.md` alongside the improved SKILL.md. Include the trigger test path in the report.

## Step 6 — Retrospective

After completing the improvement run, perform a retrospective to capture learnings for future runs.

1. Spawn the `skill-forge:retrospective` agent (Sonnet) with the following input:
   - Before and after scores for all four dimensions
   - List of applied changes and skipped changes
   - Braindump themes (if a braindump was provided)
   - The skill name and path

2. The retrospective agent analyzes:
   - Which dimensions consistently score low across improvement runs?
   - What do users ask to improve most frequently (braindump themes)?
   - Are there common patterns suggesting generation is weak in a specific area?
   - Did any skipped changes represent recurring issues?

3. The agent appends timestamped observations to `${CLAUDE_PLUGIN_ROOT}/shared/learnings.md`

4. If a pattern appears 3 or more times in the shared learnings, the agent proposes a concrete update to the relevant reference doc (e.g., `description-engineering.md`, `skill-anatomy.md`, `anti-patterns.md`). Present the proposed update via AskUserQuestion — the user must approve before any reference doc is modified.

5. Present next steps to the user:
   - Any remaining improvements that were skipped
   - Follow-up tasks (version bump, sync, etc.)
   - Suggested future improvement areas based on retrospective findings
