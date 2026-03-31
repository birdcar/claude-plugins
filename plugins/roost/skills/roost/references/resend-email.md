# Resend Email Reference

Deep reference for Resend API integration, React Email templates, and transactional email patterns.

## LLM Documentation and Tools

- Resend MCP: `npx -y resend-mcp`
- Agent Skills: `npx skills add resend/resend-skills resend/react-email resend/email-best-practices`
- React Email: `npm install @react-email/components -E`

## Resend API

### SDK Setup

```typescript
import { Resend } from 'resend';

const resend = new Resend(env.RESEND_API_KEY);
```

### Sending Email

```typescript
const { data, error } = await resend.emails.send({
  from: 'App Name <notifications@yourdomain.com>',
  to: ['user@example.com'],
  subject: 'Welcome to App Name',
  react: WelcomeEmail({ name: 'Alice' }),
});

if (error) {
  console.error('Email send failed:', error);
}
```

### Idempotency

Idempotency keys are mandatory for transactional email to prevent duplicates on retry:

```typescript
const { data, error } = await resend.emails.send(
  {
    from: 'notifications@yourdomain.com',
    to: ['user@example.com'],
    subject: 'Your invoice',
    react: InvoiceEmail({ invoiceId: '123' }),
  },
  {
    headers: {
      'Idempotency-Key': `invoice-${invoiceId}-${Date.now()}`,
    },
  }
);
```

### Batch Sending

Send up to 100 emails per request:

```typescript
const { data, error } = await resend.batch.send([
  {
    from: 'notifications@yourdomain.com',
    to: ['user1@example.com'],
    subject: 'Update',
    react: UpdateEmail({ name: 'Alice' }),
  },
  {
    from: 'notifications@yourdomain.com',
    to: ['user2@example.com'],
    subject: 'Update',
    react: UpdateEmail({ name: 'Bob' }),
  },
]);
```

## React Email Components

### Installation

```bash
npm install @react-email/components -E
```

### Available Components

| Component    | Purpose                                            |
| ------------ | -------------------------------------------------- |
| `Html`       | Root email wrapper                                 |
| `Head`       | Email head (fonts, styles)                         |
| `Body`       | Email body container                               |
| `Container`  | Centered content wrapper (max-width)               |
| `Section`    | Layout section                                     |
| `Column`     | Column layout                                      |
| `Row`        | Row layout                                         |
| `Heading`    | h1-h6 headings                                     |
| `Text`       | Paragraph text                                     |
| `Button`     | CTA button (link-based)                            |
| `Link`       | Anchor link                                        |
| `Image`      | Image with alt text                                |
| `Divider`    | Horizontal rule                                    |
| `Preview`    | Email preview text (shown in inbox before opening) |
| `Font`       | Custom font declaration                            |
| `Markdown`   | Render markdown content                            |
| `CodeBlock`  | Syntax-highlighted code                            |
| `CodeInline` | Inline code styling                                |

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
  Section,
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
            <Text className="text-gray-600 text-base">
              Your account is ready. Get started by exploring your dashboard.
            </Text>
            <Section className="text-center py-4">
              <Button
                className="bg-blue-600 text-white px-6 py-3 rounded-md font-medium"
                href={loginUrl}
              >
                Go to Dashboard
              </Button>
            </Section>
          </Container>
        </Body>
      </Tailwind>
    </Html>
  );
}
```

### Organization Invite

```tsx
interface InviteEmailProps {
  inviterName: string;
  orgName: string;
  role: string;
  acceptUrl: string;
}

export function InviteEmail({ inviterName, orgName, role, acceptUrl }: InviteEmailProps) {
  return (
    <Html>
      <Head />
      <Preview>
        {inviterName} invited you to join {orgName}
      </Preview>
      <Tailwind>
        <Body className="bg-gray-50 font-sans">
          <Container className="mx-auto py-8 px-4 max-w-xl">
            <Heading className="text-2xl font-bold text-gray-900">You've been invited</Heading>
            <Text className="text-gray-600">
              {inviterName} invited you to join <strong>{orgName}</strong> as a{' '}
              <strong>{role}</strong>.
            </Text>
            <Section className="text-center py-4">
              <Button
                className="bg-blue-600 text-white px-6 py-3 rounded-md font-medium"
                href={acceptUrl}
              >
                Accept Invitation
              </Button>
            </Section>
            <Text className="text-gray-400 text-sm">This invitation expires in 7 days.</Text>
          </Container>
        </Body>
      </Tailwind>
    </Html>
  );
}
```

### Billing Notification

```tsx
interface BillingEmailProps {
  orgName: string;
  planName: string;
  amount: string;
  billingUrl: string;
  type: 'payment_success' | 'payment_failed' | 'trial_ending';
}

export function BillingEmail({ orgName, planName, amount, billingUrl, type }: BillingEmailProps) {
  const subjects = {
    payment_success: `Payment received for ${orgName}`,
    payment_failed: `Payment failed for ${orgName}`,
    trial_ending: `Your trial is ending soon`,
  };

  return (
    <Html>
      <Head />
      <Preview>{subjects[type]}</Preview>
      <Tailwind>
        <Body className="bg-gray-50 font-sans">
          <Container className="mx-auto py-8 px-4 max-w-xl">
            <Heading className="text-2xl font-bold text-gray-900">
              {type === 'payment_success' && 'Payment Confirmed'}
              {type === 'payment_failed' && 'Payment Failed'}
              {type === 'trial_ending' && 'Trial Ending Soon'}
            </Heading>
            <Text className="text-gray-600">
              {type === 'payment_success' &&
                `We received your payment of ${amount} for the ${planName} plan.`}
              {type === 'payment_failed' &&
                `We were unable to process your payment of ${amount}. Please update your payment method.`}
              {type === 'trial_ending' &&
                `Your free trial of the ${planName} plan ends in 3 days. Upgrade to keep access.`}
            </Text>
            <Section className="text-center py-4">
              <Button
                className="bg-blue-600 text-white px-6 py-3 rounded-md font-medium"
                href={billingUrl}
              >
                {type === 'payment_failed' ? 'Update Payment' : 'View Billing'}
              </Button>
            </Section>
          </Container>
        </Body>
      </Tailwind>
    </Html>
  );
}
```

### Password Reset

```tsx
interface PasswordResetProps {
  resetUrl: string;
  expiresIn: string;
}

export function PasswordResetEmail({ resetUrl, expiresIn }: PasswordResetProps) {
  return (
    <Html>
      <Head />
      <Preview>Reset your password</Preview>
      <Tailwind>
        <Body className="bg-gray-50 font-sans">
          <Container className="mx-auto py-8 px-4 max-w-xl">
            <Heading className="text-2xl font-bold text-gray-900">Password Reset</Heading>
            <Text className="text-gray-600">
              Click the button below to reset your password. This link expires in {expiresIn}.
            </Text>
            <Section className="text-center py-4">
              <Button
                className="bg-blue-600 text-white px-6 py-3 rounded-md font-medium"
                href={resetUrl}
              >
                Reset Password
              </Button>
            </Section>
            <Text className="text-gray-400 text-sm">
              If you didn't request this, you can safely ignore this email.
            </Text>
          </Container>
        </Body>
      </Tailwind>
    </Html>
  );
}
```

## Email Sending Utility

Centralize email sending with queue integration for reliability:

```typescript
interface EmailJob {
  to: string | string[];
  template: string;
  data: Record<string, unknown>;
  idempotencyKey: string;
}

async function queueEmail(env: Env, job: EmailJob) {
  await env.QUEUE.send(job);
}

// Queue consumer
async function processEmailJob(job: EmailJob, env: Env) {
  const resend = new Resend(env.RESEND_API_KEY);
  const template = getTemplate(job.template, job.data);

  await resend.emails.send(
    {
      from: `${env.APP_NAME} <notifications@${env.EMAIL_DOMAIN}>`,
      to: Array.isArray(job.to) ? job.to : [job.to],
      subject: template.subject,
      react: template.component,
    },
    {
      headers: { 'Idempotency-Key': job.idempotencyKey },
    }
  );
}
```

## Domain Verification

Domain DNS verification is a human-required step. Resend provides DNS records to add:

- **SPF**: TXT record for sender authorization
- **DKIM**: CNAME records for email signing
- **DMARC**: TXT record for delivery policy

The bootstrap script outputs the required DNS records but cannot configure them automatically.

## Template Preview Setup

React Email includes a preview server for development:

```bash
# In package.json
{
  "scripts": {
    "email:dev": "email dev --dir packages/api/src/emails"
  }
}
```

This opens a browser-based preview of all email templates with hot reload.
