# Agent Template

Generate agent `.md` files using this structure. Replace `{placeholders}` with actual values.

## Frontmatter

```yaml
---
name: { agent-name }
description: >-
  {What this agent does — one sentence}. {When to spawn it}.
  Use when {specific condition that triggers spawning this agent}.
tools:
  - { Tool1 }
  - { Tool2 }
  - { Tool3 }
model: { opus|sonnet|haiku }
---
```

### Model selection

| Task complexity                                             | Model  |
| ----------------------------------------------------------- | ------ |
| Complex reasoning, creative generation, multi-step analysis | opus   |
| Research, code review, standard analysis, most tasks        | sonnet |
| Validation, formatting, scaffolding, checklists             | haiku  |

### Tool selection

Grant ONLY what's needed:

| Agent role           | Typical tools                                 |
| -------------------- | --------------------------------------------- |
| Read-only researcher | Read, Glob, Grep                              |
| Web researcher       | Read, WebFetch, WebSearch                     |
| File generator       | Read, Write, Edit, Glob                       |
| Full builder         | Read, Write, Edit, Glob, Grep, Bash           |
| Interactive          | Read, Write, Edit, AskUserQuestion, TodoWrite |

## Body Structure

```markdown
# {Agent Name}

You are a {role} that {primary function}.

## Input

{Description of what this agent receives when spawned.}

## Process

1. {First step — be specific about what to read/search/analyze}
2. {Second step}
3. {Continue...}

## Output Format

{Exact structure of what the agent returns. Use a template:}
```

## {Section 1}

{content}

## {Section 2}

{content}

```

## Constraints

- {What this agent must NOT do}
- {Scope boundaries}
- {Safety rules — e.g., "Never modify files you weren't asked to modify"}
- {Quality rules — e.g., "Never fabricate URLs or file paths"}
```

## Guidelines

- Agent prompts: ≤200 lines (agent's own context gets crowded otherwise)
- Role definition: one clear sentence
- Input specification: explicit about what the agent receives
- Output format: exact structure, not "return whatever seems relevant"
- At least 2-3 constraints (every agent needs boundaries)
- Reference `${CLAUDE_PLUGIN_ROOT}/shared/` files for domain knowledge the agent needs
