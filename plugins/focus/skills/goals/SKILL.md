---
name: goals
description: View the goal cascade from annual milestones down to active tasks. Use when the user asks to "show my goals", "view goals", "list goals", "what are my priorities", "show my tasks", or "trace a task". Supports "tasks" argument to show only tasks grouped by goal. Do NOT use for creating new goals — use focus:goal for that.
disable-model-invocation: true
allowed-tools: Bash
argument-hint: [issue-number|tasks]
---

# /focus:goals

View the full goal cascade or trace a specific issue.

## Configuration

Follow the setup steps in `${CLAUDE_PLUGIN_ROOT}/shared/config-preamble.md` before running any `gh` commands.

## What to do

1. Get annual milestones:

```bash
gh api /repos/$REPO/milestones --jq '.[] | select(.state == "open") | {number, title, due_on, open_issues, closed_issues}'
```

2. Get active quarterly goals:

```bash
gh issue list -R $REPO \
  --label "type.goal,status.active" \
  --state open \
  --limit 20 \
  --json number,title,milestone,labels,updatedAt
```

3. For each active quarterly goal, get its open sub-issues (tasks):

```bash
gh api "/repos/$REPO/issues/<GOAL_NUMBER>/sub_issues" \
  --jq '.[] | {number, title, state, labels: [.labels[].name]}'
```

4. Display as a tree:

```
Annual Milestone: <milestone title>
  Quarterly Goal: #<number> <title>
    - [ ] #<number> <task title>
    - [x] #<number> <completed task title>
```

5. If `$ARGUMENTS` contains an issue number (e.g., "42" or "#42"): trace it upward through the cascade. First get the issue, then check for a parent:

```bash
gh issue view <NUMBER> -R $REPO --json number,title,milestone,labels
gh api "/repos/$REPO/issues/<NUMBER>/parent" --jq '{number, title, milestone: .milestone.title}' 2>/dev/null
```

Display: task -> quarterly goal -> annual milestone.

6. If `$ARGUMENTS` is "tasks": show only tasks — skip the milestones and quarterly goals layers, list all tasks grouped by their parent quarterly goal.

## Cascade Structure

GitHub Milestones = annual goals (due year-end, one per life area)
Issues with `type.goal` label = quarterly goals (assigned to a milestone)
Issues linked as sub-issues of a quarterly goal = tasks

Cascade level is structural, not a label. An issue's level is determined by:

- Milestone membership: issue assigned to a milestone = quarterly goal
- Sub-issue depth: sub-issue of a `type.goal` issue = task

Every goal and task issue has exactly one `type.*` label, one or more `domain.*` labels, and one `status.*` label.
