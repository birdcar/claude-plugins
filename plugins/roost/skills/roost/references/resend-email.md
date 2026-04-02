# Resend Email Reference

Deep reference for Resend API integration, React Email templates, inbound email handling, and transactional email patterns in React Router 7 apps.

## LLM Documentation and Tools

- Resend LLMs.txt (full): `https://resend.com/docs/llms-full.txt`
- Resend MCP: `npx -y resend-mcp`
- Agent Skills: `npx skills add resend/resend-skills resend/react-email resend/email-best-practices`
- React Email: `bun add @react-email/components -E`

## Resend API

### SDK Setup

```typescript
import { Resend } from 'resend';

const resend = new Resend(env.RESEND_API_KEY);
```

### Sending Email

```typescript
const { data, error } = await resend.emails.send({
  from: `${env.APP_NAME} <notifications@${env.EMAIL_DOMAIN}>`,
  to: ['user@example.com'],
  subject: 'Welcome to App Name',
  react: WelcomeEmail({ name: 'Alice' }),
});
```

### Idempotency

Idempotency keys are mandatory for transactional email to prevent duplicates on retry. Use the format `<event-type>/<entity-id>` (e.g., `invoice/inv_123`). Keys expire after 24 hours, max 256 characters. Only retry on 429 (rate limit) and 500 (server error) with exponential backoff — do not retry 400, 401, 403, or 422:

```typescript
const { data, error } = await resend.emails.send(
  {
    from: `notifications@${env.EMAIL_DOMAIN}`,
    to: ['user@example.com'],
    subject: 'Your invoice',
    react: InvoiceEmail({ invoiceId: '123' }),
  },
  { headers: { 'Idempotency-Key': `invoice/${invoiceId}` } }
);
```

### Batch Sending

Send up to 100 emails per request:

```typescript
const { data, error } = await resend.batch.send([
  {
    from: sender,
    to: ['user1@example.com'],
    subject: 'Update',
    react: UpdateEmail({ name: 'Alice' }),
  },
  {
    from: sender,
    to: ['user2@example.com'],
    subject: 'Update',
    react: UpdateEmail({ name: 'Bob' }),
  },
]);
```

## Inbound Email

Resend can receive inbound email and forward to your webhook. Use for newsletter-to-feed conversion, support email, etc.

### Webhook Handler (React Router 7)

```typescript
// app/routes/api.v1.webhooks.resend.tsx
import type { Route } from './+types/api.v1.webhooks.resend';

export async function action({ request, context }: Route.ActionArgs) {
  const { env } = context.cloudflare;
  if (!env.RESEND_WEBHOOK_SECRET) return new Response('Not configured', { status: 503 });

  // Verify signature (svix headers)
  const svixId = request.headers.get('svix-id');
  const svixTimestamp = request.headers.get('svix-timestamp');
  const svixSignature = request.headers.get('svix-signature');
  const body = await request.text();

  // Verify HMAC-SHA256 signature
  const key = env.RESEND_WEBHOOK_SECRET;
  const signedContent = `${svixId}.${svixTimestamp}.${body}`;
  const encoder = new TextEncoder();
  const cryptoKey = await crypto.subtle.importKey(
    'raw',
    encoder.encode(key),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  const signature = await crypto.subtle.sign('HMAC', cryptoKey, encoder.encode(signedContent));
  // Compare signatures...

  const payload = JSON.parse(body);
  await processInboundEmail(payload, env);
  return Response.json({ ok: true });
}
```

## React Email Components

### Installation

```bash
bun add @react-email/components -E
```

### Available Components

| Component        | Purpose                              |
| ---------------- | ------------------------------------ |
| `Html`           | Root email wrapper                   |
| `Head`           | Email head (fonts, styles)           |
| `Body`           | Email body container                 |
| `Container`      | Centered content wrapper (max-width) |
| `Section`        | Layout section                       |
| `Column` / `Row` | Column/row layout                    |
| `Heading`        | h1-h6 headings                       |
| `Text`           | Paragraph text                       |
| `Button`         | CTA button (link-based)              |
| `Link`           | Anchor link                          |
| `Image`          | Image with alt text                  |
| `Divider`        | Horizontal rule                      |
| `Preview`        | Email preview text                   |
| `Tailwind`       | Tailwind CSS styling                 |

### Tailwind Support

```tsx
import { Tailwind } from '@react-email/tailwind';

function MyEmail() {
  return (
    <Tailwind>
      <Button className="bg-blue-500 text-white px-4 py-2 rounded">Get Started</Button>
    </Tailwind>
  );
}
```

## Template Patterns

### Welcome Email

```tsx
import {
  Html,
  Head,
  Body,
  Container,
  Heading,
  Text,
  Button,
  Preview,
  Tailwind,
} from '@react-email/components';

interface WelcomeEmailProps {
  name: string;
  appName: string;
  loginUrl: string;
}

export function WelcomeEmail({ name, appName, loginUrl }: WelcomeEmailProps) {
  return (
    <Html>
      <Head />
      <Preview>Welcome to {appName}</Preview>
      <Tailwind>
        <Body className="bg-gray-50 font-sans">
          <Container className="mx-auto py-8 px-4 max-w-xl">
            <Heading className="text-2xl font-bold text-gray-900">Welcome, {name}!</Heading>
            <Text className="text-gray-600 text-base">Your account is ready.</Text>
            <Button
              className="bg-blue-600 text-white px-6 py-3 rounded-md font-medium"
              href={loginUrl}
            >
              Go to Dashboard
            </Button>
          </Container>
        </Body>
      </Tailwind>
    </Html>
  );
}
```

### Organization Invite, Billing Notification, Password Reset

Follow the same pattern — see the Welcome Email above as a template. Each email:

- Has a typed props interface
- Uses Tailwind for styling
- Includes `<Preview>` text
- Is mobile-friendly (max 600px container)

## Email Sending Utility

Centralize email sending with queue integration for reliability:

```typescript
// src/core/lib/email.ts
import { Resend } from 'resend';

interface EmailJob {
  to: string | string[];
  template: string;
  data: Record<string, unknown>;
  idempotencyKey: string;
}

export async function queueEmail(env: Env, job: EmailJob) {
  await env.QUEUE.send({ type: 'send-email', ...job });
}

export async function processEmailJob(job: EmailJob, env: Env) {
  const resend = new Resend(env.RESEND_API_KEY);
  const template = getTemplate(job.template, job.data);

  await resend.emails.send(
    {
      from: `${env.APP_NAME} <notifications@${env.EMAIL_DOMAIN}>`,
      to: Array.isArray(job.to) ? job.to : [job.to],
      subject: template.subject,
      react: template.component,
    },
    { headers: { 'Idempotency-Key': job.idempotencyKey } }
  );
}
```

## Domain Verification

DNS records required (output by bootstrap, configured manually):

- **SPF**: TXT record for sender authorization
- **DKIM**: CNAME records for email signing
- **DMARC**: TXT record for delivery policy

## Template Preview

```json
{
  "scripts": {
    "email:dev": "email dev --dir src/emails"
  }
}
```

Opens a browser-based preview of all email templates with hot reload.
