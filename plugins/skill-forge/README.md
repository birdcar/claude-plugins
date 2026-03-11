# skill-forge

Turns a brain dump into a production-grade Claude Code skill. Handles the full pipeline: intake analysis, confidence gating, codebase research, file generation, validation, and delivery — with approval checkpoints at each stage.

## What problem it solves

Writing a good SKILL.md from scratch is deceptively tedious. The description needs third-person trigger phrases and negative cases. The file has to stay under 500 lines with constraints in the first 100. Agent models need to be right-sized. Anti-patterns like vague `allowed-tools` or hooks embedded in `plugin.json` are easy to miss. skill-forge bakes in all of that institutional knowledge so you don't have to carry it in your head.

## Installation

```bash
claude plugin install skill-forge
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

## Agents

Six subagents handle specialized tasks so the main thread stays orchestration-focused:

| Agent | Model | Role |
|---|---|---|
| `intake-analyst` | sonnet | Classifies brain dump into type, pattern, primitives, complexity |
| `skill-researcher` | sonnet | Scans target location for conflicts and conventions |
| `skill-generator` | opus | Writes SKILL.md, agents, commands, reference docs |
| `skill-validator` | haiku | Structural checks, anti-pattern scan, trigger test generation |
| `skill-optimizer` | sonnet | Scores existing skills across four quality dimensions |
| `scaffold-writer` | haiku | Creates plugin.json, package.json, tsconfig.json boilerplate |

## Knowledge base

The `shared/` directory contains reference docs that agents read during generation:

- `skill-anatomy.md` — file structure, frontmatter fields, progressive disclosure rules, variable substitution
- `description-engineering.md` — how to write descriptions that trigger correctly
- `anti-patterns.md` — common mistakes and how to avoid them
- `agent-design.md` — when to use agents vs. inline instructions, model selection guidance
- `workflow-patterns.md` — the five canonical workflow patterns and when each applies
- `primitives-guide.md` — tool usage patterns

## Target locations

When creating a skill, you choose one of three targets:

- **Project** — `.claude/skills/{name}/` — generates only the skill directory with SKILL.md
- **Global** — `~/.claude/skills/{name}/` — same minimal output, available across all projects
- **Marketplace** — `~/Code/birdcar/claude-plugins/plugins/{name}/` — full plugin scaffolding including plugin.json, package.json, tsconfig.json, and marketplace sync

## Honest trade-offs

The confidence gate adds a round-trip or two for ambiguous requests — that's intentional. A vague brain dump produces a vague skill, and the gate exists to catch that before generation. If you already have a precise spec, it clears in one pass.

Opus handles generation, which is slower and costs more than the validation and scaffolding steps. For simple command-only skills, that cost is often overkill, but the description quality and instruction specificity are meaningfully better than sonnet output for this task.
