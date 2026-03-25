---
name: write-for
description: Draft a message for a specific channel with optional topic
allowed-tools: Read, Glob, Grep, Bash, Agent, AskUserQuestion
argument-hint: <channel> [topic]
---

Draft content for a specific communication channel. If a topic is provided, draft about that topic. If no topic, summarize the current session context for the target channel.

## Process

1. Parse `$ARGUMENTS`:
   - `$0`: channel name (required) — e.g., `slack`, `email`, `bluesky`, `github`, or a custom channel name
   - Remaining args: topic (optional) — what to write about

2. If no channel name provided, use AskUserQuestion to ask which channel.

3. Determine the register:
   - Use the channel's default register unless the user specifies otherwise
   - Default register mapping: slack=internal, email=professional, bluesky=social, github=professional

4. Spawn `bat-kol:config-resolver` agent to load the voice profile:
   - Pass the channel name, register name, and resolve-config.sh path (`${CLAUDE_PLUGIN_ROOT}/skills/bat-kol/scripts/resolve-config.sh`)
   - If config resolution fails, show the error and instruct user to run `/train-voice`

5. Select the drafter agent based on channel:
   - `slack` → `bat-kol:slack-drafter`
   - `email` → `bat-kol:email-drafter`
   - `bluesky` → `bat-kol:bluesky-drafter`
   - `github` → `bat-kol:github-drafter`
   - anything else → `bat-kol:generic-drafter`

6. Spawn the drafter agent with:
   - The assembled voice profile from config-resolver
   - The topic (or session summary if no topic provided)
   - For GitHub: also detect content type from context (pr, issue, commit, review, comment)

7. Present the draft to the user via AskUserQuestion with options:
   - "Copy to clipboard" — run `echo {draft} | pbcopy` via Bash
   - "Edit further" — ask what to change, then re-draft
   - "Regenerate" — spawn the drafter again with the same inputs

## Examples

```
/write-for email requesting time off next week
```

Drafts an email about requesting time off.

```
/write-for slack
```

Summarizes the current session context as a Slack message.

```
/write-for bluesky thoughts on the new API design
```

Drafts a Bluesky post (or thread) about the API design.

## Important Rules

- The channel argument is required — prompt if missing
- Session summary mode (no topic) should capture the key decisions and outcomes from the conversation
- Always present drafts through AskUserQuestion, not as plain text
