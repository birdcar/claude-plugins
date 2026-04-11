---
name: labels
description: Generate or regenerate the label taxonomy for the Home system. Creates .github/labels.yml with status, type, and domain labels, then syncs to GitHub. Can also scan existing issues to discover labels retroactively.
disable-model-invocation: true
allowed-tools: Bash
---

# /focus:labels

Generate the Focus label taxonomy and sync it to GitHub.

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

### Step 1: Check mode

- If `$ARGUMENTS` contains "retroactive" or "scan": go to Step 2 (retroactive mode)
- Otherwise: go to Step 3 (canonical mode)

### Step 2: Retroactive mode

Scan the repo for labels already in use that are NOT in the canonical taxonomy:

```bash
gh label list -R $REPO --json name --jq '.[].name' | sort
```

Also check existing issues for labels:

```bash
gh issue list -R $REPO --state all --limit 100 --json labels --jq '[.[].labels[].name] | unique | .[]'
```

Compare discovered labels against the canonical set (Step 3). For any label that exists on GitHub but isn't in the canonical taxonomy, report it:

"Found non-canonical labels: `custom.label1`, `custom.label2`. These exist on your repo but aren't part of the Focus taxonomy. They'll be preserved on GitHub but won't be included in labels.yml."

Then proceed to Step 3.

### Step 3: Generate labels.yml

Write `.github/labels.yml` to the configured repo with this exact content. First ensure the directory exists:

```bash
mkdir -p /path/to/repo/.github
```

Then write the file with the canonical taxonomy:

```yaml
labels:
  # Status labels
  - name: 'status.active'
    color: '0075ca'
    description: 'Actively being worked on'
  - name: 'status.blocked'
    color: 'd73a4a'
    description: 'Blocked by a dependency or decision'
  - name: 'status.waiting'
    color: 'e4e669'
    description: 'Waiting on external input before progressing'
  - name: 'status.stale'
    color: 'e4e669'
    description: 'No activity for 30+ days — needs triage'
  - name: 'status.done'
    color: '0e8a16'
    description: 'Completed and closed'
  - name: 'status.cancelled'
    color: 'cfd3d7'
    description: 'Cancelled — no longer relevant'

  # Type labels
  - name: 'type.goal'
    color: 'a2eeef'
    description: 'A goal at any level of the cascade (annual, quarterly, weekly)'
  - name: 'type.task'
    color: 'd4c5f9'
    description: 'An actionable task or sub-task'
  - name: 'type.daily-thread'
    color: 'f9d0c4'
    description: "Today's daily planning and activity thread"
  - name: 'type.review'
    color: 'fef2c0'
    description: 'A periodic review (weekly, quarterly)'
  - name: 'type.note'
    color: 'bfd4f2'
    description: 'A reference note or captured idea'

  # Domain labels (life areas — Full Focus planner system)
  - name: 'domain.body'
    color: 'bfd4f2'
    description: 'Life domain: physical health and fitness'
  - name: 'domain.mind'
    color: 'bfd4f2'
    description: 'Life domain: mental health, learning, and growth'
  - name: 'domain.spirit'
    color: 'bfd4f2'
    description: 'Life domain: spiritual practice and inner life'
  - name: 'domain.love'
    color: 'bfd4f2'
    description: 'Life domain: romantic relationship'
  - name: 'domain.family'
    color: 'bfd4f2'
    description: 'Life domain: family relationships'
  - name: 'domain.money'
    color: 'bfd4f2'
    description: 'Life domain: finances and financial goals'
  - name: 'domain.community'
    color: 'bfd4f2'
    description: 'Life domain: community involvement and service'
  - name: 'domain.hobbies'
    color: 'bfd4f2'
    description: 'Life domain: hobbies, recreation, and creative pursuits'
  - name: 'domain.work'
    color: 'bfd4f2'
    description: 'Life domain: career and professional work'
```

Note: If running from outside the configured repo, you'll need to clone or locate the repo first. The file path should be relative to the repo root: `.github/labels.yml`.

### Step 4: Sync labels to GitHub

For each label in the taxonomy, run:

```bash
gh label create "<name>" --color "<hex>" --description "<description>" --force -R $REPO
```

The `--force` flag makes this idempotent — it creates or updates as needed.

Sync all 20 labels. Report progress and any errors.

### Step 5: Report

Display:

```
Labels synced: 20 created/updated
File written: .github/labels.yml

Status (6): active, blocked, waiting, stale, done, cancelled
Type (5): goal, task, daily-thread, review, note
Domain (9): body, mind, spirit, love, family, money, community, hobbies, work
```

## Canonical taxonomy reference

**20 labels total** across 3 categories:

| Category   | Labels                                                            | Color                                   |
| ---------- | ----------------------------------------------------------------- | --------------------------------------- |
| Status (6) | active, blocked, waiting, stale, done, cancelled                  | Blue/Red/Yellow/Green/Gray              |
| Type (5)   | goal, task, daily-thread, review, note                            | Cyan/Purple/Peach/Pale yellow/Pale blue |
| Domain (9) | body, mind, spirit, love, family, money, community, hobbies, work | All pale blue                           |
