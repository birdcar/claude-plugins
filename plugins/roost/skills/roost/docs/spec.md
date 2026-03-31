# Roost — Spec

## Component Manifest

| File                                            | Purpose                                                                   |
| ----------------------------------------------- | ------------------------------------------------------------------------- |
| `plugin.json`                                   | Plugin metadata, agent/command registration                               |
| `package.json`                                  | Workspace package definition                                              |
| `tsconfig.json`                                 | TypeScript config                                                         |
| `skills/roost/SKILL.md`                         | Main orchestrator skill — domain knowledge, workflow, agent coordination  |
| `skills/roost/references/cloudflare-stack.md`   | CF Workers, Pages, D1, KV, R2, Queues, DO, AI, Containers, wrangler CLI   |
| `skills/roost/references/workos-authkit.md`     | AuthKit, widgets, CLI commands, SSO/DSync patterns, Admin Portal          |
| `skills/roost/references/stripe-billing.md`     | Billing models, webhook patterns, entitlement middleware, Stripe CLI      |
| `skills/roost/references/resend-email.md`       | Resend API, React Email templates, transactional email patterns           |
| `skills/roost/references/stack-architecture.md` | Reference architecture: project structure, data flow, deployment topology |
| `skills/roost/scripts/load-config.sh`           | Source credentials from ~/.config/roost/                                  |
| `skills/roost/scripts/bootstrap.sh`             | Standardized provisioning: CF resources, WorkOS, Stripe, Resend           |
| `commands/new.md`                               | `/roost:new` — generate a new SaaS project from product description       |
| `commands/inspect.md`                           | `/roost:inspect` — scan existing project for stack integration gaps       |
| `commands/upgrade.md`                           | `/roost:upgrade` — audit and apply improvements to existing projects      |
| `commands/bootstrap.md`                         | `/roost:bootstrap` — run standardized setup/provisioning                  |
| `commands/retrospect.md`                        | `/roost:retrospect` — analyze session and update learnings                |
| `agents/cloudflare-architect.md`                | CF Workers, Hono, D1/KV/R2/Queues/DO, wrangler, Pages config              |
| `agents/workos-specialist.md`                   | AuthKit, Admin Portal widgets, SSO/DSync, WorkOS CLI, RBAC                |
| `agents/stripe-specialist.md`                   | Per-seat/usage/PLG/B2B billing, webhooks, entitlements                    |
| `agents/resend-specialist.md`                   | Resend API, React Email templates, transactional patterns                 |
| `agents/stack-introspector.md`                  | Scan existing projects, detect wired integrations, report gaps            |
| `agents/bootstrap-writer.md`                    | Generate/maintain standardized setup and seed scripts                     |
| `agents/roost-retrospective.md`                 | Analyze sessions, update learnings                                        |
| `skills/roost/docs/contract.md`                 | Design intent (already written)                                           |
| `skills/roost/docs/spec.md`                     | This file                                                                 |
| `skills/roost/docs/learnings.md`                | Accumulated retrospective observations                                    |

## Skill Architecture

Roost uses a **domain-specific + sequential orchestration** pattern. The main SKILL.md acts as an orchestrator that understands the full stack and coordinates domain specialists. When `/roost:new` is invoked, the orchestrator gathers product requirements via AskUserQuestion, then spawns agents sequentially: cloudflare-architect first (project scaffold), then workos-specialist (auth), stripe-specialist (billing), resend-specialist (email), and finally bootstrap-writer (provisioning scripts). Each agent writes its domain's files and returns a summary.

The `/roost:inspect` command uses the stack-introspector agent to scan an existing project and produce a gap report. The `/roost:bootstrap` command runs the standardized bootstrap script with appropriate flags.

Reference docs in `references/` provide deep domain knowledge that agents load on demand. The SKILL.md stays under 500 lines by linking to these references. Scripts handle deterministic operations (config loading, provisioning) without consuming LLM tokens.

## Per-Component Details

### Main Skill (`skills/roost/SKILL.md`)

- **Purpose**: Orchestrator — understands the full stack, coordinates agents, manages workflow
- **Key behaviors**: Product requirements gathering, agent dispatch sequence, progress tracking, deployment verification
- **Sections**: Critical rules, prerequisites/config, /roost:new workflow, /roost:inspect workflow, /roost:bootstrap workflow, reference links

### Cloudflare Architect Agent (`agents/cloudflare-architect.md`)

- **Purpose**: Scaffold Hono API + React/Vite frontend, configure wrangler.toml, set up bindings
- **Key behaviors**: Project structure generation, wrangler.toml with D1/KV/R2/Queues bindings, Hono route scaffolding, Vite config for CF Pages, middleware patterns
- **Model**: sonnet
- **Tools**: Read, Write, Edit, Glob, Grep, Bash

### WorkOS Specialist Agent (`agents/workos-specialist.md`)

- **Purpose**: Wire AuthKit, Admin Portal widgets, SSO/DSync flows, RBAC patterns
- **Key behaviors**: AuthKit middleware for Hono, widget integration in React, callback routes, session management, org-level access control, WorkOS CLI usage
- **Model**: sonnet
- **Tools**: Read, Write, Edit, Glob, Grep, Bash, WebFetch

### Stripe Specialist Agent (`agents/stripe-specialist.md`)

- **Purpose**: Implement billing based on selected model with webhook handling
- **Key behaviors**: Stripe product/price creation patterns, webhook endpoint with signature verification, entitlement middleware, billing portal integration, per-seat/usage/PLG/B2B patterns
- **Model**: sonnet
- **Tools**: Read, Write, Edit, Glob, Grep, Bash, WebFetch

### Resend Specialist Agent (`agents/resend-specialist.md`)

- **Purpose**: Set up transactional email with React Email templates
- **Key behaviors**: Resend SDK integration, React Email template generation (welcome, invite, billing, password reset), email sending utility, template preview setup
- **Model**: sonnet
- **Tools**: Read, Write, Edit, Glob, Grep, Bash

### Stack Introspector Agent (`agents/stack-introspector.md`)

- **Purpose**: Scan existing projects and identify missing stack integrations
- **Key behaviors**: Detect which services are wired (AuthKit, Stripe, Resend, CF bindings), check configuration completeness, produce structured gap report
- **Model**: haiku
- **Tools**: Read, Glob, Grep

### Bootstrap Writer Agent (`agents/bootstrap-writer.md`)

- **Purpose**: Generate standardized setup/seed scripts for any roost project
- **Key behaviors**: Generate bootstrap.sh that provisions CF resources via wrangler, configures WorkOS environment, creates Stripe products/prices, verifies Resend domain, runs migrations, seeds test data
- **Model**: haiku
- **Tools**: Read, Write, Edit, Glob, Bash

### Retrospective Agent (`agents/roost-retrospective.md`)

- **Purpose**: Analyze build sessions and capture learnings
- **Key behaviors**: Compare what was planned vs built, identify patterns across sessions, update learnings.md
- **Model**: sonnet
- **Tools**: Read, Glob, Grep, Write, Edit

### Commands

- **`/roost:new`**: Entry point for new project generation. Accepts optional product description as argument. Triggers the full orchestration workflow.
- **`/roost:inspect`**: Entry point for gap analysis. Accepts optional project path. Spawns stack-introspector.
- **`/roost:upgrade`**: Audits an existing project and applies improvements. Runs inspect first, classifies gaps by domain, lets user select scope, then dispatches specialist agents to close gaps. Reuses existing agents — no new agent needed.
- **`/roost:bootstrap`**: Runs the standardized bootstrap script. Accepts flags for provisioning scope.
- **`/roost:retrospect`**: Triggers session analysis and learnings capture.

### Reference Docs

Each reference doc is 200-400 lines of deep domain knowledge loaded on demand by agents:

- **cloudflare-stack.md**: Workers runtime, Pages deployment, D1 SQL, KV store, R2 object storage, Queues, Durable Objects, AI bindings, Containers, wrangler CLI commands
- **workos-authkit.md**: AuthKit integration patterns, widget types and usage, CLI commands (install, doctor, etc.), SSO/DSync setup, Admin Portal configuration, RBAC
- **stripe-billing.md**: Per-seat, usage-based, PLG, B2B billing patterns, webhook handling, customer portal, entitlement checks, Stripe CLI
- **resend-email.md**: Resend API, React Email component patterns, template design, sending patterns, domain verification
- **stack-architecture.md**: Project directory structure convention, API/frontend split, data flow, deployment topology, environment management

### Scripts

- **load-config.sh**: Sources credentials from `~/.config/roost/credentials.env` with permission validation
- **bootstrap.sh**: Standardized provisioning — creates CF resources, configures services, runs migrations, seeds data

## Execution Plan

### Phase 1: Scaffolding (no dependencies)

- `plugin.json`
- `package.json`
- `tsconfig.json`

### Phase 2: Reference Docs (no dependencies, parallelizable)

- `skills/roost/references/cloudflare-stack.md`
- `skills/roost/references/workos-authkit.md`
- `skills/roost/references/stripe-billing.md`
- `skills/roost/references/resend-email.md`
- `skills/roost/references/stack-architecture.md`

### Phase 3: Scripts (no dependencies, parallelizable with Phase 2)

- `skills/roost/scripts/load-config.sh`
- `skills/roost/scripts/bootstrap.sh`

### Phase 4: Agents (depends on Phase 1 for plugin.json registration)

- `agents/cloudflare-architect.md`
- `agents/workos-specialist.md`
- `agents/stripe-specialist.md`
- `agents/resend-specialist.md`
- `agents/stack-introspector.md`
- `agents/bootstrap-writer.md`
- `agents/roost-retrospective.md`

### Phase 5: Commands (depends on Phase 1)

- `commands/new.md`
- `commands/inspect.md`
- `commands/bootstrap.md`
- `commands/retrospect.md`

### Phase 6: Main Skill (depends on Phases 2-5 — references all other components)

- `skills/roost/SKILL.md`

## Retrospective Configuration

- **Recommendation**: full
- **Rationale**: Multi-agent plugin with 5 external service integrations (Cloudflare, WorkOS, Stripe, Resend, wrangler). All vendors ship frequently. Patterns learned from building one SaaS app improve the next. Full retrospective captures which billing models worked, which AuthKit patterns needed adjustment, and which CF primitives were chosen for what use cases.
- **Components**:
  - `agents/roost-retrospective.md`
  - `commands/retrospect.md`
  - `skills/roost/docs/learnings.md`

## Validation Strategy

- Structural: frontmatter validity, naming conventions, line counts, progressive disclosure
- Anti-pattern scan: check against shared anti-patterns.md
- Spec compliance: every file in manifest exists, no files created outside manifest
- Domain-specific: verify reference docs cover all major primitives listed in contract
- Build verification: `bun run typecheck && bun run build && bun run format:check`
- Script validation: load-config.sh and bootstrap.sh are executable and pass shellcheck
