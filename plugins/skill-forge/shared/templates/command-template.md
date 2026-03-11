# Command Template

Generate command `.md` files using this structure. Replace `{placeholders}` with actual values.

## Frontmatter

```yaml
---
name: { command-name }
description: { One-line description shown in / autocomplete menu }
allowed-tools: { Tool1, Tool2, Tool3 }
argument-hint: [{ hint text }]
---
```

### Common allowed-tools sets

| Command type         | Tools                                                                                       |
| -------------------- | ------------------------------------------------------------------------------------------- |
| Read-only analysis   | Read, Grep, Glob                                                                            |
| Code generation      | Read, Write, Edit, Glob, Grep, Bash                                                         |
| Interactive workflow | Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, TodoWrite                      |
| Full access          | Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, TodoWrite, WebFetch, WebSearch |

## Body Structure

```markdown
{Brief description of what this command does — 1-2 sentences.}

## Process

1. {Step 1}
2. {Step 2}
3. {Continue...}

## Arguments

| Argument            | Required | Description          |
| ------------------- | -------- | -------------------- |
| `$0` / `$ARGUMENTS` | {Yes/No} | {What it represents} |

## Examples
```

/{command-name} {example args}

```
{Expected behavior}

## Important Rules

- {Rule 1}
- {Rule 2}
```

## Guidelines

- Commands are for explicit user invocation via `/name`
- Keep the body concise — commands are entry points, not full workflows
- If the command triggers a skill, say so explicitly: "Invoke the {skill-name} skill"
- `allowed-tools` gates what Claude can use without per-use approval
- Use `argument-hint` for autocomplete: `[file-path]`, `[description]`, `[url]`
