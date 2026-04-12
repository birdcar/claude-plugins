---
name: labels
description: Generate or regenerate the Focus label taxonomy — creates .github/labels.yml with status, type, and domain labels, then syncs to GitHub. Use when the user asks to "set up labels", "sync labels", "fix labels", or "scan labels". Use the "retroactive" or "scan" argument to discover labels already in use that aren't in the canonical taxonomy.
disable-model-invocation: true
allowed-tools: Bash
---

# /focus:labels

Generate the Focus label taxonomy and sync it to GitHub.

## Configuration

Follow the setup steps in `${CLAUDE_PLUGIN_ROOT}/shared/config-preamble.md` before running any `gh` commands.

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

### Step 3: Generate labels.yml (optional)

If the user has a local checkout of the repo at a known path, copy the canonical taxonomy file to it:

```bash
mkdir -p <repo-path>/.github
cp ${CLAUDE_SKILL_DIR}/references/taxonomy.yml <repo-path>/.github/labels.yml
```

If no local checkout is available, skip this step — the sync in Step 4 is the functional step. The YAML file is optional documentation.

### Step 4: Sync labels to GitHub

Use the shared sync script to create/update all 20 labels:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/sync-labels.sh $REPO
```

If the script exits non-zero, report which labels failed.

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
