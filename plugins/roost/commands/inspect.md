---
name: inspect
description: Scan an existing project for Roost stack integration gaps (auth, billing, email, Cloudflare bindings)
allowed-tools: Read, Glob, Grep, Agent, AskUserQuestion
argument-hint: [project-path]
---

Scan an existing project and produce a gap report for Roost stack integrations.

## Process

1. Determine the project path: use `$ARGUMENTS` if provided, otherwise use AskUserQuestion to ask for the path.
2. Invoke the `roost` skill for the `/roost:inspect` workflow.

## Arguments

| Argument     | Required | Description                                                    |
| ------------ | -------- | -------------------------------------------------------------- |
| `$ARGUMENTS` | No       | Path to the project to inspect (defaults to current directory) |

## Examples

```
/roost:inspect ./my-saas-app
```

```
/roost:inspect
```

(will prompt for project path or use current directory)
