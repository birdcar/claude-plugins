# Stack Architecture Reference

Reference architecture for Roost-generated SaaS projects: directory structure, data flow, deployment topology, and environment management.

## Project Directory Structure

Every Roost project follows this monorepo structure:

```
{project-name}/
  package.json                    # Workspace root (bun workspaces)
  bun.lock
  .gitignore
  wrangler.toml                   # Top-level wrangler config (may reference packages)
  workos-seed.yaml                # WorkOS seed data
  bootstrap.sh                    # Project provisioning script

  packages/
    api/                          # Hono API on Cloudflare Workers
      package.json
      tsconfig.json
      wrangler.toml               # Worker-specific config with bindings
      src/
        index.ts                  # Hono app entry point, route mounting
        env.ts                    # Env interface (typed bindings)
        routes/
          auth.ts                 # AuthKit callback, session management
          billing.ts              # Stripe checkout, portal, webhooks
          webhooks/
            stripe.ts             # Stripe webhook handler
            workos.ts             # WorkOS DSync webhook handler
          [domain].ts             # Product-specific routes
        middleware/
          auth.ts                 # Session validation, user injection
          billing.ts              # Entitlement checks
          rbac.ts                 # Role-based access control
          cors.ts                 # CORS configuration
        lib/
          stripe.ts               # Stripe client helpers
          workos.ts               # WorkOS client helpers
          email.ts                # Email sending utility (Resend)
          id.ts                   # ID generation (nanoid/cuid)
        emails/
          welcome.tsx             # Welcome email template
          invite.tsx              # Org invitation template
          billing.tsx             # Billing notification templates
          password-reset.tsx      # Password reset template
        db/
          schema.ts               # D1 schema TypeScript types
          migrations/
            0001_initial.sql      # Core tables: users, orgs, memberships
            0002_billing.sql      # Billing tables: subscriptions, events
            [NNNN]_[name].sql     # Product-specific migrations

    web/                          # React + Vite on Cloudflare Pages
      package.json
      tsconfig.json
      vite.config.ts
      index.html
      src/
        main.tsx                  # App entry with providers
        App.tsx                   # Root component with routing
        routes/
          index.tsx               # Home/dashboard
          auth/
            callback.tsx          # AuthKit callback handler
            login.tsx             # Login page
          settings/
            billing.tsx           # Billing management (Stripe portal)
            organization.tsx      # Org settings (WorkOS widgets)
            profile.tsx           # User profile (WorkOS widget)
          [domain]/               # Product-specific routes
        components/
          layout/
            header.tsx
            sidebar.tsx
            footer.tsx
          auth/
            auth-guard.tsx        # Protected route wrapper
            org-switcher.tsx      # Organization switcher widget
          billing/
            plan-selector.tsx     # Plan selection UI
            usage-display.tsx     # Usage metrics (for metered billing)
          ui/                     # Shared Radix-based components
        lib/
          api.ts                  # API client (fetch wrapper)
          auth.ts                 # Auth context/hooks
          types.ts                # Shared frontend types
        styles/
          globals.css             # Global styles, Radix/WorkOS CSS imports

    shared/                       # Shared between api and web
      package.json
      tsconfig.json
      src/
        types.ts                  # Shared type definitions
        constants.ts              # Shared constants
        validation.ts             # Shared validation schemas (zod)
```

## Data Flow

### Authentication Flow

```
Browser -> AuthKit Hosted UI -> WorkOS -> /api/auth/callback -> D1 (user record) -> KV (session)
```

1. User clicks login -> redirect to AuthKit
2. AuthKit handles auth method (password, SSO, social)
3. AuthKit redirects to `/api/auth/callback` with code
4. Worker exchanges code for user profile
5. Upsert user in D1
6. Create session in KV with TTL
7. Return session token to frontend

### API Request Flow

```
Browser -> Worker (auth middleware -> rbac middleware -> entitlement middleware -> route handler) -> D1/KV/R2
```

1. Frontend sends request with session token
2. Auth middleware validates session from KV
3. RBAC middleware checks role permissions
4. Entitlement middleware checks subscription status
5. Route handler processes business logic
6. Response returned to frontend

### Billing Flow

```
Frontend -> /api/billing/checkout -> Stripe Checkout -> Stripe Webhook -> /api/webhooks/stripe -> D1 (subscription update)
```

1. User selects plan -> create Checkout Session
2. Stripe handles payment
3. Stripe sends webhook on completion
4. Worker updates subscription status in D1
5. Entitlement middleware reflects new access immediately

### Email Flow

```
Route Handler -> Queue (email job) -> Queue Consumer -> Resend API -> User Inbox
```

1. Business logic triggers email (welcome, invite, billing)
2. Email job sent to Cloudflare Queue
3. Queue consumer processes job with retry
4. Resend sends email using React Email template
5. Idempotency key prevents duplicates on retry

### Directory Sync Flow

```
Identity Provider -> WorkOS -> Webhook -> /api/webhooks/workos -> D1 (user/group updates)
```

1. Admin configures directory sync in Admin Portal widget
2. Identity provider syncs to WorkOS
3. WorkOS sends webhook events (user created/updated/deleted)
4. Worker processes events, updates D1
5. User access reflects org directory changes

## Deployment Topology

### Cloudflare Services

```
┌─────────────────────────────────────┐
│  Cloudflare Edge Network            │
│                                     │
│  ┌─────────┐     ┌──────────────┐  │
│  │  Pages   │     │   Worker     │  │
│  │  (web)   │────>│   (api)      │  │
│  └─────────┘     └──────┬───────┘  │
│                          │          │
│  ┌───────┬───────┬───────┼───────┐  │
│  │  D1   │  KV   │  R2   │ Queue │  │
│  │(data) │(cache)│(files)│(jobs) │  │
│  └───────┴───────┴───────┴───────┘  │
└─────────────────────────────────────┘
```

### External Services

```
┌──────────────────────┐
│  WorkOS               │
│  - AuthKit (auth UI)  │
│  - DSync (webhooks)   │
│  - SSO (SAML/OIDC)   │
└──────────────────────┘

┌──────────────────────┐
│  Stripe               │
│  - Checkout (billing) │
│  - Webhooks (events)  │
│  - Portal (self-svc)  │
└──────────────────────┘

┌──────────────────────┐
│  Resend               │
│  - Email API          │
│  - Domain verification│
└──────────────────────┘
```

## Environment Management

### Environment Variables by Context

#### Worker Secrets (via `wrangler secret put`)

```
WORKOS_API_KEY
WORKOS_CLIENT_ID
WORKOS_COOKIE_PASSWORD
WORKOS_WEBHOOK_SECRET
STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET
RESEND_API_KEY
```

#### Worker Vars (in wrangler.toml `[vars]`)

```toml
[vars]
ENVIRONMENT = "production"
APP_URL = "https://app.example.com"
APP_NAME = "My SaaS"
EMAIL_DOMAIN = "example.com"
```

#### Frontend Environment (in Vite `.env`)

```
VITE_API_URL=https://api.example.com
VITE_WORKOS_CLIENT_ID=client_xxx
VITE_APP_NAME=My SaaS
```

### Local Development

```bash
# Start API worker locally
cd packages/api && wrangler dev

# Start frontend dev server
cd packages/web && bun run dev

# Start WorkOS emulator (separate terminal)
workos emulate

# Forward Stripe webhooks locally
stripe listen --forward-to localhost:8787/api/webhooks/stripe
```

## Database Schema (Core)

Every Roost project starts with these core tables:

```sql
-- 0001_initial.sql
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  name TEXT,
  workos_user_id TEXT UNIQUE,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS organizations (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  workos_org_id TEXT UNIQUE,
  stripe_customer_id TEXT UNIQUE,
  plan TEXT DEFAULT 'free',
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS org_members (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id),
  org_id TEXT NOT NULL REFERENCES organizations(id),
  role TEXT DEFAULT 'member',
  created_at TEXT DEFAULT (datetime('now')),
  UNIQUE(user_id, org_id)
);

-- 0002_billing.sql
ALTER TABLE organizations ADD COLUMN stripe_subscription_id TEXT;
ALTER TABLE organizations ADD COLUMN stripe_subscription_status TEXT DEFAULT 'none';
ALTER TABLE organizations ADD COLUMN stripe_item_id TEXT;

CREATE TABLE IF NOT EXISTS billing_events (
  id TEXT PRIMARY KEY,
  org_id TEXT REFERENCES organizations(id),
  stripe_event_id TEXT UNIQUE,
  event_type TEXT NOT NULL,
  data TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);
```

## Bootstrap Convention

Every Roost project includes a `bootstrap.sh` at the project root that:

1. Creates Cloudflare resources (D1 database, KV namespace, R2 bucket, Queue)
2. Applies D1 migrations
3. Sets worker secrets via `wrangler secret put`
4. Seeds WorkOS environment via `workos seed`
5. Creates Stripe products/prices
6. Outputs Resend DNS records for domain verification
7. Runs `bun install` for all workspace packages

The bootstrap script is idempotent — running it twice does not create duplicate resources. It checks for existing resources before creating new ones.

### Bootstrap Flags

| Flag             | Purpose                     |
| ---------------- | --------------------------- |
| `--all`          | Full provisioning (default) |
| `--cf-only`      | Cloudflare resources only   |
| `--auth-only`    | WorkOS setup only           |
| `--billing-only` | Stripe setup only           |
| `--email-only`   | Resend setup only           |
| `--migrate`      | D1 migrations only          |
| `--seed`         | WorkOS seed data only       |
| `--dry-run`      | Show what would be created  |
