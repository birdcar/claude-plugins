# customer-voice

Research and draft customer responses in Nick's voice.

## Why

Consistency in customer-facing communication matters, especially in a pre-sales SE role where technical clarity directly affects the deal. This plugin encodes Nick's writing style (derived from real samples) so Claude can draft responses that sound like him, not like a chatbot.

Every customer reply goes through the same pipeline: research the question across the WorkOS codebase and public docs, then draft a response in voice with verified sources.

## Architecture

```
/customer-reply (skill)
  └── spawns customer-researcher (agent)
        ├── Track 1: Codebase search (Explore sub-agent)
        ├── Track 2: Docs verification (general-purpose sub-agent)
        ├── Track 3: SDK examples (general-purpose sub-agent, when relevant)
        └── Track 4: Blog search (general-purpose sub-agent, when relevant)
```

The skill is the entry point. It invokes the research agent, which spawns parallel sub-agents for each research track. Sub-agent results survive context compaction, so findings aren't lost during heavy research.

## Usage

| Component             | Type  | Description                                                         |
| --------------------- | ----- | ------------------------------------------------------------------- |
| `/customer-reply`     | Skill | Research and draft a response in Nick's voice using Slack mrkdwn    |
| `customer-researcher` | Agent | Parallel research across codebase, docs, and SDKs; returns findings |

### `/customer-reply`

Paste the customer's message after invoking the skill. It will research the question and draft a response.

```
/customer-reply

Customer says: "We're using Firebase for auth and want to add SSO. Do we need to migrate all our users to WorkOS?"
```

After you approve the draft, it'll offer to copy it to your clipboard.

### First-time setup

On first use, the research agent will ask for the path to your local WorkOS monorepo checkout and save it for future sessions. No manual configuration needed.

### Shared voice guide

Both components reference `shared/voice.md`, which contains the full voice specification: tone, sentence style, formatting rules, anti-patterns, and real example responses. Edit this file to refine the voice over time.

### Source priority

Codebase > API Reference > Public docs > SDKs > Blog. The agent never shares proprietary code with customers or fabricates URLs.
