# skill-forge

Generates production-grade Claude Code skills from brain dumps, and scaffolds agentic harnesses into target repositories. Spec-driven pipelines with deterministic structural validators, retrospective learning, and per-skill self-evaluation.

## What problem it solves

Writing a good SKILL.md from scratch is deceptively tedious. The description needs third-person trigger phrases and negative cases. The file has to stay under 500 lines with constraints in the first 100. Agent models need to be right-sized. Anti-patterns like vague `allowed-tools` or out-of-date primitives (`TodoWrite`) are easy to miss. skill-forge bakes in that institutional knowledge so you don't have to carry it in your head.

Setting up a _repository_ for reliable agent work is a different problem with overlapping shape — the agent needs instructions (`AGENTS.md`/`CLAUDE.md`), state (`feature_list.json`, `progress.md`), verification (`init.sh`), scope (feature dependencies), and lifecycle (session handoff). `forge-harness` solves that one.

## Installation

```bash
claude plugin install skill-forge@birdcar-plugins
```

## Commands

### `/forge-skill [brain dump]`

Creates a new Claude Code skill from a brain dump. Pass a description inline or leave it empty to be prompted.

```
/forge-skill a skill that reviews PRs by fetching the diff, running tests, and summarizing issues
```

The pipeline runs in 6 steps:

1. **Intake analysis** — classifies skill type, identifies workflow pattern, estimates complexity, decides routing (forge-skill vs forge-harness)
2. **Target + name selection** — project-local, global, or marketplace plugin; user-confirmed kebab-case name
3. **Spec formation loop** — scores understanding across 5 dimensions (trigger clarity, workflow definition, tool requirements, output spec, scope boundaries); asks clarifying questions until ≥90/100; writes `contract.md` + `spec.md` + `learnings.md` to `{skill-dir}/docs/`
4. **Spec execution** — `skill-generator` reads the approved spec and creates all files exactly as specified, including `evals/evals.json` + `evals/validate.mjs` so the skill ships with its own deterministic validator
5. **Validation** — `scripts/validate-skill.mjs` (deterministic, 5-subsystem scoring) + `skill-validator` agent (semantic checks); 20 trigger test queries written to `trigger-tests.md`
6. **Retrospective + delivery** — pattern observations appended to `shared/learnings.md`; reference doc updates proposed if a pattern hits 3+ recurrences

### `/forge-harness [target path] [create|audit|report]`

Scaffolds an agentic harness _into_ a target repository — `AGENTS.md` or `CLAUDE.md`, `feature_list.json`, `progress.md`, `init.sh`, and `session-handoff.md`. Detects the target's stack (Node, Python, Go, Rust, Java, .NET) and emits stack-appropriate verification commands.

```
/forge-harness /path/to/repo create
/forge-harness /path/to/repo audit
/forge-harness /path/to/repo report
```

Three intents:

- **create** — scaffolds the 5-subsystem harness from scratch; never silently overwrites existing files (asks for explicit `--force` consent)
- **audit** — runs `scripts/validate-harness.mjs` against an existing harness; surfaces the lowest-scoring subsystem as a candidate bottleneck
- **report** — generates a self-contained HTML assessment (open in browser)

The 5 subsystems checked: Instructions, State, Verification, Scope, Lifecycle. See `shared/agentic-subsystems.md` for the mental model.

### `/improve-skill [path or name] [optional braindump]`

Analyzes and optimizes an existing SKILL.md. Pass a file path, a skill name, or nothing (to pick from a list). Optional second argument is a braindump of specific improvements.

```
/improve-skill my-skill
/improve-skill ~/.claude/skills/review-pr/SKILL.md
/improve-skill my-skill the description triggers on too many unrelated queries
```

Reads the skill alongside its `docs/spec.md` (if present) and runs three-way analysis: spec vs reality drift, braindump vs spec alignment, braindump vs spec conflict. Then scores four dimensions (0–25 each): description quality, structural compliance, instruction quality, agent/tool optimization.

If the skill has an `evals/validate.mjs`, the deterministic structural score from that script is authoritative for the Structural Compliance dimension. You choose which dimensions to improve, then approve each individual change before it's applied. The final report shows a before/after scorecard, appends a score history entry to `docs/learnings.md` and `docs/history.json`, and runs a retrospective.

### `/optimize-description [path]`

Optimizes a skill's description for trigger accuracy through automated testing. Generates eval queries, runs them, and iterates up to 5 rounds until trigger accuracy improves. Requires `claude` CLI and `uv`.

### `/eval-skill [path]`

Execution-based evaluation. Runs real prompts with and without the skill installed (or between two versions), grades outputs against assertions, and opens a browser-based viewer. Two modes:

- **Create mode** — compares having the skill vs not having it
- **Improve mode** — compares old version against new (file path or git ref)

Pipeline: parallel execution runs → blind A/B comparison → assertion grading → aggregate benchmark → viewer → optional iteration. Requires `uv`.

## Skills + Agents

| Skill           | Role                                                                |
| --------------- | ------------------------------------------------------------------- |
| `forge-skill`   | Generates Claude Code skills (the original creator workflow)        |
| `forge-harness` | Scaffolds agentic harnesses into target repos (NEW in 0.8.0)        |
| `improve-skill` | Analyzes and optimizes existing skills with three-way spec analysis |

Ten subagents handle specialized work:

| Agent              | Model  | Role                                                                 |
| ------------------ | ------ | -------------------------------------------------------------------- |
| `intake-analyst`   | sonnet | Classifies brain dump; routes between forge-skill and forge-harness  |
| `skill-researcher` | sonnet | Scans target location for conflicts and conventions during spec loop |
| `skill-generator`  | opus   | Writes SKILL.md, agents, commands, reference docs, evals/            |
| `skill-validator`  | haiku  | Semantic checks after `validate-skill.mjs` runs deterministic ones   |
| `skill-optimizer`  | sonnet | Three-way analysis (spec + skill + braindump); 4-dimension scoring   |
| `scaffold-writer`  | haiku  | Creates plugin.json, package.json, tsconfig.json boilerplate         |
| `grader`           | sonnet | Grades assertion pass/fail from execution transcripts                |
| `comparator`       | sonnet | Blind A/B quality comparison of two execution outputs                |
| `analyzer`         | sonnet | Post-hoc analysis and benchmark pattern detection                    |
| `retrospective`    | sonnet | Captures patterns into the knowledge base; proposes ref-doc updates  |

## Scripts (deterministic, pure Node.js or Python)

| Script                         | Purpose                                                                      |
| ------------------------------ | ---------------------------------------------------------------------------- |
| `scripts/validate-skill.mjs`   | Scores a skill directory across 5 subsystems; JSON + HTML output             |
| `scripts/validate-harness.mjs` | Scores a target repo's harness across 5 subsystems; JSON + HTML output       |
| `scripts/create-harness.mjs`   | Scaffolds AGENTS.md/feature_list.json/progress.md/init.sh into a target repo |
| `scripts/quick_validate.py`    | Fast Python-based pre-flight checker for generation                          |
| `scripts/run_eval.py`          | Drives the eval pipeline                                                     |
| `scripts/aggregate_history.py` | Summarizes `docs/history.json` across improve runs                           |

The harness scripts are ported from [`walkinglabs/learn-harness-engineering`](https://github.com/walkinglabs/learn-harness-engineering) (MIT).

## Knowledge base

The `shared/` directory contains reference docs that agents read during generation:

- `agentic-subsystems.md` — the 5-subsystem mental model (Instructions/State/Verification/Scope/Lifecycle) used by both forge-skill and forge-harness
- `skill-anatomy.md` — file structure, frontmatter, progressive disclosure, the single-file plugin auto-loading pattern
- `description-engineering.md` — how to write descriptions that trigger correctly
- `anti-patterns.md` — 36 anti-patterns organized as Problem → Golden Rules → Trade-offs → Implementation → Gotchas
- `agent-design.md` — when to use agents, model selection, modern frontmatter fields
- `workflow-patterns.md` — the 5 canonical workflow patterns and when each applies
- `primitives-guide.md` — built-in tool usage (`Task*`, `Monitor`, `LSP`, etc.)
- `checkpointing.md` — when to embed `/rewind` warnings in generated skills
- `local-config-pattern.md` — `userConfig` vs `$XDG_CONFIG_HOME` env-file patterns
- `quality-checklist.md` — pre-generation quality gate
- `eval-schemas.md` — JSON schemas for grading.json, comparison.json
- `history-schema.md` — schema for `docs/history.json`
- `learnings.md` — cross-run pattern observations (this file IS updated by retrospectives)
- `references/` — 6 deep-dive reference docs ported from harness-creator: memory-persistence, context-engineering, tool-registry, multi-agent, lifecycle-bootstrap, gotchas

## Target locations for generated skills

When creating a skill, you choose one of three targets:

- **Project** — `.claude/skills/{name}/` — only the skill directory with SKILL.md
- **Global** — `~/.claude/skills/{name}/` — same minimal output, available across all projects
- **Marketplace** — `{your-marketplace-repo}/plugins/{name}/` — full plugin scaffolding including plugin.json, package.json, tsconfig.json, `evals/evals.json`, `evals/validate.mjs`, `docs/contract.md`, `docs/spec.md`, `docs/learnings.md`, marketplace sync. You'll be asked for the repo path and npm scope at runtime.

Marketplace target gets the full self-improving pattern (evals, docs, history.json). Project/global skills are minimal.

## Self-improving generated skills (new in 0.8.0)

Every marketplace skill generated by skill-forge ships with:

- `evals/evals.json` — 5+ eval cases derived from the spec's success criteria
- `evals/validate.mjs` — wraps `scripts/validate-skill.mjs` with skill-specific component-manifest assertions
- `docs/contract.md`, `docs/spec.md`, `docs/learnings.md` — design record, execution plan, accumulating observations
- `docs/history.json` — version-tracked score history across improve runs

The result: `/improve-skill` has deterministic ground truth across versions. Re-running the same evals on a new version gives an objective regression check.

## Honest trade-offs

The spec formation loop adds a round-trip or two for ambiguous requests — that's intentional. A vague brain dump produces a vague skill; the spec is the catch.

Opus handles generation, which is slower and costs more than validation and scaffolding. For simple command-only skills that cost is often overkill, but the description quality is meaningfully better than sonnet output for this task.

`/eval-skill` runs multiple parallel Claude API calls per prompt — two execution runs plus grading and comparison agents. For 3 test prompts, expect 8–10 API calls before the browser viewer opens. Thorough but not cheap.

`/forge-harness` outputs files INTO the target repo, not the plugin — `--force` is required to overwrite anything that already exists, and the skill explicitly asks for consent before passing it.

## Attribution

The harness-scaffolding capability (`/forge-harness`, the 6 reference docs in `shared/references/`, the 5-subsystem mental model, and the harness validator scripts) is ported and adapted from [`walkinglabs/learn-harness-engineering`](https://github.com/walkinglabs/learn-harness-engineering) under its MIT license.
