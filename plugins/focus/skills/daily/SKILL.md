---
name: daily
description: View today's daily thread — Big 3 status, ritual progress, and recent activity. Use when the user asks to "see my daily thread", "check today's status", "log an activity", or "what's on my thread today". Do NOT use when the user wants to choose or plan today's Big 3 — use focus:plan for that.
disable-model-invocation: true
allowed-tools: Bash
---

# /focus:daily

View today's daily thread and optionally update it.

## Configuration

Follow the setup steps in `${CLAUDE_PLUGIN_ROOT}/shared/config-preamble.md` before running any `gh` commands.

## What to do

1. Find today's daily thread:

```bash
TODAY=$(TZ="$TZ_NAME" date +%Y-%m-%d)
gh issue list -R $REPO \
  --label "type.daily-thread" \
  --state open \
  --search "\"Daily Thread — $TODAY\" in:title" \
  --json number,title,body,url \
  --jq '.[0]'
```

2. Display in this order:
   - Thread title and URL
   - Big 3 items with checkbox status (checked = done, unchecked = pending)
   - Morning Ritual completion percentage (count checked boxes / total boxes)
   - Recent comments (last 3–5, newest first):

```bash
gh issue view <NUMBER> -R $REPO \
  --json comments \
  --jq '[.comments | sort_by(.createdAt) | reverse | .[:5][] | {created: .createdAt, body: .body}]'
```

3. If `$ARGUMENTS` is non-empty and is not "refresh": treat it as a log entry and post it as a comment:

```bash
gh issue comment <NUMBER> -R $REPO --body "<message>"
```

4. If `$ARGUMENTS` is "refresh": not applicable — data is fetched live via gh CLI.
5. If no thread is found for today: display "No daily thread found for today. The GitHub Action creates it overnight."

## Daily Thread Structure

The daily thread is a GitHub issue with these sections in the body:

- **## Big 3** — Three checkbox items. Placeholder format when unset: `- [ ] _[to be selected]_`. When set by `/focus:plan`: `- [ ] Task title`. Checked means completed today.
- **## Morning Ritual** — Checklist items for energy check, top blocker, and Big 3 confirmation. Track completion percentage from these checkboxes.
- **## Goal Context** — Active quarterly goals and their open tasks, auto-populated when the thread is created. Read-only reference section.

The daily thread title uses the Unicode em dash U+2014 (—), not a hyphen (-). Format: `Daily Thread — YYYY-MM-DD`.

Comments on the thread are the timestamped activity log for the day.
