---
name: bootstrap
description: Run standardized Roost provisioning — create Cloudflare resources, configure WorkOS, Stripe, and Resend
allowed-tools: Read, Glob, Grep, Bash, Agent, AskUserQuestion
argument-hint: [--all|--cf-only|--auth-only|--billing-only|--email-only|--migrate|--seed|--dry-run]
---

Run the Roost bootstrap script to provision external resources for a SaaS project.

## Process

1. Parse flags from `$ARGUMENTS`. Default to `--all` if no flags provided.
2. Invoke the `roost` skill for the `/roost:bootstrap` workflow.

## Arguments

| Argument     | Required | Description                                                                                                                |
| ------------ | -------- | -------------------------------------------------------------------------------------------------------------------------- |
| `$ARGUMENTS` | No       | Bootstrap flags: `--all`, `--cf-only`, `--auth-only`, `--billing-only`, `--email-only`, `--migrate`, `--seed`, `--dry-run` |

## Examples

```
/roost:bootstrap --dry-run
```

```
/roost:bootstrap --cf-only
```

```
/roost:bootstrap
```

(runs full provisioning with `--all`)
