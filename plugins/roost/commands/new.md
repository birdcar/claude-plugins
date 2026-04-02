---
name: new
description: Generate a new full-stack SaaS project on the Cloudflare Workers + React Router 7 + WorkOS + Stripe + Resend + Twilio + PostHog stack from a product description
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion
argument-hint: [product description]
---

Generate a new Roost SaaS project from a product description.

## Process

1. If `$ARGUMENTS` is provided, use it as the initial product description. Otherwise, use AskUserQuestion to gather the product description.
2. Invoke the `roost` skill for the full `/roost:new` workflow.

## Arguments

| Argument     | Required | Description                                                                         |
| ------------ | -------- | ----------------------------------------------------------------------------------- |
| `$ARGUMENTS` | No       | Brief product description (e.g., "project management tool with team collaboration") |

## Examples

```
/roost:new project management tool for small teams with task boards and time tracking
```

```
/roost:new
```

(will prompt for product description interactively)
