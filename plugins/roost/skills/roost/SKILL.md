---
name: roost
description: >-
  Generates full-stack SaaS applications on Cloudflare Workers with React Router 7,
  Drizzle ORM, WorkOS (full suite), Stripe billing, Resend email, Twilio messaging,
  and PostHog analytics from a product description. Orchestrates domain specialists
  to scaffold, wire auth, implement billing, set up email, messaging, and analytics.
  Use when the user asks to "build a SaaS app", "create a new SaaS project",
  "generate a full-stack app on Cloudflare", "set up auth and billing",
  "upgrade my project to latest patterns", or start a greenfield SaaS application.
  Do NOT use for frontend-only projects, non-Cloudflare deployments, or
  general code review unrelated to stack integrations.
---

# Roost

Full-stack SaaS builder for the Cloudflare Workers + React Router 7 + WorkOS + Stripe + Resend + Twilio + PostHog stack. Generates production-ready applications with auth, billing, email, messaging, analytics, and deployment from a product description.

## Critical Rules

- Use AskUserQuestion for all decisions that need user input — product description, billing model, feature choices. Plain text questions cannot capture structured responses.
- Never hardcode API keys, tokens, or credentials in generated code. All secrets go through `wrangler secret put` and are accessed via `env.SECRET_NAME` bindings.
- Always verify webhook signatures (Stripe and Resend) before processing events — unverified webhooks are a security vulnerability.
- Use the WorkOS Events API for Directory Sync, NOT webhooks — WorkOS recommends this to avoid spiky traffic.
- Send email via Cloudflare Queues, not synchronously — queue-based sending provides retry and prevents request timeouts.
- Use idempotency keys for all transactional email and SMS to prevent duplicates on retry.
- Use Drizzle ORM for all database access — never raw SQL in application code.
- Use React Router 7 in framework mode for all full-stack projects — Hono only for API-only services.
- Run `workos install` early in the workflow — it uses WorkOS's AI agent and billing, saving tokens.
- Agents are dispatched sequentially: cloudflare-architect -> workos install -> workos-specialist -> stripe-specialist -> resend-specialist -> twilio-specialist -> posthog-specialist -> bootstrap-writer. Each depends on previous output.
- Summarize agent results for the user after each agent completes — the user cannot see raw agent output.
- Generated projects must follow the directory structure defined in `${CLAUDE_SKILL_DIR}/references/stack-architecture.md`.
- All service integrations must gracefully degrade (return 503) when their API keys are not configured.

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
5. **WorkOS feature analysis**: After gathering items 1–4, analyze the product description and billing model to recommend which WorkOS features the product needs. Use the decision matrix below, then present recommendations via AskUserQuestion for the user to confirm or adjust.

#### WorkOS Feature Decision Matrix

Analyze the product against these signals. A feature is **recommended** if 2+ signals match, **suggested** if 1 signal matches, and **not recommended** if none match.

| Feature                              | Signals That Indicate Need                                                                                                                                                        |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Directory Sync** (Events API)      | Multi-tenant / team-based, B2B billing model, enterprise customers, org management features, user provisioning from IdP                                                           |
| **FGA** (fine-grained authorization) | Resource-level permissions (documents, projects, files), sharing/collaboration features, permission hierarchies beyond admin/member/viewer, multi-team access to shared resources |
| **Audit Logs**                       | Enterprise/compliance requirements, B2B billing model, sensitive data handling (finance, healthcare, legal), admin actions that need accountability                               |
| **Feature Flags**                    | Multiple plan tiers with different feature sets, PLG billing model, gradual rollout needs, entitlement-gated features                                                             |
| **Vault**                            | Stores customer secrets (API keys, tokens, credentials), integration platform, customer-provided configuration secrets                                                            |

**Always included** (do not ask):

- AuthKit (authentication baseline)
- SSO + Admin Portal widgets (enterprise readiness)
- RBAC with default roles: admin, member, viewer

#### Presenting Recommendations

Use AskUserQuestion to present a structured recommendation like:

```
Based on your product description ("{summary}") and {billing model} billing:

**Recommended** (strong fit for your product):
- [Feature]: [1-sentence reason tied to their product]

**Worth considering** (moderate fit):
- [Feature]: [1-sentence reason tied to their product]

**Not needed now** (no clear signal):
- [Feature]: [brief note on when they might need it later]

**Always included**: AuthKit, SSO, Admin Portal widgets, RBAC

Would you like to adjust these selections?
```

The user can accept the recommendations as-is, add features, or remove recommended ones. Respect their decision — the analysis is advisory, not prescriptive.

6. **Cloudflare primitives**: Which are needed beyond defaults (D1, KV, R2, Queues):
   - Workers AI (for AI features)
   - Vectorize (for semantic search)
   - Durable Objects (for real-time/WebSocket features)
   - Containers (for sidecar services)
7. **Additional services**:
   - Twilio: SMS notifications, verification codes, WhatsApp
   - PostHog: Always included by default for product analytics

### Step 2: Scaffold Project

Spawn the `roost:cloudflare-architect` agent:

```
Prompt: Generate the project scaffold for "{project-name}" based on these requirements:
- Product: {product description}
- Billing model: {selected model}
- Target directory: {path}
- CF primitives: {selected primitives}
- Additional services: {Twilio yes/no}
Reference: ${CLAUDE_SKILL_DIR}/references/cloudflare-stack.md
Reference: ${CLAUDE_SKILL_DIR}/references/stack-architecture.md
```

Summarize what was created for the user.

### Step 3: Run `workos install`

Run `workos install` in the project directory. This uses WorkOS's AI agent to scaffold AuthKit integration automatically, using their billing — not your tokens.

```bash
cd {project-path} && workos install
```

If `workos install` fails or the CLI is not installed, fall back to manual AuthKit scaffolding via the workos-specialist agent.

### Step 4: Enhance WorkOS Integration

Spawn the `roost:workos-specialist` agent:

```
Prompt: Enhance the WorkOS integration in the project at {path}.
workos install has already configured basic AuthKit. Now add:
- JWT verification enhancement (jose + JWKS)
- Auto-provision users in D1 via Drizzle
- RBAC middleware with roles: {role list}
- Directory Sync via Events API (cron polling)
- WorkOS widgets: {selected widgets}
- Additional products: {FGA, Audit Logs, Feature Flags, Vault as confirmed by user}

Product context (use this to inform implementation depth and patterns):
- Product: {product description summary}
- Billing model: {billing model}
- Why these features were selected: {brief rationale from the recommendation step}

Reference: ${CLAUDE_SKILL_DIR}/references/workos.md
```

Summarize the auth and WorkOS setup for the user.

### Step 5: Implement Billing

Spawn the `roost:stripe-specialist` agent:

```
Prompt: Implement {billing-model} billing in the project at {path}:
- Plans: {plan structure}
- Implement: webhook handler (RR7 action), checkout flow, customer portal, entitlement middleware
- Use Drizzle ORM for all database access
- Graceful 503 when Stripe not configured
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
- RR7 action for inbound webhooks if needed
Reference: ${CLAUDE_SKILL_DIR}/references/resend-email.md
```

Summarize email templates for the user.

### Step 7: Set Up Messaging (if Twilio requested)

Spawn the `roost:twilio-specialist` agent:

```
Prompt: Set up Twilio messaging in the project at {path}:
- Features: {SMS, verification, WhatsApp as selected}
- Use REST API (not Node SDK) for Workers compatibility
- Queue-based sending for reliability
Reference: ${CLAUDE_SKILL_DIR}/references/twilio.md
```

Summarize messaging setup for the user.

### Step 8: Set Up Analytics

Spawn the `roost:posthog-specialist` agent:

```
Prompt: Set up PostHog analytics in the project at {path}:
- Client-side: PostHogProvider, page view tracking, user identification
- Server-side: capture utility for webhook/cron events
- Key events: user_signed_up, billing_upgrade_clicked, feature_used
- Group analytics for organizations
Reference: ${CLAUDE_SKILL_DIR}/references/posthog.md
```

Summarize analytics setup for the user.

### Step 9: Generate Development Scripts

Spawn the `roost:bootstrap-writer` agent:

```
Prompt: Generate the script/ directory for the project at {path}.
Scan wrangler.toml for resource names, workos-seed.yaml for seed data, and service config.
Create: script/setup, script/bootstrap, script/dev, script/seed, script/teardown
Reference: ${CLAUDE_SKILL_DIR}/references/stack-architecture.md
```

### Step 10: Final Summary

Present to the user:

1. **Project structure** — what was generated and where
2. **Next steps** — ordered list:
   - Run `script/setup` to configure .dev.vars
   - Run `script/bootstrap` to install deps and provision resources
   - Run `workos env claim` to link WorkOS environment
   - Run `script/dev` to start local development
   - Configure Stripe webhook endpoint in dashboard
   - Add Resend DNS records for domain verification
   - Set worker secrets for production: `wrangler secret put`
3. **Development commands**:
   - `script/dev` or `bun dev` — start dev server
   - `script/seed` — seed test data
   - `bun run test` — run tests
   - `bun run typecheck` — type check
   - `wrangler deploy` — deploy to production

## /roost:inspect Workflow

### Step 1: Determine Target

Use `$ARGUMENTS` as the project path, or AskUserQuestion to get it, or default to the current directory.

### Step 2: Run Inspection

Spawn the `roost:stack-introspector` agent:

```
Prompt: Scan the project at {path} and produce a gap report.
Check for: React Router 7, Drizzle ORM, Cloudflare bindings, WorkOS (full suite), Stripe billing, Resend email, Twilio, PostHog, script/ directory, local dev setup.
Reference: ${CLAUDE_SKILL_DIR}/references/stack-architecture.md
```

### Step 3: Present Report

Show the structured gap report to the user. For each gap, suggest the specific action to close it.

## /roost:upgrade Workflow

Audits an existing project against current reference docs and applies improvements.

### Step 1: Inspect First

Run the full `/roost:inspect` workflow to produce a gap report.

### Step 2: Classify Gaps

Categorize each gap:

| Category    | Examples                                               | Agent                        |
| ----------- | ------------------------------------------------------ | ---------------------------- |
| Cloudflare  | Missing bindings, needs RR7 migration, missing Drizzle | `roost:cloudflare-architect` |
| Auth/WorkOS | Missing widgets, needs Events API DSync, missing FGA   | `roost:workos-specialist`    |
| Billing     | Missing webhook verification, outdated patterns        | `roost:stripe-specialist`    |
| Email       | Missing templates, no queue integration                | `roost:resend-specialist`    |
| Messaging   | Missing Twilio integration                             | `roost:twilio-specialist`    |
| Analytics   | Missing PostHog setup                                  | `roost:posthog-specialist`   |
| Dev Scripts | Missing script/ directory, outdated bootstrap          | `roost:bootstrap-writer`     |

### Step 3: Present Upgrade Plan

Use AskUserQuestion to present gaps and let the user choose:

1. **Apply all** — fix everything
2. **Select categories** — pick which domains
3. **Review individually** — go through each gap

### Step 4: Apply Upgrades

For each selected category, spawn the appropriate agent. Dispatch sequentially.

### Step 5: Verify and Report

After all agents complete:

1. Run `wrangler types` if wrangler.toml was changed
2. Run the project's build command to verify nothing broke
3. Present summary of changes
4. Suggest running `/roost:retrospect`

## /roost:bootstrap Workflow

### Step 1: Check script/ Directory

Check for `script/bootstrap` in the project. If missing, offer to generate via bootstrap-writer.

### Step 2: Execute

```bash
script/bootstrap
```

Report the output, highlighting any manual steps needed.

## /roost:retrospect Workflow

### Step 1: Determine Target

Use `$ARGUMENTS` or default to current directory.

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

- `${CLAUDE_SKILL_DIR}/references/cloudflare-stack.md` — Workers runtime, RR7, D1/Drizzle, KV, R2, Queues, DO, AI, Vectorize, Containers, wrangler CLI
- `${CLAUDE_SKILL_DIR}/references/workos.md` — Full WorkOS suite: AuthKit, widgets, CLI, FGA, Audit Logs, Feature Flags, Vault, DSync Events API, MCP Auth, Pipes
- `${CLAUDE_SKILL_DIR}/references/stripe-billing.md` — Billing models, webhooks, entitlements, Stripe CLI, Drizzle patterns
- `${CLAUDE_SKILL_DIR}/references/resend-email.md` — Resend API, React Email templates, inbound email, queue patterns
- `${CLAUDE_SKILL_DIR}/references/twilio.md` — SMS, voice, WhatsApp, Verify, REST API patterns for Workers
- `${CLAUDE_SKILL_DIR}/references/posthog.md` — Product analytics, event tracking, feature flags, server-side capture
- `${CLAUDE_SKILL_DIR}/references/stack-architecture.md` — Project structure, data flow, local dev, deployment topology
