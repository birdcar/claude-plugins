---
name: upgrade
description: Audit an existing Roost stack project and apply improvements — updates patterns, closes integration gaps, and applies latest best practices from reference docs
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion
argument-hint: [project-path]
---

Audit and upgrade an existing Roost stack project to the latest patterns and best practices.

## Process

1. Determine the project path: use `$ARGUMENTS` if provided, otherwise default to the current directory.
2. Invoke the `roost` skill for the `/roost:upgrade` workflow.

## Arguments

| Argument     | Required | Description                                                    |
| ------------ | -------- | -------------------------------------------------------------- |
| `$ARGUMENTS` | No       | Path to the project to upgrade (defaults to current directory) |

## Examples

```
/roost:upgrade ./my-saas-app
```

```
/roost:upgrade
```

(will audit and upgrade the project in the current directory)
