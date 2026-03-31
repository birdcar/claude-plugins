# WorkOS AuthKit Reference

Deep reference for WorkOS AuthKit integration, widgets, CLI, SSO/DSync, and RBAC patterns.

## LLM Documentation

WorkOS does not publish an llms.txt. Use WebFetch on `https://workos.com/docs` pages or the WorkOS CLI `workos doctor` for diagnostics.

## AuthKit Overview

AuthKit provides drop-in authentication with enterprise features: SSO, Directory Sync, MFA, and user management. It handles the auth flow and returns user/org data to the application.

### Core Flow

1. User clicks "Sign in" -> redirect to AuthKit hosted UI
2. AuthKit handles email/password, social, or SSO login
3. AuthKit redirects back with authorization code
4. Backend exchanges code for user session
5. Session stored in KV (for Workers) or cookie

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

### Key Commands

| Command                                                               | Purpose                                               |
| --------------------------------------------------------------------- | ----------------------------------------------------- |
| `workos install`                                                      | AI-powered AuthKit scaffolder, auto-detects framework |
| `workos auth login/logout/status`                                     | Authentication management                             |
| `workos env add/remove/switch/list/claim`                             | Environment management                                |
| `workos doctor`                                                       | Diagnose integration issues                           |
| `workos skills install/uninstall/list`                                | Manage coding agent skills                            |
| `workos dev`                                                          | Start local emulator + app together                   |
| `workos emulate`                                                      | Standalone local WorkOS API emulator (port 4100)      |
| `workos seed`                                                         | Declarative resource provisioning from YAML           |
| `workos setup-org "Name" --domain x.com --roles admin,viewer`         | One-shot org onboarding                               |
| `workos onboard-user email@x.com --org org_01ABC --role admin --wait` | User onboarding                                       |
| `workos debug-sso conn_01ABC`                                         | SSO connection diagnostics                            |
| `workos debug-sync directory_01ABC`                                   | Directory sync diagnostics                            |
| `workos seed --clean`                                                 | Tear down seed resources                              |

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

## AuthKit Integration for Hono (Workers)

### Middleware Pattern

```typescript
import { WorkOS } from '@workos-inc/node';

const workos = new WorkOS(env.WORKOS_API_KEY);

async function authMiddleware(c, next) {
  const sessionToken = c.req.header('Authorization')?.replace('Bearer ', '');
  if (!sessionToken) {
    return c.json({ error: 'Unauthorized' }, 401);
  }

  try {
    const session = await workos.userManagement.loadSealedSession({
      sessionData: sessionToken,
      cookiePassword: env.WORKOS_COOKIE_PASSWORD,
    });
    const authResult = await session.authenticate();
    if (authResult.authenticated) {
      c.set('user', authResult.user);
      c.set('organizationId', authResult.organizationId);
      await next();
    } else {
      return c.json({ error: 'Session expired' }, 401);
    }
  } catch {
    return c.json({ error: 'Invalid session' }, 401);
  }
}
```

### Callback Route

```typescript
app.get('/api/auth/callback', async (c) => {
  const code = c.req.query('code');
  if (!code) return c.json({ error: 'Missing code' }, 400);

  const { user, organizationId } = await workos.userManagement.authenticateWithCode({
    clientId: c.env.WORKOS_CLIENT_ID,
    code,
  });

  // Create/update user in D1
  await c.env.DB.prepare(
    'INSERT OR REPLACE INTO users (id, email, name, workos_user_id) VALUES (?, ?, ?, ?)'
  )
    .bind(generateId(), user.email, `${user.firstName} ${user.lastName}`, user.id)
    .run();

  // Create session in KV
  const sessionId = generateId();
  await c.env.KV.put(
    `session:${sessionId}`,
    JSON.stringify({
      userId: user.id,
      organizationId,
      email: user.email,
    }),
    { expirationTtl: 86400 }
  );

  return c.redirect(`/?session=${sessionId}`);
});
```

## WorkOS Widgets

Prebuilt React components for user management, SSO, and admin portal functionality.

### Dependencies

```bash
npm install @workos-inc/widgets @radix-ui/themes @tanstack/react-query
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
      <AuthKitProvider>
        <Theme>{/* Widgets go here */}</Theme>
      </AuthKitProvider>
    </QueryClientProvider>
  );
}
```

### Authorization Token Endpoint

Widgets require a backend endpoint that issues scoped authorization tokens:

```typescript
app.post('/api/auth/widget-token', authMiddleware, async (c) => {
  const user = c.get('user');
  const orgId = c.get('organizationId');

  const token = await workos.widgets.getToken({
    userId: user.id,
    organizationId: orgId,
  });

  return c.json({ token: token.token });
});
```

## SSO (Single Sign-On)

### Flow

1. User enters email -> app detects org domain -> redirects to SSO provider
2. SSO provider authenticates -> redirects to WorkOS
3. WorkOS normalizes profile -> redirects to app callback
4. App creates/updates user session

### Admin Portal SSO Widget

The SSO Connection widget lets org admins self-service configure their SSO provider (Okta, Azure AD, Google Workspace, etc.) without developer intervention.

## Directory Sync (DSync)

### Overview

Syncs user/group data from identity providers (Okta, Azure AD, etc.) into WorkOS. Events are delivered via webhooks.

### Key Webhooks

| Event                      | Purpose                 |
| -------------------------- | ----------------------- |
| `dsync.user.created`       | New user provisioned    |
| `dsync.user.updated`       | User attributes changed |
| `dsync.user.deleted`       | User deprovisioned      |
| `dsync.group.created`      | New group created       |
| `dsync.group.user_added`   | User added to group     |
| `dsync.group.user_removed` | User removed from group |

### Handling DSync Events

```typescript
app.post('/api/webhooks/workos', async (c) => {
  const payload = await c.req.json();
  const sigHeader = c.req.header('WorkOS-Signature');

  // Verify signature
  const isValid = workos.webhooks.verifyHeader({
    payload: JSON.stringify(payload),
    sigHeader,
    secret: c.env.WORKOS_WEBHOOK_SECRET,
  });
  if (!isValid) return c.json({ error: 'Invalid signature' }, 400);

  switch (payload.event) {
    case 'dsync.user.created':
      await provisionUser(payload.data, c.env);
      break;
    case 'dsync.user.deleted':
      await deprovisionUser(payload.data, c.env);
      break;
  }

  return c.json({ ok: true });
});
```

## RBAC Pattern

WorkOS supports role-based access control at the organization level.

### Roles in Roost Projects

Default roles generated for every project:

- `admin` — Full access, billing, settings
- `member` — Standard access, no billing
- `viewer` — Read-only access

### Middleware Pattern

```typescript
function requireRole(...roles: string[]) {
  return async (c, next) => {
    const user = c.get('user')
    const orgId = c.get('organizationId')

    const membership = await workos.userManagement.getOrganizationMembership({
      userId: user.id,
      organizationId: orgId,
    })

    if (!roles.includes(membership.role?.slug)) {
      return c.json({ error: 'Forbidden' }, 403)
    }

    await next()
  }
}

// Usage
app.delete('/api/org/settings', requireRole('admin'), async (c) => { ... })
```
