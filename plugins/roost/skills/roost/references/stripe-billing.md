# Stripe Billing Reference

Deep reference for Stripe billing integration patterns, webhook handling, entitlements, and CLI usage.

## LLM Documentation

- Stripe docs in markdown: append `.md` to any docs URL, e.g. `https://docs.stripe.com/billing.md`
- Full LLM index: `https://docs.stripe.com/llms.txt`
- MCP server: `npx -y @stripe/mcp --api-key=...` (local) or `https://mcp.stripe.com` (remote, OAuth)
- Claude Code plugin: `claude /plugin install stripe@claude-plugins-official`
- Agent toolkit: `npm install @stripe/agent-toolkit`

## Security Rules

- Use Restricted API Keys scoped to only the operations needed — never use the full secret key in production
- Webhook signatures must always be verified before processing events
- Never log or expose full API keys — use `sk_...xxxx` format for debugging

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

Seat count update on member add/remove:

```typescript
async function updateSeatCount(orgId: string, env: Env) {
  const org = await env.DB.prepare('SELECT stripe_subscription_id FROM organizations WHERE id = ?')
    .bind(orgId)
    .first();

  const memberCount = await env.DB.prepare(
    'SELECT COUNT(*) as count FROM org_members WHERE org_id = ?'
  )
    .bind(orgId)
    .first();

  await stripe.subscriptions.update(org.stripe_subscription_id, {
    items: [{ id: org.stripe_item_id, quantity: memberCount.count }],
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
    { up_to: 1000, unit_amount: 0 }, // First 1000 free
    { up_to: 10000, unit_amount: 10 }, // $0.10 per unit
    { up_to: 'inf', unit_amount: 5 }, // $0.05 per unit after 10k
  ],
});
```

Usage reporting:

```typescript
// Report usage via meter events (new API)
await stripe.billing.meterEvents.create({
  event_name: 'api_calls',
  payload: {
    stripe_customer_id: customerId,
    value: '1',
  },
});
```

### Product-Led Growth (PLG)

Free tier with self-service upgrade. Focus on conversion.

```typescript
// Free tier (no payment required)
const freePlan = await stripe.prices.create({
  product: product.id,
  unit_amount: 0,
  currency: 'usd',
  recurring: { interval: 'month' },
});

// Pro tier
const proPlan = await stripe.prices.create({
  product: product.id,
  unit_amount: 2900, // $29/month
  currency: 'usd',
  recurring: { interval: 'month' },
});
```

### B2B / Enterprise

Annual contracts with custom pricing, invoicing, and negotiated terms.

```typescript
// Create a quote for enterprise deals
const quote = await stripe.quotes.create({
  customer: customerId,
  line_items: [
    { price: annualPriceId, quantity: 50 }, // 50 seats
  ],
  collection_method: 'send_invoice',
  days_until_due: 30,
});
```

## Webhook Handling

### Endpoint Pattern for Hono

```typescript
import Stripe from 'stripe';

app.post('/api/webhooks/stripe', async (c) => {
  const sig = c.req.header('stripe-signature');
  const body = await c.req.text();

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(body, sig!, c.env.STRIPE_WEBHOOK_SECRET);
  } catch (err) {
    return c.json({ error: 'Invalid signature' }, 400);
  }

  switch (event.type) {
    case 'checkout.session.completed':
      await handleCheckoutCompleted(event.data.object, c.env);
      break;
    case 'customer.subscription.updated':
      await handleSubscriptionUpdated(event.data.object, c.env);
      break;
    case 'customer.subscription.deleted':
      await handleSubscriptionDeleted(event.data.object, c.env);
      break;
    case 'invoice.payment_failed':
      await handlePaymentFailed(event.data.object, c.env);
      break;
  }

  return c.json({ received: true });
});
```

### Critical Webhooks to Handle

| Event                           | Action                                       |
| ------------------------------- | -------------------------------------------- |
| `checkout.session.completed`    | Provision access, create subscription record |
| `customer.subscription.updated` | Update plan/seats, sync entitlements         |
| `customer.subscription.deleted` | Revoke access, downgrade to free             |
| `invoice.payment_failed`        | Notify user, grace period logic              |
| `invoice.paid`                  | Confirm payment, clear warnings              |
| `customer.created`              | Link Stripe customer to internal user        |

## Entitlement Middleware

Check subscription status before allowing access to paid features:

```typescript
function requireEntitlement(feature: string) {
  return async (c, next) => {
    const orgId = c.get('organizationId')

    const org = await c.env.DB.prepare(
      'SELECT plan, stripe_subscription_status FROM organizations WHERE id = ?'
    ).bind(orgId).first()

    if (!org || org.stripe_subscription_status !== 'active') {
      return c.json({ error: 'Subscription required', upgrade_url: '/billing' }, 403)
    }

    const entitlements = getPlanEntitlements(org.plan)
    if (!entitlements.includes(feature)) {
      return c.json({ error: 'Feature not available on current plan', upgrade_url: '/billing' }, 403)
    }

    await next()
  }
}

function getPlanEntitlements(plan: string): string[] {
  const plans: Record<string, string[]> = {
    free: ['basic_access'],
    pro: ['basic_access', 'advanced_features', 'api_access', 'priority_support'],
    enterprise: ['basic_access', 'advanced_features', 'api_access', 'priority_support', 'sso', 'audit_log', 'custom_roles'],
  }
  return plans[plan] || plans.free
}

// Usage
app.get('/api/reports/advanced', requireEntitlement('advanced_features'), async (c) => { ... })
```

## Customer Portal

Let users manage their own billing (update payment, change plan, cancel):

```typescript
app.post('/api/billing/portal', authMiddleware, async (c) => {
  const orgId = c.get('organizationId');
  const org = await c.env.DB.prepare('SELECT stripe_customer_id FROM organizations WHERE id = ?')
    .bind(orgId)
    .first();

  const session = await stripe.billingPortal.sessions.create({
    customer: org.stripe_customer_id,
    return_url: `${c.env.APP_URL}/settings/billing`,
  });

  return c.json({ url: session.url });
});
```

## Checkout Flow

```typescript
app.post('/api/billing/checkout', authMiddleware, async (c) => {
  const { priceId } = await c.req.json();
  const orgId = c.get('organizationId');
  const org = await c.env.DB.prepare('SELECT stripe_customer_id FROM organizations WHERE id = ?')
    .bind(orgId)
    .first();

  const session = await stripe.checkout.sessions.create({
    customer: org.stripe_customer_id,
    mode: 'subscription',
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `${c.env.APP_URL}/settings/billing?success=true`,
    cancel_url: `${c.env.APP_URL}/settings/billing?canceled=true`,
    metadata: { org_id: orgId },
  });

  return c.json({ url: session.url });
});
```

## Stripe CLI

For local development and webhook testing:

```bash
# Listen for webhooks locally
stripe listen --forward-to localhost:8787/api/webhooks/stripe

# Trigger test events
stripe trigger checkout.session.completed
stripe trigger customer.subscription.updated

# Create test resources
stripe products create --name="Pro Plan"
stripe prices create --product=prod_xxx --unit-amount=2900 --currency=usd --recurring[interval]=month
```

## Database Schema for Billing

```sql
-- Add to organizations table
ALTER TABLE organizations ADD COLUMN plan TEXT DEFAULT 'free';
ALTER TABLE organizations ADD COLUMN stripe_customer_id TEXT UNIQUE;
ALTER TABLE organizations ADD COLUMN stripe_subscription_id TEXT;
ALTER TABLE organizations ADD COLUMN stripe_subscription_status TEXT DEFAULT 'none';
ALTER TABLE organizations ADD COLUMN stripe_item_id TEXT;

-- Billing events log
CREATE TABLE billing_events (
  id TEXT PRIMARY KEY,
  org_id TEXT REFERENCES organizations(id),
  stripe_event_id TEXT UNIQUE,
  event_type TEXT NOT NULL,
  data TEXT, -- JSON
  created_at TEXT DEFAULT (datetime('now'))
);
```
