#!/usr/bin/env bash
set -euo pipefail

input=$(cat)
cmd=$(echo "$input" | jq -r '.tool_input.command // empty')

# Determine the target directory for the init command
if [[ "$cmd" =~ ^cargo\ new\ (.+) ]]; then
  # cargo new creates a subdirectory
  arg="${BASH_REMATCH[1]}"
  arg="${arg%% *}" # first arg only
  if [[ "$arg" == /* || "$arg" == ~/* ]]; then
    target="$arg"
  else
    target="$(pwd)/$arg"
  fi
elif [[ "$cmd" =~ [[:space:]]([~/][^ ]+) ]]; then
  # init with explicit path argument
  target="${BASH_REMATCH[1]}"
else
  # init in CWD
  target="$(pwd)"
fi

# Expand tilde
target="${target/#\~/$HOME}"

# Normalize
target=$(cd "$target" 2>/dev/null && pwd || echo "$target")

# Allow if target is under ~/Code/{owner}/{project}
if [[ "$target" =~ ^$HOME/Code/[^/]+/[^/]+ ]]; then
  exit 0
fi

# Allow underscore directories
if [[ "$target" =~ ^$HOME/Code/_[^/]+ ]]; then
  exit 0
fi

# Allow workos SDK/demo paths
if [[ "$target" =~ ^$HOME/Code/workos/(sdk|demos)/ ]]; then
  exit 0
fi

# Block — not in a valid location
tilde_target="${target/#$HOME/\~}"
jq -n --arg reason "Init commands must run under ~/Code/{OWNER}/{PROJECT_NAME}. Current target: $tilde_target" \
  '{"decision":"block","reason":$reason}' >&2
exit 2
