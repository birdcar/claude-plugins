#!/usr/bin/env bash
set -euo pipefail

input=$(cat)
cmd=$(echo "$input" | jq -r '.tool_input.command // empty')

# Only validate clone commands — exit 0 (allow) for everything else
[[ "$cmd" =~ ^(git\ clone|gh\ repo\ clone) ]] || exit 0

# Extract org/repo from URL formats
if [[ "$cmd" =~ github\.com[:/]([^/[:space:]]+)/([^/[:space:].]+) ]]; then
  org="${BASH_REMATCH[1]}"
  repo="${BASH_REMATCH[2]%.git}"
elif [[ "$cmd" =~ ^gh\ repo\ clone\ ([^/[:space:]]+)/([^[:space:]]+) ]]; then
  org="${BASH_REMATCH[1]}"
  repo="${BASH_REMATCH[2]%.git}"
else
  exit 0
fi

# Determine correct target directory
if [[ "$org" == "workos" ]]; then
  if [[ "$repo" == se-demo-* ]]; then
    target="$HOME/Code/workos/demos/${repo#se-demo-}"
  elif [[ "$repo" == authkit-* ]]; then
    target="$HOME/Code/workos/sdk/${repo#authkit-}"
  elif [[ "$repo" == workos-*-* ]]; then
    # Framework-specific binding: last hyphen-separated segment
    target="$HOME/Code/workos/sdk/${repo##*-}"
  elif [[ "$repo" == workos-* ]]; then
    # Core language SDK: strip workos- prefix
    target="$HOME/Code/workos/sdk/${repo#workos-}"
  else
    target="$HOME/Code/workos/$repo"
  fi
else
  target="$HOME/Code/$org/$repo"
fi

tilde_target="${target/#$HOME/\~}"

# Allow if the correct target already appears in the command
if [[ "$cmd" == *"$target"* ]] || [[ "$cmd" == *"$tilde_target"* ]]; then
  exit 0
fi

# Allow exceptions
if [[ "$cmd" == *"$HOME/Code/workos/demo"* && "$cmd" != *"$HOME/Code/workos/demos"* ]] ||
   [[ "$cmd" == *"~/Code/workos/demo"* && "$cmd" != *"~/Code/workos/demos"* ]]; then
  exit 0
fi
[[ "$cmd" == *"$HOME/Code/_"* || "$cmd" == *"~/Code/_"* ]] && exit 0

# Build corrected command
parent_tilde="$(dirname "$tilde_target")"
if [[ "$cmd" =~ ^gh\ repo\ clone ]]; then
  fixed="mkdir -p $parent_tilde && gh repo clone $org/$repo $tilde_target"
else
  url=$(echo "$cmd" | grep -oE '(https?://|git@)[^ ]+')
  fixed="mkdir -p $parent_tilde && git clone $url $tilde_target"
fi

jq -n --arg reason "Clone target should be $tilde_target. Corrected command: $fixed" \
  '{"decision":"block","reason":$reason}' >&2
exit 2
