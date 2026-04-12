---
name: plan
description: Runs the Big 3 planner — queries the goal cascade, scores tasks by priority criteria, proposes the 3 most important tasks for today, and updates the daily thread on approval. Use when the user asks to "plan my day", "pick my Big 3", "what should I work on today", or "set today's priorities". Do NOT use to view the current thread or log activity — use focus:daily for that.
disable-model-invocation: true
allowed-tools: Bash
---

# /focus:plan

Select today's Big 3 from the goal cascade and update the daily thread on confirmation.

## Configuration

Follow the setup steps in `${CLAUDE_PLUGIN_ROOT}/shared/config-preamble.md` before running any `gh` commands.

## Step 1: Gather data

1. Get all active quarterly goals with their milestone:

```bash
gh issue list -R $REPO \
  --label "type.goal,status.active" \
  --state open \
  --limit 20 \
  --json number,title,milestone,labels,updatedAt
```

2. For each quarterly goal, get its open sub-issues:

```bash
gh api "/repos/$REPO/issues/<GOAL_NUMBER>/sub_issues" \
  --jq '.[] | {number, title, state, labels: [.labels[].name], updatedAt: .updated_at}'
```

3. Get today's daily thread:

```bash
TODAY=$(TZ="$TZ_NAME" date +%Y-%m-%d)
gh issue list -R $REPO \
  --label "type.daily-thread" \
  --state open \
  --search "\"Daily Thread — $TODAY\" in:title" \
  --json number,title,body,url \
  --jq '.[0]'
```

## Step 2: Score quarterly goals

Score each quarterly goal on 3 criteria and sum for a composite score:

1. **Due date proximity** — check the goal's milestone due date:
   - Due within 30 days: +3
   - Due within 90 days: +2
   - Due within 180 days: +1
   - Due beyond 180 days or no due date: 0

2. **Open task count** — count open sub-issues from Step 1:
   - 1–3 open tasks: +2 (focused, actionable)
   - 4–7 open tasks: +1 (manageable)
   - 8+ open tasks: 0 (too many signals no focus)

3. **Recent activity** — check the goal issue's `updatedAt`:
   - Updated within last 7 days: +2
   - Updated within last 30 days: +1
   - Not updated in 30+ days: 0

Select the top 1–3 quarterly goals with the highest composite scores as focus goals for today.

## Step 3: Select tasks from focus goals

From the open tasks of the focus goals, select 3 most actionable tasks using these criteria (in priority order):

1. **Specificity** — tasks with clear, concrete actions score higher (e.g., "Sign up for 5K race by April 30" beats "Think about fitness goals")
2. **Unblocked** — prefer tasks without a `status.blocked` label
3. **Momentum** — prefer tasks updated more recently

One task per focus goal when possible. If a focus goal has no tasks, skip it.

## Step 4: Propose to user

Present the proposed Big 3 as a numbered list with goal context for each item:

```
Here are your proposed Big 3 for today:

1. #42 Sign up for 5K race by April 30 (from: Q2 Build running base — 20 miles/week)
2. #17 Schedule dentist appointment (from: Q1 Health maintenance)
3. #8 Finish chapter 3 reading (from: Q1 Mind — read 12 books)

Reply 'yes' to update the daily thread, or describe any adjustments.
```

Do NOT update the daily thread yet. Wait for the user to respond.

## Step 5: Update thread on approval

When the user approves (replies: yes, ok, looks good, approve, sounds right, or similar affirmative):

1. Get the current issue body:

```bash
gh issue view <THREAD_NUMBER> -R $REPO --json body --jq '.body'
```

2. Replace the Big 3 placeholder lines (`- [ ] _[to be selected]_`) with the selected tasks. Build the updated body by replacing those lines with `- [ ] <task title>`.

3. Update the issue:

```bash
gh issue edit <THREAD_NUMBER> -R $REPO --body "<updated body>"
```

4. Confirm: "Daily thread updated. Big 3 set for today."

If the user requests adjustments, apply them and re-present the updated proposal. Wait for confirmation again before updating.

## Edge cases

- If `$ARGUMENTS` is "dry-run": complete Steps 1–4 and show the proposal, but skip Step 5 entirely. Do not prompt for update.
- If today's daily thread is not found: complete Steps 1–4 and show the proposal. Note: "No daily thread found for today — the proposal is ready but the thread could not be updated."
- If no active goals exist: show "No active quarterly goals found. Add goals first with `/focus:goals`."
- If a focus goal has no open tasks: note this in the proposal and pull the next-highest-scoring goal.
- If the user approves the proposal but no daily thread was found in Step 1: respond "The proposal is ready but I couldn't find today's thread to update. The GitHub Action creates it overnight — try again after it runs, or create the thread manually with `/focus:daily`."
