---
name: goal
description: Create a quarterly goal with coaching. Walks through domain selection, outcome definition, measurable milestones, and initial task decomposition. Pushes back on vague or overambitious goals. Use at the start of a quarter or whenever adding a new goal.
disable-model-invocation: true
allowed-tools: Bash, AskUserQuestion
---

# /focus:goal

Create a quarterly goal with coaching, milestone assignment, and task decomposition.

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

## Step 1: Gather context

Fetch existing milestones and active goals to understand the current landscape:

```bash
gh api /repos/$REPO/milestones \
  --jq '.[] | select(.state == "open") | {number, title, due_on}'
```

```bash
gh issue list -R $REPO \
  --label "type.goal,status.active" \
  --state open \
  --json number,title,milestone,labels \
  --jq '.[] | {number, title, milestone: .milestone.title, domains: [.labels[].name | select(startswith("domain."))]}'
```

Count active goals per domain for the domain selection step.

**Overcommitment check**: If there are already 5+ active goals total, note this. If 8+, warn strongly: "You have N active goals. Adding another means spreading thinner. Consider closing or pausing a goal before adding a new one."

## Step 2: Select domain

If `$ARGUMENTS` specifies a domain (e.g., `/focus:goal body`), use it and skip to Step 3.

Otherwise, use AskUserQuestion to present the 9 life domains. Show how many active goals each domain already has:

```
"Which life domain is this goal for?"

Options:
- "Body (N active goals)" — Physical health and fitness
- "Mind (N active goals)" — Mental health, learning, growth
- "Spirit (N active goals)" — Spiritual practice and inner life
- "Love (N active goals)" — Romantic relationship
- "Family (N active goals)" — Family relationships
- "Money (N active goals)" — Finances and financial goals
- "Community (N active goals)" — Community involvement and service
- "Hobbies (N active goals)" — Hobbies, recreation, creative pursuits
- "Work (N active goals)" — Career and professional work
```

This helps the user see gaps and balance their focus.

## Step 3: Define the outcome

Ask via AskUserQuestion (open-ended — the user types their answer):

"What do you want to achieve in **[domain]** this quarter? Be specific about the outcome, not the activities."

Provide 2-3 domain-specific examples to calibrate:

- **Body**: "Run a 5K in under 30 minutes", "Lose 10 lbs through consistent gym routine"
- **Mind**: "Read 6 books on system design", "Complete AWS Solutions Architect certification"
- **Spirit**: "Meditate daily for 20 minutes for 12 weeks", "Complete a 3-day silent retreat"
- **Love**: "Establish weekly date night (12 consecutive weeks)", "Plan and take anniversary trip"
- **Family**: "Have monthly family dinners (3 this quarter)", "Set up college fund for kids"
- **Money**: "Save $5K emergency fund", "Pay off credit card balance"
- **Community**: "Volunteer 30 hours at food bank", "Mentor one junior engineer through quarter"
- **Hobbies**: "Ship v2 of side project", "Complete beginner woodworking course"
- **Work**: "Launch feature X to production", "Grow team from 4 to 6 engineers"

### Coaching gate: Evaluate the outcome

Apply these checks. Push back when warranted — be direct, not apologetic.

**Vague** ("get healthier", "learn more", "be better at X"):

> "That's too vague to track. What's the specific, observable outcome? For example, instead of 'get healthier,' try 'Run 3x per week for 12 consecutive weeks.'"

**Unmeasurable** ("improve my relationship", "grow professionally"):

> "How would you know you achieved this? What's the evidence? A good goal has a number or a concrete deliverable."

**Overambitious** (would require 10+ tasks, spans multiple quarters, or depends on too many external factors):

> "This sounds like it could be 2-3 separate goals, or might take longer than a quarter. Can we narrow it to what's achievable in ~13 weeks? What's the most important piece?"

**Good** (specific, measurable, achievable in a quarter):

> Proceed to Step 4.

If the user pushes back on coaching ("I know, just do it"), respect their decision and proceed. Coaching is firm but not blocking.

## Step 4: Decompose into tasks

Ask via AskUserQuestion (open-ended):

"What are the concrete steps to get there? Brain dump 3-7 tasks — don't overthink it, just list what comes to mind."

### Coaching gate: Evaluate the tasks

**Too few** (< 2 tasks):

> "This goal needs more concrete steps to be actionable. What's the very first thing you'd do? And what comes after that?"

**Too many** (> 7 tasks):

> "That's a lot for one quarter. Which 3-5 are most critical to making real progress? The rest can be added later via `/focus:task`."

**Too vague** (tasks like "think about X", "look into Y", "figure out Z"):

> "These need to be actionable. 'Think about X' isn't a task — 'Research X and write a 1-page summary' is. 'Figure out Z' becomes 'Spike Z for 2 hours and document findings.' Can you sharpen these?"

Iterate until 2-5 solid tasks remain. After 2 rounds of coaching, accept what the user has.

## Step 5: Create artifacts

### 5a: Ensure milestone exists

Check if a milestone exists for this domain (from Step 1 data).

If one exists, use it.

If not, ask via AskUserQuestion:

> "No annual milestone exists for [domain]. Should I create one? What's your annual goal for [domain]?"

Create the milestone if needed:

```bash
gh api -X POST /repos/$REPO/milestones \
  -f title="<Year> <Domain>: <Annual goal>" \
  -f due_on="<year-end>T23:59:59Z"
```

### 5b: Create the goal issue

```bash
gh issue create -R $REPO \
  --title "<Specific quarterly goal title>" \
  --body "<structured body — see format below>" \
  --label "type.goal,status.active,domain.<domain>" \
  --milestone "<milestone title>"
```

**Goal issue body format**:

```markdown
## Outcome

<What success looks like — specific and measurable>

## Measurement

<How progress is tracked — observable evidence>

## Timeline

Q<N> <Year> (<start month> — <end month>)

## Tasks

_Sub-issues will be linked below as they are created._
```

Capture the goal's issue number and node ID from the output:

```bash
gh issue view <GOAL_NUMBER> -R $REPO --json id --jq '.id'
```

### 5c: Create tasks as sub-issues

For each task from Step 4, create an issue and link it as a sub-issue of the goal.

Create the task:

```bash
gh issue create -R $REPO \
  --title "<Clear imperative task title>" \
  --body "<structured body>" \
  --label "type.task,status.active,domain.<domain>"
```

**Task issue body format** (matches `/focus:task` convention):

```markdown
## What

<Clear description of what needs to happen>

## Why

Supports goal #<GOAL_NUMBER>: <goal title>

## Done when

<Acceptance criteria — specific, testable>
```

After creating each task, get its node ID and link as sub-issue:

```bash
TASK_NODE_ID=$(gh issue view <TASK_NUMBER> -R $REPO --json id --jq '.id')
gh api graphql -f query='mutation { addSubIssue(input: { issueId: "<GOAL_NODE_ID>", subIssueId: "'"$TASK_NODE_ID"'" }) { issue { id } } }'
```

### 5d: If sub-issue API fails

Fall back: add a comment on the goal listing the tasks:

```bash
gh issue comment <GOAL_NUMBER> -R $REPO \
  --body "Tasks created for this goal:
- #<TASK_1> <title>
- #<TASK_2> <title>
- #<TASK_3> <title>"
```

## Step 6: Report

```
Created goal #<N>: <title>
  Domain: domain.<domain>
  Milestone: <milestone title>
  Tasks:
    - #<A>: <task 1 title>
    - #<B>: <task 2 title>
    - #<C>: <task 3 title>

Next: Run /focus:plan to include these tasks in your daily Big 3.
```

## Edge cases

- If `$ARGUMENTS` is empty: proceed to Step 2 (domain selection).
- If `$ARGUMENTS` includes both domain and description (e.g., `/focus:goal body Run a 5K by June`): use the domain and pre-populate the outcome for coaching evaluation in Step 3.
- If the user has 0 milestones and 0 goals: this is likely a first-time setup. Suggest: "Looks like a fresh start. Consider running `/focus:init` for full onboarding, or continue here to add one goal at a time."
- If `gh` commands fail with auth errors: report "gh CLI auth error — run `gh auth login` to fix."
