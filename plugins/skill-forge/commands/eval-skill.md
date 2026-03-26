---
name: eval-skill
description: >-
  Test skill quality through execution-based evaluation. Runs prompts with and
  without the skill (or old vs new versions), grades outputs against assertions,
  and presents results in a browser-based viewer. Use for measuring actual output
  quality, not just structural compliance.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Agent
  - AskUserQuestion
  - TodoWrite
argument-hint: '[skill-path]'
---

## Critical Rules

- ALL eval runs MUST launch in parallel — never sequentially
- Capture `timing.json` IMMEDIATELY when each subagent completes — this data is transient
- The comparator MUST NOT know which config produced which output (blind A/B)
- Track the A/B mapping separately to unblind during analysis
- Use TodoWrite to track progress through every pipeline stage
- Use AskUserQuestion for ALL decisions — never plain text questions

## Step 1 — Resolve Skill

Parse `$ARGUMENTS`:

- If `$ARGUMENTS` contains `/` or ends in `.md`, treat it as a direct path
- Otherwise treat it as a skill name and search:
  1. `.claude/skills/{name}/SKILL.md`
  2. `~/.claude/skills/{name}/SKILL.md`
  3. `plugins/*/skills/{name}/SKILL.md`
  4. `**/skills/{name}/SKILL.md`

If no `$ARGUMENTS` provided:

- Use Glob to discover all `**/skills/*/SKILL.md` files
- Present the list via AskUserQuestion and ask the user to select one

If multiple matches are found for a name, use AskUserQuestion to ask the user to select one.

Read the resolved SKILL.md to confirm it exists. Extract the skill name from the frontmatter `name` field.

## Step 2 — Choose Mode

Use AskUserQuestion with these options:

- "Create mode (with skill vs without skill)" — compares having the skill installed vs not having it
- "Improve mode (old vs new skill)" — compares two versions of the skill

If the user selects "Improve mode", use AskUserQuestion to ask for the path or git ref for the old version:

- "Provide a file path to the old SKILL.md"
- "Provide a git ref (branch, tag, or commit SHA) for the old version"

If a git ref is provided, run:

```bash
git show <ref>:<relative-skill-path> > /tmp/old-skill.md
```

Store the old skill path for use in runs labeled `old_skill`. The current skill path is `new_skill`.

In create mode: runs are labeled `with_skill` and `without_skill`.

## Step 3 — Define Test Prompts

Use AskUserQuestion with these options:

- "I'll provide my own prompts"
- "Auto-generate from skill content"
- "Both (auto-generate, then I'll review and add)"

If auto-generating:

1. Read the SKILL.md
2. Extract the skill's description, workflow steps, and stated goals
3. Generate 2–3 prompts that exercise each major workflow step — prompts should be realistic user requests that would trigger the skill and exercise its key behaviors
4. Present the generated prompts via AskUserQuestion:
   - "Approve these prompts"
   - "Edit prompts"
   - "Regenerate"
   - If "Both" mode: "Approve and add my own prompts" (let the user type additional prompts)

If the user is providing their own prompts, use AskUserQuestion to collect them. Ask for 2–3 prompts and confirm.

Finalize the prompt list before proceeding.

## Step 4 — Launch Runs (Parallel) + Step 5 — Draft Assertions (Concurrent)

Use TodoWrite to initialize a task list tracking each run, the assertion-drafting session, grading, comparison, and aggregation.

Create the workspace directory: `{skill-name}-workspace/iteration-0/`

For each prompt, assign an ID (0, 1, 2, ...) and create `eval-{ID}/` inside the iteration directory.

**Launch ALL runs simultaneously as parallel subagents.** Do not wait for one run to finish before starting another. For each prompt, spawn both runs at the same time:

For create mode, each subagent runs:

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/run_eval.py \
  --prompt "<prompt text>" \
  --eval-id <ID> \
  --eval-name "<skill-name>" \
  --output-dir <path-to-eval-{ID}/with_skill> \
  --model claude-sonnet-4-5 \
  --skill-path <resolved-skill-path>
```

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/run_eval.py \
  --prompt "<prompt text>" \
  --eval-id <ID> \
  --eval-name "<skill-name>" \
  --output-dir <path-to-eval-{ID}/without_skill> \
  --model claude-sonnet-4-5
```

For improve mode, replace `with_skill` / `without_skill` with `new_skill` / `old_skill` and pass the appropriate `--skill-path` to each.

**Timing capture:** When each subagent completes, immediately write `timing.json` to its config directory using the `total_tokens` and `duration_ms` from the task completion notification:

```json
{ "total_tokens": <value>, "duration_ms": <value> }
```

This data is not available after the fact — write it immediately.

**Concurrently while runs execute**, help the user define assertions (Step 5):

Explain that good assertions are:

- Objectively verifiable (not "the output was good" — but "the output contains a valid JSON file")
- Descriptively named
- Discriminating (hard to satisfy without actually doing the work)
- Based on the skill's stated goals

Suggest 3–5 assertions derived from the skill's description and workflow steps. Use AskUserQuestion to let the user review, edit, and add assertions.

Once finalized, write the assertions into each `eval-{ID}/eval_metadata.json`:

```json
{
  "eval_id": <ID>,
  "prompt": "<prompt text>",
  "skill_name": "<name>",
  "mode": "create|improve",
  "assertions": [
    { "text": "<assertion text>" }
  ]
}
```

Update the TodoWrite task list as runs and assertion drafting complete.

## Step 6 — Grade

For each completed run, spawn a `skill-forge:grader` agent (use Sonnet model) with:

- Path to `transcript.txt` in the run's config directory
- Path to `outputs/` directory in the run's config directory
- The assertions from `eval_metadata.json`

The grader writes `grading.json` to the config directory. Spawn grading agents in parallel across all runs.

Wait for all grading agents to complete before proceeding.

## Step 7 — Compare

For each eval directory, assign the two config directories randomly as "A" and "B". Record the mapping (which config is A, which is B) — you will need this to unblind the results in analysis. Do NOT pass the config names to the comparator.

Spawn a `skill-forge:comparator` agent (Sonnet) for each eval with:

- Path to "Output A" directory (the config assigned to A)
- Path to "Output B" directory (the config assigned to B)
- The original prompt text
- The assertions from `eval_metadata.json`

The comparator writes `comparison.json` to the eval directory. Spawn all comparator agents in parallel.

Wait for all comparators to complete before proceeding.

## Step 8 — Aggregate

Run:

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/aggregate_benchmark.py \
  --iteration-dir <path-to-iteration-0> \
  --skill-name <skill-name>
```

This writes `benchmark.json` to the iteration directory. Wait for it to complete.

## Step 9 — Analyze

Spawn two `skill-forge:analyzer` agents in parallel (both Sonnet):

**Post-hoc analysis** — one per eval pair, each receiving:

- Both skill version files (SKILL.md for each config)
- Both transcript files
- The `comparison.json` for that eval (with the A/B mapping unblinded — tell the analyzer which config won)

Each analyzer writes `analysis.json` to the eval directory.

**Benchmark analysis** — one agent receiving:

- The full `benchmark.json`

The benchmark analyzer writes its output (a JSON array of observation strings) to `benchmark_analysis.json` in the iteration directory.

Wait for all analyzer agents to complete.

## Step 10 — Generate Viewer

Run:

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/generate_report.py \
  --iteration-dir <path-to-iteration-0> \
  --skill-name <skill-name> \
  --benchmark <path-to-benchmark.json>
```

This starts a local HTTP server and opens the eval viewer in the browser. Tell the user the viewer is open and they can review results, then submit feedback through the form.

## Step 11 — Collect Feedback

Wait for the user to submit feedback through the browser form. Then read `feedback.json` from the iteration directory.

Present a summary of the feedback, including:

- The overall rating
- Key observations
- The `next_action` field value

**If `next_action` is `"iterate"`:**

1. Present the analyzer's `improvement_suggestions` to the user
2. Use AskUserQuestion to confirm which suggestions to apply
3. Help the user revise the SKILL.md (use Edit for targeted changes)
4. Increment the iteration counter
5. Update the workspace path to `{skill-name}-workspace/iteration-{N}/`
6. Return to Step 4 with the revised skill

**If `next_action` is `"accept"`:**

Report the final benchmark scores. If in a marketplace plugin, remind about version bump and sync.

**If `next_action` is `"reject"`:**

Report what went wrong based on the benchmark and analysis. Suggest next steps — either deeper iteration or use of `/improve-skill` for structural changes first.
