# Spec: Phase 3 — Improve Mode

## Overview

Build the skill improvement workflow: an `/improve-skill` command + `improve-skill` skill for natural language triggering + a specialized optimizer agent. This mode takes any existing skill (project, global, or marketplace) and produces measurable improvements across description, structure, instruction quality, and agent/tool optimization.

## Technical Approach

The improve workflow is an analysis → recommendation → apply pipeline:

```
LOCATE → ANALYZE → SCORE → RECOMMEND → APPROVE → APPLY → VALIDATE → REPORT
   ↓        ↓        ↓         ↓          ↓        ↓         ↓         ↓
 Find     Read     Rate 4    Generate   AskUser  Edit     Re-score   Before/
 skill    all      dimensions improve-   review   files    after      after
 files    content  0-100     ments       each     with     improve    metrics
                                        change   Edit
```

Key decisions:

- **Non-destructive** — all changes are proposed, shown as diffs, and approved individually via AskUserQuestion
- **Measurable** — produces a before/after scorecard so the user can see the impact
- **Incremental** — applies changes one category at a time, not all at once
- **Universal** — works on any SKILL.md regardless of where it lives

## File Changes

### New Files

| File                                                | Purpose                                                           |
| --------------------------------------------------- | ----------------------------------------------------------------- |
| `plugins/skill-forge/commands/improve-skill.md`     | Slash command entry point for improve mode                        |
| `plugins/skill-forge/skills/improve-skill/SKILL.md` | Natural language trigger skill for improve mode                   |
| `plugins/skill-forge/agents/skill-optimizer.md`     | Analyzes skill and generates improvement recommendations (Sonnet) |

### Modified Files

| File                              | Change                                  |
| --------------------------------- | --------------------------------------- |
| `plugins/skill-forge/plugin.json` | Add improve command and optimizer agent |

## Implementation Details

### Component 1: `/improve-skill` Command

**File**: `commands/improve-skill.md`

```yaml
---
name: improve-skill
description: Analyze and optimize an existing Claude Code skill for better trigger precision, structure, instruction quality, and agent efficiency. Works on any skill anywhere.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, TodoWrite
argument-hint: [path to SKILL.md or skill name]
---
```

**Body workflow**:

1. If `$ARGUMENTS` provided: resolve to a SKILL.md path
   - If it's a path, use directly
   - If it's a name, search common locations: `.claude/skills/`, `~/.claude/skills/`, `plugins/*/skills/`
2. If no arguments: use AskUserQuestion to ask which skill to improve, listing discovered skills
3. Invoke the `improve-skill` skill with the resolved path

### Component 2: `improve-skill` Skill — SKILL.md

**File**: `skills/improve-skill/SKILL.md`

```yaml
---
name: improve-skill
description: >-
  Analyzes and optimizes existing Claude Code skills for better trigger precision,
  structural compliance, instruction quality, and agent efficiency. Produces
  measurable before/after scorecards. Use when the user asks to "improve a skill",
  "optimize a skill", "review a skill", "audit skill quality", "fix skill triggers",
  or points to an existing SKILL.md that needs work.
  Do NOT use for creating new skills (use create-skill instead) or for general
  code review.
---
```

**SKILL.md body structure**:

#### Section 1: Quick Start

- Accept skill path from `$ARGUMENTS` or locate via search
- State the pipeline: Locate → Analyze → Score → Recommend → Apply → Validate → Report

#### Section 2: Step 1 — Locate Skill

- If path provided, read the SKILL.md and all files in the skill directory
- If name provided, search:
  1. `.claude/skills/{name}/SKILL.md` (project)
  2. `~/.claude/skills/{name}/SKILL.md` (global)
  3. `plugins/*/skills/{name}/SKILL.md` (marketplace)
  4. Any `**/skills/{name}/SKILL.md` in working directory
- Also read: parent plugin.json (if in a plugin), any agent .md files referenced, any command .md files, hooks.json, references/ directory contents
- Use AskUserQuestion if multiple matches found

#### Section 3: Step 2 — Analysis & Scoring

- Spawn `skill-forge:skill-optimizer` agent (Sonnet) with all skill content
- The agent scores four dimensions (0-25 each, total /100):

**Description Quality (0-25)**:
| Score | Criteria |
|---|---|
| 0-5 | Missing or vague, no trigger phrases |
| 6-10 | Present but generic, unclear when to activate |
| 11-15 | Specific with some triggers, but missing negative cases |
| 16-20 | Good triggers, third-person, includes "do NOT use for" |
| 21-25 | Excellent — precise triggers, negative cases, concise, tested |

**Structural Compliance (0-25)**:
| Score | Criteria |
|---|---|
| 0-5 | Wrong file name, no frontmatter, missing required fields |
| 6-10 | Valid frontmatter but poor structure, content >500 lines in SKILL.md |
| 11-15 | Good structure, some content should be in references/ |
| 16-20 | Progressive disclosure, constraints front-loaded, good references/ usage |
| 21-25 | Optimal — lean SKILL.md, rich references/, templates in templates/ |

**Instruction Quality (0-25)**:
| Score | Criteria |
|---|---|
| 0-5 | Vague, abstract, no examples |
| 6-10 | Some specifics but mixed with prose, constraints buried |
| 11-15 | Imperative form, numbered steps, but missing examples or error handling |
| 16-20 | Specific + actionable, constraints in first 100 lines, includes examples |
| 21-25 | Optimal — scripts for determinism, rationale over ALL CAPS, complete examples |

**Agent/Tool Optimization (0-25)**:
| Score | Criteria |
|---|---|
| 0-5 | No tool restrictions, no agent definitions, everything runs in main thread |
| 6-10 | Some allowed-tools, but overly broad or missing needed tools |
| 11-15 | Right tools, but model assignments not optimized or agents missing |
| 16-20 | Right-sized models, principle-of-least-privilege tools, agents for parallelizable work |
| 21-25 | Optimal — agent team with right models, minimal tool grants, Task-based spawning, AskUserQuestion for all interactions |

#### Section 4: Step 3 — Recommendations

- Present the scorecard using AskUserQuestion:
  - Show each dimension's score with the most impactful improvement opportunity
  - Options: "Improve all", "Description only", "Structure only", "Instructions only", "Agents/Tools only", "I'm satisfied"
- For each selected dimension, generate specific improvements:
  - Description: rewritten description with trigger phrases, negative cases
  - Structure: file reorganization plan (what moves to references/, what gets split)
  - Instructions: specific rewrites with before/after diffs
  - Agents/Tools: new agent definitions, adjusted tool lists, model reassignments

#### Section 5: Step 4 — Apply Changes

- For each improvement, use AskUserQuestion to show the diff and get approval:
  - Options: "Apply", "Skip", "Modify" (with preview showing old vs new)
- Apply approved changes with Edit tool (surgical, not full rewrites)
- Track applied vs skipped with TodoWrite

#### Section 6: Step 5 — Re-validate & Report

- Re-run the scoring on the modified skill
- Present before/after scorecard:
  ```
  Dimension          Before  After  Change
  ─────────────────  ──────  ─────  ──────
  Description          12      22    +10
  Structure            15      21     +6
  Instructions         18      23     +5
  Agents/Tools          8      19    +11
  ─────────────────  ──────  ─────  ──────
  TOTAL                53      85    +32
  ```
- If in a marketplace plugin: run `bun run typecheck && bun run build`
- Generate trigger tests if the description was changed
- Suggest next steps

### Component 3: `skill-optimizer` Agent

**File**: `agents/skill-optimizer.md`

```yaml
---
name: skill-optimizer
description: >-
  Analyzes existing skills and generates scored improvement recommendations
  across description quality, structural compliance, instruction quality, and
  agent/tool optimization. Use when the improve-skill workflow needs analysis.
tools:
  - Read
  - Glob
  - Grep
model: sonnet
---
```

**System prompt body**:

- Role: You are a skill quality analyst and optimizer
- Input: All skill files (SKILL.md, agents, commands, hooks, references, parent plugin.json)
- Process:
  1. Read `${CLAUDE_PLUGIN_ROOT}/shared/anti-patterns.md` for the anti-pattern checklist
  2. Read `${CLAUDE_PLUGIN_ROOT}/shared/description-engineering.md` for description scoring
  3. Read `${CLAUDE_PLUGIN_ROOT}/shared/skill-anatomy.md` for structural compliance
  4. Read `${CLAUDE_PLUGIN_ROOT}/shared/primitives-guide.md` for agent/tool scoring
  5. Score each dimension with specific evidence
  6. Generate concrete improvement recommendations with before/after examples
- Output format: structured analysis with scores, evidence, and recommendations per dimension
- Constraint: never modify files — analysis and recommendations only

## Testing Requirements

- `/improve-skill` command appears in Claude Code's `/` menu
- Natural language "improve this skill" triggers the improve-skill skill
- Scoring produces consistent results across runs for the same skill
- AskUserQuestion is used for all approvals (never text questions)
- Applied changes are surgical (Edit, not full rewrites)
- Before/after scorecard is accurate

## Validation Commands

```bash
cd /Users/birdcar/Code/birdcar/claude-plugins
bun run typecheck
bun run build
bun run format:check
```

## Open Items

- The scoring rubric will likely need calibration after testing on real skills — consider running it against customer-voice, octoflow, and github-actions-generator skills to calibrate
- Preview support in AskUserQuestion for showing diffs may have rendering limitations — test and fall back to inline markdown if needed
