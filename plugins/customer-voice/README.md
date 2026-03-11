# customer-voice

Researches customer questions across the WorkOS codebase and docs, then drafts a response in Nick's voice.

## The problem

Pre-sales SE responses are only as good as two things: technical accuracy and voice consistency. Getting both right on every reply is slower than it should be. The research is tedious (codebase, docs, SDKs, all separate), and drafting in a consistent voice while staying technically precise takes real concentration. This plugin handles the research pipeline automatically and applies voice constraints from the first word rather than as a post-draft checklist.

## How it works

`/customer-reply` is the entry point. Paste the customer's message after invoking it. The skill reads the voice guide, then spawns the `customer-researcher` agent to run parallel research across:

- The local WorkOS monorepo (via `Explore` sub-agent)
- Public docs at workos.com/docs (URL verification included)
- Relevant SDK repos when the question involves code examples
- The WorkOS blog when explainer content would help

Sub-agents run in parallel and their results survive context compaction, so findings aren't lost during heavy research sessions. The draft only starts after research completes; speculative drafts waste revision cycles.

After you approve the draft, it copies to your clipboard via `pbcopy`.

## Setup

On first use, the researcher agent will ask for two paths and save them to `config.local.md` (gitignored):

- `workos_monorepo_path`: absolute path to your local WorkOS monorepo checkout
- `sdk_base_path`: absolute path to the directory containing local SDK checkouts

It won't ask again after that.

## Usage

```
/customer-reply

Customer message goes here. Paste the full thread or just the latest message.
```

The skill handles the rest: intake, triage, parallel research, draft in voice, review loop, clipboard copy.

## Voice

The voice rules are encoded in `shared/voice.md` and inlined in the skill. The short version: direct, conversational, technically precise, Slack mrkdwn by default. No em-dashes (ever), no corporate closers, no restating what the customer already said.

Edit `shared/voice.md` to refine the voice over time as new writing samples accumulate. The inlined quick-reference in the skill stays as a reliability fallback; the full guide is where refinement happens.

## Source priority

When research results conflict, the skill trusts in this order: codebase > API reference > other docs > SDKs > blog. Fabricated URLs are a hard failure; the researcher only returns links it verified.
