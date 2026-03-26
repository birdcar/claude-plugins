# skill-forge

Turns a brain dump into a production-grade Claude Code skill. Handles the full pipeline: intake analysis, confidence gating, codebase research, file generation, validation, and delivery — with approval checkpoints at each stage.

## What problem it solves

Writing a good SKILL.md from scratch is deceptively tedious. The description needs third-person trigger phrases and negative cases. The file has to stay under 500 lines with constraints in the first 100. Agent models need to be right-sized. Anti-patterns like vague `allowed-tools` or hooks embedded in `plugin.json` are easy to miss. skill-forge bakes in all of that institutional knowledge so you don't have to carry it in your head.

## Installation

```bash
claude plugin install skill-forge@birdcar-plugins
```

## Commands

### `/forge-skill [brain dump]`

Creates a new skill from scratch. Pass a description inline or leave it empty to be prompted.

```
/forge-skill a skill that reviews PRs by fetching the diff, running tests, and summarizing issues
```

The pipeline runs through eight steps:

1. **Intake analysis** — classifies skill type (`command-only`, `skill-only`, `command+skill`, `multi-skill-plugin`), identifies the workflow pattern, and estimates complexity
2. **Target selection** — asks where to install: project-local (`.claude/skills/`), global (`~/.claude/skills/`), or marketplace plugin
3. **Confidence gate** — scores five dimensions (trigger clarity, workflow definition, tool requirements, output spec, scope boundaries) and asks clarifying questions until the total reaches 90/100
4. **Codebase research** — scans the target location for naming conflicts and existing conventions
5. **Generation plan** — presents the proposed skill name, description, component list, and workflow summary for your approval before writing anything
6. **Scaffolding and writing** — generates SKILL.md, agents, commands, and plugin boilerplate as needed
7. **Validation** — structural checks, anti-pattern scan, and 20 trigger test queries written to `trigger-tests.md`
8. **Delivery** — lists all files written with absolute paths and the exact phrase to trigger the new skill

### `/improve-skill [path or name]`

Analyzes and optimizes an existing SKILL.md. Pass a file path, a skill name, or nothing (to pick from a list).

```
/improve-skill my-skill
/improve-skill ~/.claude/skills/review-pr/SKILL.md
```

The workflow scores four dimensions (0–25 each):

- **Description quality** — trigger phrases, third-person voice, negative cases
- **Structural compliance** — frontmatter, line count, progressive disclosure
- **Instruction quality** — imperative form, constraints placement, examples
- **Agent/tool optimization** — least-privilege tools, right-sized models

You choose which dimensions to improve, then approve each individual change before it's applied. The final report shows a before/after scorecard. If the description was modified, new trigger tests are generated automatically.

### `/optimize-description [path]`

Optimizes a skill's description for trigger accuracy through automated testing. Unlike the quality audit in `/improve-skill`, this command focuses entirely on the description field — generating eval queries, running them, and iterating until trigger accuracy improves.

```
/optimize-description ~/.claude/skills/my-skill/SKILL.md
```

Requires `claude` CLI and `uv`. The optimization loop runs up to five iterations, presenting a before/after score comparison and letting you choose which version to apply.

### `/eval-skill [path]`

Execution-based evaluation of a skill. Runs real prompts with and without the skill installed (or between two versions), grades outputs against assertions, and opens a browser-based viewer to review results. This measures actual output quality, not structural compliance.

```
/eval-skill my-skill
/eval-skill ~/.claude/skills/review-pr/SKILL.md
```

Two modes:

- **Create mode** — compares having the skill installed vs. not having it, to confirm the skill actually improves outputs
- **Improve mode** — compares an old version against a new version; accepts a file path or a git ref for the old version

The pipeline: parallel execution runs → blind A/B comparison → assertion grading → aggregate benchmark → browser viewer → optional iteration. All runs launch in parallel. The comparator is blind — it doesn't know which config produced which output.

Requires `uv`.

## Agents

Ten subagents handle specialized tasks so the main thread stays orchestration-focused:

| Agent              | Model  | Role                                                              |
| ------------------ | ------ | ----------------------------------------------------------------- |
| `intake-analyst`   | sonnet | Classifies brain dump into type, pattern, primitives, complexity  |
| `skill-researcher` | sonnet | Scans target location for conflicts and conventions               |
| `skill-generator`  | opus   | Writes SKILL.md, agents, commands, reference docs                 |
| `skill-validator`  | haiku  | Structural checks, anti-pattern scan, trigger test generation     |
| `skill-optimizer`  | sonnet | Scores existing skills across four quality dimensions             |
| `scaffold-writer`  | haiku  | Creates plugin.json, package.json, tsconfig.json boilerplate      |
| `grader`           | sonnet | Grades assertion pass/fail from execution transcripts             |
| `comparator`       | sonnet | Blind A/B quality comparison of two execution outputs             |
| `analyzer`         | sonnet | Post-hoc analysis and benchmark pattern detection                 |
| `retrospective`    | sonnet | Captures patterns from forge/improve runs into the knowledge base |

## Knowledge base

The `shared/` directory contains reference docs that agents read during generation:

- `skill-anatomy.md` — file structure, frontmatter fields, progressive disclosure rules, variable substitution
- `description-engineering.md` — how to write descriptions that trigger correctly
- `anti-patterns.md` — common mistakes and how to avoid them
- `agent-design.md` — when to use agents vs. inline instructions, model selection guidance
- `workflow-patterns.md` — the five canonical workflow patterns and when each applies
- `primitives-guide.md` — tool usage patterns
- `eval-schemas.md` — JSON schemas for grading.json, comparison.json, and related eval artifacts

## Target locations

When creating a skill, you choose one of three targets:

- **Project** — `.claude/skills/{name}/` — generates only the skill directory with SKILL.md
- **Global** — `~/.claude/skills/{name}/` — same minimal output, available across all projects
- **Marketplace** — `{your-marketplace-repo}/plugins/{name}/` — full plugin scaffolding including plugin.json, package.json, tsconfig.json, and marketplace sync. You'll be asked for the repo path and npm scope at runtime.

## Honest trade-offs

The confidence gate adds a round-trip or two for ambiguous requests — that's intentional. A vague brain dump produces a vague skill, and the gate exists to catch that before generation. If you already have a precise spec, it clears in one pass.

Opus handles generation, which is slower and costs more than the validation and scaffolding steps. For simple command-only skills, that cost is often overkill, but the description quality and instruction specificity are meaningfully better than sonnet output for this task.

`/eval-skill` runs multiple parallel Claude API calls per prompt — two execution runs plus grading and comparison agents. For 3 test prompts, expect 8–10 API calls total before the browser viewer opens. It's thorough but not cheap.
