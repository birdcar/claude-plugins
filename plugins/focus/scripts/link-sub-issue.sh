#!/usr/bin/env bash
set -euo pipefail

# link-sub-issue.sh — Link a task as a sub-issue of a goal
# Usage: link-sub-issue.sh <GOAL_NUMBER> <TASK_NUMBER> <REPO>
#
# Uses the GraphQL addSubIssue mutation. Falls back to posting a
# comment on the goal if the mutation fails.

GOAL_NUMBER="${1:?Usage: link-sub-issue.sh <GOAL_NUMBER> <TASK_NUMBER> <REPO>}"
TASK_NUMBER="${2:?Usage: link-sub-issue.sh <GOAL_NUMBER> <TASK_NUMBER> <REPO>}"
REPO="${3:?Usage: link-sub-issue.sh <GOAL_NUMBER> <TASK_NUMBER> <REPO>}"

GOAL_NODE_ID=$(gh issue view "$GOAL_NUMBER" -R "$REPO" --json id --jq '.id')
TASK_NODE_ID=$(gh issue view "$TASK_NUMBER" -R "$REPO" --json id --jq '.id')

if gh api graphql -f query="mutation { addSubIssue(input: { issueId: \"${GOAL_NODE_ID}\", subIssueId: \"${TASK_NODE_ID}\" }) { issue { id } } }" >/dev/null 2>&1; then
  echo "Linked #${TASK_NUMBER} as sub-issue of #${GOAL_NUMBER}"
else
  echo "Sub-issue API failed — falling back to comment" >&2
  TASK_TITLE=$(gh issue view "$TASK_NUMBER" -R "$REPO" --json title --jq '.title')
  gh issue comment "$GOAL_NUMBER" -R "$REPO" \
    --body "Task linked (fallback): #${TASK_NUMBER} ${TASK_TITLE}"
  echo "Posted fallback comment on #${GOAL_NUMBER}"
fi
