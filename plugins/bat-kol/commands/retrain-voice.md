---
name: retrain-voice
description: Upgrade existing bat-kol voice configs without full retraining — fills in missing sections, re-analyzes sources, and applies schema updates
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, TaskCreate, TaskUpdate, TaskList
argument-hint: [--register <name> | --channel <name> | --style | --all]
---

Incrementally upgrade existing voice configs to match the current schema without redoing the full interview. Detects what's missing, re-reads existing sources, and fills gaps.

## Critical Rules

- ALL user interactions MUST use AskUserQuestion — never ask questions in plain text
- Do NOT redo the full interview — only ask about sections that are genuinely missing
- Preserve all existing config content — only add, never remove or overwrite existing rules
- Use TaskCreate to track each upgrade step

## Step 1: Resolve Config and Assess

Run `${CLAUDE_PLUGIN_ROOT}/skills/bat-kol/scripts/resolve-config.sh` to find the config root.

Parse `$ARGUMENTS`:

- `--register <name>`: upgrade a specific register
- `--channel <name>`: upgrade a specific channel
- `--style`: upgrade the global style
- `--all`: upgrade everything
- No arguments: use AskUserQuestion to ask what to upgrade, or offer "Scan all configs and upgrade everything that's outdated"

Read each config file in scope and check for these sections (the current schema):

| Section             | Required for registers | Required for channels | Required for style |
| ------------------- | ---------------------- | --------------------- | ------------------ |
| Overview            | yes                    | yes                   | yes                |
| Voice Rules         | yes                    | no                    | yes                |
| Sentence Patterns   | yes                    | no                    | yes                |
| Vocabulary Profile  | yes                    | no                    | no                 |
| Tone Markers        | yes                    | no                    | no                 |
| Openers and Closers | yes                    | no                    | no                 |
| Examples (5+)       | yes                    | yes                   | yes                |
| Sources             | yes                    | yes                   | yes                |
| Default Register    | no                     | yes                   | no                 |
| Format Rules        | no                     | yes                   | no                 |

The **Sources** section is critical — it records what interview answers, sample files, and API scraping built this config. Format:

```markdown
## Sources

- Interview: {date} — tone: warm but professional, formality: 2, ...
- Samples: ~/writing/emails/\*.txt (analyzed {date})
- GitHub: scraped {date}, {N} PRs, {N} issues, {N} comments
- Bluesky: scraped {date}, {N} posts
```

Create a Task for each file that needs upgrading.

## Step 2: Fill Missing Sections

For each config file missing sections:

1. **Check for existing analysis files** in `{config_root}/samples/` — if `github-analysis.md`, `bluesky-analysis.md`, etc. exist, read them to populate missing sections without re-scraping.

2. **Check for existing raw data** in `{config_root}/samples/` — if raw scraped data exists but no analysis file matches the current schema, re-analyze the raw data.

3. **If no sources exist at all** for a missing section, use AskUserQuestion with options:
   - "Re-scrape my APIs to fill this in" — specify which sources
   - "Let me provide writing samples"
   - "Ask me the missing questions" — targeted interview for just the missing sections
   - "Skip this section for now"

4. Use the Edit tool to add missing sections to the existing config file. Never overwrite existing content.

5. Add or update the Sources section to track what was used.

## Step 3: Schema Migration

If a config file uses an older format (e.g. has "Rules" instead of "Voice Rules", has "Patterns" instead of "Sentence Patterns"), rename the sections in-place using Edit. Preserve all content — just update the headers.

If a config file has fewer than 3 examples, generate additional examples based on the existing rules and patterns to reach at least 5.

## Step 4: Refresh Scraping (optional)

If existing sources are older than 30 days (check the Sources section dates), use AskUserQuestion:

- "Re-scrape to update with recent writing"
- "Keep existing data — my voice hasn't changed"

If re-scraping, spawn the `bat-kol:voice-trainer` agent with:

- Scope: the specific file being upgraded
- Instruction: "Re-scrape these sources and MERGE new findings with the existing config. Do not replace — append new patterns, update examples, and note the refresh date in Sources."

## Step 5: Report

Summarize what was upgraded:

- Files upgraded with their paths
- Sections added to each file
- Sources refreshed (if any)
- Files that were already up-to-date
