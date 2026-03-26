# Spec: Phase 2 — Create Mode

## Overview

Build the skill creation workflow: a `/forge-skill` command + `create-skill` skill for natural language triggering + specialized agents that handle intake, research, generation, scaffolding, and validation. This is the core value prop — brain dump in, production-grade plugin out.

## Technical Approach

The create workflow follows a confidence-gated pipeline inspired by ideation but customized for skill authoring:

```
INTAKE → SKILL ANALYSIS → CONFIDENCE GATE → GENERATION → SCAFFOLDING → VALIDATION → DELIVERY
   ↓           ↓               ↓                ↓            ↓             ↓           ↓
 Accept     Classify:        AskUser         Parallel:     Write all     Quality     Present
 brain     skill type,      Questions       - SKILL.md     files to     pipeline    results +
 dump      workflow,       until ≥90%       - agents       target       checks      next steps
           primitives                       - commands      path
           needed                           - references
```

Key architectural decisions:

- **The skill orchestrates, agents execute** — the SKILL.md defines the workflow and decision points; agents handle the heavy lifting (research, generation, validation) in parallel where possible
- **Right-sized models** — intake analyst (Sonnet), researcher (Sonnet), generator (Opus via main thread), validator (Haiku), scaffold writer (Haiku)
- **AskUserQuestion at every decision point** — target path, skill type, workflow pattern, confidence gaps, generation review, delivery confirmation

## File Changes

### New Files

| File                                               | Purpose                                                                                        |
| -------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `plugins/skill-forge/commands/forge-skill.md`      | Slash command entry point for create mode                                                      |
| `plugins/skill-forge/skills/create-skill/SKILL.md` | Natural language trigger skill for create mode                                                 |
| `plugins/skill-forge/agents/intake-analyst.md`     | Analyzes brain dump, classifies skill type, identifies primitives needed (Sonnet)              |
| `plugins/skill-forge/agents/skill-researcher.md`   | Researches existing codebase for patterns, conventions, similar skills (Sonnet)                |
| `plugins/skill-forge/agents/skill-generator.md`    | Generates SKILL.md content, agent definitions, command definitions (Opus)                      |
| `plugins/skill-forge/agents/scaffold-writer.md`    | Writes plugin scaffolding files — plugin.json, package.json, tsconfig.json, hooks.json (Haiku) |

### Modified Files

| File                              | Change                                                              |
| --------------------------------- | ------------------------------------------------------------------- |
| `plugins/skill-forge/plugin.json` | Add commands and agents entries (created in Phase 1, modified here) |

## Implementation Details

### Component 1: `/forge-skill` Command

**File**: `commands/forge-skill.md`

```yaml
---
name: forge-skill
description: Create a production-grade Claude Code skill from a brain dump. Generates complete plugin scaffolding with optimized skills, agents, commands, and hooks.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, TodoWrite
argument-hint: [brain dump or description of the skill you want]
---
```

**Body workflow**:

1. If `$ARGUMENTS` is empty, use AskUserQuestion to ask what skill they want to build
2. Invoke the `create-skill` skill with the arguments
3. The command is a thin wrapper — all logic lives in the skill

### Component 2: `create-skill` Skill — SKILL.md

**File**: `skills/create-skill/SKILL.md`

```yaml
---
name: create-skill
description: >-
  Generates production-grade Claude Code skills from unstructured brain dumps.
  Creates complete plugin packages with optimized SKILL.md, agents, commands,
  and hooks. Use when the user asks to "create a skill", "build a skill",
  "make a skill that...", "write a skill for...", "generate a skill", or
  describes functionality they want as a reusable skill.
  Do NOT use for general code generation, documentation writing, or when
  the user wants to modify existing code that isn't a skill.
---
```

**SKILL.md body structure** (must stay under 500 lines — heavy content in references/):

#### Section 1: Quick Start

- Accept brain dump from `$ARGUMENTS` or conversation context
- State the pipeline: Intake → Analysis → Confidence Gate → Generation → Scaffolding → Validation → Delivery

#### Section 2: Step 1 — Intake & Analysis

- Accept whatever messy input the user provides
- Spawn `skill-forge:intake-analyst` agent via Agent tool (Sonnet) with the brain dump
- The agent returns a structured analysis:
  - **Skill classification**: command-only, skill-only, command+skill, multi-skill plugin
  - **Workflow pattern**: which of the 5 canonical patterns (sequential, iterative, etc.)
  - **Primitives needed**: which Claude tools the skill will use
  - **Agent needs**: how many agents, what roles, what models
  - **Complexity estimate**: simple (1 SKILL.md), moderate (skill + agents), complex (multi-skill + agent team)
  - **Similar existing skills**: any in the target location that might conflict or overlap

#### Section 3: Step 2 — Target Selection

- Use AskUserQuestion to determine where to write the skill:
  - Project skill (`.claude/skills/` in current directory)
  - Global skill (`~/.claude/skills/`)
  - Marketplace plugin (`~/Code/birdcar/claude-plugins/plugins/`)
- If marketplace: generate full plugin scaffolding
- If project/global: generate skill directory only (SKILL.md + references/ + scripts/)

#### Section 4: Step 3 — Confidence Gate

- Score five dimensions (0-20 each, skill-specific):

| Dimension            | Question                                                                 |
| -------------------- | ------------------------------------------------------------------------ |
| Trigger Clarity      | Can I write a description that activates precisely on the right queries? |
| Workflow Definition  | Do I know the exact steps this skill should follow?                      |
| Tool Requirements    | Do I know which Claude primitives and external tools are needed?         |
| Output Specification | Do I know what artifacts this skill produces and in what format?         |
| Scope Boundaries     | Do I know what this skill does NOT do?                                   |

- Threshold: ≥90% to proceed (skill-specific — higher than ideation's 95% because the domain is narrower)
- Use AskUserQuestion for all clarifying questions with structured options
- Loop until threshold met

#### Section 5: Step 4 — Codebase Research (if target has existing code)

- Spawn `skill-forge:skill-researcher` agent (Sonnet) to examine:
  - Existing skills at the target location (naming patterns, conventions)
  - Similar skills that might conflict (for description negative cases)
  - Codebase patterns to reference in the skill's instructions
- Skip for greenfield/empty target locations

#### Section 6: Step 5 — Generation

- Use the research findings + intake analysis + confidence answers
- Read the appropriate templates from `${CLAUDE_SKILL_DIR}/../shared/templates/`
- Read the knowledge base docs from `${CLAUDE_SKILL_DIR}/../shared/` as needed
- Generate all artifacts in memory first, then present for review:
  - **SKILL.md** — using skill-template.md, with all frontmatter fields populated
  - **Agent definitions** — one per identified agent need, using agent-template.md
  - **Command definition** — if command+skill pattern, using command-template.md
  - **Reference docs** — any heavy content extracted from SKILL.md to stay under 500 lines
  - **Scripts** — any validation or helper scripts the skill needs
  - **Hooks** — if the skill workflow requires pre/post tool hooks

- Use AskUserQuestion to present the generated plan:
  - Show: skill name, description, component list, workflow summary
  - Options: "Approved", "Adjust description", "Change workflow", "Add/remove components", "Start over"

#### Section 7: Step 6 — Scaffolding & Writing

- If marketplace target:
  - Spawn `skill-forge:scaffold-writer` agent (Haiku) to write: plugin.json, package.json, tsconfig.json, src/index.ts
  - Write all skill/agent/command/hook files
  - Add reference to root tsconfig.json
  - Run `bun run sync`
- If project/global target:
  - Create skill directory at target path
  - Write SKILL.md + references/ + scripts/
- Use TodoWrite to track file creation progress

#### Section 8: Step 7 — Validation

- Run the quality pipeline (details in Phase 4, but inline basics here):
  1. **Structural check**: frontmatter fields valid, naming correct, line count OK
  2. **Trigger test generation**: produce 20 test queries in a `trigger-tests.md` file alongside the skill
  3. **Anti-pattern scan**: check against `shared/anti-patterns.md`
- If marketplace: run `bun run typecheck && bun run build && bun run format:check`
- Use AskUserQuestion to present validation results

#### Section 9: Step 8 — Delivery

- Present summary: files created, location, next steps
- If marketplace: remind to bump version and sync before committing
- Generate a "getting started" snippet showing how to invoke the new skill
- Suggest running trigger tests to verify activation precision

### Component 3: `intake-analyst` Agent

**File**: `agents/intake-analyst.md`

```yaml
---
name: intake-analyst
description: >-
  Analyzes brain dumps to classify skill type, identify workflow patterns,
  determine primitive needs, and estimate complexity. Use when the create-skill
  workflow needs to understand what the user wants to build.
tools:
  - Read
  - Glob
  - Grep
model: sonnet
---
```

**System prompt body**:

- Role: You are a skill requirements analyst
- Input: Raw brain dump text + optional codebase context
- Process: Extract signals for each classification dimension
- Read `${CLAUDE_PLUGIN_ROOT}/shared/workflow-patterns.md` to classify the workflow pattern
- Read `${CLAUDE_PLUGIN_ROOT}/shared/primitives-guide.md` to identify needed primitives
- Output format: structured JSON-like analysis with all classification fields
- Constraint: never generate skill content — only analyze and classify

### Component 4: `skill-researcher` Agent

**File**: `agents/skill-researcher.md`

```yaml
---
name: skill-researcher
description: >-
  Researches the target codebase for existing skill patterns, naming conventions,
  potential conflicts, and referenceable code patterns. Use when creating a skill
  that targets a location with existing code.
tools:
  - Read
  - Glob
  - Grep
model: sonnet
---
```

**System prompt body**:

- Role: You are a codebase researcher for skill creation
- Input: Target path + skill classification from intake-analyst
- Process: Search for existing skills, analyze their structure, identify conflicts
- Search patterns: `**/SKILL.md`, `**/plugin.json`, `**/.claude/skills/`
- Output: structured findings (existing skills list, naming patterns, potential conflicts, useful patterns to reference)
- Constraint: read-only — never modify files

### Component 5: `skill-generator` Agent

**File**: `agents/skill-generator.md`

```yaml
---
name: skill-generator
description: >-
  Generates complete skill artifacts (SKILL.md, agent definitions, command
  definitions, reference docs) from analyzed requirements. The core generation
  engine of skill-forge.
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
model: opus
---
```

**System prompt body**:

- Role: You are an expert skill author generating production-grade Claude Code skills
- Input: Intake analysis + research findings + confidence-gate answers + user-approved plan
- Process:
  1. Read all relevant templates from `${CLAUDE_PLUGIN_ROOT}/shared/templates/`
  2. Read knowledge base docs as needed from `${CLAUDE_PLUGIN_ROOT}/shared/`
  3. Generate SKILL.md with full frontmatter, progressive disclosure, front-loaded constraints
  4. Generate agent definitions with right-sized models and minimal tool grants
  5. Generate command definitions with appropriate allowed-tools
  6. Generate reference docs for any content that pushes SKILL.md over 500 lines
  7. Generate hooks.json if the workflow requires tool interception
- Key rules (from knowledge base — inline the critical ones):
  - Description: third-person, trigger phrases, negative cases, ≤1024 chars
  - SKILL.md: ≤500 lines, constraints in first 100 lines, imperative form
  - Agents: tools list = principle of least privilege, model = right-sized
  - Progressive disclosure: heavy content → references/, scripts → execute don't load
- Output: all generated files written to target path
- Constraint: must follow templates exactly for structural consistency

### Component 6: `scaffold-writer` Agent

**File**: `agents/scaffold-writer.md`

```yaml
---
name: scaffold-writer
description: >-
  Writes plugin scaffolding files (plugin.json, package.json, tsconfig.json,
  src/index.ts) for marketplace plugins. Handles workspace integration and sync.
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
model: haiku
---
```

**System prompt body**:

- Role: You are a plugin scaffolding writer
- Input: Plugin name, description, version, list of commands/agents/skills to register
- Process:
  1. Read `${CLAUDE_PLUGIN_ROOT}/shared/templates/plugin-json-template.md` for plugin.json structure
  2. Create directory structure at `plugins/{name}/`
  3. Write plugin.json, package.json, tsconfig.json, src/index.ts
  4. Add project reference to root tsconfig.json
  5. Run `bun run sync` to update marketplace.json
  6. Run `bun run typecheck && bun run build` to verify
- Constraint: only write scaffolding files — never write skill/agent/command content

## Testing Requirements

- `/forge-skill` command appears in Claude Code's `/` menu
- Natural language "create a skill that..." triggers the create-skill skill
- Intake analyst correctly classifies at least 3 different brain dump types
- AskUserQuestion is used at every decision point (never text questions)
- Generated SKILL.md files have valid frontmatter
- Generated agent files have valid tools lists
- Marketplace scaffold passes typecheck + build + sync

## Validation Commands

```bash
cd /Users/birdcar/Code/birdcar/claude-plugins
bun run typecheck
bun run build
bun run sync
bun run format:check
```

## Open Items

- The `skill-generator` agent is the most complex component — it may need its own reference docs to inline critical rules without exceeding its context. Consider splitting generation into sub-tasks if the agent prompt exceeds ~200 lines.
- The exact AskUserQuestion options at each step will be refined during implementation based on what feels natural in testing.
