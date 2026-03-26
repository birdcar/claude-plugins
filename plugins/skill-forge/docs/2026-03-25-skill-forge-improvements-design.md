# Skill-Forge Improvements: Description Optimization, Scripts, Iteration Tracking

**Date:** 2026-03-25
**Scope:** plugins/skill-forge
**Status:** Approved

## Problem

Skill-forge has a strong creation/generation pipeline but lacks:

1. **Automated description optimization** — `description-engineering.md` has the theory but no automated loop to test and improve descriptions
2. **Deterministic scripts** — all work runs through agents, even tasks that are purely mechanical (validation, aggregation)
3. **Iteration tracking** — no history of improve runs, so trends and regressions go unnoticed

The Anthropic skill-creator reference has all three. This spec adds them to skill-forge.

## Design

### 1. Python Scripts (`scripts/`)

Four uv-scripted Python files. Each embeds its dependencies via `# /// script` headers so `uv run` resolves them automatically.

#### `scripts/quick_validate.py`

Fast structural validation without spawning an agent. Checks:

- Frontmatter exists and has required fields (name, description)
- Description ≤1024 chars
- SKILL.md ≤500 lines
- kebab-case naming
- No XML in frontmatter
- No reserved words in name
- Agent files ≤200 lines

**Input:** Path to skill directory or SKILL.md
**Output:** JSON to stdout: `{ "passed": bool, "checks": [{ "name": str, "severity": str, "passed": bool, "message": str }] }`
**Exit code:** 0 if all CRITICAL checks pass, 1 otherwise

#### `scripts/generate_trigger_queries.py`

Generates 20 trigger test queries from a skill's description and SKILL.md content.

**Input:** `--skill-path <path>` and `--model <model-id>` (default: claude-sonnet-4-6)
**Output:** JSON file at `{skill-dir}/docs/trigger-eval.json`:

```json
{
  "skill_name": "my-skill",
  "generated_at": "2026-03-25T...",
  "queries": [
    { "id": 0, "text": "...", "should_trigger": true, "category": "exact_match" },
    { "id": 1, "text": "...", "should_trigger": false, "category": "adjacent_domain" }
  ]
}
```

Categories follow the existing `trigger-test-template.md` distribution:

- Should trigger (10): 3 exact, 3 paraphrased, 2 edge case, 2 embedded
- Should not trigger (10): 3 adjacent domain, 3 general programming, 2 keyword overlap, 2 other-skill targets

Uses `claude -p` with a system prompt to generate the queries.

#### `scripts/optimize_description.py`

Automated description optimization loop.

**Input:** `--skill-path <path>` `--eval-set <trigger-eval.json>` `--model <model-id>` `--max-iterations 5` `--verbose`
**Process:**

1. Split eval set 60/40 train/test
2. Run each query 3x via `claude -p` — check if skill triggers by examining output
3. Score: trigger accuracy on train set
4. Use Claude to propose improved description based on failures
5. Re-run train set with new description
6. Select best by test-set score (to avoid overfitting)
7. Repeat up to `--max-iterations`

**Output:** JSON at `{skill-dir}/docs/optimization-result.json`:

```json
{
  "skill_name": "my-skill",
  "started_at": "...",
  "iterations": [
    {
      "iteration": 0,
      "description": "original description...",
      "train_score": 0.75,
      "test_score": 0.7
    }
  ],
  "best_iteration": 2,
  "best_description": "improved description...",
  "best_test_score": 0.95
}
```

#### `scripts/aggregate_history.py`

Summarizes iteration history across improve runs for a skill.

**Input:** `--history-path <path-to-history.json>`
**Output:** Human-readable summary to stdout + optional `--json` flag for machine-readable output. Includes:

- Total iterations, date range
- Score trends per dimension (improving/stable/declining)
- Most frequently applied vs skipped recommendation categories
- Description change count and trigger test trend

### 2. Iteration Tracking (`history.json`)

#### Schema (`shared/history-schema.md`)

```json
{
  "skill_name": "my-skill",
  "entries": [
    {
      "timestamp": "2026-03-25T14:30:00Z",
      "version": "0.2.0",
      "parent_version": "0.1.0",
      "trigger": "improve-skill run",
      "scores": {
        "before": {
          "description_quality": 18,
          "structural_compliance": 22,
          "instruction_quality": 20,
          "agent_tool_optimization": 15,
          "total": 75
        },
        "after": {
          "description_quality": 23,
          "structural_compliance": 22,
          "instruction_quality": 22,
          "agent_tool_optimization": 19,
          "total": 86
        }
      },
      "changes": {
        "applied": ["Rewrote description with trigger phrases", "Added negative cases"],
        "skipped": ["Reduce agent count"]
      },
      "description_changed": true,
      "trigger_test_results": {
        "should_trigger_accuracy": 0.9,
        "should_not_trigger_accuracy": 0.95
      }
    }
  ]
}
```

#### Integration points

- **improve-skill/SKILL.md Step 5**: After re-scoring, append entry to `{skill-dir}/docs/history.json` (create if doesn't exist)
- **skill-optimizer agent**: Read `history.json` if present to identify trends and inform recommendations
- **aggregate_history.py**: Standalone summary tool

### 3. Description Optimization Command

New command: `/optimize-description [skill-path]`

**File:** `commands/optimize-description.md`
**Flow:**

1. Resolve skill path (same logic as improve-skill)
2. Run `quick_validate.py` — abort on CRITICAL failures
3. Run `generate_trigger_queries.py` — present queries to user for review/edit via AskUserQuestion
4. Run `optimize_description.py` with approved eval set
5. Present best description with before/after comparison
6. User approves → apply to SKILL.md frontmatter via Edit
7. Append optimization results to `docs/history.json`

### 4. Eval Loop (Future — Spec Only)

Not implemented in this iteration. A separate spec will cover:

- Parallel with-skill vs without-skill execution testing
- Grader, comparator, analyzer agents
- Benchmark aggregation
- Eval viewer
- Integration with the forge/improve pipelines

## Files to Create

| File                                  | Purpose                        |
| ------------------------------------- | ------------------------------ |
| `scripts/quick_validate.py`           | Fast structural validation     |
| `scripts/generate_trigger_queries.py` | Generate trigger test queries  |
| `scripts/optimize_description.py`     | Description optimization loop  |
| `scripts/aggregate_history.py`        | History summarization          |
| `shared/history-schema.md`            | history.json schema reference  |
| `commands/optimize-description.md`    | Slash command for optimization |

## Files to Modify

| File                            | Change                               |
| ------------------------------- | ------------------------------------ |
| `skills/improve-skill/SKILL.md` | Add history.json write in Step 5     |
| `agents/skill-optimizer.md`     | Read history.json for trend analysis |
| `plugin.json`                   | Version bump to 0.5.0                |

## Non-Goals

- Eval loop implementation (future spec)
- Changes to forge pipeline
- Agent model reassignment
- Breaking changes to existing improve flow
