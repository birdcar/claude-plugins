---
name: train-voice
description: Guided voice training for bat-kol registers, channels, and writing style
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion
argument-hint: [--register <name> | --channel <name> | --style]
---

Train or update bat-kol voice profiles through a guided interview with optional sample analysis and API scraping.

## Process

1. Parse arguments from `$ARGUMENTS`:
   - `--register <name>`: scope = register, name = provided value
   - `--channel <name>`: scope = channel, name = provided value
   - `--style`: scope = style
   - No arguments: proceed to step 2

2. **If no arguments were provided**, use AskUserQuestion to ask the user what to train. This MUST happen in the command context, not in the agent — present these options:
   - "Train a voice register" — tone, formality, vocabulary for a specific register
   - "Train a channel" — format rules and conventions for a specific channel
   - "Set up global writing style" — choose and configure a writing style framework
   - "Full setup (style + all registers)" — complete initial voice training

3. **If the user chose register or channel training without specifying a name**, use AskUserQuestion again to ask which one. For registers, offer: professional, internal, personal, social, or custom. For channels, offer the built-in list (slack, email, bluesky, github) plus "Add a new custom channel".

4. Spawn the `bat-kol:voice-trainer` agent with:
   - The resolved training scope (register, channel, style, or full)
   - The specific name (if register or channel)
   - The resolve-config.sh path: `${CLAUDE_PLUGIN_ROOT}/skills/bat-kol/scripts/resolve-config.sh`
   - Explicit instruction: "The user has already chosen what to train. Do NOT re-ask for training scope — proceed directly with the interview for the specified scope."

5. The voice-trainer agent handles the interview, sample analysis, and API scraping — wait for it to complete.

6. Summarize what was created or updated for the user.

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
