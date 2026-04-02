# Twilio Reference

Deep reference for Twilio SMS, voice, and messaging integration in React Router 7 apps on Cloudflare Workers.

## LLM Documentation

- Twilio LLMs.txt: `https://www.twilio.com/docs/llms.txt`
- Use WebFetch on specific docs as needed

## SDK Setup

Twilio's Node SDK has Node.js dependencies that may not work in Workers. Use the REST API directly with `fetch()`:

```typescript
// src/core/lib/twilio.ts
export async function sendSms(env: Env, to: string, body: string) {
  const accountSid = env.TWILIO_ACCOUNT_SID;
  const authToken = env.TWILIO_AUTH_TOKEN;
  const from = env.TWILIO_FROM_NUMBER;

  const response = await fetch(
    `https://api.twilio.com/2010-04-01/Accounts/${accountSid}/Messages.json`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        Authorization: `Basic ${btoa(`${accountSid}:${authToken}`)}`,
      },
      body: new URLSearchParams({ To: to, From: from, Body: body }),
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(`Twilio error: ${error.message}`);
  }

  return response.json();
}
```

## Common Use Cases

### Transactional SMS

```typescript
// Send verification code
await sendSms(env, phoneNumber, `Your verification code is: ${code}`);

// Send billing alert
await sendSms(env, phoneNumber, `Payment of ${amount} received for ${orgName}.`);

// Send notification
await sendSms(env, phoneNumber, `New team member ${name} joined ${orgName}.`);
```

### Queue-Based Sending

Like email, send SMS via queue for reliability:

```typescript
await env.QUEUE.send({
  type: 'send-sms',
  to: phoneNumber,
  body: message,
  idempotencyKey: `sms-${eventId}`,
});
```

### Webhook Handler (React Router 7)

```typescript
// app/routes/api.v1.webhooks.twilio.tsx
import type { Route } from './+types/api.v1.webhooks.twilio';

export async function action({ request, context }: Route.ActionArgs) {
  const { env } = context.cloudflare;

  // Verify Twilio signature
  const twilioSignature = request.headers.get('X-Twilio-Signature');
  // Verify using HMAC-SHA1 of URL + sorted params with auth token
  // See: https://www.twilio.com/docs/usage/security#validating-requests

  const formData = await request.formData();
  const from = formData.get('From') as string;
  const body = formData.get('Body') as string;

  // Process inbound SMS
  await processInboundSms(from, body, env);

  // Return TwiML response
  return new Response('<?xml version="1.0" encoding="UTF-8"?><Response></Response>', {
    headers: { 'Content-Type': 'text/xml' },
  });
}
```

## Environment Variables

```toml
# wrangler.toml [vars]
TWILIO_ACCOUNT_SID = "ACxxxxxxxx"
TWILIO_FROM_NUMBER = "+1xxxxxxxxxx"
```

```bash
# Secrets (via wrangler secret put)
TWILIO_AUTH_TOKEN=xxxxxxxx
```

## Twilio Verify (OTP)

For phone number verification:

```typescript
export async function sendVerification(env: Env, phoneNumber: string) {
  const response = await fetch(
    `https://verify.twilio.com/v2/Services/${env.TWILIO_VERIFY_SID}/Verifications`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        Authorization: `Basic ${btoa(`${env.TWILIO_ACCOUNT_SID}:${env.TWILIO_AUTH_TOKEN}`)}`,
      },
      body: new URLSearchParams({ To: phoneNumber, Channel: 'sms' }),
    }
  );
  return response.json();
}

export async function checkVerification(env: Env, phoneNumber: string, code: string) {
  const response = await fetch(
    `https://verify.twilio.com/v2/Services/${env.TWILIO_VERIFY_SID}/VerificationCheck`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        Authorization: `Basic ${btoa(`${env.TWILIO_ACCOUNT_SID}:${env.TWILIO_AUTH_TOKEN}`)}`,
      },
      body: new URLSearchParams({ To: phoneNumber, Code: code }),
    }
  );
  return response.json();
}
```

## WhatsApp Business API

Same REST API pattern, but use `whatsapp:+1xxx` format for the To/From numbers:

```typescript
await sendMessage(env, `whatsapp:${phoneNumber}`, message);
```

## Security

- Always verify webhook signatures from Twilio before processing
- Store auth tokens as Worker secrets, never in code
- Use restricted API keys where possible
- Rate limit outbound SMS to prevent abuse
