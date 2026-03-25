---
name: train-voice
description: Guided voice training for bat-kol registers, channels, and writing style
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, TaskCreate, TaskUpdate, TaskList, mcp__claude_ai_Slack__slack_search_public_and_private, mcp__claude_ai_Slack__slack_read_channel, mcp__claude_ai_Glean__search, mcp__claude_ai_Glean__gmail_search
argument-hint: [--register <name> | --channel <name> | --style]
---

Train or update bat-kol voice profiles through a guided interview with optional sample analysis and API scraping.

## Critical Rules

- ALL user interactions MUST use AskUserQuestion — never ask questions in plain text output
- Do NOT spawn an agent for the interview — handle all AskUserQuestion calls directly in this command
- Do NOT delegate scraping to agents — MCP tools (Slack, Glean) are only available in the main context, not in subagents. ALL scraping must happen in this command.
- Only spawn the `bat-kol:voice-trainer` agent AFTER collecting all interview answers AND completing all scraping. Pass file paths to scraped data, not the data itself.
- Use TaskCreate at the start to track each training step — this survives context compaction

## Step 1: Parse Arguments, Determine Scope, and Create Tasks

Parse `$ARGUMENTS`:

- `--register <name>`: scope = register, name = provided value
- `--channel <name>`: scope = channel, name = provided value
- `--style`: scope = style
- No arguments: use AskUserQuestion immediately:

If no arguments, use AskUserQuestion with these options:

- "Train a voice register" — tone, formality, vocabulary for a specific register
- "Train a channel" — format rules and conventions for a specific channel
- "Set up global writing style" — choose and configure a writing style framework
- "Full setup (style + registers + channels)" — complete initial voice training

After determining scope, create Tasks to track progress:

For full setup:

- TaskCreate: "Complete style interview"
- TaskCreate: "Complete register interviews (professional, internal, personal, social)"
- TaskCreate: "Complete channel setup (slack, email, bluesky, github)"
- TaskCreate: "Scrape communication history" (if opted in)
- TaskCreate: "Write config files via voice-trainer agent"

For single scope: create one task for the interview, one for scraping (if applicable), and one for writing.

## Step 2: Run the Interview (inline — do NOT delegate)

Based on the scope, follow the appropriate interview section below. Each section uses AskUserQuestion for EVERY question. Mark each task as in_progress when starting it, completed when done.

### Style Interview

Read `${CLAUDE_PLUGIN_ROOT}/skills/bat-kol/references/style-frameworks.md` for context.

**Q1 — Writing framework**: AskUserQuestion with options:

- "Strunk & White — clarity, brevity, active voice, no unnecessary words"
- "Stanley Fish — sentence-level craft, subordination, periodic sentences"
- "George Orwell — plain English, concrete imagery, no pretentious diction"
- "Plain Language — accessibility, short sentences, common words"

**Q2 — Sentence structure**: AskUserQuestion with options:

- "Short and direct — punchy, declarative"
- "Varied — mix of short and long, rhythm matters"
- "Complex — subordinate clauses, periodic structure"

**Q3 — Word choice**: AskUserQuestion with options:

- "Plain — everyday words, no jargon unless necessary"
- "Technical — domain terms are fine, precision over simplicity"
- "Elevated — literary vocabulary, deliberate word selection"

Record all answers.

### Register Interview

If no register name was provided, use AskUserQuestion:

- "Professional" — client-facing, careful, polished
- "Internal" — team-facing, direct, efficient
- "Personal" — informal, authentic, relaxed
- "Social" — public-facing, conversational, engaging

Then for the selected register, ask each question via AskUserQuestion:

**Q1 — Tone**: AskUserQuestion:

- "Formal and measured"
- "Warm but professional"
- "Direct and casual"
- "Playful and conversational"

**Q2 — Formality**: AskUserQuestion:

- "1 — Very casual (hey team, quick thing)"
- "2 — Relaxed (Hi all, wanted to share)"
- "3 — Balanced (Hello, I'd like to discuss)"
- "4 — Formal (Dear colleague, I am writing to)"

**Q3 — Sentence style**: AskUserQuestion:

- "Short and punchy — get to the point"
- "Flowing — connective, builds momentum"
- "Mixed — varies by emphasis"

**Q4 — Personality markers**: AskUserQuestion (multiSelect: true):

- "Emoji occasionally"
- "Exclamation points for emphasis"
- "Humor when appropriate"
- "Hedging language (I think, perhaps, might)"

**Q5 — Writing samples**: AskUserQuestion:

- "Yes, I have writing samples to analyze"
- "No, the interview is enough"

If yes: ask for file paths via AskUserQuestion.

**Q6 — API scraping**: AskUserQuestion (multiSelect: true):

- "Scrape my GitHub history (PRs, issues, comments via gh CLI)"
- "Scrape my Bluesky posts (public API)"
- "Scrape my Slack messages (via Slack MCP)"
- "Scrape my email history (via Glean)"
- "Skip API scraping"

If GitHub selected, ask for their GitHub username via AskUserQuestion (or detect with `gh api /user --jq '.login'`).
If Bluesky selected, ask for their handle via AskUserQuestion.
If Slack selected, ask which channels to scrape via AskUserQuestion.

Record all answers.

### Channel Interview

If no channel name was provided, use AskUserQuestion:

- "Slack"
- "Email"
- "Bluesky"
- "GitHub"

Read `${CLAUDE_PLUGIN_ROOT}/skills/bat-kol/references/channel-formats.md` for built-in defaults.

**Q1 — Default register**: AskUserQuestion:

- "Professional"
- "Internal"
- "Personal"
- "Social"

**Q2 — Any customizations?**: AskUserQuestion:

- "Use defaults for this channel"
- "Customize format rules" — follow up with specific questions about length, markup, structure

Record all answers.

### Full Setup

Run in this order:

1. Style Interview
2. Register Interview for each of: professional, internal, personal, social. Between registers, use AskUserQuestion: "Continue to {next register}?" with "Yes, continue" and "Stop here for now".
3. Channel setup for each of: slack, email, bluesky, github. Between channels, use AskUserQuestion: "Continue to {next channel}?" with "Yes, continue" and "Stop here for now".

Mark each interview task as completed as you finish it.

## Step 3: Scrape Communication History (inline — do NOT delegate)

This step MUST run in the command context because MCP tools are not available to subagents. Mark the scraping task as in_progress.

First, resolve the config root:

```bash
CONFIG_ROOT="${XDG_CONFIG_HOME:-$HOME/.config}/bat-kol"
mkdir -p "$CONFIG_ROOT/samples"
```

For each scraping source the user opted into, run the appropriate scraper. Track which sources succeeded and which failed.

### GitHub — run the script

Run the scraping script via Bash and check its output:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/scrape-github.sh "$CONFIG_ROOT/samples/github-raw.md"
```

The script handles pagination, error handling, and writes directly to the output file. Check the exit code — if non-zero, report the error but continue with other sources.

### Bluesky — run the script

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/scrape-bluesky.sh "{handle}" "$CONFIG_ROOT/samples/bluesky-raw.md"
```

Replace `{handle}` with the user's handle from the interview.

### Slack — use MCP tools directly (main context only)

Use the Slack MCP tools directly — they are only available in this command context, NOT in subagents:

1. Use `mcp__claude_ai_Slack__slack_search_public_and_private` to search for messages from the user in the channels they specified
2. For each channel, use `mcp__claude_ai_Slack__slack_read_channel` to fetch message history

Collect all messages authored by the user. Write the results to `$CONFIG_ROOT/samples/slack-raw.md` using the Write tool.

If Slack MCP tools are not available (not in `allowed-tools` or not configured), inform the user and suggest exporting Slack messages as text files to use as writing samples instead.

### Email — use Glean MCP directly (main context only)

Use `mcp__claude_ai_Glean__gmail_search` to search for the user's recent sent emails. Write results to `$CONFIG_ROOT/samples/email-raw.md` using the Write tool.

If Glean MCP tools are not available, inform the user and suggest exporting emails as text files to use as writing samples instead.

### After scraping

Report what succeeded and what failed. List each output file written and its size. Mark the scraping task as completed with a note of the results.

## Step 4: Write Config Files

Mark the writing task as in_progress.

Spawn the `bat-kol:voice-trainer` agent with:

- The scope and name
- Every answer from the interview (as structured text)
- The resolve-config.sh path: `${CLAUDE_PLUGIN_ROOT}/skills/bat-kol/scripts/resolve-config.sh`
- If sample files were provided: their paths
- Paths to ALL scraped raw data files in `{config_root}/samples/` (the agent reads these for analysis)
- Explicit instruction: "The interview and scraping are complete. All raw scraped data is in the files listed. Analyze the raw data files, then write config files incorporating both interview answers and scraping analysis. Do NOT attempt to scrape APIs yourself — all data is already in files."

Wait for the agent to complete. Mark the writing task as completed.

## Step 5: Confirm

Summarize what was created or updated — list each file path written. Include scraping stats (how many items per source). Remind the user they can run `/retrain-voice` later to upgrade existing configs with new features without redoing the full interview.
