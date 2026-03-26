# bat-kol

Drafts messages in your authentic voice for Slack, email, Bluesky, GitHub, or any custom channel.

bat-kol (בת קול) means "daughter of a voice" in Hebrew — a divine echo, the authentic thing reflected back. The practical problem it solves: AI writing assistants produce generic text that sounds like no one. You end up editing more than you would have starting from scratch. This one learns your voice, your registers, your style preferences, and applies all of that based on where you're writing.

## Installation

```bash
claude plugin install bat-kol@birdcar-plugins
```

After installing, run `/train-voice` to set up your first voice profile. Without a profile, bat-kol will tell you to do this rather than guessing your voice.

## Quick start

Once your voice is trained, describe what you want to say naturally:

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

bat-kol detects the channel from your request, loads your voice profile, drafts the message, and presents it via an interactive prompt where you can copy to clipboard, edit further, or regenerate.

## How it works

There are three layers that combine to produce a draft:

**Writing style** is the base layer. A global framework (Strunk & White, George Orwell, Plain Language, etc.) that sets your baseline approach to sentences and structure. Most registers inherit this unless you override.

**Registers** are voice and tone rules. bat-kol ships with four: `professional` (client-facing, careful), `internal` (team-facing, direct), `personal` (informal, yourself), and `social` (public, conversational). Each channel has a sensible default — email defaults to professional, Slack to internal, Bluesky to social — but you can override per message. Channel and register are independent dimensions: channel controls formatting, register controls voice.

**Channels** are format rules. How long, what markup, what structure. Slack gets mrkdwn. Email gets a subject line, greeting, and closing. Bluesky respects the 300-character limit and splits into threads when needed. GitHub produces GFM with the right conventions per content type (PR, issue, commit message, review comment).

When you ask for a draft, bat-kol resolves your config, assembles the composite voice (style + register + channel format), and routes to the appropriate channel drafter agent.

## Config

Config lives outside the repo at `~/.config/bat-kol/` (or `$XDG_CONFIG_HOME/bat-kol/`):

```
~/.config/bat-kol/
├── style.md
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
    └── discord.md       # Custom channels you add
```

All files are human-readable markdown. Edit them directly if you want to tweak something without running through the full training flow.

### Project overrides

If a repo needs a different voice — say, an open source project where you write more formally than you would internally — create a `.bat-kol/` directory at the repo root with the files you want to override:

```
my-project/
└── .bat-kol/
    └── registers/
        └── professional.md
```

bat-kol walks up from your current directory looking for `.bat-kol/`, then falls back to the global config. You can also set `$BAT_KOL_CONFIG` to point directly to a config root.

## Commands

### `/train-voice`

Sets up or updates your voice profiles through a guided interview, optional sample analysis, and API scraping. Without arguments it asks what you want to train. With flags it goes directly to that scope:

```
/train-voice --register professional
/train-voice --style
/train-voice --channel slack
```

Scraping sources: GitHub (via `gh` CLI), Bluesky (public API), Slack (via Slack MCP), email (via Glean), LinkedIn (Glean or data export), Gong call transcripts (Glean), Granola meeting notes (Granola MCP), or any local transcript file (.txt, .srt, .vtt).

### `/retrain-voice`

Incremental upgrade for existing voice configs — fills in missing sections, re-analyzes sources, and applies schema updates without redoing the full interview. Useful after bat-kol adds new config sections or if your writing style has evolved.

```
/retrain-voice --register internal
/retrain-voice --all
```

### `/write-for <channel> [topic]`

Explicit drafting command. The channel is required. Topic is optional — if omitted, bat-kol summarizes the current session context for that channel.

```
/write-for email requesting time off next week
/write-for slack                   # summarizes session
/write-for github                  # drafts PR description from git context
```

### `/add-channel <name>`

Creates a new custom channel definition. Walks you through format rules (markup, length limits, structural conventions), default register, and optionally a delivery mechanism (shell script, CLI command, MCP tool, or clipboard + open app).

```
/add-channel discord
/add-channel notion
```

## What it doesn't do

bat-kol drafts. It does not send by default — you get the draft and decide what to do with it. Delivery is an opt-in feature you configure per channel via `/add-channel`. Even when delivery is configured, it always confirms before sending.

It won't write customer support replies, monitor your inbox, or clone anyone else's voice.
