#!/usr/bin/env bash
set -euo pipefail

input=$(cat)
cmd=$(echo "$input" | jq -r '.tool_input.command // empty')

# Only validate git commit commands — exit 0 (allow) for everything else
echo "$cmd" | grep -qE '\bgit[[:space:]]+commit\b' || exit 0

# Allow if the command already carries a conventional commit type prefix
# (optional scope in parens, optional ! for breaking changes, then a colon).
# This lets /commit's own generated commits pass through untouched.
if echo "$cmd" | grep -qE '(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([^)]*\))?!?:'; then
  exit 0
fi

reason="Use /commit instead of raw git commit — it handles staging, message generation, and committing for you.

If you were already running /commit and this fired, the commit message is missing a conventional commit type prefix. Start the message with one of: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert — with an optional scope in parens and optional ! for breaking changes, then a colon. Example: feat(auth): Add login flow."

jq -n --arg reason "$reason" '{"decision":"block","reason":$reason}' >&2
exit 2
