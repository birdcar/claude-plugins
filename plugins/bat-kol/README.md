# bat-kol

Drafts messages in your authentic voice for any communication channel — Slack, email, Bluesky, GitHub, or anything custom.

## The problem

I write in a lot of different places. A Slack message to my team reads differently than a client email, which reads differently than a Bluesky post or a PR description. That's fine and correct — but the context-switching overhead is real. Every time I sit down to write something, I'm rebuilding the mental model for that channel: what's the tone, what's the format, how long should this be, does this sound like me?

AI writing assistants make this worse, not better. They produce generic text that doesn't sound like anyone. You end up editing more than you would have if you'd just started from scratch.

bat-kol (בת קול) means "daughter of a voice" in Hebrew — a divine echo, the authentic thing reflected back. The idea is that it learns your voice, your registers, your style preferences, and then applies all of that automatically based on where you're writing. You describe what you want to say. It drafts in your voice for your channel.

## Installation

```bash
claude plugin install bat-kol
```

After installing, run `/train-voice` to set up your first voice profile. Without a profile, bat-kol will tell you to do this rather than guessing your voice.

## Quick start

Once your voice is trained, just write naturally:

```
draft a slack message about the deploy being done
```

```
write an email to the client about the timeline change
```

```
summarize this for slack
```

```
/write-for bluesky thoughts on the new API design
```

bat-kol detects the channel from your request, loads your voice profile, drafts the message, and presents it via an interactive prompt with options to copy to clipboard, edit further, or regenerate.

## How it works

There are three layers that combine to produce a draft:

**Writing style** is the base layer. A global framework like Strunk & White or Stanley Fish that sets your baseline approach to sentences, clarity, and structure. Any register can override this if needed, but most of the time one framework applies everywhere.

**Registers** are voice and tone rules. bat-kol ships with four: `professional` (client-facing, careful), `internal` (team-facing, direct), `personal` (informal, yourself), and `social` (public, conversational). Each channel has a sensible default — email defaults to professional, Slack to internal, Bluesky to social — but you can override per message.

**Channels** are format rules. How long, what markup, what structure. Slack gets mrkdwn. Email gets a subject line, greeting, and closing. Bluesky respects the 300-character limit and splits into threads when needed. GitHub produces GFM with the right conventions per content type (PR, issue, commit message, review comment).

When you ask for a draft, bat-kol resolves your config, assembles the composite voice (style + register + channel format), and routes to the appropriate channel drafter agent.

## Config resolution

Config lives outside the repo at `~/.config/bat-kol/` (or `$XDG_CONFIG_HOME/bat-kol/` if you set that). The directory looks like this:

```
~/.config/bat-kol/
├── style.md                 # Global writing style framework
├── registers/
│   ├── professional.md
│   ├── internal.md
│   ├── personal.md
│   └── social.md
└── channels/
    ├── slack.md
    ├── email.md
    ├── bluesky.md
    ├── github.md
    └── discord.md           # Custom channels you add
```

All these files are human-readable markdown. You can edit them directly if you want to tweak something without running through the full training flow.

### Project overrides

If a repo needs a different voice — say, an open source project where you write more formally than you would internally — create a `.bat-kol/` directory at the repo root with the files you want to override:

```
my-project/
└── .bat-kol/
    └── registers/
        └── professional.md  # Overrides global professional register for this repo
```

bat-kol walks up from your current directory looking for `.bat-kol/`, then falls back to the global config. Same resolution pattern as `.gitignore`. You can also set `$BAT_KOL_CONFIG` to point directly to a config root if you need something more explicit.

## Commands

### `/train-voice`

Sets up or updates your voice profiles. Without arguments it asks what you want to train. With flags it goes directly to that scope:

```
/train-voice --register professional
/train-voice --style
/train-voice --channel slack
```

The training flow combines a guided interview (what's your tone, how do you handle formality, what do you avoid), sample analysis (paste in writing you're happy with), and API scraping when available (`gh` CLI for GitHub history, Bluesky AT Protocol for post history, Slack MCP for message history).

### `/write-for <channel> [topic]`

Explicit drafting command. The channel is required. The topic is optional — if you leave it out, bat-kol summarizes the current session context for that channel instead.

```
/write-for email requesting time off next week
/write-for slack                   # summarizes session
/write-for github                  # drafts PR description from git context
```

### `/add-channel <name>`

Creates a new custom channel definition. Walks you through format rules (markup, length limits, structural conventions) and default register, then writes the channel config file. Use it to add Discord, LinkedIn, Notion, internal wikis, whatever you write in.

```
/add-channel discord
/add-channel linkedin
```

## What it doesn't do

bat-kol drafts. It does not send. No Slack posting, no email sending, no API calls to deliver content. You get the draft, you decide what to do with it. MCP-based sending may come later as an opt-in, but the core tool stays a drafter.

It also won't write customer support replies (that's a separate plugin), won't monitor your inbox, and won't clone anyone else's voice — only yours.
