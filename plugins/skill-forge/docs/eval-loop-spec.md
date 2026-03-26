# Eval Loop Spec

**Date:** 2026-03-25
**Version target:** 0.6.0
**Status:** Approved

## Problem

Skill-forge validates skills structurally (frontmatter, line counts, anti-patterns) and via trigger testing (does the description cause the skill to activate?). But it never tests whether the skill actually produces good output when triggered. The Anthropic skill-creator's core innovation is a create → test → grade → compare → iterate loop that measures execution quality.

## Goals

1. Test skill output quality through actual execution with parallel subagent runs
2. Compare with-skill vs without-skill (create mode) or old-skill vs new-skill (improve mode)
3. Grade outputs against user-defined assertions with evidence
4. Blind A/B comparison to remove bias
5. Aggregate results with statistical rigor (mean/stddev across runs)
6. Browser-based review with feedback capture for iteration
7. Standalone `/eval-skill` command + optional integration into forge/improve pipelines

## Component Manifest

### New Files

| File                             | Purpose                                                   |
| -------------------------------- | --------------------------------------------------------- |
| `agents/grader.md`               | Evaluates assertions against execution transcript/outputs |
| `agents/comparator.md`           | Blind A/B quality comparison                              |
| `agents/analyzer.md`             | Post-hoc analysis and benchmark pattern detection         |
| `scripts/run_eval.py`            | Orchestrates a single eval run via `claude -p`            |
| `scripts/aggregate_benchmark.py` | Aggregates grading into benchmark.json                    |
| `scripts/generate_report.py`     | Generates HTML eval viewer                                |
| `commands/eval-skill.md`         | Standalone `/eval-skill` command                          |
| `shared/eval-schemas.md`         | JSON schema reference for all eval artifacts              |
| `eval-viewer/viewer.html`        | HTML template for eval review UI                          |

### Modified Files

| File                            | Change                                       |
| ------------------------------- | -------------------------------------------- |
| `skills/create-skill/SKILL.md`  | Add optional eval step after generation      |
| `skills/improve-skill/SKILL.md` | Add optional eval step after changes applied |
| `plugin.json`                   | Register 3 new agents, bump to 0.6.0         |

## Architecture

### Workspace Layout

```
{skill-name}-workspace/
  iteration-{N}/
    eval-{ID}/
      eval_metadata.json
      with_skill/
        outputs/
        transcript.txt
        timing.json
        grading.json
        metrics.json
      without_skill/          # or old_skill/ in improve mode
        outputs/
        transcript.txt
        timing.json
        grading.json
        metrics.json
      comparison.json
      analysis.json
    benchmark.json
    feedback.json
```

### Data Flow

```
User prompts + assertions
        │
        ▼
   ┌─────────┐    parallel    ┌──────────────┐
   │run_eval  │───────────────│run_eval      │
   │(with)    │               │(without/old) │
   └────┬─────┘               └──────┬───────┘
        │                             │
        ▼                             ▼
   ┌─────────┐               ┌──────────────┐
   │ grader   │               │ grader       │
   └────┬─────┘               └──────┬───────┘
        │                             │
        └──────────┬──────────────────┘
                   ▼
            ┌─────────────┐
            │ comparator  │  (blind A/B)
            └──────┬──────┘
                   ▼
            ┌─────────────┐
            │aggregate +  │
            │analyzer     │
            └──────┬──────┘
                   ▼
            ┌─────────────┐
            │generate     │
            │report.py    │
            └──────┬──────┘
                   ▼
            Browser viewer
            (feedback.json)
```

## Agent Designs

### grader (Sonnet)

**Tools:** Read, Glob, Grep
**Role:** Evaluate assertions against execution output.

**Input:** Execution transcript, output files, assertions list.

**Process:**

1. Read the full execution transcript
2. Examine all output files in the outputs/ directory
3. For each assertion: determine PASS or FAIL with evidence
4. PASS requires genuine substance — surface compliance or coincidental matches don't count
5. Extract and verify any implicit claims in the output
6. Critique the assertions themselves (flag non-discriminating or impossible ones)

**Output:** `grading.json`

```json
{
  "expectations": [{ "text": "assertion text", "passed": true, "evidence": "specific evidence" }],
  "summary": { "passed": 3, "failed": 1, "total": 4, "pass_rate": 0.75 },
  "execution_metrics": {
    "tool_calls": 12,
    "files_created": 3,
    "errors": 0
  },
  "claims": [{ "claim": "implicit claim found", "verified": true, "evidence": "..." }],
  "eval_feedback": [{ "assertion": "...", "issue": "non-discriminating — passes trivially" }]
}
```

**Constraints:**

- Field names must be exactly `text`/`passed`/`evidence` (viewer depends on these)
- Never fabricate evidence — quote directly from transcript/files
- ≤200 lines

### comparator (Sonnet)

**Tools:** Read, Glob, Grep
**Role:** Blind A/B quality comparison.

**Input:** Two sets of output files labeled "Output A" and "Output B" (randomized mapping to configurations). The original task prompt. Optionally, assertions.

**Process:**

1. Read both outputs without knowing which configuration produced which
2. Understand the task from the original prompt
3. Generate evaluation rubric:
   - Content: correctness (1-5), completeness (1-5), accuracy (1-5)
   - Structure: organization (1-5), formatting (1-5), usability (1-5)
4. Score each output
5. If assertions provided, check both outputs against them
6. Declare winner

**Output:** `comparison.json`

```json
{
  "winner": "A",
  "reasoning": "A produced more complete output with better structure...",
  "rubric": {
    "A": { "content_score": 4.3, "structure_score": 3.7, "overall_score": 4.0 },
    "B": { "content_score": 3.0, "structure_score": 3.5, "overall_score": 3.25 }
  },
  "output_quality": {
    "A": { "strengths": ["..."], "weaknesses": ["..."] },
    "B": { "strengths": ["..."], "weaknesses": ["..."] }
  }
}
```

**Constraints:**

- Ties should be rare — there's almost always a qualitative difference
- Output quality is primary; assertion pass rates are secondary evidence
- ≤200 lines

### analyzer (Sonnet)

**Tools:** Read, Glob, Grep
**Role:** Two modes — post-hoc analysis and benchmark analysis.

**Post-hoc analysis input:** Both skill versions, both transcripts, comparison result.
**Post-hoc output:** `analysis.json`

```json
{
  "comparison_summary": "...",
  "winner_strengths": ["..."],
  "loser_weaknesses": ["..."],
  "instruction_following": { "with_skill": 8, "without_skill": 5 },
  "improvement_suggestions": [
    {
      "description": "...",
      "priority": "high",
      "category": "instructions"
    }
  ],
  "transcript_insights": ["..."]
}
```

Categories: `instructions`, `tools`, `examples`, `error_handling`, `structure`, `references`.

**Benchmark analysis input:** Full benchmark.json with aggregated results.
**Benchmark output:** JSON array of observation strings — patterns the aggregate stats hide (non-discriminating assertions, broken assertions, flaky evals, time/token tradeoffs).

**Constraints:** ≤200 lines

## Script Designs

### `scripts/run_eval.py`

**Dependencies:** stdlib only
**Input:** `--prompt "text"` `--eval-id 0` `--eval-name "name"` `--output-dir <path>` `--model <model-id>` `--skill-path <path>` (optional, for with-skill config)
**Process:**

1. Create output directory structure
2. Write `eval_metadata.json`
3. Run `claude -p "<prompt>" --output-format json [--skill <path>]` — capture full output
4. Write `transcript.txt` from the JSON output
5. Extract any files created into `outputs/`
6. Write `metrics.json` (tool call count, files created, error count)

**Output:** Populates the eval directory with transcript, outputs, and metrics. Does NOT write timing.json — that's captured by the caller when the subagent completes.

### `scripts/aggregate_benchmark.py`

**Dependencies:** stdlib only
**Input:** `--iteration-dir <path>` `--skill-name <name>`
**Process:**

1. Read all `grading.json` files across eval directories
2. For each assertion: compute pass rate, mean, stddev across configurations
3. For each configuration: compute overall pass rate, token usage (mean/stddev), duration (mean/stddev)
4. Flag non-discriminating assertions (pass in both configs), broken assertions (fail in both), and high-variance assertions

**Output:** `benchmark.json` in the iteration directory

```json
{
  "skill_name": "...",
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
      "text": "...",
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

**Constraint:** `configuration` values must be exactly `"with_skill"` or `"without_skill"` (or `"old_skill"` / `"new_skill"` in improve mode). The viewer reads these exactly.

### `scripts/generate_report.py`

**Dependencies:** stdlib only (generates self-contained HTML)
**Input:** `--iteration-dir <path>` `--skill-name <name>` `--benchmark <path>` `--static <output-path>` (optional, for headless environments)
**Process:**

1. Read benchmark.json, all grading.json files, comparison.json files, analysis.json files
2. Generate self-contained HTML that displays:
   - Assertion pass rates per configuration (bar chart via inline SVG)
   - Side-by-side output comparison
   - Blind comparison results with rubric scores
   - Token/time metrics
   - Analyzer insights
   - Feedback form
3. If `--static`: write HTML to the output path
4. Otherwise: start a local HTTP server, open in browser, serve until feedback submitted

**Output:** HTML file + optionally `feedback.json` when user submits feedback through the form.

The HTML embeds all data as inline JSON — no external fetches needed. The feedback form writes to `feedback.json` in the iteration directory (via a small embedded server, or via download prompt in static mode).

## Command Design: `/eval-skill`

**File:** `commands/eval-skill.md`

### Flow

1. **Resolve skill** — accept path or name, same resolution logic as improve-skill
2. **Choose mode** via AskUserQuestion:
   - "Create mode (with vs without skill)"
   - "Improve mode (old vs new skill)" — requires a second skill path or git ref
3. **Define test prompts** — ask user for 2-3 prompts that exercise the skill. Offer to auto-generate from the skill's description and workflow steps.
4. **Launch runs** — ALL runs in parallel as subagents:
   - For each prompt: spawn with-skill run AND without-skill run simultaneously
   - Use `run_eval.py` for execution
   - Capture `total_tokens` and `duration_ms` from task completion notification into `timing.json` immediately
5. **Draft assertions** — while runs execute, help user define quantitative assertions. Good assertions are:
   - Objectively verifiable
   - Descriptively named
   - Discriminating (hard to satisfy without actually doing the work)
6. **Grade** — spawn grader agent for each completed run
7. **Compare** — spawn comparator for each eval pair (blind A/B, randomized assignment)
8. **Aggregate** — run `aggregate_benchmark.py`
9. **Analyze** — spawn analyzer in both modes (post-hoc per eval + benchmark analysis)
10. **Generate viewer** — run `generate_report.py`, open in browser
11. **Collect feedback** — read `feedback.json` after user submits
12. **Iterate** — if user wants changes, revise skill and repeat from step 4

### Parallelization

Steps 4-5 run concurrently (runs execute while user drafts assertions).
Steps 6-7 run concurrently per eval (grade both configs, then compare).
Steps 8-9 run sequentially (aggregate first, then analyze).

## Pipeline Integration

### Forge pipeline (create-skill/SKILL.md)

After Step 4 (Execute Spec), before Step 5 (Validate), add an optional eval gate:

> After generation completes, offer eval testing via AskUserQuestion:
>
> - "Run eval loop (recommended for complex skills)"
> - "Skip to validation"
>
> If selected, run the eval loop in create mode (with-skill vs without-skill).
> Use the skill's workflow steps to auto-generate 2-3 test prompts.
> After the eval loop completes and the user is satisfied, continue to validation.

### Improve pipeline (improve-skill/SKILL.md)

After Step 4 (Apply Changes), before Step 5 (Re-validate), add an optional eval gate:

> After changes are applied, offer eval comparison via AskUserQuestion:
>
> - "Run eval comparison (old vs new)"
> - "Skip to re-validation"
>
> If selected, run the eval loop in improve mode. The "old" version is the skill
> state before this improve run (use git stash or a temp copy). The "new" version
> is the current state after changes.

## Schemas Reference

All schemas go in `shared/eval-schemas.md`. Critical contracts:

- `grading.json` field names: `text`, `passed`, `evidence` — exact match required
- `benchmark.json` configuration values: `"with_skill"` or `"without_skill"` — exact match required
- `timing.json`: `{ "total_tokens": int, "duration_ms": int }` — captured from subagent task completion, not from the run itself
- `comparison.json`: `winner` is `"A"` or `"B"` or `"TIE"`

## Execution Plan

### Phase 1: Schemas + Agents (parallel)

- Write `shared/eval-schemas.md`
- Write `agents/grader.md`
- Write `agents/comparator.md`
- Write `agents/analyzer.md`

### Phase 2: Scripts (parallel, after Phase 1 schemas)

- Write `scripts/run_eval.py`
- Write `scripts/aggregate_benchmark.py`
- Write `scripts/generate_report.py`

### Phase 3: Viewer + Command (parallel, after Phase 2)

- Write `eval-viewer/viewer.html`
- Write `commands/eval-skill.md`

### Phase 4: Integration (sequential, after Phase 3)

- Update `skills/create-skill/SKILL.md`
- Update `skills/improve-skill/SKILL.md`
- Update `plugin.json` (register agents, bump version)
- Run sync + typecheck + format

## Non-Goals

- Real-time streaming of eval progress (future)
- Persisting eval results across sessions (workspace is ephemeral)
- Automatic skill revision without user approval
- CI integration (future)
