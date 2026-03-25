---
name: add-channel
description: Add a new custom channel definition to bat-kol
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion
argument-hint: <channel-name>
---

Create a new channel configuration for bat-kol with format rules, conventions, default register, and optional delivery mechanism.

## Process

1. Parse `$0` as the channel name. If missing, use AskUserQuestion to ask for it.

2. Run `bash ${CLAUDE_PLUGIN_ROOT}/skills/bat-kol/scripts/resolve-config.sh` to find the config root. If no config exists, instruct the user to run `/train-voice` first to set up the base config directory.

3. Check if a channel file already exists at `{config_root}/channels/{name}.md`. If it does, use AskUserQuestion to confirm overwrite or edit.

4. Use AskUserQuestion to gather channel format details:
   - **Markup format**: plain text, markdown, mrkdwn, HTML, or other
   - **Character limit**: hard limit, soft recommendation, or none
   - **Structural conventions**: headers, greeting/closing, thread support, etc.
   - **Default register**: which register to use by default for this channel

5. Use AskUserQuestion to ask about delivery:

   "Should bat-kol be able to send drafts directly to this channel?"
   - "No — draft only" — bat-kol copies to clipboard, user delivers manually (default)
   - "Yes, via a shell script or CLI command" — specify a command that accepts the draft
   - "Yes, via an MCP tool" — specify the MCP tool name and how to pass the draft
   - "Yes, via clipboard + open app" — copy to clipboard and open the target app

   If delivery is configured, ask about confirmation mode via AskUserQuestion:
   - "Always confirm before sending (Recommended)" — AskUserQuestion with the full draft before delivery
   - "Send immediately after approval" — the existing "Copy to clipboard" approval is sufficient
   - "Ask each time" — let me choose per draft whether to confirm

6. Write the channel config file to `{config_root}/channels/{name}.md` with format rules and delivery config.

7. Confirm creation and suggest testing with `/write-for {name} test message`.

## Channel Config Format

```markdown
# Channel — {name}

## Format Rules

- Markup: {format}
- Character limit: {limit or "none"}
- Structure: {conventions}

## Default Register

{register_name}

## Delivery (optional)

- method: {script | cli | mcp | clipboard-and-open | none}
- command: {the command to run — see below for template syntax}
- confirmation: {always | after-approval | ask}

### Command template syntax

The command string supports these placeholders:

- `{draft}` — replaced with a path to a temp file containing the draft
- `{channel}` — the channel name
- `{subject}` — the email subject line (email channel only)

Examples:

- Script: `bash ~/scripts/post-to-discord.sh {draft}`
- CLI: `gh pr create --body-file {draft}`
- MCP: `mcp__claude_ai_Slack__slack_post_message` (tool name — draft passed as message param)
- Clipboard + open: `pbcopy < {draft} && open -a "Discord"`
```

## Examples

```
/add-channel discord
```

Walks through Discord formatting rules, optionally sets up a webhook script for posting.

```
/add-channel linkedin
```

Sets up LinkedIn post formatting. Delivery = clipboard + open LinkedIn.

```
/add-channel notion
```

Sets up Notion page formatting with MCP delivery via Notion MCP tools.

## Important Rules

- Write channel files only to the user's config directory, not the repo
- Create parent directories if needed (`mkdir -p`)
- Do not overwrite existing channels without confirmation
- Channel config files are format-focused (not voice-focused) — keep format rules concise. Voice depth lives in register files.
- Delivery is always opt-in. Default is "no delivery" (draft only).
- Never auto-send without at least one user confirmation step.
