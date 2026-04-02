# Roost — Contract

## Problem Statement

Building a production SaaS application on the Cloudflare Workers stack requires stitching together 7+ services (Cloudflare Workers/D1/KV/R2/Queues/AI/DO, WorkOS full suite, Stripe billing, Resend email, Twilio messaging, PostHog analytics) with correct patterns for each. A developer starting from scratch spends days wiring auth flows, billing webhooks, transactional email, analytics, and deployment config — all before writing any product logic. Each service has its own CLI, SDK patterns, and gotchas that are easy to get wrong. Additionally, local development setup is often an afterthought, leading to poor DX.

## Goals

1. Generate a fully-wired, deployable SaaS application from a product description in a single session
2. Every generated app follows the same project structure and development script convention so operational knowledge transfers across projects
3. Enterprise-ready by default: SSO, Directory Sync, FGA, Audit Logs, Feature Flags, Admin Portal widgets, and RBAC are wired from the start
4. Billing patterns (per-seat, usage-based, PLG, B2B) are correctly implemented with Stripe webhooks, entitlement checks, and graceful degradation
5. Transactional email uses React Email templates via Resend with queue-based sending
6. Product analytics from day one with PostHog: event tracking, user identification, group analytics
7. Local development works with one command (`script/dev`) after initial setup (`script/setup` + `script/bootstrap`)
8. All database access uses Drizzle ORM — no raw SQL in application code
9. React Router 7 in framework mode with SSR for SEO and AI SEO readiness

## Success Criteria

- [ ] `/roost:new` generates a working React Router 7 SSR project deployable to Cloudflare Workers
- [ ] AuthKit integration via `workos install` with enhanced JWT verification and auto-provisioning
- [ ] Full WorkOS suite available: FGA, Audit Logs, Feature Flags, Vault, DSync via Events API
- [ ] Billing integration matches the selected model with Stripe webhooks and Drizzle-based entitlements
- [ ] Transactional email via Resend + React Email with queue-based sending
- [ ] PostHog analytics wired with client and server-side tracking
- [ ] `script/setup` interactively creates .dev.vars from template
- [ ] `script/bootstrap` provisions all resources and runs migrations
- [ ] `script/dev` starts local dev server with all sidecar services
- [ ] `script/seed` seeds test data across all services
- [ ] `/roost:inspect` scans a project and reports gaps against full stack
- [ ] All database access uses Drizzle ORM with proper schema definitions
- [ ] All service integrations gracefully degrade when API keys are not configured

## Scope Boundaries

### In Scope

- Greenfield SaaS project generation from product description
- React Router 7 (framework mode, SSR) on Cloudflare Workers
- Drizzle ORM on D1 for all database access
- Cloudflare primitives: D1, KV, R2, Queues, Workers AI, Vectorize, Durable Objects, Containers
- Full WorkOS suite: AuthKit, widgets, FGA, Audit Logs, Feature Flags, Vault, DSync (Events API), MCP Auth, Pipes
- Stripe billing with webhook handling and entitlement middleware
- Resend transactional email with React Email templates and inbound email
- Twilio SMS, verification, WhatsApp messaging
- PostHog product analytics with client and server-side tracking
- script/ convention for local development (setup, bootstrap, dev, seed, teardown)
- Docker Compose for sidecar services (Cloudflare Containers in production)
- bun:test for testing
- Project introspection for gap analysis
- Upgrading existing projects to latest patterns

### Out of Scope

- Non-Cloudflare deployment targets
- Non-React frontends (Radix and WorkOS widgets are React-specific)
- Custom domain setup / DNS management
- CI/CD pipeline generation

## Design Decisions

| Decision             | Choice                               | Rationale                                                             |
| -------------------- | ------------------------------------ | --------------------------------------------------------------------- |
| Full-stack framework | React Router 7 (SSR)                 | SEO/AI SEO readiness, single Worker deploy, unified routing           |
| API-only framework   | Hono (when no UI needed)             | Lighter weight for pure API services                                  |
| Database access      | Drizzle ORM on D1                    | Type-safe queries, generated migrations, no raw SQL                   |
| Auth approach        | WorkOS full suite + `workos install` | CLI saves tokens, enterprise-ready, expanding beyond AuthKit          |
| DSync method         | Events API (not webhooks)            | WorkOS recommendation, no spiky traffic, simpler cursor-based polling |
| Deployment           | Single Worker (not monorepo)         | Simpler than Pages+Workers split, lessons from overtone migration     |
| Analytics            | PostHog from day one                 | Product understanding compounds, free tier generous                   |
| Local dev            | script/ convention                   | Consistent DX across all Roost projects                               |
| Agent architecture   | 9 domain specialists                 | Each service domain warrants dedicated context                        |
| Config management    | .dev.vars + wrangler secret put      | Standard Cloudflare patterns, no custom config files                  |
