---
name: bat-kol
description: >-
  Drafts messages in the user's authentic voice for communication channels
  (Slack, email, Bluesky, GitHub, custom). Combines writing style frameworks,
  voice registers, and channel format rules via cascading config resolution.
  Use when the user asks to "draft an email", "respond in slack", "write a
  bluesky post", "draft a PR description", "compose a message for",
  "summarize this for", "send a message", "reply to this", or "write a
  LinkedIn post" for a communication channel.
  Do NOT use for general writing tasks (code, documentation, READMEs),
  customer support replies, git commit messages, or real-time monitoring.
---

# bat-kol

Drafts messages in the user's authentic voice for any communication channel by combining a global writing style, voice registers (tone/formality), and channel format rules (markup/constraints).

## Critical Rules

- Use AskUserQuestion for all user interactions — never ask questions in plain text because users cannot respond structurally
- Present every draft via AskUserQuestion with options: "Copy to clipboard", "Edit further", "Regenerate"
- Never send or post messages on behalf of the user — bat-kol drafts, the user delivers
- Never fabricate voice profile content — use only what exists in the user's config files
- Never read config files directly with the Read tool — run resolve-config.sh via Bash to get paths, then read the resolved files
- Never store PII, credentials, or machine-specific paths in plugin files — voice config lives in `${XDG_CONFIG_HOME:-$HOME/.config}/bat-kol/`
- If no voice config exists, instruct the user to run `/train-voice` to set up their profile rather than guessing a voice
- Channel and register are independent dimensions — channel controls formatting, register controls voice. Do not conflate them.
- All drafter agents inherit shared instructions from `${CLAUDE_PLUGIN_ROOT}/shared/drafter-base.md`

## Workflow

### Step 1: Detect Channel and Register

Parse the user's request to identify:

- **Channel**: the target platform (slack, email, bluesky, github, or a custom name)
  - Look for explicit mentions: "draft a slack message", "write an email", "bluesky post"
  - Look for implicit signals: "respond to this PR" → github, "send this to the team" → slack
  - If ambiguous, ask via AskUserQuestion with the available channels as options

- **Register**: the voice register to use (professional, internal, personal, social)
  - If the user specifies a register explicitly ("write a casual email"), use it
  - Otherwise, use the channel's default: slack→internal, email→professional, bluesky→social, github→professional
  - For custom channels, the channel config specifies its default register

- **Content type** (for GitHub): detect whether this is a PR, issue, commit message, review comment, or general comment from context

### Step 2: Resolve Voice Config

Spawn the `bat-kol:config-resolver` agent with:

- Channel name from Step 1
- Register name from Step 1
- Resolve script path: `${CLAUDE_SKILL_DIR}/scripts/resolve-config.sh`

The config-resolver runs the cascading resolution script and reads the resolved config files. It returns an assembled voice profile with global style, register rules, and channel format rules.

If config resolution fails (no config found), present the user with setup instructions:

- Run `/train-voice` to set up voice profiles from scratch
- Run `/retrain-voice` to upgrade existing older configs to the current schema
- Or create config manually at `~/.config/bat-kol/`

See `${CLAUDE_SKILL_DIR}/references/voice-resolution.md` for the full resolution algorithm.

### Step 3: Prepare Content Prompt

Determine what to draft:

- **Explicit topic**: the user said what to write about → use their description as the content prompt
- **Session summary**: the user wants to share session context ("summarize this for slack") → distill the current conversation into key decisions, outcomes, and action items as the content prompt
- **Reply context**: the user is replying to something → include the original message or context

For GitHub content, gather additional context:

- Run `git diff --stat` or `git log --oneline -5` if drafting a PR or commit message
- Include relevant issue numbers or PR context if mentioned

### Step 4: Draft

Select and spawn the appropriate drafter agent:

| Channel       | Agent                     | Notes                                              |
| ------------- | ------------------------- | -------------------------------------------------- |
| `slack`       | `bat-kol:slack-drafter`   | mrkdwn formatting                                  |
| `email`       | `bat-kol:email-drafter`   | Subject line + body                                |
| `bluesky`     | `bat-kol:bluesky-drafter` | 300-char limit, thread splitting                   |
| `github`      | `bat-kol:github-drafter`  | Pass content type (pr/issue/commit/review/comment) |
| anything else | `bat-kol:generic-drafter` | Adapts to custom channel config                    |

Pass to the drafter:

- The assembled voice profile from Step 2
- The content prompt from Step 3
- Channel-specific metadata (content type for GitHub, thread context for Slack, etc.)

### Step 5: Present and Iterate

Check whether the channel config has a `## Delivery` section with a configured method. Build the AskUserQuestion options accordingly.

**Base options (always present):**

- **"Copy to clipboard"**: Write the draft to a temp file via Bash, then `pbcopy < "$TMPFILE" && rm "$TMPFILE"`.
- **"Edit further"**: Ask what to change (tone, length, content, format), then re-spawn the drafter with revision instructions appended to the prompt
- **"Regenerate"**: Re-spawn the drafter with the same inputs for a fresh take

**Delivery option (only if channel has delivery configured):**

- **"Send directly"**: Execute the delivery command from the channel config.
  1. Write the draft to a temp file
  2. If `confirmation: always`, show the full draft via AskUserQuestion first: "About to send this via {method}. Confirm?" with "Send" / "Edit first" / "Cancel"
  3. Replace `{draft}` in the command template with the temp file path
  4. For `method: script` or `method: cli`: run via Bash
  5. For `method: mcp`: call the specified MCP tool with the draft as the message parameter
  6. For `method: clipboard-and-open`: run `pbcopy < "$TMPFILE"` then the open command
  7. Report success or failure. Clean up the temp file.

Continue the edit/regenerate loop until the user is satisfied, copies, or sends.

## Channel Format Reference

See `${CLAUDE_SKILL_DIR}/references/channel-formats.md` for default format rules per channel:

- Slack: mrkdwn syntax, length guidelines, thread conventions
- Email: structure, greeting/closing, subject line rules
- Bluesky: 300-char limit, thread splitting, hashtag conventions
- GitHub: GFM, content type conventions (PR, issue, commit, review)
- Generic: plain text fallback for custom channels

## Writing Style Reference

See `${CLAUDE_SKILL_DIR}/references/style-frameworks.md` for known writing style frameworks:

- Strunk & White, Stanley Fish, George Orwell, Plain Language
- How frameworks integrate as the base layer of voice assembly

## Examples

### Example 1: Slack Update

**Input**: "draft a slack message about the API migration being done"
**Process**: channel=slack, register=internal (default), resolve config, spawn slack-drafter
**Output**: A mrkdwn-formatted Slack message in the user's internal voice announcing the migration completion, presented via AskUserQuestion with copy/edit/regenerate options.

### Example 2: Professional Email

**Input**: "write an email to the client about the project timeline change"
**Process**: channel=email, register=professional (default), resolve config, spawn email-drafter
**Output**: A structured email with subject line, greeting, body, and closing in the user's professional register, presented via AskUserQuestion.

### Example 3: Bluesky Thread

**Input**: "draft a bluesky post about what I learned building this feature"
**Process**: channel=bluesky, register=social (default), resolve config, spawn bluesky-drafter
**Output**: One or more 300-char posts (thread if needed) in the user's social voice, presented via AskUserQuestion.

### Example 4: Session Summary for Slack

**Input**: "summarize this for slack"
**Process**: channel=slack, register=internal, no topic → summarize session, resolve config, spawn slack-drafter with session summary
**Output**: A concise Slack message capturing the key decisions and outcomes from the conversation.

### Example 5: GitHub PR Description

**Input**: "draft a PR description for these changes"
**Process**: channel=github, content_type=pr, register=professional, gather git diff context, resolve config, spawn github-drafter
**Output**: A structured PR description with title, summary, and testing notes in GFM.
