---
name: train-voice
description: Guided voice training for bat-kol registers, channels, and writing style
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, TaskCreate, TaskUpdate, TaskList
argument-hint: [--register <name> | --channel <name> | --style]
---

Train or update bat-kol voice profiles through a guided interview with optional sample analysis and API scraping.

## Critical Rules

- ALL user interactions MUST use AskUserQuestion — never ask questions in plain text output
- Do NOT spawn an agent for the interview — handle all AskUserQuestion calls directly in this command
- Only spawn the `bat-kol:voice-trainer` agent AFTER collecting all interview answers, to write config files and optionally scrape APIs
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
- TaskCreate: "Write config files via voice-trainer agent"

For single scope: create one task for the interview and one for writing.

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
- "Scrape my Slack messages (if MCP available)"
- "Skip API scraping"

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

## Step 3: Write Config Files

Mark the writing task as in_progress.

Spawn the `bat-kol:voice-trainer` agent with ALL collected interview answers. Pass:

- The scope and name
- Every answer from the interview (as structured text)
- The resolve-config.sh path: `${CLAUDE_PLUGIN_ROOT}/skills/bat-kol/scripts/resolve-config.sh`
- If sample files were provided: their paths
- If API scraping was opted in: which sources (and any handles/usernames provided)
- Explicit instruction: "The interview is complete. Write the config files based on the provided answers. If sample analysis or API scraping was requested, do that first and incorporate findings. Write scraped data to files in the samples/ directory."

Wait for the agent to complete. Mark the writing task as completed.

## Step 4: Confirm

Summarize what was created or updated — list each file path written. Remind the user they can run `/retrain-voice` later to upgrade existing configs with new features without redoing the full interview.
