# customer-voice

Research and draft customer responses in Nick's voice.

## Why

Consistency in customer-facing communication matters, especially in a pre-sales SE role where technical clarity directly affects the deal. This plugin encodes Nick's writing style (derived from real samples) so Claude can draft responses that sound like him, not like a chatbot.

Every customer reply goes through the same pipeline: research the question across the WorkOS codebase and public docs, then draft a response in voice with verified sources.

## Architecture

```
/customer-reply (command)
  └── invokes customer-reply (skill)
        ├── Inlines voice rules as pre-draft constraint
        ├── Reads shared/voice.md for full voice reference
        └── Spawns customer-researcher (agent)
              ├── Track 1: Codebase search (Explore sub-agent)
              ├── Track 2: Docs verification (general-purpose sub-agent)
              ├── Track 3: SDK examples (general-purpose sub-agent, when relevant)
              └── Track 4: Blog search (general-purpose sub-agent, when relevant)
```

The command is the entry point. It invokes the skill, which reads the voice guide, then spawns the research agent for parallel sub-agent research. Sub-agent results survive context compaction, so findings aren't lost during heavy research. Voice rules are inlined in the skill and applied before drafting, not as a post-draft checklist.

## Usage

| Component             | Type    | Description                                                         |
| --------------------- | ------- | ------------------------------------------------------------------- |
| `/customer-reply`     | Command | Entry point; invokes the customer-reply skill                       |
| `customer-reply`      | Skill   | Voice-constrained workflow: research, draft in voice, review        |
| `customer-researcher` | Agent   | Parallel research across codebase, docs, and SDKs; returns findings |

### `/customer-reply`

Paste the customer's message after invoking the command. It will research the question and draft a response in Nick's voice.

```
/customer-reply

Customer says: "We're using Firebase for auth and want to add SSO. Do we need to migrate all our users to WorkOS?"
```

After you approve the draft, it copies it to your clipboard.

### First-time setup

On first use, the research agent will ask for the path to your local WorkOS monorepo checkout and save it for future sessions. No manual configuration needed.

### Voice guide

The skill inlines critical voice rules (anti-patterns, formatting, tone) directly so they're always present. It also reads `shared/voice.md` at runtime for the full specification including real example responses. Edit `shared/voice.md` to refine the voice over time.

### Source priority

Codebase > API Reference > Public docs > SDKs > Blog. The agent never shares proprietary code with customers or fabricates URLs.
