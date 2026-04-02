# Stack Architecture Reference

Reference architecture for Roost-generated SaaS projects: directory structure, framework decisions, data flow, deployment topology, local development, and environment management.

## Framework Decision: React Router 7 vs Hono

Roost defaults to **React Router 7 in framework mode on Cloudflare Workers** for all new projects. This provides SSR, SEO, API routes, and a unified deployment — no monorepo split needed.

| Scenario                         | Framework                              | Rationale                                                 |
| -------------------------------- | -------------------------------------- | --------------------------------------------------------- |
| Full-stack SaaS with UI          | React Router 7                         | SSR for SEO/AI SEO, unified routing, single deploy        |
| API-only service (no UI)         | Hono                                   | Lighter weight, pure API, no SSR overhead                 |
| Existing Hono API + new frontend | React Router 7 (new) + Hono (existing) | Migrate incrementally, RR7 calls Hono via service binding |

React Router 7 replaces the previous Hono + Vite/Pages split because:

- Hono SPAs are invisible to search engines and AI crawlers (no SSR)
- Two deploy targets (Workers + Pages) adds operational complexity
- React Router 7 handles both SSR pages and API resource routes in one Worker

## Project Directory Structure

Every Roost project follows this flat structure (not a monorepo):

```
{project-name}/
  package.json                    # Dependencies and scripts
  bun.lock
  .gitignore
  .dev.vars.example               # Template for local secrets
  wrangler.toml                   # Cloudflare Worker config with all bindings
  react-router.config.ts          # RR7 config (ssr: true)
  vite.config.ts                  # Vite + @cloudflare/vite-plugin + @react-router/dev
  tsconfig.json                   # Strict, ES2022, paths: { "~/*": ["./*"] }
  drizzle.config.ts               # Drizzle Kit config for D1 migrations
  workos-seed.yaml                # WorkOS seed data (roles, orgs, users)
  docker-compose.yml              # Sidecar services (RSSHub, etc.) if needed

  script/
    setup                         # Interactive first-time setup (keys → .dev.vars)
    bootstrap                     # Install deps, provision dev resources, run migrations
    dev                           # Start local dev server (wrangler dev via Vite)
    seed                          # Seed local/dev databases and services
    teardown                      # Clean up dev resources

  workers/
    app.ts                        # Worker entry: fetch, scheduled, queue handlers

  app/                            # React Router 7 routes and app-level code
    root.tsx                      # Root layout with providers
    routes/
      _index.tsx                  # Landing/home page (SSR, public)
      _app.tsx                    # Authenticated layout wrapper
      _app.dashboard.tsx          # Dashboard (protected)
      _app.settings.tsx           # Settings layout
      _app.settings.billing.tsx   # Billing management
      _app.settings.profile.tsx   # User profile (WorkOS widget)
      _app.settings.org.tsx       # Org settings (WorkOS widgets)
      login.tsx                   # Login page → WorkOS AuthKit
      api.v1.[resource].tsx       # API resource routes (loader/action)
      api.v1.webhooks.stripe.tsx  # Stripe webhook handler
      api.v1.webhooks.workos.tsx  # WorkOS webhook handler (deprecated — use Events API)
      api.v1.webhooks.resend.tsx  # Resend inbound webhook handler
      [domain]/                   # Product-specific routes

  src/
    core/                         # Framework-agnostic domain logic
      db/
        schema.ts                 # Drizzle schema definitions (all tables)
        migrations/               # Drizzle Kit generated SQL migrations
        db.ts                     # Database factory (getDb wrapping D1 + Drizzle)
      lib/
        stripe.ts                 # Stripe API helpers
        email.ts                  # Resend email sending utility
        id.ts                     # ID generation (crypto.randomUUID)
        org-sync.ts               # WorkOS Events API polling for DSync
      middleware/
        jwt.ts                    # JWT verification against WorkOS JWKS
        tier.ts                   # Subscription tier gating
      types.ts                    # Env bindings interface + shared domain types
      durable-objects/            # Durable Object classes (if needed)
      agents/                     # Workers AI agent logic (if needed)

    pages/                        # React page components
    components/                   # React UI components
      ui/                         # Shared Radix-based components
      layout/                     # Header, sidebar, footer
      auth/                       # Auth guard, org switcher
      billing/                    # Plan selector, usage display
    hooks/                        # React hooks
    lib/                          # Client-side utilities
      api.ts                      # API client (typed fetch wrapper)
    styles/
      globals.css                 # Radix, WorkOS widget CSS imports

  public/                         # Static assets
  content/                        # Blog/marketing markdown (if needed)
```

### Import Convention

Use `~/` path alias mapping to project root:

```typescript
import { getDb } from '~/src/core/db/db';
import { users } from '~/src/core/db/schema';
import type { Env } from '~/src/core/types';
```

## Worker Entry Point

The Worker entry lives at `workers/app.ts` and exports the standard `ExportedHandler`:

```typescript
import { createRequestHandler } from 'react-router';

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    // WebSocket upgrade, cache logic, etc. before RR7
    const requestHandler = createRequestHandler(
      // @ts-expect-error virtual module
      () => import('virtual:react-router/server-build'),
      import.meta.env.MODE
    );
    return requestHandler(request, { env, ctx });
  },

  async scheduled(controller: ScheduledController, env: Env, ctx: ExecutionContext) {
    // Cron jobs: feed polling, org sync, cleanup
  },

  async queue(batch: MessageBatch, env: Env, ctx: ExecutionContext) {
    // Queue consumer: email sending, background jobs
  },
} satisfies ExportedHandler<Env>;
```

## Database: Drizzle ORM on D1

All database access uses Drizzle ORM. Never write raw SQL except in generated migration files.

### Schema Definition

```typescript
// src/core/db/schema.ts
import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';

export const users = sqliteTable('users', {
  id: text('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name'),
  workosUserId: text('workos_user_id').unique(),
  stripeCustomerId: text('stripe_customer_id').unique(),
  tier: text('tier').default('free'),
  createdAt: text('created_at').default(sql`(datetime('now'))`),
  updatedAt: text('updated_at').default(sql`(datetime('now'))`),
});

export const organizations = sqliteTable('organizations', {
  id: text('id').primaryKey(),
  name: text('name').notNull(),
  workosOrgId: text('workos_org_id').unique(),
  stripeCustomerId: text('stripe_customer_id').unique(),
  stripeSubscriptionId: text('stripe_subscription_id'),
  stripeSubscriptionStatus: text('stripe_subscription_status').default('none'),
  plan: text('plan').default('free'),
  createdAt: text('created_at').default(sql`(datetime('now'))`),
  updatedAt: text('updated_at').default(sql`(datetime('now'))`),
});

export const orgMembers = sqliteTable('org_members', {
  id: text('id').primaryKey(),
  userId: text('user_id')
    .notNull()
    .references(() => users.id),
  orgId: text('org_id')
    .notNull()
    .references(() => organizations.id),
  role: text('role').default('member'),
  createdAt: text('created_at').default(sql`(datetime('now'))`),
});

export const billingEvents = sqliteTable('billing_events', {
  id: text('id').primaryKey(),
  orgId: text('org_id').references(() => organizations.id),
  stripeEventId: text('stripe_event_id').unique(),
  eventType: text('event_type').notNull(),
  data: text('data'), // JSON
  createdAt: text('created_at').default(sql`(datetime('now'))`),
});
```

### Database Factory

```typescript
// src/core/db/db.ts
import { drizzle } from 'drizzle-orm/d1';
import * as schema from './schema';

export function getDb(d1: D1Database) {
  return drizzle(d1, { schema });
}
```

### Migration Workflow

```bash
# Edit schema.ts, then generate migration
bunx drizzle-kit generate

# Apply locally
bun run db:migrate  # wraps: wrangler d1 migrations apply <DB_NAME> --local

# Apply to production
wrangler d1 migrations apply <DB_NAME> --remote
```

### Drizzle Config

```typescript
// drizzle.config.ts
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  schema: './src/core/db/schema.ts',
  out: './src/core/db/migrations',
  dialect: 'sqlite',
});
```

## Data Flow

### Authentication Flow

```
Browser → AuthKit Hosted UI → WorkOS → /api/v1/auth/callback (RR7 loader) → D1 (user upsert) → JWT session
```

1. User clicks login → redirect to AuthKit
2. AuthKit handles auth method (password, SSO, social)
3. AuthKit redirects to callback route
4. RR7 loader exchanges code for user profile via `@workos-inc/node`
5. Upsert user in D1 via Drizzle
6. Return sealed session (WorkOS manages session, verified via JWT)

### API Request Flow

```
Browser → Worker fetch → RR7 loader/action → JWT verify → tier check → Drizzle query → Response
```

1. Frontend sends request with Bearer JWT
2. `requireAuth()` in loader/action verifies JWT against WorkOS JWKS
3. Tier middleware checks subscription status
4. Route handler processes business logic via Drizzle
5. Response returned (JSON for API routes, SSR HTML for pages)

### Billing Flow

```
Frontend → /api/v1/billing (action) → Stripe Checkout → Stripe Webhook → /api/v1/webhooks/stripe (action) → D1 update
```

### Email Flow

```
Route Handler → Queue (email job) → Queue Consumer → Resend API → User Inbox
```

### Directory Sync Flow (Events API — preferred over webhooks)

```
Identity Provider → WorkOS → Events API ← Cron poll (every 15min) → D1 update
```

WorkOS recommends the Events API over webhooks for DSync because:

- No spiky webhook traffic to handle
- Cursor-based polling is simpler to implement
- No webhook signature verification needed
- Automatic retry via cursor (re-read from last position)

## Deployment Topology

### Single Cloudflare Worker

```
┌──────────────────────────────────────────────────┐
│  Cloudflare Worker (React Router 7 SSR)          │
│                                                  │
│  ┌──────────┐  ┌────────┐  ┌──────────────────┐ │
│  │  SSR     │  │  API   │  │  Scheduled/Queue │ │
│  │  Routes  │  │  Routes│  │  Handlers        │ │
│  └──────────┘  └────────┘  └──────────────────┘ │
│                                                  │
│  ┌──────┬──────┬──────┬───────┬──────┬────────┐ │
│  │  D1  │  KV  │  R2  │ Queue │  AI  │   DO   │ │
│  │(data)│(cache│(files│(jobs) │(LLM) │(state) │ │
│  │      │ /kv) │     )│       │      │        │ │
│  └──────┴──────┴──────┴───────┴──────┴────────┘ │
└──────────────────────────────────────────────────┘
```

### External Services

```
┌────────────────────────┐  ┌──────────────────────┐
│  WorkOS                │  │  Stripe               │
│  - AuthKit (auth UI)   │  │  - Checkout (billing) │
│  - Organizations/FGA   │  │  - Webhooks (events)  │
│  - Audit Logs          │  │  - Portal (self-svc)  │
│  - Feature Flags       │  │  - Meter Events       │
│  - Vault (secrets)     │  └──────────────────────┘
│  - Directory Sync      │
│  - Events API          │  ┌──────────────────────┐
│  - MCP Auth            │  │  Resend               │
│  - Connect / Pipes     │  │  - Outbound email     │
└────────────────────────┘  │  - Inbound email      │
                            │  - React Email         │
┌────────────────────────┐  └──────────────────────┘
│  Twilio                │
│  - SMS notifications   │  ┌──────────────────────┐
│  - WhatsApp (optional) │  │  PostHog              │
│  - Voice (optional)    │  │  - Product analytics  │
└────────────────────────┘  │  - Feature flags*     │
                            │  - Session replay      │
                            └──────────────────────┘
```

\*PostHog feature flags complement WorkOS Feature Flags — use WorkOS for entitlement-gated flags, PostHog for A/B testing and gradual rollouts.

## Environment Management

### Worker Secrets (via `wrangler secret put`)

```
WORKOS_API_KEY
WORKOS_CLIENT_ID
WORKOS_COOKIE_PASSWORD
STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET
RESEND_API_KEY
RESEND_WEBHOOK_SECRET
TWILIO_AUTH_TOKEN
POSTHOG_API_KEY
```

### Worker Vars (in wrangler.toml `[vars]`)

```toml
[vars]
ENVIRONMENT = "production"
APP_URL = "https://app.example.com"
APP_NAME = "My SaaS"
EMAIL_DOMAIN = "example.com"
TWILIO_ACCOUNT_SID = "AC..."
TWILIO_FROM_NUMBER = "+1..."
POSTHOG_HOST = "https://us.i.posthog.com"
```

### Frontend Environment (via `import.meta.env`)

```
VITE_WORKOS_CLIENT_ID=client_xxx
VITE_APP_NAME=My SaaS
VITE_POSTHOG_KEY=phc_xxx
VITE_POSTHOG_HOST=https://us.i.posthog.com
```

### .dev.vars.example

```bash
# WorkOS (required)
WORKOS_API_KEY=sk_test_xxx
WORKOS_CLIENT_ID=client_xxx
VITE_WORKOS_CLIENT_ID=client_xxx

# Stripe (optional — billing routes return 503 if missing)
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Resend (optional — email routes return 503 if missing)
RESEND_API_KEY=re_xxx
RESEND_WEBHOOK_SECRET=whsec_xxx

# Twilio (optional — SMS features disabled if missing)
TWILIO_ACCOUNT_SID=AC_xxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_FROM_NUMBER=+1xxx

# PostHog (optional — analytics disabled if missing)
POSTHOG_API_KEY=phc_xxx
VITE_POSTHOG_KEY=phc_xxx
VITE_POSTHOG_HOST=https://us.i.posthog.com

# Cloudflare (for remote dev bindings)
CLOUDFLARE_ACCOUNT_ID=xxx
CLOUDFLARE_API_TOKEN=xxx
```

## Local Development

### script/ Convention

Every Roost project includes these scripts as **TypeScript files executed via bun** (using `#!/usr/bin/env bun` shebang). This gives access to bun's built-in APIs (`Bun.spawn`, `Bun.file`, `Bun.write`, `process.env`) and lets scripts share types/utilities with the main app.

#### `script/setup` — First-time interactive setup

```typescript
#!/usr/bin/env bun

// Interactively prompts for all required/optional keys
// Reads .dev.vars.example as template
// Groups keys by service (WorkOS, Stripe, Resend, Twilio, PostHog)
// Writes .dev.vars with correct permissions
// Validates required keys are non-empty

import { existsSync } from 'fs';

const template = await Bun.file('.dev.vars.example').text();
// Parse template, prompt for each key via console.log + readline...
await Bun.write('.dev.vars', result, { mode: 0o600 });
```

#### `script/bootstrap` — Install everything

```typescript
#!/usr/bin/env bun

// 1. bun install
// 2. Docker Compose up (sidecar services)
// 3. Provision dev Cloudflare resources if using remote bindings:
//    - wrangler d1 create {name}-dev
//    - wrangler kv namespace create {name}-dev
// 4. Run migrations: wrangler d1 migrations apply {name}-dev --local
// 5. workos seed (if workos-seed.yaml exists)
// 6. Verify all tools installed (wrangler, stripe CLI, etc.)

import { $ } from 'bun';

await $`bun install`;
if (existsSync('docker-compose.yml')) await $`docker compose up -d`;
await $`bunx wrangler d1 migrations apply ${dbName} --local`;
```

#### `script/dev` — Start development

```typescript
#!/usr/bin/env bun

// 1. Check .dev.vars exists (prompt to run script/setup if not)
// 2. Start sidecar services if docker-compose.yml exists
// 3. Start Stripe CLI webhook forwarding (background)
// 4. Start Vite dev server (wrangler dev via @cloudflare/vite-plugin)

import { $ } from 'bun';

if (!existsSync('.dev.vars')) {
  console.error('Run script/setup first to create .dev.vars');
  process.exit(1);
}

const stripe = Bun.spawn([
  'stripe',
  'listen',
  '--forward-to',
  'localhost:5173/api/v1/webhooks/stripe',
]);
process.on('exit', () => stripe.kill());

await $`bun run dev`;
```

Also available as `bun dev` / `bun run dev` (via package.json scripts).

#### `script/seed` — Seed development data

```typescript
#!/usr/bin/env bun

// 1. Run Drizzle seed script (if src/core/db/seed.ts exists)
// 2. workos seed (provisions test orgs/users)
// 3. Stripe test data (create test products/prices via Stripe CLI)

import { $ } from 'bun';

if (existsSync('src/core/db/seed.ts')) await $`bun run src/core/db/seed.ts`;
if (existsSync('workos-seed.yaml')) await $`workos seed`;
```

#### `script/teardown` — Clean up dev resources

```typescript
#!/usr/bin/env bun

// 1. workos seed --clean
// 2. Delete dev Cloudflare resources (if remote)
// 3. Docker Compose down
// 4. Remove .wrangler/ local state

import { $ } from 'bun';
import { rmSync } from 'fs';

if (existsSync('workos-seed.yaml')) await $`workos seed --clean`;
if (existsSync('docker-compose.yml')) await $`docker compose down`;
rmSync('.wrangler', { recursive: true, force: true });
```

### Vite Config for Cloudflare

```typescript
// vite.config.ts
import { cloudflare } from '@cloudflare/vite-plugin';
import { reactRouter } from '@react-router/dev/vite';
import tsconfigPaths from 'vite-tsconfig-paths';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [cloudflare({ viteEnvironment: { name: 'ssr' } }), reactRouter(), tsconfigPaths()],
});
```

### React Router Config

```typescript
// react-router.config.ts
import type { Config } from '@react-router/dev/config';

export default {
  ssr: true,
  future: {
    v8_viteEnvironmentApi: true,
  },
} satisfies Config;
```

## Testing

Use **bun:test** for testing — it's fast, zero-config, and built into the bun runtime.

```typescript
// src/core/lib/stripe.test.ts
import { describe, it, expect, mock } from 'bun:test';
import { createMockEnv } from '~/src/core/test-helpers';

describe('updateSeatCount', () => {
  it('updates Stripe subscription quantity', async () => {
    const env = createMockEnv();
    // ...
    expect(result).toBeDefined();
  });
});
```

Test helpers mock Cloudflare bindings:

```typescript
// src/core/test-helpers.ts
export function createMockEnv(): Env {
  return {
    DB: createMockD1(),
    KV: createMockKV(),
    STORAGE: createMockR2(),
    // ... all bindings
  };
}
```

Run tests: `bun test` (no config file needed — bun discovers `*.test.ts` automatically).

For DOM/component testing, use `@happy-dom/global-registrator` or set `jsdom` in bunfig.toml:

```toml
# bunfig.toml
[test]
preload = ["./src/test-setup.ts"]
```

## Docker Compose (Sidecar Services)

For services deployed to Cloudflare Containers that need local equivalents:

```yaml
# docker-compose.yml
services:
  rsshub:
    image: diygod/rsshub:latest
    ports:
      - '1200:1200'
    environment:
      NODE_ENV: production
```

In production, these run as Cloudflare Containers with service bindings in `wrangler.toml`.

## Bootstrap Convention

Every Roost project uses the `script/` convention instead of a monolithic `bootstrap.sh`. The scripts are:

| Script             | Purpose                                    | Idempotent |
| ------------------ | ------------------------------------------ | ---------- |
| `script/setup`     | Interactive .dev.vars creation             | Yes        |
| `script/bootstrap` | Install deps, provision resources, migrate | Yes        |
| `script/dev`       | Start local dev server with all services   | N/A        |
| `script/seed`      | Seed test data in all services             | Yes        |
| `script/teardown`  | Clean up dev resources                     | Yes        |

All scripts are TypeScript with `#!/usr/bin/env bun` shebangs, use `import { $ } from 'bun'` for shell commands, and check for required tools before executing.
