---
name: retrospect
description: Analyze the current Roost build session and capture learnings about stack integration patterns
allowed-tools: Read, Glob, Grep, Write, Edit, Agent
argument-hint: [project-path]
---

Analyze a Roost build session and update the learnings knowledge base.

## Process

1. Determine the project path: use `$ARGUMENTS` if provided, otherwise use the current directory.
2. Invoke the `roost` skill for the `/roost:retrospect` workflow.

## Arguments

| Argument     | Required | Description                                                    |
| ------------ | -------- | -------------------------------------------------------------- |
| `$ARGUMENTS` | No       | Path to the project to analyze (defaults to current directory) |

## Examples

```
/roost:retrospect ./my-saas-app
```

```
/roost:retrospect
```

(analyzes current directory)
