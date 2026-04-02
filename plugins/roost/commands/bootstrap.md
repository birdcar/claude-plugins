---
name: bootstrap
description: Run standardized Roost provisioning via script/bootstrap — install deps, provision resources, run migrations
allowed-tools: Read, Glob, Grep, Bash, Agent, AskUserQuestion
argument-hint: [project-path]
---

Run the Roost bootstrap script to provision external resources for a SaaS project.

## Process

1. Determine the project path: use `$ARGUMENTS` if provided, otherwise default to the current directory.
2. Invoke the `roost` skill for the `/roost:bootstrap` workflow.

## Arguments

| Argument     | Required | Description                                         |
| ------------ | -------- | --------------------------------------------------- |
| `$ARGUMENTS` | No       | Path to the project (defaults to current directory) |

## Examples

```
/roost:bootstrap ./my-saas-app
```

```
/roost:bootstrap
```

(runs script/bootstrap in the current directory)
