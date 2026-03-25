---
name: train-voice
description: Guided voice training for bat-kol registers, channels, and writing style
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion
argument-hint: [--register <name> | --channel <name> | --style]
---

Train or update bat-kol voice profiles through a guided interview with optional sample analysis and API scraping.

## Process

1. Parse arguments from `$ARGUMENTS`:
   - `--register <name>`: train a specific register
   - `--channel <name>`: train a specific channel
   - `--style`: train the global writing style
   - No arguments: ask what to train via AskUserQuestion

2. Spawn the `bat-kol:voice-trainer` agent with:
   - The training scope (register, channel, style, or all)
   - The specific name if provided
   - The resolve-config.sh path: `${CLAUDE_SKILL_DIR}/scripts/resolve-config.sh`
   - Note: `${CLAUDE_SKILL_DIR}` here refers to `${CLAUDE_PLUGIN_ROOT}/skills/bat-kol`

3. The voice-trainer agent handles the entire interactive flow — wait for it to complete.

4. Summarize what was created or updated for the user.

## Examples

```
/train-voice --register professional
```

Trains the professional register through guided interview.

```
/train-voice --style
```

Sets up or updates the global writing style framework.

```
/train-voice
```

Asks what to train, then proceeds with the full flow.

## Important Rules

- All voice config files are written to the user's config directory, not to the repo
- Do not overwrite existing profiles without user confirmation
- The voice-trainer agent handles all AskUserQuestion interactions during training
