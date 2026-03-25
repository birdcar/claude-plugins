---
name: add-channel
description: Add a new custom channel definition to bat-kol
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion
argument-hint: <channel-name>
---

Create a new channel configuration for bat-kol with format rules, conventions, and a default register.

## Process

1. Parse `$0` as the channel name. If missing, use AskUserQuestion to ask for it.

2. Run `bash ${CLAUDE_PLUGIN_ROOT}/skills/bat-kol/scripts/resolve-config.sh` to find the config root. If no config exists, instruct the user to run `/train-voice` first to set up the base config directory.

3. Check if a channel file already exists at `{config_root}/channels/{name}.md`. If it does, use AskUserQuestion to confirm overwrite.

4. Use AskUserQuestion to gather channel details:
   - **Markup format**: plain text, markdown, mrkdwn, HTML, or other
   - **Character limit**: hard limit, soft recommendation, or none
   - **Structural conventions**: headers, greeting/closing, thread support, etc.
   - **Default register**: which register to use by default for this channel

5. Write the channel config file to `{config_root}/channels/{name}.md` with the gathered rules.

6. Confirm creation and suggest testing with `/write-for {name} test message`.

## Examples

```
/add-channel discord
```

Walks through Discord formatting rules and creates a channel config.

```
/add-channel linkedin
```

Sets up LinkedIn post formatting and conventions.

## Important Rules

- Write channel files only to the user's config directory, not the repo
- Create parent directories if needed (`mkdir -p`)
- Do not overwrite existing channels without confirmation
- Channel config files are format-focused (not voice-focused), so keep them concise — under 50 lines of format rules. Voice depth lives in register files, not channel files.
