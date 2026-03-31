---
name: roost
description: >-
  Generates full-stack SaaS applications on Cloudflare Workers with WorkOS auth,
  Stripe billing, and Resend email from a product description. Orchestrates
  domain specialists to scaffold, wire auth, implement billing, and set up email.
  Use when the user asks to "build a SaaS app", "create a new SaaS project",
  "generate a full-stack app on Cloudflare", "set up auth and billing",
  "upgrade my project to latest patterns", or start a greenfield SaaS application.
  Do NOT use for frontend-only projects, non-Cloudflare deployments, or
  general code review unrelated to stack integrations.
---

# Roost

Full-stack SaaS builder for the Cloudflare Workers + WorkOS + Stripe + Resend stack. Generates production-ready applications with auth, billing, email, and deployment from a product description.

## Critical Rules

- Use AskUserQuestion for all decisions that need user input — product description, billing model selection, feature choices. Plain text questions cannot capture structured responses.
- Never hardcode API keys, tokens, or credentials in generated code. All secrets go through `wrangler secret put` and are accessed via `env.SECRET_NAME` bindings.
- Never read config files directly — use `bash ${CLAUDE_SKILL_DIR}/scripts/load-config.sh` for credential access.
- Always verify webhook signatures (Stripe and WorkOS) before processing events — unverified webhooks are a security vulnerability.
- Send email via Cloudflare Queues, not synchronously — queue-based sending provides retry and prevents request timeouts.
- Use idempotency keys for all transactional email to prevent duplicates on retry.
- Agents are dispatched sequentially: cloudflare-architect -> workos-specialist -> stripe-specialist -> resend-specialist -> bootstrap-writer. Each depends on the previous agent's output.
- Summarize agent results for the user after each agent completes — the user cannot see raw agent output.
- Generated projects must follow the directory structure defined in `${CLAUDE_SKILL_DIR}/references/stack-architecture.md`.

## Prerequisites

This skill requires local configuration at `~/.config/roost/`:

| File              | Required | Keys                                                                                                         |
| ----------------- | -------- | ------------------------------------------------------------------------------------------------------------ |
| `credentials.env` | Yes      | `CF_API_TOKEN`, `CF_ACCOUNT_ID`, `WORKOS_API_KEY`, `WORKOS_CLIENT_ID`, `STRIPE_SECRET_KEY`, `RESEND_API_KEY` |

If missing, instruct the user to create it:

```bash
mkdir -p ~/.config/roost && chmod 700 ~/.config/roost
cat > ~/.config/roost/credentials.env << 'EOF'
CF_API_TOKEN=your-cloudflare-api-token
CF_ACCOUNT_ID=your-cloudflare-account-id
WORKOS_API_KEY=your-workos-api-key
WORKOS_CLIENT_ID=your-workos-client-id
STRIPE_SECRET_KEY=your-stripe-restricted-key
RESEND_API_KEY=your-resend-api-key
EOF
chmod 600 ~/.config/roost/credentials.env
```

## /roost:new Workflow

### Step 1: Gather Requirements

Use AskUserQuestion to collect:

1. **Product description**: What does the app do? (use `$ARGUMENTS` if provided)
2. **Project name**: kebab-case name for the project directory
3. **Billing model**: Present options with descriptions:
   - **Per-seat**: Charge per user/seat in an org (most B2B SaaS)
   - **Usage-based**: Charge by consumption (API calls, storage, compute)
   - **PLG (Product-Led Growth)**: Free tier with self-service upgrade
   - **B2B/Enterprise**: Annual contracts, custom pricing, invoicing
4. **Plan structure**: Plan names, pricing, and features per plan
5. **Auth features**: Which features to enable:
   - SSO (always included for enterprise readiness)
   - Directory Sync (for team/org management)
   - Admin Portal widgets (self-service SSO/DSync config)
   - RBAC roles (default: admin, member, viewer)

### Step 2: Load Configuration

Run `bash ${CLAUDE_SKILL_DIR}/scripts/load-config.sh` and capture output.

- If exit code is non-zero, show the error and instruct the user to set up config
- Parse the key-value pairs for use by agents that need them

### Step 3: Scaffold Project

Spawn the `roost:cloudflare-architect` agent:

```
Prompt: Generate the project scaffold for "{project-name}" based on these requirements:
- Product: {product description}
- Billing model: {selected model}
- Target directory: {path}
Reference: ${CLAUDE_SKILL_DIR}/references/cloudflare-stack.md
Reference: ${CLAUDE_SKILL_DIR}/references/stack-architecture.md
```

Summarize what was created for the user.

### Step 4: Wire Authentication

Spawn the `roost:workos-specialist` agent:

```
Prompt: Wire WorkOS AuthKit into the project at {path}:
- Auth features: {selected features}
- RBAC roles: {role list}
- Implement: callback route, auth middleware, RBAC middleware, DSync webhooks, widget integration
Reference: ${CLAUDE_SKILL_DIR}/references/workos-authkit.md
```

Summarize the auth flow for the user.

### Step 5: Implement Billing

Spawn the `roost:stripe-specialist` agent:

```
Prompt: Implement {billing-model} billing in the project at {path}:
- Plans: {plan structure}
- Implement: webhook handler, checkout flow, customer portal, entitlement middleware
Reference: ${CLAUDE_SKILL_DIR}/references/stripe-billing.md
```

Summarize the billing setup for the user.

### Step 6: Set Up Email

Spawn the `roost:resend-specialist` agent:

```
Prompt: Set up transactional email in the project at {path}:
- Templates needed: welcome, invite, billing notifications, password reset
- Product-specific templates: {any from requirements}
- Use queue-based sending for reliability
Reference: ${CLAUDE_SKILL_DIR}/references/resend-email.md
```

Summarize email templates for the user.

### Step 7: Generate Bootstrap Script

Spawn the `roost:bootstrap-writer` agent:

```
Prompt: Generate the bootstrap.sh provisioning script for the project at {path}.
Scan wrangler.toml for resource names, workos-seed.yaml for seed data, and billing config for Stripe setup.
Reference: ${CLAUDE_SKILL_DIR}/references/stack-architecture.md
Template: ${CLAUDE_SKILL_DIR}/scripts/bootstrap.sh
```

### Step 8: Final Summary

Present to the user:

1. **Project structure** — what was generated and where
2. **Next steps** — ordered list of manual actions:
   - Run `bun install` in the project root
   - Run `./bootstrap.sh --dry-run` to preview provisioning
   - Run `./bootstrap.sh` to create all resources
   - Configure WorkOS redirect URI in dashboard
   - Configure Stripe webhook endpoint in dashboard
   - Add Resend DNS records for domain verification
   - Set worker secrets via `wrangler secret put`
3. **Development commands** — how to run locally:
   - `cd packages/api && wrangler dev`
   - `cd packages/web && bun run dev`
   - `workos emulate` (local auth)
   - `stripe listen --forward-to localhost:8787/api/webhooks/stripe`

## /roost:inspect Workflow

### Step 1: Determine Target

Use `$ARGUMENTS` as the project path, or AskUserQuestion to get it, or default to the current directory.

### Step 2: Run Inspection

Spawn the `roost:stack-introspector` agent:

```
Prompt: Scan the project at {path} and produce a gap report.
Check for: Cloudflare bindings, WorkOS AuthKit, Stripe billing, Resend email, bootstrap script.
Reference: ${CLAUDE_SKILL_DIR}/references/stack-architecture.md
```

### Step 3: Present Report

Show the structured gap report to the user. For each gap, suggest the specific action to close it.

## /roost:upgrade Workflow

Audits an existing project against current reference docs and applies improvements. This is the primary way to bring an existing roost project up to date when the skill's reference docs or patterns evolve.

### Step 1: Inspect First

Run the full `/roost:inspect` workflow (Steps 1-3 above) to produce a gap report. This is the input to the upgrade.

### Step 2: Classify Gaps

Categorize each gap from the report:

| Category   | Examples                                                                   | Agent                        |
| ---------- | -------------------------------------------------------------------------- | ---------------------------- |
| Cloudflare | Missing bindings, outdated wrangler.toml patterns, missing typed Env       | `roost:cloudflare-architect` |
| Auth       | Missing widgets, outdated AuthKit patterns, missing RBAC middleware        | `roost:workos-specialist`    |
| Billing    | Missing webhook verification, outdated checkout flow, missing entitlements | `roost:stripe-specialist`    |
| Email      | Missing templates, no queue integration, missing idempotency keys          | `roost:resend-specialist`    |
| Bootstrap  | Missing or outdated bootstrap.sh, missing provisioning steps               | `roost:bootstrap-writer`     |

### Step 3: Present Upgrade Plan

Use AskUserQuestion to present the categorized gaps and let the user choose:

1. **Apply all** — fix everything identified
2. **Select categories** — pick which domains to upgrade (multiSelect)
3. **Review individually** — go through each gap one by one

### Step 4: Apply Upgrades

For each selected category, spawn the appropriate specialist agent with:

```
Prompt: Upgrade the {domain} integration in the project at {path}.
Current state: {relevant gaps from inspection report}
Apply current best practices from the reference docs.
Reference: ${CLAUDE_SKILL_DIR}/references/{domain-reference}.md

IMPORTANT: Do not remove or break existing functionality. Only add missing pieces
and update patterns that have improved. Show a summary of changes made.
```

Dispatch agents sequentially (same order as /roost:new) since later agents may depend on earlier changes.

### Step 5: Verify and Report

After all agents complete:

1. Run `wrangler types` if wrangler.toml was changed (regenerate typed bindings)
2. Run the project's build command if it exists to verify nothing broke
3. Present a summary of all changes made, grouped by category
4. Suggest running `/roost:retrospect` to capture learnings from the upgrade

## /roost:bootstrap Workflow

### Step 1: Locate Bootstrap Script

Check for `bootstrap.sh` in the current project directory. If missing, offer to generate one via the bootstrap-writer agent.

### Step 2: Load Config

Run `bash ${CLAUDE_SKILL_DIR}/scripts/load-config.sh` to verify credentials are available.

### Step 3: Execute

Run the project's `bootstrap.sh` with the flags from `$ARGUMENTS` (default `--all`):

```bash
bash ./bootstrap.sh {flags}
```

Report the output to the user, highlighting any manual steps needed.

## /roost:retrospect Workflow

### Step 1: Determine Target

Use `$ARGUMENTS` as the project path or default to the current directory.

### Step 2: Run Analysis

Spawn the `roost:roost-retrospective` agent:

```
Prompt: Analyze the build session for the project at {path}.
Compare what was built against the contract goals.
Capture learnings about stack integration patterns.
Learnings file: ${CLAUDE_SKILL_DIR}/docs/learnings.md
Contract: ${CLAUDE_SKILL_DIR}/docs/contract.md
```

### Step 3: Report

Summarize the retrospective findings for the user.

## References

- `${CLAUDE_SKILL_DIR}/references/cloudflare-stack.md` — Workers runtime, D1, KV, R2, Queues, DO, wrangler CLI
- `${CLAUDE_SKILL_DIR}/references/workos-authkit.md` — AuthKit, widgets, CLI, SSO/DSync, RBAC
- `${CLAUDE_SKILL_DIR}/references/stripe-billing.md` — Billing models, webhooks, entitlements, Stripe CLI
- `${CLAUDE_SKILL_DIR}/references/resend-email.md` — Resend API, React Email templates, transactional patterns
- `${CLAUDE_SKILL_DIR}/references/stack-architecture.md` — Project structure, data flow, deployment topology
