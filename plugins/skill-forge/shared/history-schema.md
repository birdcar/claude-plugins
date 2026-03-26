# Iteration History Schema

Reference for `{skill-root}/docs/history.json` — tracks improve-skill runs over time.

## Schema

```json
{
  "skill_name": "string — kebab-case skill name",
  "entries": [
    {
      "timestamp": "string — ISO 8601 (e.g., 2026-03-25T14:30:00Z)",
      "version": "string — skill version after this run (e.g., 0.2.0)",
      "parent_version": "string — skill version before this run",
      "trigger": "string — what initiated the run (braindump summary or 'systematic improvement')",
      "scores": {
        "before": {
          "description_quality": "number — 0-25",
          "structural_compliance": "number — 0-25",
          "instruction_quality": "number — 0-25",
          "agent_tool_optimization": "number — 0-25",
          "total": "number — 0-100"
        },
        "after": {
          "description_quality": "number — 0-25",
          "structural_compliance": "number — 0-25",
          "instruction_quality": "number — 0-25",
          "agent_tool_optimization": "number — 0-25",
          "total": "number — 0-100"
        }
      },
      "changes": {
        "applied": ["string — description of each applied change"],
        "skipped": ["string — description of each skipped change"]
      },
      "description_changed": "boolean — whether the description field was modified",
      "trigger_test_results": {
        "should_trigger_accuracy": "number — 0.0-1.0, omit if no trigger tests ran",
        "should_not_trigger_accuracy": "number — 0.0-1.0, omit if no trigger tests ran"
      }
    }
  ]
}
```

## Field Notes

- `version` / `parent_version`: Read from `plugin.json` if the skill is in a marketplace plugin. For project/global skills without versioning, use `"unversioned"`.
- `trigger_test_results`: Only present when the description was changed and trigger tests were regenerated.
- `entries` is append-only. Never modify or remove existing entries.
- The `aggregate_history.py` script in `${CLAUDE_PLUGIN_ROOT}/scripts/` can summarize this file.

## Usage

The improve-skill pipeline writes a new entry at the end of Step 5 (Re-validate & Report). The skill-optimizer agent reads this file during analysis to identify trends across runs.
