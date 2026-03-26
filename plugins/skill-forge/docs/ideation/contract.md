# Contract: skill-forge

## Problem

Writing Claude Code skills is painful despite multiple community tools attempting to help. The pain points are:

1. **No single tool captures best practices from all sources** — Anthropic's guide, community skill authors (dot-skills, ratacat, pytorch), official docs, and agent research all have valuable but scattered insights
2. **Existing skill creators don't leverage Claude's full primitive set** — AskUserQuestion, Tasks, Agents with right-sized models, progressive disclosure, tool restrictions
3. **No quality validation** — skills get written and shipped without trigger testing, structural validation, or anti-pattern checking
4. **No improve path** — existing skills rot without a structured way to audit and optimize them
5. **Skill authoring knowledge isn't embedded in the tool** — users must independently learn frontmatter rules, description engineering, progressive disclosure, and agent design patterns

## Goals

Build a `skill-forge` plugin in the birdcar-plugins marketplace that:

1. Takes a brain dump (messy input) and produces a complete, optimized, production-grade plugin with skills, agents, commands, and hooks — full scaffolding
2. Uses a skill-specific confidence-gated intake (inspired by ideation's pattern) to clarify requirements before generating anything
3. Leverages every Claude primitive: AskUserQuestion for all interactions, Tasks/Todos for state tracking, specifically defined Agents with right-sized models for parallel work
4. Maximizes all available skill metadata: frontmatter fields (name, description, allowed-tools, disable-model-invocation, user-invocable, context, agent, model, argument-hint, hooks, metadata), progressive disclosure structure, `!`command`` dynamic injection
5. Supports three output targets: project skills (`.claude/skills/`), global skills (`~/.claude/skills/`), and marketplace plugins (`~/Code/birdcar/claude-plugins/plugins/`)
6. Includes an improve mode that can analyze and optimize any existing skill anywhere — covering description optimization, structure refactoring, instruction quality, and agent/tool optimization
7. Enforces all known best practices and anti-patterns as guardrails during generation

## Success Criteria

1. **Trigger precision**: Generated skills activate on 90%+ of relevant queries and <10% of irrelevant queries, validated by a generated trigger test suite (20 queries: 10 should-trigger, 10 should-not-trigger)
2. **Structural compliance**: Every generated skill passes automated checks — kebab-case names, no XML in frontmatter, SKILL.md ≤500 lines, progressive disclosure (references/ for heavy content), description ≤1024 chars with trigger phrases in third person
3. **Primitive utilization**: Generated skills use AskUserQuestion (not text questions), appropriate agent definitions with model assignments, allowed-tools restrictions, and Task-based subagent spawning where applicable
4. **Consistency**: Running the same brain dump 3 times produces structurally equivalent output (same components, same workflow shape, same quality score)
5. **Improve mode coverage**: Can take any existing SKILL.md and produce a measurable improvement report with before/after metrics on description quality, structural compliance, instruction specificity, and agent efficiency

## Scope

### In Scope

- Plugin scaffolding generation (plugin.json, package.json, tsconfig.json, src/index.ts)
- SKILL.md generation with full frontmatter and progressive disclosure
- Agent definition generation (.md files with tools, model assignments)
- Command generation (.md files with allowed-tools)
- Hook generation (hooks/hooks.json) when the skill workflow requires them
- Reference document generation (references/ directory)
- Slash command `/forge-skill` for explicit create invocation
- Slash command `/improve-skill` for explicit improve invocation (replacing the existing one in plugin-tools)
- Natural language skill trigger for "create a skill", "build me a skill", etc.
- Natural language skill trigger for "improve this skill", "optimize this skill", etc.
- Confidence-gated intake with AskUserQuestion for requirement clarification
- Trigger test suite generation (20 queries per skill)
- Structural validation checklist
- Dry-run test prompt generation
- Anti-pattern checklist enforcement
- Support for project, global, and marketplace target paths
- Root tsconfig.json reference updates (marketplace target only)
- `bun run sync` execution (marketplace target only)

### Out of Scope

- Runtime TypeScript logic (plugins are prompt-only, src/index.ts is a stub)
- MCP server development
- Plugin marketplace infrastructure changes
- CI/CD pipeline modifications
- Automated trigger test execution (generates tests, user runs them)
- Cross-plugin dependency management

## Constraints

- All plugin intelligence lives in Markdown prompt files, not TypeScript
- Must follow existing repo conventions (kebab-case, Bun workspace, Prettier formatting)
- Skills use SKILL.md with YAML frontmatter (not INSTRUCTIONS.md)
- Hooks go in hooks/hooks.json, never inline in plugin.json
- Agent model assignments: Opus for complex generation, Sonnet for research/agents, Haiku for validation/formatting
- Version bumps required for every functional change to plugin.json

## Key Decisions

1. **Embedded intake over ideation dependency** — The skill-specific confidence-gated workflow asks skill-relevant questions (trigger phrases, workflow type, tools needed, agent complexity) rather than general project questions
2. **Full scaffolding** — Generates complete plugin packages, not just SKILL.md files
3. **Any-skill improve mode** — Works on project, global, and marketplace skills regardless of where they live
4. **Full quality pipeline** — Structural validation + trigger tests + dry-run prompts + anti-pattern checklist
5. **Both command + skill invocation** — `/forge-skill` for intentional use + natural language for conversational discovery

## Execution Plan

### Dependency Graph

```
Phase 1 (Foundation + References)
    ├── Phase 2 (Create Mode)
    └── Phase 3 (Improve Mode)
            └── Phase 4 (Quality Pipeline)
```

Phase 2 and Phase 3 are independent once Phase 1 is complete. Phase 4 depends on Phase 3 (improve mode's analysis patterns inform validation).

### Execution Steps

1. **Phase 1** (sequential — must complete first):

   ```
   /execute-spec docs/ideation/skill-forge/spec-phase-1.md
   ```

2. **Phase 2 + Phase 3** (parallel — independent after Phase 1):
   Start a delegate-mode session and paste the agent team prompt below.

3. **Phase 4** (sequential — after Phase 2 + 3):
   ```
   /execute-spec docs/ideation/skill-forge/spec-phase-4.md
   ```

### Agent Team Prompt (for Phase 2 + 3)

```
Execute two specs in parallel as an agent team:

Teammate 1 — Create Mode:
  Spec: docs/ideation/skill-forge/spec-phase-2.md
  Scope: Build the /forge-skill command, create-skill skill, and all supporting agents for the create workflow.

Teammate 2 — Improve Mode:
  Spec: docs/ideation/skill-forge/spec-phase-3.md
  Scope: Build the /improve-skill command, improve-skill skill, and all supporting agents for the improve workflow.

Coordinate on shared files:
  - plugins/skill-forge/plugin.json (both add entries — Teammate 1 creates it, Teammate 2 appends)
  - plugins/skill-forge/shared/ (both may reference shared knowledge base from Phase 1)
Only one teammate should modify a shared file at a time.
```
