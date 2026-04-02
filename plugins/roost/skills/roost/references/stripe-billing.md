# Stripe Billing Reference

Deep reference for Stripe billing integration patterns, webhook handling, entitlements, and CLI usage in React Router 7 apps with Drizzle ORM.

## LLM Documentation and Tools

- Full LLM docs: `https://docs.stripe.com/llms.txt`
- Building with LLMs guide: `https://docs.stripe.com/building-with-llms`
- Any docs page in markdown: append `.md` to the URL (e.g., `https://docs.stripe.com/billing.md`)
- MCP server: `npx -y @stripe/mcp --api-key=...` (local) or `https://mcp.stripe.com` (remote, OAuth)
- Agent toolkit: `npm install @stripe/agent-toolkit`

## Security Rules

- Use Restricted API Keys scoped to only the operations needed — never use the full secret key in production
- Webhook signatures must always be verified before processing events
- Never log or expose full API keys — use `sk_...xxxx` format for debugging
- Stripe routes should return 503 if `STRIPE_SECRET_KEY` is not configured (graceful degradation)

## Billing Models

### Per-Seat Billing

Charge per active user/seat in an organization. Most common for B2B SaaS.

```typescript
// Stripe product/price setup
const product = await stripe.products.create({
  name: 'Pro Plan',
  metadata: { billing_model: 'per_seat' },
});

const price = await stripe.prices.create({
  product: product.id,
  unit_amount: 1500, // $15/seat/month
  currency: 'usd',
  recurring: { interval: 'month' },
  billing_scheme: 'per_unit',
});
```

Seat count update on member add/remove (Drizzle):

```typescript
import { eq, count } from 'drizzle-orm';
import { organizations, orgMembers } from '~/src/core/db/schema';

async function updateSeatCount(orgId: string, env: Env) {
  const db = getDb(env.DB);
  const org = await db.select().from(organizations).where(eq(organizations.id, orgId)).get();

  const [{ memberCount }] = await db
    .select({ memberCount: count() })
    .from(orgMembers)
    .where(eq(orgMembers.orgId, orgId));

  await stripe.subscriptions.update(org.stripeSubscriptionId, {
    items: [{ id: org.stripeItemId, quantity: memberCount }],
  });
}
```

### Usage-Based Billing

Charge based on consumption (API calls, storage, compute minutes).

```typescript
const price = await stripe.prices.create({
  product: product.id,
  currency: 'usd',
  recurring: { interval: 'month', usage_type: 'metered' },
  billing_scheme: 'tiered',
  tiers_mode: 'graduated',
  tiers: [
    { up_to: 1000, unit_amount: 0 },
    { up_to: 10000, unit_amount: 10 },
    { up_to: 'inf', unit_amount: 5 },
  ],
});
```

Usage reporting:

```typescript
await stripe.billing.meterEvents.create({
  event_name: 'api_calls',
  payload: { stripe_customer_id: customerId, value: '1' },
});
```

### Product-Led Growth (PLG)

Free tier with self-service upgrade. Focus on conversion.

### B2B / Enterprise

Annual contracts with custom pricing, invoicing, and negotiated terms.

```typescript
const quote = await stripe.quotes.create({
  customer: customerId,
  line_items: [{ price: annualPriceId, quantity: 50 }],
  collection_method: 'send_invoice',
  days_until_due: 30,
});
```

## Webhook Handling (React Router 7)

```typescript
// app/routes/api.v1.webhooks.stripe.tsx
import type { Route } from './+types/api.v1.webhooks.stripe';
import Stripe from 'stripe';
import { getDb } from '~/src/core/db/db';
import { organizations, billingEvents } from '~/src/core/db/schema';
import { eq } from 'drizzle-orm';

export async function action({ request, context }: Route.ActionArgs) {
  const { env } = context.cloudflare;
  if (!env.STRIPE_SECRET_KEY) return new Response('Billing not configured', { status: 503 });

  const stripe = new Stripe(env.STRIPE_SECRET_KEY);
  const sig = request.headers.get('stripe-signature');
  const body = await request.text();

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(body, sig!, env.STRIPE_WEBHOOK_SECRET);
  } catch {
    return Response.json({ error: 'Invalid signature' }, { status: 400 });
  }

  const db = getDb(env.DB);

  // Idempotency check
  const existing = await db
    .select()
    .from(billingEvents)
    .where(eq(billingEvents.stripeEventId, event.id))
    .get();
  if (existing) return Response.json({ received: true });

  // Log event
  await db.insert(billingEvents).values({
    id: crypto.randomUUID(),
    stripeEventId: event.id,
    eventType: event.type,
    data: JSON.stringify(event.data.object),
  });

  switch (event.type) {
    case 'checkout.session.completed':
      await handleCheckoutCompleted(event.data.object as Stripe.Checkout.Session, db, env);
      break;
    case 'customer.subscription.updated':
      await handleSubscriptionUpdated(event.data.object as Stripe.Subscription, db);
      break;
    case 'customer.subscription.deleted':
      await handleSubscriptionDeleted(event.data.object as Stripe.Subscription, db);
      break;
    case 'invoice.payment_failed':
      await handlePaymentFailed(event.data.object as Stripe.Invoice, db, env);
      break;
  }

  return Response.json({ received: true });
}
```

### Critical Webhooks to Handle

| Event                           | Action                                       |
| ------------------------------- | -------------------------------------------- |
| `checkout.session.completed`    | Provision access, create subscription record |
| `customer.subscription.updated` | Update plan/seats, sync entitlements         |
| `customer.subscription.deleted` | Revoke access, downgrade to free             |
| `invoice.payment_failed`        | Notify user, grace period logic              |
| `invoice.paid`                  | Confirm payment, clear warnings              |

## Billing Routes (React Router 7)

```typescript
// app/routes/api.v1.billing.tsx
import type { Route } from './+types/api.v1.billing';
import { requireAuth } from '~/app/lib/api-auth';
import { getDb } from '~/src/core/db/db';
import { organizations } from '~/src/core/db/schema';
import { eq } from 'drizzle-orm';
import Stripe from 'stripe';

// GET /api/v1/billing — return current billing status
export async function loader({ request, context }: Route.LoaderArgs) {
  const { env } = context.cloudflare;
  const { user, organizationId } = await requireAuth(request, env);
  const db = getDb(env.DB);

  const org = await db
    .select()
    .from(organizations)
    .where(eq(organizations.id, organizationId))
    .get();

  return Response.json({
    plan: org?.plan || 'free',
    status: org?.stripeSubscriptionStatus || 'none',
  });
}

// POST /api/v1/billing — create checkout or portal session
export async function action({ request, context }: Route.ActionArgs) {
  const { env } = context.cloudflare;
  if (!env.STRIPE_SECRET_KEY) return new Response('Billing not configured', { status: 503 });

  const { user, organizationId } = await requireAuth(request, env);
  const stripe = new Stripe(env.STRIPE_SECRET_KEY);
  const db = getDb(env.DB);
  const { intent, priceId } = await request.json();

  const org = await db
    .select()
    .from(organizations)
    .where(eq(organizations.id, organizationId))
    .get();

  if (intent === 'checkout') {
    const session = await stripe.checkout.sessions.create({
      customer: org.stripeCustomerId,
      mode: 'subscription',
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: `${env.APP_URL}/settings/billing?success=true`,
      cancel_url: `${env.APP_URL}/settings/billing?canceled=true`,
      metadata: { org_id: organizationId },
    });
    return Response.json({ url: session.url });
  }

  if (intent === 'portal') {
    const session = await stripe.billingPortal.sessions.create({
      customer: org.stripeCustomerId,
      return_url: `${env.APP_URL}/settings/billing`,
    });
    return Response.json({ url: session.url });
  }
}
```

## Entitlement Middleware

```typescript
// app/lib/api-tier.ts
import { getDb } from '~/src/core/db/db';
import { organizations } from '~/src/core/db/schema';
import { eq } from 'drizzle-orm';

const PLAN_ENTITLEMENTS: Record<string, string[]> = {
  free: ['basic_access'],
  pro: ['basic_access', 'advanced_features', 'api_access', 'priority_support'],
  enterprise: [
    'basic_access',
    'advanced_features',
    'api_access',
    'priority_support',
    'sso',
    'audit_log',
    'custom_roles',
  ],
};

export async function requireEntitlement(feature: string, orgId: string, env: Env) {
  const db = getDb(env.DB);
  const org = await db.select().from(organizations).where(eq(organizations.id, orgId)).get();

  if (!org || org.stripeSubscriptionStatus !== 'active') {
    throw Response.json(
      { error: 'Subscription required', upgrade_url: '/billing' },
      { status: 403 }
    );
  }

  const entitlements = PLAN_ENTITLEMENTS[org.plan] || PLAN_ENTITLEMENTS.free;
  if (!entitlements.includes(feature)) {
    throw Response.json(
      { error: 'Feature not available on current plan', upgrade_url: '/billing' },
      { status: 403 }
    );
  }
}
```

## Stripe CLI — Local Development

```bash
# Listen for webhooks locally
stripe listen --forward-to localhost:5173/api/v1/webhooks/stripe

# Trigger test events
stripe trigger checkout.session.completed
stripe trigger customer.subscription.updated

# Create test resources
stripe products create --name="Pro Plan"
stripe prices create --product=prod_xxx --unit-amount=2900 --currency=usd --recurring[interval]=month
```

The `script/dev` script automatically starts `stripe listen` in the background when `STRIPE_SECRET_KEY` is configured in `.dev.vars`.

## Database Schema (Drizzle)

See `${CLAUDE_SKILL_DIR}/references/stack-architecture.md` for the full Drizzle schema. Key billing fields:

- `organizations.plan` — Current plan tier (free, pro, enterprise)
- `organizations.stripeCustomerId` — Link to Stripe customer
- `organizations.stripeSubscriptionId` — Active subscription
- `organizations.stripeSubscriptionStatus` — none, active, past_due, canceled
- `billingEvents` — Idempotent event log for webhook processing
