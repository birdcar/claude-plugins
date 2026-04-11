---
name: daily
description: View and update today's daily thread. Shows Big 3 status, ritual progress, and recent activity. Use to check daily priorities, log an activity, or update the thread.
disable-model-invocation: true
allowed-tools: Bash
---

# /focus:daily

View today's daily thread and optionally update it.

## Configuration

Before running any `gh` commands, resolve the target repository and timezone:

```bash
CONFIG_JSON=$(${CLAUDE_PLUGIN_ROOT}/scripts/resolve-config.sh)
```

If this fails, tell the user: "Focus is not configured. Run `/focus:init` to set up, or create `~/.config/focus/config.json` with `{"repo": "owner/repo", "timezone": "America/Chicago"}`."

Extract values:

```bash
REPO=$(echo "$CONFIG_JSON" | jq -r '.repo')
TZ_NAME=$(echo "$CONFIG_JSON" | jq -r '.timezone')
```

**All `gh` commands MUST use `-R $REPO`** instead of a hardcoded repo. All timezone-sensitive operations MUST use `TZ="$TZ_NAME"` instead of a hardcoded timezone.

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

3. If `$ARGUMENTS` contains "log" or any message text: post it as a comment:

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
