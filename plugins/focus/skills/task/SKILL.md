---
name: task
description: Create a task in the Focus system. Provide enough context and it creates directly; vague input triggers a short interview to clarify scope, goal linkage, and acceptance criteria. Use when the user asks to "add a task", "create a task", "log a to-do", or capture ad-hoc work. Do NOT use for viewing or listing tasks — use focus:goals with "tasks" argument. Do NOT use for creating goals — use focus:goal.
disable-model-invocation: true
allowed-tools: Bash, AskUserQuestion
argument-hint: [task description or "for goal #N: description"]
---

# /focus:task

Create a well-formed task issue in the Focus system.

## Configuration

Follow the setup steps in `${CLAUDE_PLUGIN_ROOT}/shared/config-preamble.md` before running any `gh` commands.

## Step 1: Score confidence

Evaluate `$ARGUMENTS` against this rubric. Score each of the 4 dimensions from 0–15 using the ranges below. Sum the scores (max 60). Do NOT show the scores to the user.

| Dimension         | 0–5 (Ask — information missing)         | 6–10 (Maybe ask — information implied)   | 11–15 (Create — information present)                               |
| ----------------- | --------------------------------------- | ---------------------------------------- | ------------------------------------------------------------------ |
| **What**          | No clear action ("something about API") | Action implied but vague ("fix the API") | Specific action ("Fix 500 error on /api/users when email is null") |
| **Why/Goal**      | No context on which goal this serves    | Domain identifiable but goal unclear     | Explicit goal linkage or obvious domain                            |
| **Done criteria** | No idea what "done" means               | Implied completion state                 | Clear definition of done                                           |
| **Scope**         | Could mean anything                     | Roughly bounded                          | Specific and bounded                                               |

**Threshold**: Total >= 40 out of 60 → proceed to Step 3 (create directly). Total < 40 → proceed to Step 2 (interview).

## Step 2: Interview (only when confidence < 40)

Ask 1-3 targeted questions using AskUserQuestion, focusing on the lowest-scoring dimensions:

**Low "What"** — Ask:

- "What specifically needs to happen? Describe the concrete action or deliverable."

**Low "Why/Goal"** — First, fetch active goals for context:

```bash
gh issue list -R $REPO \
  --label "type.goal,status.active" \
  --state open \
  --json number,title,labels \
  --jq '.[] | "#\(.number) \(.title) [\([.labels[].name | select(startswith("domain."))] | join(", "))]"'
```

Then ask via AskUserQuestion:

- "Which goal does this task serve?" — present active goals as options, plus "Standalone task (no goal)" and "Other"

**Low "Done criteria"** — Ask:

- "How will you know this is finished? What's the observable evidence of completion?"

**Low "Scope"** — Ask:

- "Is this a single action or does it involve multiple steps? Can you describe the boundary?"

If the user says "just create it" or "I know what I want": stop the interview and proceed to Step 3 with whatever context is available. Coaching is firm but not blocking.

After the interview, re-score. If still < 40, ask one more round. After 2 rounds, proceed regardless with whatever context is available.

## Step 3: Determine labels

Every task gets:

- `type.task` (always)
- `status.active` (always)
- One `domain.*` label:
  - If linked to a goal: inherit the goal's domain label
  - If standalone with clear domain: infer from content
  - If ambiguous: ask via AskUserQuestion — "Which life domain does this belong to?" with the 9 domains as options

## Step 4: Determine goal linkage

If a parent goal was identified (from Step 2 interview or from `$ARGUMENTS` mentioning a goal number):

1. Verify the goal exists:
   ```bash
   gh issue view <GOAL_NUMBER> -R $REPO --json number,title,state --jq '{number, title, state}'
   ```
2. If it exists and is open: note for sub-issue linkage in Step 6
3. If it doesn't exist or is closed: warn and create as standalone

If no goal identified: create as standalone task.

## Step 5: Build the issue

Compose the issue title and body.

**Title**: Clear imperative sentence. "Fix X", "Add Y", "Research Z". Not a sentence fragment, not a question.

**Body**:

```markdown
## What

<Clear description of what needs to happen>

## Why

<Context: which goal this serves, or why it matters independently>

## Done when

<Acceptance criteria — specific, testable>

## Notes

<Any additional context, links, references. Omit this section if empty.>
```

## Step 6: Create the issue

```bash
gh issue create -R $REPO \
  --title "<title>" \
  --body "<body>" \
  --label "type.task,status.active,domain.<domain>"
```

Capture the issue number from the output.

If a parent goal was identified in Step 4, link as sub-issue using the shared script (handles fallback automatically):

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/link-sub-issue.sh <GOAL_NUMBER> <TASK_NUMBER> $REPO
```

## Step 7: Report

If linked to a goal:

```
Created task #<N>: <title>
  Domain: domain.<domain>
  Linked to goal #<M>: <goal title>
  URL: <issue URL>
```

If standalone:

```
Created task #<N>: <title>
  Domain: domain.<domain>
  Standalone (no goal linkage)
  URL: <issue URL>
```

## Edge cases

- If `$ARGUMENTS` is empty: score will be very low. Interview will ask "What task do you want to create?" as the first question.
- If `$ARGUMENTS` references a goal by number (e.g., "for goal #5: research API options"): extract the goal number and use it for linkage.
- If `gh` commands fail with auth errors: report "gh CLI auth error — run `gh auth login` to fix."
