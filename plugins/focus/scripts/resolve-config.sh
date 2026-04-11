#!/usr/bin/env bash
set -euo pipefail

# resolve-config.sh — Cascading config resolution for focus
# Walks from cwd upward looking for .focus/, falls back to XDG global.
# Outputs JSON with the target repo and timezone.

GLOBAL_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/focus"
CONFIG_ROOT=""
CONFIG_FILE=""

# Priority 1: Explicit env var override
if [[ -n "${FOCUS_REPO:-}" ]]; then
  # Env var directly sets the repo — skip file lookup
  REPO="$FOCUS_REPO"
  TZ_NAME="${FOCUS_TZ:-America/Chicago}"
  cat <<EOF
{
  "repo": "$REPO",
  "timezone": "$TZ_NAME",
  "source": "env"
}
EOF
  exit 0
fi

# Priority 2: Walk from cwd upward looking for .focus/config.json
SEARCH_DIR="$(pwd)"
while [[ "$SEARCH_DIR" != "/" ]]; do
  if [[ -f "$SEARCH_DIR/.focus/config.json" ]]; then
    CONFIG_FILE="$SEARCH_DIR/.focus/config.json"
    CONFIG_ROOT="$SEARCH_DIR/.focus"
    break
  fi
  SEARCH_DIR="$(dirname "$SEARCH_DIR")"
done

# Priority 3: Global XDG config
if [[ -z "$CONFIG_FILE" && -f "$GLOBAL_CONFIG/config.json" ]]; then
  CONFIG_FILE="$GLOBAL_CONFIG/config.json"
  CONFIG_ROOT="$GLOBAL_CONFIG"
fi

# No config found
if [[ -z "$CONFIG_FILE" ]]; then
  echo "ERROR: No focus config found. Searched:" >&2
  echo "  - \$FOCUS_REPO env var (not set)" >&2
  echo "  - .focus/config.json in cwd and parent directories" >&2
  echo "  - $GLOBAL_CONFIG/config.json" >&2
  echo "" >&2
  echo "Quick setup:" >&2
  echo "  mkdir -p $GLOBAL_CONFIG" >&2
  echo "  echo '{\"repo\": \"owner/repo\", \"timezone\": \"America/Chicago\"}' > $GLOBAL_CONFIG/config.json" >&2
  echo "" >&2
  echo "Or run /focus:init to configure interactively." >&2
  exit 1
fi

# Parse config file
if command -v jq &>/dev/null; then
  REPO=$(jq -r '.repo // empty' "$CONFIG_FILE")
  TZ_NAME=$(jq -r '.timezone // "America/Chicago"' "$CONFIG_FILE")
else
  # Fallback: simple grep parsing for {"repo": "...", "timezone": "..."}
  REPO=$(grep -o '"repo"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" | head -1 | sed 's/.*"repo"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
  TZ_NAME=$(grep -o '"timezone"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" | head -1 | sed 's/.*"timezone"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
  TZ_NAME="${TZ_NAME:-America/Chicago}"
fi

if [[ -z "$REPO" ]]; then
  echo "ERROR: config.json at $CONFIG_FILE is missing 'repo' field." >&2
  echo "Expected format: {\"repo\": \"owner/repo\", \"timezone\": \"America/Chicago\"}" >&2
  exit 1
fi

SOURCE="project"
if [[ "$CONFIG_ROOT" == "$GLOBAL_CONFIG" ]]; then
  SOURCE="global"
fi

cat <<EOF
{
  "repo": "$REPO",
  "timezone": "$TZ_NAME",
  "config_file": "$CONFIG_FILE",
  "source": "$SOURCE"
}
EOF
