# Eval Pipeline JSON Schemas

**CRITICAL: Field names are exact contracts.** The eval viewer HTML and aggregation scripts
parse these files by literal key name. Do not rename fields, use synonyms, or add nesting
without updating the viewer and aggregation scripts accordingly.

---

## `eval_metadata.json`

Written by `run_eval.py` before execution begins. Identifies the eval and carries the
assertions that the grader will evaluate.

```json
{
  "eval_id": 0,
  "eval_name": "string — short human-readable label for this eval",
  "prompt": "string — the exact prompt sent to the executor",
  "assertions": ["string — each assertion is a declarative statement, objectively verifiable"]
}
```

Field types:

- `eval_id`: integer, 0-indexed within the iteration
- `eval_name`: string
- `prompt`: string, the verbatim task prompt
- `assertions`: array of strings

---

## `grading.json`

Written by the `grader` agent after evaluating a single configuration's execution output.

**Viewer-critical field names:** `text`, `passed`, `evidence` inside `expectations[]`.
These three field names are parsed literally by the HTML viewer. Do not change them.

```json
{
  "expectations": [
    {
      "text": "string — verbatim assertion text",
      "passed": true,
      "evidence": "string — direct quote from transcript or output files"
    }
  ],
  "summary": {
    "passed": 3,
    "failed": 1,
    "total": 4,
    "pass_rate": 0.75
  },
  "execution_metrics": {
    "tool_calls": 12,
    "files_created": 3,
    "errors": 0
  },
  "claims": [
    {
      "claim": "string — implicit claim extracted from the output",
      "verified": true,
      "evidence": "string — direct quote supporting or refuting the claim"
    }
  ],
  "eval_feedback": [
    {
      "assertion": "string — the assertion being critiqued",
      "issue": "string — e.g. 'non-discriminating — passes trivially', 'impossible given tool constraints', 'missing coverage area'"
    }
  ]
}
```

Field types:

- `expectations[].text`: string, verbatim assertion
- `expectations[].passed`: boolean
- `expectations[].evidence`: string, direct quote (never fabricated)
- `summary.pass_rate`: float 0.0–1.0
- `execution_metrics.tool_calls`: integer
- `execution_metrics.files_created`: integer
- `execution_metrics.errors`: integer
- `claims[].verified`: boolean
- `eval_feedback`: array, may be empty `[]`

---

## `metrics.json`

Written by `run_eval.py` after execution completes. Raw execution telemetry.

```json
{
  "tool_calls": 12,
  "files_created": 3,
  "errors": 0,
  "output_chars": 4200,
  "transcript_chars": 18500
}
```

Field types: all integers.

---

## `timing.json`

Written by the eval orchestrator (the command or calling skill) after the executor
subagent completes. **Not written by `run_eval.py`** — the caller captures wall-clock
timing from task completion notifications.

```json
{
  "total_tokens": 15000,
  "duration_ms": 45000,
  "total_duration_seconds": 45.0,
  "executor_start": "2026-03-25T10:00:00Z",
  "executor_end": "2026-03-25T10:00:45Z",
  "executor_duration_seconds": 45.0,
  "grader_start": "2026-03-25T10:00:46Z",
  "grader_end": "2026-03-25T10:01:05Z",
  "grader_duration_seconds": 19.0
}
```

Field types:

- `total_tokens`: integer, total tokens consumed by executor + grader
- `duration_ms`: integer, total wall-clock milliseconds
- `total_duration_seconds`: float
- `executor_start`, `executor_end`, `grader_start`, `grader_end`: ISO 8601 UTC strings
- `executor_duration_seconds`, `grader_duration_seconds`: float

---

## `benchmark.json`

Written by `aggregate_benchmark.py`. Aggregates grading results across all eval runs in
an iteration into statistical summaries.

**Viewer-critical constraint:** configuration keys must be exactly `"with_skill"` and
`"without_skill"` (create mode) or `"old_skill"` and `"new_skill"` (improve mode).
The viewer reads these exact strings to label columns.

```json
{
  "skill_name": "string",
  "iteration": 0,
  "configurations": {
    "with_skill": {
      "runs": 3,
      "result": {
        "pass_rate": { "mean": 0.85, "stddev": 0.05 },
        "tokens": { "mean": 15000, "stddev": 2000 },
        "duration_ms": { "mean": 45000, "stddev": 5000 }
      }
    },
    "without_skill": {
      "runs": 3,
      "result": {
        "pass_rate": { "mean": 0.4, "stddev": 0.1 },
        "tokens": { "mean": 12000, "stddev": 1500 },
        "duration_ms": { "mean": 30000, "stddev": 3000 }
      }
    }
  },
  "assertions": [
    {
      "text": "string — assertion text",
      "with_skill_pass_rate": 1.0,
      "without_skill_pass_rate": 0.33,
      "discriminating": true
    }
  ],
  "run_summary": {
    "total_evals": 3,
    "winner": "with_skill",
    "margin": 0.45
  }
}
```

Field types:

- `configurations`: object keyed by config name (see constraint above)
- `configurations.*.runs`: integer
- `configurations.*.result.pass_rate.mean`: float 0.0–1.0
- `configurations.*.result.pass_rate.stddev`: float
- `configurations.*.result.tokens.mean`: float
- `configurations.*.result.tokens.stddev`: float
- `configurations.*.result.duration_ms.mean`: float
- `configurations.*.result.duration_ms.stddev`: float
- `assertions[].discriminating`: boolean — true when pass rates differ meaningfully between configs
- `run_summary.winner`: string, one of the configuration key names
- `run_summary.margin`: float, difference in mean pass rates

---

## `comparison.json`

Written by the `comparator` agent. Result of blind A/B quality comparison.

**Viewer-critical constraint:** `winner` must be exactly `"A"`, `"B"`, or `"TIE"`.

```json
{
  "winner": "A",
  "reasoning": "string — concrete explanation citing specific differences",
  "rubric": {
    "A": {
      "content_score": 4.3,
      "structure_score": 3.7,
      "overall_score": 4.0
    },
    "B": {
      "content_score": 3.0,
      "structure_score": 3.5,
      "overall_score": 3.25
    }
  },
  "output_quality": {
    "A": {
      "strengths": ["string"],
      "weaknesses": ["string"]
    },
    "B": {
      "strengths": ["string"],
      "weaknesses": ["string"]
    }
  }
}
```

Field types:

- `winner`: string, exactly `"A"` | `"B"` | `"TIE"`
- `rubric.*.content_score`: float 1.0–5.0 (correctness 1-5, completeness 1-5, accuracy 1-5, averaged)
- `rubric.*.structure_score`: float 1.0–5.0 (organization 1-5, formatting 1-5, usability 1-5, averaged)
- `rubric.*.overall_score`: float 1.0–5.0 (average of content and structure)
- `output_quality.*.strengths`: array of strings
- `output_quality.*.weaknesses`: array of strings

---

## `analysis.json`

Written by the `analyzer` agent in post-hoc mode. Explains WHY the winner won after
unblinding the comparison.

```json
{
  "comparison_summary": "string — 2-3 sentence synthesis of what drove the outcome",
  "winner_strengths": [
    "string — specific behavior or output quality observed in the winning config"
  ],
  "loser_weaknesses": ["string — specific gap or failure observed in the losing config"],
  "instruction_following": {
    "with_skill": 8,
    "without_skill": 5
  },
  "improvement_suggestions": [
    {
      "description": "string — actionable change with specific before/after or concrete steps",
      "priority": "high",
      "category": "instructions"
    }
  ],
  "transcript_insights": [
    "string — interesting pattern, unexpected tool usage, or notable behavior"
  ]
}
```

Field types:

- `instruction_following`: object keyed by config name, values integer 1–10
- `improvement_suggestions[].priority`: string, exactly `"high"` | `"medium"` | `"low"`
- `improvement_suggestions[].category`: string, exactly one of:
  `"instructions"` | `"tools"` | `"examples"` | `"error_handling"` | `"structure"` | `"references"`
- `transcript_insights`: array of strings, may be empty `[]`

In benchmark mode, the analyzer outputs a JSON array of observation strings directly
(not wrapped in an object). Each string describes a pattern the aggregate stats hide:
non-discriminating assertions, broken assertions, flaky evals, or time/token tradeoffs.

---

## `feedback.json`

Written by the eval viewer when the user submits the feedback form. Read by the
`/eval-skill` command to decide whether to iterate or accept.

```json
{
  "submitted_at": "2026-03-25T10:05:00Z",
  "overall_rating": 4,
  "notes": "string — freeform user notes",
  "assertion_feedback": [
    {
      "text": "string — verbatim assertion text",
      "keep": true,
      "note": "string — optional per-assertion comment"
    }
  ],
  "next_action": "iterate"
}
```

Field types:

- `submitted_at`: ISO 8601 UTC string
- `overall_rating`: integer 1–5
- `notes`: string, may be empty `""`
- `assertion_feedback[].keep`: boolean — whether to retain this assertion in the next iteration
- `next_action`: string, exactly `"iterate"` | `"accept"` | `"reject"`
