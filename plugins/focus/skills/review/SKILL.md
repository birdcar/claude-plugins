---
name: review
description: Scan external sources (Slack, meetings, email, calendar) for action items and commitments, then create or update tasks. Cross-references against open tasks to close completed ones and flag resolved stale items. Configurable sources — tell it where to look.
disable-model-invocation: true
allowed-tools: Bash, AskUserQuestion, mcp__claude_ai_Slack__*, mcp__claude_ai_Granola__*, mcp__claude_ai_Google_Calendar__*, mcp__claude_ai_Gmail__*, mcp__claude_ai_Glean__*, mcp__claude_ai_Notion__*, mcp__claude_ai_Linear__*
---

# /focus:review

Scan external sources for action items and commitments, then create or update GitHub issues. Cross-references against open tasks to flag completed ones without auto-closing them.

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

## Step 1: Source selection

Determine which sources to scan and the time window to use.

**Sources**:

If `$ARGUMENTS` specifies sources (e.g., `/focus:review slack granola`), parse them from the arguments — supported source names are: `slack`, `granola`, `calendar`, `gmail`, `all`.

If no sources are specified, ask via AskUserQuestion:

- Question: "Which sources should I scan for action items?"
- Type: multiSelect
- Options: `Slack`, `Granola (meetings)`, `Google Calendar`, `Gmail`, `All available`

If the user selects "All available", attempt each source and skip any whose MCP tools don't respond.

**Time window**:

- Default: today (since midnight in configured timezone)
- If `$ARGUMENTS` contains `yesterday`, `this week`, or a date like `2026-04-10`, use that range
- If ambiguous (e.g., "last few days"), ask via AskUserQuestion: "What time window should I use?" with options: `Today`, `Yesterday`, `This week`, `Custom date`

Determine the window boundaries in ISO 8601 format using:

```bash
TZ="$TZ_NAME" date +%Y-%m-%d
```

## Step 2: Gather open tasks and goals

Fetch open tasks and active goals before scanning sources. These are used for deduplication and goal linkage.

```bash
gh issue list -R $REPO \
  --label "type.task" \
  --state open \
  --limit 100 \
  --json number,title,body,labels,updatedAt
```

```bash
gh issue list -R $REPO \
  --label "type.goal,status.active" \
  --state open \
  --json number,title,labels
```

Hold both result sets in memory for use in Steps 4 and 5.

## Step 3: Scan sources

Process each selected source. If a source's MCP tools are unavailable or return an error, skip it and note the name in the "Not scanned" list for the final report. Process sources sequentially and summarize findings between them to manage context window pressure.

### Slack

Search for messages in the time window that involve commitments or action items:

1. Call `mcp__claude_ai_Slack__slack_search_public_and_private` with a query that:
   - Filters to the time window (e.g., `after:2026-04-11`)
   - Targets messages from or mentioning the user
   - Looks for commitment patterns: "I'll", "I will", "action item", "TODO", "follow up", "can you", "will do", "@user"

2. For each relevant result, call `mcp__claude_ai_Slack__slack_read_thread` to get full thread context before deciding whether it contains a real commitment.

3. Extract only clear, unambiguous commitments — not casual mentions. When in doubt, skip it. A false positive creates noise; a miss can be caught on the next review.

### Granola (meetings)

Retrieve meetings and extract action items:

1. Call `mcp__claude_ai_Granola__list_meetings` (or `mcp__claude_ai_Granola__get_meetings`) filtered to the time window.

2. For each meeting, call `mcp__claude_ai_Granola__get_meeting_transcript` to read the full transcript.

3. Extract: action items explicitly assigned to the user, decisions that require follow-up, and commitments made during the meeting.

### Google Calendar

List calendar events to supplement Granola coverage:

1. Call `mcp__claude_ai_Google_Calendar__gcal_list_events` for the time window.

2. Cross-reference with any Granola meetings fetched above. Meetings that appear in Calendar but have no Granola transcript represent a potential coverage gap — note them in the report as "meetings without transcripts" but do not create tasks solely from a calendar entry title.

3. Meeting titles themselves may imply follow-up (e.g., "Contract review call") — use this as weak signal only when combined with other context.

### Gmail

Search for actionable emails:

1. Call `mcp__claude_ai_Gmail__gmail_search_messages` with a date-filtered query. Look for: direct asks, "can you", "please", "by [date]", "action required", and reply-needed threads.

2. For each candidate, call `mcp__claude_ai_Gmail__gmail_read_message` to read the full message before deciding whether it contains a real task.

3. Only extract tasks from messages that require a concrete response or deliverable. Informational emails, newsletters, and automated notifications are not action items.

## Step 4: Deduplicate and cross-reference

Before creating anything, run every discovered item through these checks using the data gathered in Step 2.

**For each discovered action item**:

- Compare its title and key terms against the open tasks list (number, title, body)
- If the item closely matches an existing open task (title similarity or body keyword overlap): mark as "already tracked" — do not create a duplicate
- If the item matches a recently closed task: mark as "already done" — skip entirely
- If no match found: mark as "new task"

**For each open task**:

- Look for external signals suggesting the task is completed:
  - **Slack**: the user posted "done", "shipped", "completed", "sent", or "resolved" in a thread related to the task
  - **Granola**: a meeting transcript says the item was resolved or closed
  - **Gmail**: a sent reply fulfills what the task was asking for
- If completed signals found: mark the task as "suggest close" with the specific signal as evidence

Perform deduplication across sources as well — if the same action item appears in both a Slack thread and a Granola transcript, create one task, not two. Use the richer source as the primary attribution and note both.

## Step 5: Create, update, and close

Work through the classified items in this order: new tasks first, then suggest-close comments, then updates to existing tasks.

### New tasks (auto-create)

For each item marked "new task", create a GitHub issue immediately — no approval step:

```bash
gh issue create -R $REPO \
  --title "<clear imperative title>" \
  --body "<structured body>" \
  --label "type.task,status.active,domain.<inferred>"
```

**Title**: Clear imperative sentence. "Follow up with Sarah on API proposal." Not a fragment, not a question.

**Body format** (match the `/focus:task` pattern exactly):

```markdown
## What

<Clear description of what needs to happen>

## Why

<Context: which goal this serves, or why it matters. If source context is all that's available, use that.>

## Done when

<Acceptance criteria — specific and testable. If unclear from source, write the most reasonable interpretation.>

## Notes

Source: <source type> — <source detail>, <date>
```

Example Notes line: `Source: Slack thread in #engineering, 2026-04-11`
Example Notes line: `Source: Meeting with Sarah — Granola transcript, 2026-04-11`
Example Notes line: `Source: Gmail from finance@company.com, 2026-04-11`

**Domain inference**:

- Work-related Slack channels, work meetings, work email → `domain.work`
- Personal calendar events, personal email → `domain.personal`
- Health/fitness context → `domain.health`
- If ambiguous, default to `domain.work`

**Goal linkage**: If the task clearly relates to an open goal (from Step 2), link it as a sub-issue after creation:

```bash
# Get the task's node ID
gh issue view <TASK_NUMBER> -R $REPO --json id --jq '.id'

# Get the goal's node ID
gh issue view <GOAL_NUMBER> -R $REPO --json id --jq '.id'

# Link as sub-issue
gh api graphql -f query='mutation { addSubIssue(input: { issueId: "<GOAL_NODE_ID>", subIssueId: "<TASK_NODE_ID>" }) { issue { id } } }'
```

### Suggest close (comment only, never auto-close)

For each open task marked "suggest close", post a comment with the evidence. Do NOT close the issue:

```bash
gh issue comment <NUMBER> -R $REPO \
  --body "This task may be resolved based on [specific signal: e.g., 'your Slack message in #engineering saying \"shipped\" at 2:15 PM today']. Close if done, or remove this comment if still in progress."
```

The comment must include the specific signal — not a generic statement. The user needs enough detail to verify without hunting through the source.

### Update existing tasks (new context from source)

For open tasks that have new relevant context from a scanned source (but are not candidates for closing), post a comment:

```bash
gh issue comment <NUMBER> -R $REPO \
  --body "Update from <source> (<date>): <relevant new information or context>"
```

Only post an update comment if the new context materially changes the understanding of the task. Don't comment just because the task was mentioned in passing.

## Step 6: Report

After all actions are complete, present a summary. Use exact issue numbers from the `gh issue create` output.

```
Review complete (scanned: Slack, Granola, Calendar)

Created N new tasks:
  - #45 Follow up with Sarah on API proposal (source: Slack #engineering)
  - #46 Review Q2 budget draft (source: Gmail from finance@)

May be resolved (commented):
  - #32 Respond to Sarah about API — replied in Slack 2h ago
  - #29 Submit expense report — email confirmation found in Gmail

Updated with new context:
  - #38 Platform migration — meeting notes added from today's standup

Already tracked (skipped):
  - "Deploy auth service" — matches #41

Not scanned (unavailable): Gong, Linear
```

Omit any section that has zero entries (e.g., don't show "Updated with new context" if there are no updates).

If no action items were found across all sources, say: "Review complete (scanned: <sources>). No new action items found."

## Edge cases

- **Empty arguments**: Prompt for source selection via AskUserQuestion (Step 1).
- **MCP tool unavailable**: Catch the error, skip the source, add it to the "Not scanned" list. Do not abort the skill.
- **Rate limits or large context**: Process sources one at a time. If a time window produces too much data, warn the user and suggest narrowing to today.
- **Ambiguous commitment**: When uncertain whether a message is a real commitment, skip it. A missed task is less harmful than task noise.
- **`gh` auth error**: Report "gh CLI auth error — run `gh auth login` to fix." and stop.
- **All sources unavailable**: Report "No sources could be scanned. Check that your MCP integrations are connected in this Claude Code session." and stop.
