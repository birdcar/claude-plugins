# Roost — Contract

## Problem Statement

Building a production SaaS application on the Cloudflare Workers stack requires stitching together 5+ services (Cloudflare Workers/Pages/D1/KV/R2/Queues, WorkOS AuthKit, Stripe billing, Resend email) with correct patterns for each. A developer starting from scratch spends days wiring auth flows, billing webhooks, transactional email, and deployment config — all before writing any product logic. Each service has its own CLI, SDK patterns, and gotchas that are easy to get wrong.

## Goals

1. Generate a fully-wired, deployable SaaS application from a product description in a single session
2. Every generated app follows the same project structure and bootstrap convention so operational knowledge transfers across projects
3. Enterprise-ready by default: SSO, Directory Sync, Admin Portal widgets, and RBAC patterns are wired from the start for any org/team use case
4. Billing patterns (per-seat, usage-based, PLG, B2B) are correctly implemented with Stripe webhooks and entitlement checks
5. Transactional email uses React Email templates via Resend with consistent, branded design

## Success Criteria

- [ ] `/roost:new` generates a working Hono API + React/Vite frontend project deployable to Cloudflare Workers + Pages
- [ ] Generated project includes WorkOS AuthKit with SSO and DSync flows via Admin Portal widgets
- [ ] Billing integration matches the selected model (per-seat, usage, PLG, B2B) with Stripe webhooks
- [ ] Transactional email templates render correctly via Resend + React Email
- [ ] `roost bootstrap` provisions all external resources (CF D1/KV/R2, WorkOS env, Stripe products, Resend domain)
- [ ] `/roost:inspect` scans an existing project and identifies missing stack integrations
- [ ] All generated projects share the same bootstrap script interface regardless of product specifics

## Scope Boundaries

### In Scope

- Greenfield SaaS project generation from product description
- Hono API on Cloudflare Workers with D1, KV, R2, Queues, Durable Objects as needed
- React + Vite frontend on Cloudflare Pages with Radix components and framer-motion
- WorkOS AuthKit integration with widgets (SSO, DSync, Admin Portal)
- Stripe billing with webhook handling and entitlement middleware
- Resend transactional email with React Email templates
- Standardized bootstrap/provisioning script
- Project introspection for gap analysis
- Upgrading existing projects: audit against current best practices and apply improvements
- Local config management for API credentials
- Wrangler CLI integration for deployment

### Out of Scope

- Non-Cloudflare deployment targets — this is a Cloudflare-native stack
- Non-React frontends — Radix and framer-motion are React-specific
- Custom domain setup / DNS management — handled separately
- CI/CD pipeline generation — deployment is via wrangler, CI is project-specific

### Future Considerations

- Cloudflare AI and Vectorize integration for AI-powered features
- Cloudflare Containers for workloads that need full runtime
- Template marketplace for common SaaS patterns (CRM, project management, etc.)

## Design Decisions

| Decision                 | Choice                           | Rationale                                                                                       |
| ------------------------ | -------------------------------- | ----------------------------------------------------------------------------------------------- |
| Frontend framework       | React + Vite                     | Radix and framer-motion are React-native; Vite is the standard CF Pages build tool              |
| Deployment split         | Pages (frontend) + Workers (API) | Follows Cloudflare reference architecture for full-stack apps; better caching, separate scaling |
| Auth approach            | WorkOS AuthKit + widgets         | Enterprise-ready SSO/DSync out of the box; widgets reduce implementation effort                 |
| Greenfield only for /new | Yes                              | Keeps command focused; /inspect handles existing projects                                       |
| Bootstrap scope          | Full provisioning                | Creates CF resources, configures WorkOS, sets up Stripe products, Resend domain                 |
| Agent architecture       | 6 domain specialists             | Each service domain is complex enough to warrant dedicated context and expertise                |
| Config management        | XDG_CONFIG_HOME pattern          | Credentials never enter repo or LLM context; standardized across all roost projects             |
