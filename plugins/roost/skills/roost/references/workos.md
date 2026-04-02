# WorkOS Reference

Deep reference for the full WorkOS product suite: AuthKit, Organizations, FGA, Audit Logs, Feature Flags, Vault, Directory Sync, MCP Auth, Connect/Pipes, and CLI.

## LLM Documentation

- WorkOS LLMs.txt: `https://workos.com/docs/llms.txt`
- WorkOS LLMs.txt (full): `https://workos.com/docs/llms-full.txt`
- Use WebFetch on individual product docs as needed: `https://workos.com/docs/{product}`

## WorkOS CLI

### Installation and Auth

```bash
# Install globally
npm install -g @workos-inc/cli

# Login
workos auth login

# Check status
workos auth status
```

### `workos install` — AI-Powered AuthKit Scaffolder

**This is the recommended first step for any new project.** `workos install` auto-detects the framework (React Router, Next.js, etc.) and scaffolds AuthKit integration with their own AI agent using their billing. This saves tokens and ensures correct patterns.

```bash
# Run in project root after initial scaffold
workos install
```

- Auto-detects framework and configures AuthKit
- Provisions a temporary environment (use `workos env claim` to link to your account)
- Sets up redirect URIs, session management, and middleware
- Uses WorkOS's AI agent and billing — not your tokens

### Key Commands

| Command                                                               | Purpose                                                |
| --------------------------------------------------------------------- | ------------------------------------------------------ |
| `workos install`                                                      | AI-powered AuthKit scaffolder (auto-detects framework) |
| `workos auth login/logout/status`                                     | Authentication management                              |
| `workos env add/remove/switch/list/claim`                             | Environment management                                 |
| `workos doctor`                                                       | Diagnose integration issues                            |
| `workos dev`                                                          | Start local emulator + app together                    |
| `workos emulate`                                                      | Standalone local WorkOS API emulator (port 4100)       |
| `workos seed`                                                         | Declarative resource provisioning from YAML            |
| `workos seed --clean`                                                 | Tear down seed resources                               |
| `workos setup-org "Name" --domain x.com --roles admin,viewer`         | One-shot org onboarding                                |
| `workos onboard-user email@x.com --org org_01ABC --role admin --wait` | User onboarding                                        |
| `workos debug-sso conn_01ABC`                                         | SSO connection diagnostics                             |
| `workos debug-sync directory_01ABC`                                   | Directory sync diagnostics                             |
| `workos skills install/uninstall/list`                                | Manage coding agent skills                             |

### Unclaimed Environments

`workos install` provisions a temporary environment. Use `workos env claim` to link it to a WorkOS account. Until claimed, the environment is ephemeral.

### Seed File Format

```yaml
# workos-seed.yaml
organizations:
  - name: 'Acme Corp'
    domains:
      - 'acme.com'
    roles:
      - admin
      - member
      - viewer
users:
  - email: 'admin@acme.com'
    organization: 'Acme Corp'
    role: admin
```

## AuthKit — Authentication

AuthKit provides drop-in authentication with enterprise features: SSO, Directory Sync, MFA, and user management.

### Core Flow (React Router 7)

1. User clicks "Sign in" -> redirect to AuthKit hosted UI
2. AuthKit handles email/password, social, or SSO login
3. AuthKit redirects back with authorization code
4. RR7 loader exchanges code for user session
5. JWT verified on subsequent requests via WorkOS JWKS

### Client-Side Setup (React Router 7)

```typescript
// app/root.tsx
import { AuthKitProvider } from '@workos-inc/authkit-react';

export default function Root() {
  return (
    <AuthKitProvider clientId={import.meta.env.VITE_WORKOS_CLIENT_ID}>
      <Outlet />
    </AuthKitProvider>
  );
}
```

```typescript
// app/routes/login.tsx
import { useAuth } from '@workos-inc/authkit-react';

export default function Login() {
  const { signIn } = useAuth();
  useEffect(() => { signIn(); }, []);
  return <div>Redirecting to login...</div>;
}
```

### Server-Side JWT Verification

```typescript
// src/core/middleware/jwt.ts
import * as jose from 'jose';

let jwks: jose.JWTVerifyGetKey;

export async function verifyJwt(token: string, clientId: string) {
  if (!jwks) {
    jwks = jose.createRemoteJWKSet(new URL(`https://api.workos.com/sso/jwks/${clientId}`));
  }
  const { payload } = await jose.jwtVerify(token, jwks);
  return payload;
}
```

### Auth Helper for RR7 Loaders/Actions

```typescript
// app/lib/api-auth.ts
import { verifyJwt } from '~/src/core/middleware/jwt';
import { getDb } from '~/src/core/db/db';
import { users } from '~/src/core/db/schema';
import { eq } from 'drizzle-orm';

export async function requireAuth(request: Request, env: Env) {
  const token = request.headers.get('Authorization')?.replace('Bearer ', '');
  if (!token) throw new Response('Unauthorized', { status: 401 });

  const payload = await verifyJwt(token, env.WORKOS_CLIENT_ID);
  const db = getDb(env.DB);

  let user = await db.select().from(users).where(eq(users.workosUserId, payload.sub!)).get();

  if (!user) {
    // Auto-provision on first request
    user = await db
      .insert(users)
      .values({
        id: crypto.randomUUID(),
        email: payload.email as string,
        workosUserId: payload.sub!,
      })
      .returning()
      .get();
  }

  return { user, organizationId: payload.org_id as string };
}
```

## WorkOS Widgets

Prebuilt React components for user management, SSO, and admin portal functionality.

### Dependencies

```bash
bun add @workos-inc/widgets @radix-ui/themes @tanstack/react-query
```

### CSS Setup

```css
@import '@radix-ui/themes/styles.css';
@import '@workos-inc/widgets/styles.css';
```

### Available Widgets

| Widget                | Purpose                                    |
| --------------------- | ------------------------------------------ |
| User Management       | User list, invite, CRUD                    |
| User Profile          | Self-service profile editing               |
| User Sessions         | Active session management                  |
| User Security         | MFA, password, passkeys                    |
| API Keys              | Personal API key management                |
| Pipes                 | Integration/webhook management             |
| Organization Switcher | Multi-org context switching                |
| Domain Verification   | Admin Portal: verify org domains           |
| SSO Connection        | Admin Portal: configure SSO provider       |
| Directory Sync        | Admin Portal: configure directory provider |
| Audit Log Streaming   | Admin Portal: configure log destinations   |

### Widget Integration Pattern

```tsx
import { AuthKitProvider } from '@workos-inc/authkit-react';
import { Theme } from '@radix-ui/themes';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthKitProvider clientId={import.meta.env.VITE_WORKOS_CLIENT_ID}>
        <Theme>{/* Widgets go here */}</Theme>
      </AuthKitProvider>
    </QueryClientProvider>
  );
}
```

### Authorization Token Endpoint (RR7 Action)

```typescript
// app/routes/api.v1.auth.widget-token.tsx
import { requireAuth } from '~/app/lib/api-auth';
import { WorkOS } from '@workos-inc/node';

export async function action({ request, context }: Route.ActionArgs) {
  const { env } = context.cloudflare;
  const { user, organizationId } = await requireAuth(request, env);
  const workos = new WorkOS(env.WORKOS_API_KEY);

  const token = await workos.widgets.getToken({
    userId: user.workosUserId,
    organizationId,
  });

  return Response.json({ token: token.token });
}
```

## Organizations & RBAC

WorkOS manages organizations with role-based access control.

### Default Roles

- `admin` — Full access, billing, settings
- `member` — Standard access, no billing
- `viewer` — Read-only access

### RBAC Middleware Pattern

```typescript
// app/lib/api-rbac.ts
import { WorkOS } from '@workos-inc/node';

export function requireRole(...roles: string[]) {
  return async (request: Request, env: Env) => {
    const { user, organizationId } = await requireAuth(request, env);
    const workos = new WorkOS(env.WORKOS_API_KEY);

    const membership = await workos.userManagement.getOrganizationMembership({
      userId: user.workosUserId,
      organizationId,
    });

    if (!roles.includes(membership.role?.slug)) {
      throw new Response('Forbidden', { status: 403 });
    }

    return { user, organizationId, role: membership.role?.slug };
  };
}
```

## Fine-Grained Authorization (FGA)

WorkOS FGA provides relationship-based access control (like Zanzibar/OpenFGA).

### Use Cases

- Document-level permissions (can user X edit document Y?)
- Team-scoped resources
- Custom permission hierarchies beyond simple roles

### Pattern

```typescript
const workos = new WorkOS(env.WORKOS_API_KEY);

// Check permission
const result = await workos.fga.check({
  checks: [
    {
      resource: { resourceType: 'document', resourceId: docId },
      relation: 'editor',
      subject: { resourceType: 'user', resourceId: userId },
    },
  ],
});

// Grant permission
await workos.fga.writeWarrants([
  {
    resource: { resourceType: 'document', resourceId: docId },
    relation: 'editor',
    subject: { resourceType: 'user', resourceId: userId },
  },
]);
```

## Audit Logs

Enterprise audit trail for compliance. Log sensitive actions automatically.

```typescript
const workos = new WorkOS(env.WORKOS_API_KEY);

await workos.auditLogs.createEvent(organizationId, {
  action: 'document.updated',
  occurredAt: new Date(),
  actor: { type: 'user', id: userId },
  targets: [{ type: 'document', id: docId }],
  context: { location: '127.0.0.1', userAgent: request.headers.get('user-agent') },
});
```

Admins can configure log streaming destinations via the Audit Log Streaming widget.

## Feature Flags

WorkOS Feature Flags for entitlement-gated rollouts tied to organizations.

```typescript
const workos = new WorkOS(env.WORKOS_API_KEY);

const flag = await workos.featureFlags.getFlag('new-dashboard', {
  organizationId,
  userId,
});

if (flag.enabled) {
  // Show new dashboard
}
```

Use WorkOS Feature Flags for entitlement-based flags (tied to plans/orgs). Use PostHog for A/B testing and percentage-based rollouts.

## Vault — Secrets Management

Secure storage for sensitive customer data (API keys, tokens, credentials).

```typescript
const workos = new WorkOS(env.WORKOS_API_KEY);

// Store a secret
await workos.vault.createSecret({
  name: 'customer-api-key',
  value: apiKey,
  environmentId: envId,
});

// Retrieve
const secret = await workos.vault.getSecret(secretId);
```

## Directory Sync — Events API (Preferred)

WorkOS recommends the **Events API** over webhooks for Directory Sync because:

- No spiky webhook traffic to handle
- Cursor-based polling is simpler and more reliable
- No webhook signature verification needed
- Automatic retry via cursor position

### Events API Polling Pattern

```typescript
// src/core/lib/org-sync.ts
import { WorkOS } from '@workos-inc/node';

export async function syncOrganizations(env: Env) {
  const workos = new WorkOS(env.WORKOS_API_KEY);

  // Read cursor from KV
  let cursor = await env.KV.get('workos:events:cursor');

  const events = await workos.events.listEvents({
    events: [
      'dsync.user.created',
      'dsync.user.updated',
      'dsync.user.deleted',
      'dsync.group.created',
      'dsync.group.user_added',
      'dsync.group.user_removed',
    ],
    after: cursor || undefined,
  });

  for (const event of events.data) {
    await processEvent(event, env);
  }

  // Save cursor for next poll
  if (events.data.length > 0) {
    await env.KV.put('workos:events:cursor', events.listMetadata.after);
  }
}
```

Call this from a cron trigger (every 15 minutes):

```typescript
// workers/app.ts
async scheduled(controller: ScheduledController, env: Env, ctx: ExecutionContext) {
  ctx.waitUntil(syncOrganizations(env));
}
```

### DSync Event Types

| Event                      | Action                 |
| -------------------------- | ---------------------- |
| `dsync.user.created`       | Provision user in D1   |
| `dsync.user.updated`       | Update user attributes |
| `dsync.user.deleted`       | Deprovision user       |
| `dsync.group.created`      | Create group/team      |
| `dsync.group.user_added`   | Add user to group      |
| `dsync.group.user_removed` | Remove user from group |

## MCP Auth

WorkOS MCP Auth provides OAuth 2.1 authentication for MCP (Model Context Protocol) servers. Use when building AI agent integrations that need secure third-party access.

## Connect / Pipes

WorkOS Connect (Pipes) provides pre-built integrations with third-party services. The Pipes widget lets end users configure their own integrations.

## SSO (Single Sign-On)

### Flow

1. User enters email -> app detects org domain -> redirects to SSO provider
2. SSO provider authenticates -> redirects to WorkOS
3. WorkOS normalizes profile -> redirects to app callback
4. App creates/updates user session

### Admin Portal SSO Widget

The SSO Connection widget lets org admins self-service configure their SSO provider (Okta, Azure AD, Google Workspace, etc.) without developer intervention.

## Integration Sequence for New Projects

1. **`workos install`** — Let the CLI scaffold AuthKit integration automatically
2. **`workos env claim`** — Link the temporary environment to your WorkOS account
3. **Add widgets** — Integrate WorkOS widgets for admin portal features
4. **Configure FGA** — Set up fine-grained authorization if needed
5. **Enable Audit Logs** — Wire audit events for compliance
6. **Set up DSync** — Configure Events API polling in cron
7. **Enable Feature Flags** — For entitlement-gated features
