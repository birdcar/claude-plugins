# Roost — Spec

## Component Manifest

| File                                            | Purpose                                                                                                            |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `plugin.json`                                   | Plugin metadata, agent/command registration                                                                        |
| `package.json`                                  | Workspace package definition                                                                                       |
| `tsconfig.json`                                 | TypeScript config                                                                                                  |
| `skills/roost/SKILL.md`                         | Main orchestrator skill — domain knowledge, workflow, agent coordination                                           |
| `skills/roost/references/cloudflare-stack.md`   | CF Workers, RR7, D1/Drizzle, KV, R2, Queues, DO, AI, Vectorize, Containers, wrangler CLI                           |
| `skills/roost/references/workos.md`             | Full WorkOS suite: AuthKit, widgets, CLI, FGA, Audit Logs, Feature Flags, Vault, DSync Events API, MCP Auth, Pipes |
| `skills/roost/references/stripe-billing.md`     | Billing models, webhook patterns, entitlement middleware, Stripe CLI, Drizzle                                      |
| `skills/roost/references/resend-email.md`       | Resend API, React Email templates, inbound email, queue patterns                                                   |
| `skills/roost/references/twilio.md`             | SMS, voice, WhatsApp, Verify, REST API patterns for Workers                                                        |
| `skills/roost/references/posthog.md`            | Product analytics, event tracking, feature flags, server-side capture                                              |
| `skills/roost/references/stack-architecture.md` | Reference architecture: project structure, data flow, local dev, deployment                                        |
| `commands/new.md`                               | `/roost:new` — generate a new SaaS project from product description                                                |
| `commands/inspect.md`                           | `/roost:inspect` — scan existing project for stack integration gaps                                                |
| `commands/upgrade.md`                           | `/roost:upgrade` — audit and apply improvements to existing projects                                               |
| `commands/bootstrap.md`                         | `/roost:bootstrap` — run standardized setup/provisioning                                                           |
| `commands/retrospect.md`                        | `/roost:retrospect` — analyze session and update learnings                                                         |
| `agents/cloudflare-architect.md`                | RR7 scaffold, Drizzle, wrangler, Vite, bindings, script/ directory                                                 |
| `agents/workos-specialist.md`                   | Full WorkOS suite post-workos-install: widgets, FGA, Audit Logs, DSync Events API                                  |
| `agents/stripe-specialist.md`                   | Per-seat/usage/PLG/B2B billing, RR7 actions, Drizzle, webhooks                                                     |
| `agents/resend-specialist.md`                   | Resend API, React Email templates, queue sending, inbound email                                                    |
| `agents/twilio-specialist.md`                   | SMS, Verify, WhatsApp via REST API (not Node SDK)                                                                  |
| `agents/posthog-specialist.md`                  | Client + server analytics, feature flags, group analytics                                                          |
| `agents/stack-introspector.md`                  | Scan existing projects, detect wired integrations, report gaps                                                     |
| `agents/bootstrap-writer.md`                    | Generate script/ directory with setup, bootstrap, dev, seed, teardown                                              |
| `agents/roost-retrospective.md`                 | Analyze sessions, update learnings                                                                                 |
| `skills/roost/docs/contract.md`                 | Design intent                                                                                                      |
| `skills/roost/docs/spec.md`                     | This file                                                                                                          |
| `skills/roost/docs/learnings.md`                | Accumulated retrospective observations                                                                             |

## Skill Architecture

Roost uses a **domain-specific + sequential orchestration** pattern. The main SKILL.md acts as an orchestrator that coordinates domain specialists. When `/roost:new` is invoked, the orchestrator:

1. Gathers product requirements via AskUserQuestion
2. Spawns cloudflare-architect (RR7 scaffold + Drizzle + bindings)
3. Runs `workos install` (CLI-based AuthKit integration using WorkOS billing)
4. Spawns workos-specialist (enhance auth, add FGA/Audit Logs/DSync/widgets)
5. Spawns stripe-specialist (billing model implementation)
6. Spawns resend-specialist (email templates + queue sending)
7. Spawns twilio-specialist (SMS/messaging if requested)
8. Spawns posthog-specialist (analytics — always included)
9. Spawns bootstrap-writer (script/ directory for local dev)

Reference docs in `references/` provide deep domain knowledge loaded on demand. The SKILL.md stays focused on orchestration by linking to these references.

## Per-Component Details

### Main Skill (`skills/roost/SKILL.md`)

- **Purpose**: Orchestrator — coordinates agents, manages workflow
- **Key behaviors**: Requirements gathering, agent dispatch, progress tracking
- **Sections**: Critical rules, /roost:new workflow (10 steps), /roost:inspect, /roost:upgrade, /roost:bootstrap, /roost:retrospect, references

### Agents

| Agent                | Model  | Purpose                                      |
| -------------------- | ------ | -------------------------------------------- |
| cloudflare-architect | sonnet | RR7 scaffold, Drizzle, bindings, script/     |
| workos-specialist    | sonnet | Full WorkOS suite, post-install enhancements |
| stripe-specialist    | sonnet | Billing models, webhooks, entitlements       |
| resend-specialist    | sonnet | Email templates, queue sending               |
| twilio-specialist    | sonnet | SMS/messaging via REST API                   |
| posthog-specialist   | sonnet | Product analytics, client + server           |
| stack-introspector   | haiku  | Read-only gap analysis                       |
| bootstrap-writer     | sonnet | script/ directory generation                 |
| roost-retrospective  | sonnet | Session analysis, learnings capture          |

### Commands

- **`/roost:new`**: Full orchestration workflow for new projects
- **`/roost:inspect`**: Gap analysis via stack-introspector
- **`/roost:upgrade`**: Inspect + classify + apply improvements
- **`/roost:bootstrap`**: Run project's script/bootstrap
- **`/roost:retrospect`**: Session analysis and learnings

### Reference Docs

7 reference docs providing deep domain knowledge:

- **cloudflare-stack.md**: Workers, RR7, D1+Drizzle, KV, R2, Queues, DO, AI, Vectorize, Containers, wrangler
- **workos.md**: Full product suite with CLI, Events API, FGA, widgets
- **stripe-billing.md**: All billing models, RR7 patterns, Drizzle
- **resend-email.md**: Email API, React Email, inbound, queues
- **twilio.md**: REST API patterns for Workers (not Node SDK)
- **posthog.md**: Client + server analytics, feature flags
- **stack-architecture.md**: Project structure, data flow, local dev, deploy

## Retrospective Configuration

- **Recommendation**: full
- **Rationale**: Multi-agent plugin with 7 external service integrations. All vendors ship frequently. Patterns learned from building one SaaS app improve the next.
- **Components**:
  - `agents/roost-retrospective.md`
  - `commands/retrospect.md`
  - `skills/roost/docs/learnings.md`

## Validation Strategy

- Structural: frontmatter validity, naming conventions, line counts
- Anti-pattern scan: check against shared anti-patterns
- Spec compliance: every file in manifest exists
- Domain-specific: verify reference docs cover all major primitives
- Build verification: `bun run typecheck && bun run build && bun run format:check`
