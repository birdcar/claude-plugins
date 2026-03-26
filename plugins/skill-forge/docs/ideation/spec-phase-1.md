# Spec: Phase 1 — Plugin Foundation + Knowledge Base

## Overview

Scaffold the `skill-forge` plugin structure and create the shared knowledge base (reference documents) that power both create and improve modes. This phase produces no user-facing workflows — it lays the foundation.

## Technical Approach

This plugin follows the repo's convention: all intelligence in Markdown, TypeScript stubs for workspace management only. The knowledge base lives in `shared/` and `references/` directories, loaded progressively by skills and agents in later phases.

Key decision: the knowledge base is **compiled from research** (official docs, community sources, prompting guide) into opinionated reference documents, not raw copies of external content. This ensures the skill-forge agents get consistent, actionable guidance without needing to re-research at runtime.

## File Changes

### New Files

| File                                                           | Purpose                                                                                                                                                          |
| -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plugins/skill-forge/package.json`                             | Bun workspace package                                                                                                                                            |
| `plugins/skill-forge/tsconfig.json`                            | Extends base config                                                                                                                                              |
| `plugins/skill-forge/src/index.ts`                             | Stub export                                                                                                                                                      |
| `plugins/skill-forge/plugin.json`                              | Plugin manifest (name, version, description, commands, skills)                                                                                                   |
| `plugins/skill-forge/shared/skill-anatomy.md`                  | Complete reference: what a skill is, all frontmatter fields, directory structure, progressive disclosure rules                                                   |
| `plugins/skill-forge/shared/description-engineering.md`        | The art of writing descriptions: formula, trigger phrases, third-person rule, negative cases, character budget, optimization loop                                |
| `plugins/skill-forge/shared/anti-patterns.md`                  | Comprehensive anti-pattern checklist compiled from all sources with explanations and fixes                                                                       |
| `plugins/skill-forge/shared/agent-design.md`                   | Agent definition patterns: tools list, model sizing, subagent spawning, context:fork, allowed-tools                                                              |
| `plugins/skill-forge/shared/workflow-patterns.md`              | The five structural patterns: sequential orchestration, multi-MCP coordination, iterative refinement, context-aware tool selection, domain-specific intelligence |
| `plugins/skill-forge/shared/primitives-guide.md`               | How to use every Claude primitive effectively: AskUserQuestion patterns, Task/Todo usage, Agent spawning, model selection, dynamic injection                     |
| `plugins/skill-forge/shared/quality-checklist.md`              | The full quality pipeline checklist: structural compliance, trigger tests, dry-run format, anti-pattern scan                                                     |
| `plugins/skill-forge/shared/templates/skill-template.md`       | SKILL.md generation template with all frontmatter fields and section structure                                                                                   |
| `plugins/skill-forge/shared/templates/agent-template.md`       | Agent .md generation template with tools, model, and system prompt structure                                                                                     |
| `plugins/skill-forge/shared/templates/command-template.md`     | Command .md generation template with allowed-tools and workflow sections                                                                                         |
| `plugins/skill-forge/shared/templates/plugin-json-template.md` | plugin.json generation template with all valid fields                                                                                                            |
| `plugins/skill-forge/shared/templates/hooks-json-template.md`  | hooks/hooks.json generation template with PreToolUse/PostToolUse patterns                                                                                        |

### Modified Files

| File                   | Change                                          |
| ---------------------- | ----------------------------------------------- |
| `tsconfig.json` (root) | Add project reference for `plugins/skill-forge` |

## Implementation Details

### Component 1: Plugin Scaffolding

Standard plugin scaffold following repo conventions.

**plugin.json**:

```json
{
  "name": "skill-forge",
  "version": "0.1.0",
  "description": "Generate and optimize production-grade Claude Code skills from brain dumps",
  "commands": ["./commands/"],
  "agents": [
    "./agents/intake-analyst.md",
    "./agents/skill-researcher.md",
    "./agents/skill-generator.md",
    "./agents/skill-validator.md",
    "./agents/skill-optimizer.md",
    "./agents/scaffold-writer.md"
  ]
}
```

Note: skills auto-discovered from `skills/` directory — no explicit `"skills"` field needed.

**package.json**:

```json
{
  "name": "@birdcar/claude-plugin-skill-forge",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts"
}
```

### Component 2: Knowledge Base — `shared/skill-anatomy.md`

Compile from research into a single authoritative reference. Must cover:

1. **Directory structure** — exact file names (SKILL.md, not INSTRUCTIONS.md), kebab-case folders, references/ and scripts/ conventions
2. **Frontmatter fields** — complete field reference with types, constraints, and examples:
   - `name`: kebab-case, no XML, no "claude"/"anthropic", max 64 chars
   - `description`: max 1024 chars, no XML, third-person, trigger phrases
   - `allowed-tools`: comma-separated or space-separated, MCP tools need `ServerName:tool_name`
   - `disable-model-invocation`: boolean, prevents auto-loading
   - `user-invocable`: boolean, hides from / menu
   - `context`: `fork` for isolated subagent execution
   - `agent`: subagent type (Explore, Plan, general-purpose, custom)
   - `model`: override model for this skill
   - `argument-hint`: autocomplete hint text
   - `hooks`: skill-scoped lifecycle hooks
   - `metadata`: arbitrary key-value pairs (author, version, tags, etc.)
3. **Progressive disclosure** — three levels (metadata → SKILL.md body → references/), one-level-deep rule, 500-line limit
4. **`$ARGUMENTS` handling** — `$ARGUMENTS`, `$N`, `${CLAUDE_SESSION_ID}`, `${CLAUDE_SKILL_DIR}`
5. **`!`command`` dynamic injection** — preprocessing pattern, use cases
6. **Invocation matrix** — disable-model-invocation × user-invocable combinations

### Component 3: Knowledge Base — `shared/description-engineering.md`

The highest-leverage field. Must cover:

1. **The formula**: `[What it does] + [When to use it] + [Key trigger terms]`
2. **Third-person rule** with good/bad examples
3. **Trigger phrase engineering** — include exact phrases users say, domain terms, file types
4. **Negative cases** — `"Do NOT use for..."` to prevent activation conflicts
5. **Character budget** — 1024 max, context window 2% budget, competition with other skills
6. **Optimization loop** — generate 20 trigger-eval queries (10 should, 10 shouldn't), test, refine
7. **Debugging** — "Ask Claude: when would you use the [name] skill?"

### Component 4: Knowledge Base — `shared/anti-patterns.md`

Compiled checklist with severity ratings:

- CRITICAL: XML in frontmatter, non-kebab-case names, SKILL.MD vs SKILL.md, names with "claude"/"anthropic", descriptions >1024 chars
- HIGH: Vague descriptions, overlapping descriptions, buried constraints, deeply nested references, ALL CAPS without rationale, >500 lines in SKILL.md
- MEDIUM: Time-sensitive information, inconsistent terminology, Windows paths, no examples, no error handling in scripts
- LOW: Missing metadata fields, no argument-hint, verbose instructions where concise would work

### Component 5: Knowledge Base — `shared/agent-design.md`

Agent definition patterns:

1. **Agent .md structure** — frontmatter (name, description, tools, model) + system prompt body
2. **Model right-sizing** — Opus for complex reasoning/generation, Sonnet for research/analysis/standard agents, Haiku for validation/formatting/simple ops
3. **Tools list** — only grant what's needed (principle of least privilege)
4. **Subagent spawning** — `Task` with `subagent_type: "plugin-name:agent-name"`
5. **Agent teams** — when to use parallel agents, delegate mode, shared file coordination
6. **context:fork** — when to use, caveats (needs explicit task, not reference-only)

### Component 6: Knowledge Base — `shared/workflow-patterns.md`

Five canonical patterns with when-to-use guidance:

1. **Sequential orchestration** — linear steps with dependencies and rollback
2. **Multi-MCP coordination** — phase separation, data passing, central error handling
3. **Iterative refinement** — draft → validate → refine with quality criteria and termination
4. **Context-aware tool selection** — decision trees for which tool when
5. **Domain-specific intelligence** — compliance logic before tool calls, audit trails

Each pattern includes: description, when to use, SKILL.md structure template, example.

### Component 7: Knowledge Base — `shared/primitives-guide.md`

How to use Claude's primitives effectively in skills:

1. **AskUserQuestion** — always use for decisions, provide 2-4 options, use multiSelect, keep headers ≤12 chars, use preview for comparisons
2. **Tasks/Todos** — TodoWrite for checklists in multi-step workflows, Task for spawning agents, TaskList/TaskGet for state tracking across compaction
3. **Agent tool** — subagent_type selection, model override, run_in_background for parallel work, isolation:worktree for git safety
4. **Read/Write/Edit** — when to use each, Edit for surgical changes, Write for new files
5. **Glob/Grep** — pattern-based search, Grep for content, Glob for file discovery
6. **WebFetch/WebSearch** — research patterns, when to use agents for research vs inline
7. **Bash** — only for operations without dedicated tools, script execution
8. **Model selection** — opus for main skill logic, sonnet for agent teams, haiku for formatting/validation

### Component 8: Generation Templates

Parameterized templates in `shared/templates/` that the generator agents fill in. Each template has:

- All valid fields with `{placeholder}` markers
- Comments explaining each field's purpose
- Conditional sections (e.g., "include if skill uses agents")
- Examples of filled-in values

## Testing Requirements

- `bun run typecheck` passes with new plugin
- `bun run build` succeeds
- `bun run sync` updates marketplace.json with skill-forge entry
- All reference documents are valid Markdown
- Templates have no unfilled placeholders (they should use `{placeholder}` format consistently)

## Validation Commands

```bash
cd /Users/birdcar/Code/birdcar/claude-plugins
bun run typecheck
bun run build
bun run sync
bun run format:check
# Verify marketplace.json includes skill-forge
grep -q "skill-forge" .claude-plugin/marketplace.json && echo "OK" || echo "MISSING"
```

## Open Items

- Exact wording of each reference doc emerges during implementation — the structure above is the blueprint, content should be compiled from the research findings
- Template syntax (`{placeholder}` vs `{{placeholder}}` vs `$PLACEHOLDER`) — use `{placeholder}` for consistency with ideation templates
