# customer-voice

Draft customer responses in Nick's voice, with optional codebase and docs research.

## Why

Consistency in customer-facing communication matters, especially in a pre-sales SE role where technical clarity directly affects the deal. This plugin encodes Nick's writing style (derived from real samples) so Claude can draft responses that sound like him, not like a chatbot.

Two components cover different scenarios: quick replies when you already know the answer, and researched replies when the question needs investigation first.

## Usage

| Component             | Type  | Description                                                     |
| --------------------- | ----- | --------------------------------------------------------------- |
| `/customer-reply`     | Skill | Draft a response in Nick's voice using Slack mrkdwn             |
| `customer-researcher` | Agent | Research codebase + docs, then draft a response in Nick's voice |

### `/customer-reply`

For when you already know the answer and just need it written in voice. Paste the customer's message, and the skill drafts a response following Nick's voice guide: direct, casual, semicolons over em-dashes, brevity-first, inline doc links. Outputs Slack mrkdwn by default.

```
/customer-reply

Customer says: "We're using Firebase for auth and want to add SSO. Do we need to migrate all our users to WorkOS?"
```

After you approve the draft, it'll offer to copy it to your clipboard.

### `customer-researcher`

For when the question requires investigation. The agent pulls latest on the WorkOS monorepo, searches the codebase for actual behavior, verifies public doc URLs, checks SDK repos if relevant, then drafts a response in voice.

The agent is invoked automatically when Claude determines research is needed, or you can ask for it explicitly:

```
Use the customer-researcher agent to answer this:

Customer says: "Why is our Google OAuth user getting an email verification prompt?"
```

Source priority for factual accuracy: Codebase > API Reference > Public docs > SDKs > Blog. The agent will never share proprietary code with the customer or fabricate URLs.

### Shared voice guide

Both components reference `shared/voice.md`, which contains the full voice specification: tone, sentence style, formatting rules, anti-patterns, and real example responses. Edit this file to refine the voice over time.
