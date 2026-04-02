# PostHog Reference

Deep reference for PostHog product analytics integration in React Router 7 apps on Cloudflare Workers.

## LLM Documentation

- PostHog AI Engineering docs: `https://posthog.com/docs/ai-engineering`
- Use WebFetch on specific docs as needed

## Why PostHog from Day One

PostHog provides product understanding that compounds over time:

- **Event tracking** — understand what users actually do
- **Session replay** — see exactly where users struggle
- **Feature flags** — gradual rollouts and A/B testing
- **Funnels** — track conversion through key flows (signup, activation, upgrade)
- **Retention** — measure if users come back

## Client-Side Setup (React Router 7)

### Installation

```bash
bun add posthog-js
```

### Provider Setup

```tsx
// app/root.tsx or app/routes/_app.tsx
import posthog from 'posthog-js';
import { PostHogProvider } from 'posthog-js/react';

// Initialize once
if (typeof window !== 'undefined') {
  posthog.init(import.meta.env.VITE_POSTHOG_KEY, {
    api_host: import.meta.env.VITE_POSTHOG_HOST || 'https://us.i.posthog.com',
    capture_pageview: false, // We handle this in RR7 navigation
    capture_pageleave: true,
  });
}

export default function AppLayout() {
  return (
    <PostHogProvider client={posthog}>
      <Outlet />
    </PostHogProvider>
  );
}
```

### Page View Tracking with React Router

```tsx
// app/hooks/usePostHogPageView.ts
import { useLocation } from 'react-router';
import { usePostHog } from 'posthog-js/react';
import { useEffect } from 'react';

export function usePostHogPageView() {
  const location = useLocation();
  const posthog = usePostHog();

  useEffect(() => {
    posthog?.capture('$pageview', { $current_url: window.location.href });
  }, [location.pathname]);
}
```

### Event Tracking

```typescript
import { usePostHog } from 'posthog-js/react';

function UpgradeButton() {
  const posthog = usePostHog();

  const handleUpgrade = () => {
    posthog?.capture('billing_upgrade_clicked', {
      current_plan: 'free',
      target_plan: 'pro',
    });
    // ... proceed with upgrade
  };

  return <button onClick={handleUpgrade}>Upgrade</button>;
}
```

### User Identification

After login, identify the user:

```typescript
posthog?.identify(user.id, {
  email: user.email,
  name: user.name,
  plan: user.plan,
  organization_id: organizationId,
});
```

### Group Analytics (Organizations)

```typescript
posthog?.group('organization', organizationId, {
  name: orgName,
  plan: orgPlan,
  member_count: memberCount,
});
```

## Server-Side Tracking (Workers)

For server-side events (webhooks, cron jobs, API-only actions):

```typescript
// src/core/lib/posthog.ts
export async function captureServerEvent(
  env: Env,
  event: {
    distinctId: string;
    event: string;
    properties?: Record<string, unknown>;
  }
) {
  if (!env.POSTHOG_API_KEY) return;

  await fetch(`${env.POSTHOG_HOST || 'https://us.i.posthog.com'}/capture/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      api_key: env.POSTHOG_API_KEY,
      distinct_id: event.distinctId,
      event: event.event,
      properties: {
        ...event.properties,
        $lib: 'cloudflare-worker',
      },
    }),
  });
}
```

### Server-Side Usage

```typescript
// In a webhook handler or cron job
await captureServerEvent(env, {
  distinctId: userId,
  event: 'subscription_created',
  properties: { plan: 'pro', billing_model: 'per_seat' },
});
```

## Feature Flags (A/B Testing)

Use PostHog feature flags for **A/B testing and percentage-based rollouts**. Use WorkOS Feature Flags for **entitlement-based flags** tied to plans/orgs.

```typescript
import { useFeatureFlagEnabled } from 'posthog-js/react';

function Dashboard() {
  const showNewUI = useFeatureFlagEnabled('new-dashboard-ui');
  return showNewUI ? <NewDashboard /> : <OldDashboard />;
}
```

## Key Events to Track

| Event                          | When                     | Properties                            |
| ------------------------------ | ------------------------ | ------------------------------------- |
| `user_signed_up`               | After first login        | `auth_method`, `referral_source`      |
| `onboarding_completed`         | After setup flow         | `steps_completed`, `time_to_complete` |
| `feature_used`                 | Key feature interactions | `feature_name`, `plan`                |
| `billing_upgrade_clicked`      | Upgrade CTA clicked      | `current_plan`, `target_plan`         |
| `billing_checkout_completed`   | Stripe checkout success  | `plan`, `amount`, `billing_model`     |
| `billing_cancellation_started` | Cancel flow initiated    | `plan`, `reason`                      |
| `invite_sent`                  | Team invite sent         | `org_id`, `role`                      |
| `api_key_created`              | API key generated        | `org_id`, `scope`                     |

## Environment Variables

```bash
# Frontend (via import.meta.env)
VITE_POSTHOG_KEY=phc_xxx
VITE_POSTHOG_HOST=https://us.i.posthog.com

# Backend (for server-side capture)
POSTHOG_API_KEY=phc_xxx
POSTHOG_HOST=https://us.i.posthog.com
```

## Privacy & Compliance

- PostHog supports EU hosting if needed (`eu.i.posthog.com`)
- Session replay can be disabled per-user or per-page
- Respect `Do Not Track` headers: `posthog.init(key, { respect_dnt: true })`
- No PII in event properties unless necessary for the use case
