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

If a braindump was provided, hold it for Step 2 — the user's ideas are passed to the optimizer alongside the skill content so the analysis addresses both systematic quality issues and the user's specific concerns.

## Step 2 — Analysis & Scoring

Spawn the `skill-forge:skill-optimizer` agent (Sonnet) with all collected skill content provided in the prompt.

If the user provided a braindump, include it in the agent prompt under a `## User-Requested Improvements` section. The optimizer should:

1. Score all four dimensions as normal (the braindump doesn't skip systematic analysis)
2. Map each braindump item to the most relevant dimension
3. Incorporate braindump items into its recommendations, prioritizing them when they align with findings
4. Flag any braindump items that conflict with best practices, explaining the trade-off

The agent scores four dimensions (0–25 each, total /100):

### Description Quality (0–25)

| Range | Criteria                                            |
| ----- | --------------------------------------------------- |
| 0–5   | Missing or vague, no trigger phrases                |
| 6–10  | Present but generic, unclear activation             |
| 11–15 | Specific with some triggers, missing negative cases |
| 16–20 | Good triggers, third-person, includes negatives     |
| 21–25 | Excellent — precise, tested, concise                |

### Structural Compliance (0–25)

| Range | Criteria                                              |
| ----- | ----------------------------------------------------- |
| 0–5   | Wrong file name, no frontmatter, missing fields       |
| 6–10  | Valid frontmatter, poor structure, >500 lines         |
| 11–15 | Good structure, some content should be in references/ |
| 16–20 | Progressive disclosure, front-loaded constraints      |
| 21–25 | Optimal — lean SKILL.md, rich references/             |

### Instruction Quality (0–25)

| Range | Criteria                                                                        |
| ----- | ------------------------------------------------------------------------------- |
| 0–5   | Vague, abstract, no examples                                                    |
| 6–10  | Some specifics, constraints buried                                              |
| 11–15 | Imperative form, numbered steps, missing examples                               |
| 16–20 | Specific, constraints in first 100 lines, has examples                          |
| 21–25 | Optimal — scripts for deterministic ops, rationale over ALL CAPS, error handled |

### Agent/Tool Optimization (0–25)

| Range | Criteria                                               |
| ----- | ------------------------------------------------------ |
| 0–5   | No restrictions, no agents, main thread only           |
| 6–10  | Some allowed-tools but overly broad                    |
| 11–15 | Right tools, models not optimized                      |
| 16–20 | Right-sized models, least-privilege tools              |
| 21–25 | Optimal — agent teams, minimal grants, AskUserQuestion |

Wait for the agent to return the full scored analysis before proceeding.

## Step 3 — Recommendations

Present the scorecard via AskUserQuestion. Show each dimension score and the most impactful improvement for that dimension. If braindump items were provided, show how they map to dimensions.

Ask the user which improvements to apply. Options:

- "Improve all"
- "Description only"
- "Structure only"
- "Instructions only"
- "Agents/Tools only"
- "I'm satisfied"

If the user selects "I'm satisfied", stop here and summarize the scores.

For each selected dimension, generate specific improvements with concrete before/after examples drawn from the agent's recommendations.

## Step 4 — Apply Changes

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
─────────────────  ──────  ─────  ──────
Description           12     22    +10
Structure             15     21     +6
Instructions          18     23     +5
Agents/Tools           8     19    +11
─────────────────  ──────  ─────  ──────
TOTAL                 53     85    +32
```

4. If the skill is inside a marketplace plugin (a `package.json` exists in the plugin directory with `bun` scripts), run:

   ```bash
   bun run typecheck && bun run build
   ```

   Report the result.

5. If the description field was changed, spawn the `skill-forge:skill-validator` agent (Haiku) with the skill directory path. The validator generates 20 trigger test queries and writes them to `trigger-tests.md` alongside the improved SKILL.md. Include the trigger test path in the report.

6. Present next steps: any remaining improvements the user skipped, any follow-up tasks (version bump, sync, etc.).
