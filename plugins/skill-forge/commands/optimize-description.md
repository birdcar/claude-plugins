---
name: optimize-description
description: >-
  Optimize a skill's description for better trigger accuracy using automated
  testing. Generates eval queries, runs them against the skill, and iteratively
  improves the description.
allowed-tools:
  - Read
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
argument-hint: '[skill-path]'
---

## Critical Rules

- ALWAYS use AskUserQuestion for decisions — never plain text questions
- ALWAYS validate the skill exists before running optimization
- ALWAYS let the user review and edit the trigger queries before optimization
- NEVER apply the optimized description without user approval
- Requires `claude` CLI and `uv` to be installed

## Step 1 — Resolve Skill

If `$ARGUMENTS` is provided, treat it as a path to a skill directory or SKILL.md.

If not provided, use Glob to find all `**/skills/*/SKILL.md` files and present them via AskUserQuestion for the user to select.

Read the SKILL.md to confirm it exists and extract the current description.

## Step 2 — Pre-flight Validation

Run `${CLAUDE_PLUGIN_ROOT}/scripts/quick_validate.py` via uv:

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/quick_validate.py --skill-path <resolved-path>
```

If any CRITICAL checks fail, report them and stop. The skill must pass structural validation before optimization.

## Step 3 — Generate Trigger Queries

Run `${CLAUDE_PLUGIN_ROOT}/scripts/generate_trigger_queries.py`:

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/generate_trigger_queries.py --skill-path <resolved-path>
```

Read the generated `trigger-eval.json` and present the queries to the user via AskUserQuestion:

- Show should-trigger and should-not-trigger queries grouped by category
- Options: "Approve queries", "Edit queries", "Regenerate"
- If "Edit queries": let the user specify changes, apply them to the JSON, re-present
- If "Regenerate": re-run the script

## Step 4 — Run Optimization

Once queries are approved, run the optimization loop:

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/optimize_description.py \
  --skill-path <resolved-path> \
  --eval-set <trigger-eval.json-path> \
  --max-iterations 5 \
  --verbose
```

This will take time. Inform the user it's running and may take several minutes.

## Step 5 — Present Results

Read `optimization-result.json` from the skill's docs/ directory.

Present the results via AskUserQuestion:

- Current description vs best description
- Score progression across iterations (train and test scores)
- Options: "Apply best description", "Apply specific iteration", "Discard"

If applying:

1. Use Edit to update the description in SKILL.md frontmatter
2. If `{skill-root}/docs/history.json` exists, append an entry recording the description change
3. Report the change

## Step 6 — Wrap Up

Present next steps:

- Suggest running `/improve-skill` for a full quality audit
- If in a marketplace plugin, remind about version bump and sync
- Suggest manual testing with a few real prompts
