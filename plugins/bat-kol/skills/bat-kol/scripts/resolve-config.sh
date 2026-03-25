#!/usr/bin/env bash
set -euo pipefail

# resolve-config.sh — Cascading config resolution for bat-kol
# Walks from cwd upward looking for .bat-kol/, falls back to XDG global.
# Outputs JSON with paths to active config files.

CHANNEL=""
REGISTER=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --channel)
      CHANNEL="$2"
      shift 2
      ;;
    --register)
      REGISTER="$2"
      shift 2
      ;;
    *)
      echo "ERROR: Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

GLOBAL_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/bat-kol"
CONFIG_ROOT=""
PROJECT_OVERRIDE=false

# Priority 1: Explicit env var override
if [[ -n "${BAT_KOL_CONFIG:-}" ]]; then
  if [[ -d "$BAT_KOL_CONFIG" ]]; then
    CONFIG_ROOT="$BAT_KOL_CONFIG"
    PROJECT_OVERRIDE=true
  else
    echo "ERROR: BAT_KOL_CONFIG points to non-existent directory: $BAT_KOL_CONFIG" >&2
    exit 1
  fi
fi

# Priority 2: Walk from cwd upward looking for .bat-kol/
if [[ -z "$CONFIG_ROOT" ]]; then
  SEARCH_DIR="$(pwd)"
  while [[ "$SEARCH_DIR" != "/" ]]; do
    if [[ -d "$SEARCH_DIR/.bat-kol" ]]; then
      CONFIG_ROOT="$SEARCH_DIR/.bat-kol"
      PROJECT_OVERRIDE=true
      break
    fi
    SEARCH_DIR="$(dirname "$SEARCH_DIR")"
  done
fi

# Priority 3: Global XDG config
if [[ -z "$CONFIG_ROOT" ]]; then
  if [[ -d "$GLOBAL_CONFIG" ]]; then
    CONFIG_ROOT="$GLOBAL_CONFIG"
    PROJECT_OVERRIDE=false
  fi
fi

# No config found anywhere
if [[ -z "$CONFIG_ROOT" ]]; then
  echo "ERROR: No bat-kol config found. Searched:" >&2
  echo "  - \$BAT_KOL_CONFIG env var (not set)" >&2
  echo "  - .bat-kol/ in cwd and parent directories" >&2
  echo "  - $GLOBAL_CONFIG" >&2
  echo "" >&2
  echo "Create a config directory:" >&2
  echo "  mkdir -p $GLOBAL_CONFIG/registers $GLOBAL_CONFIG/channels $GLOBAL_CONFIG/samples" >&2
  exit 1
fi

# Resolve file paths within config root
STYLE_PATH=""
if [[ -f "$CONFIG_ROOT/style.md" ]]; then
  STYLE_PATH="$CONFIG_ROOT/style.md"
elif [[ "$PROJECT_OVERRIDE" == "true" && -f "$GLOBAL_CONFIG/style.md" ]]; then
  # Project override can inherit global style if not overridden
  STYLE_PATH="$GLOBAL_CONFIG/style.md"
fi

REGISTER_PATH=""
if [[ -n "$REGISTER" ]]; then
  if [[ -f "$CONFIG_ROOT/registers/$REGISTER.md" ]]; then
    REGISTER_PATH="$CONFIG_ROOT/registers/$REGISTER.md"
  elif [[ "$PROJECT_OVERRIDE" == "true" && -f "$GLOBAL_CONFIG/registers/$REGISTER.md" ]]; then
    REGISTER_PATH="$GLOBAL_CONFIG/registers/$REGISTER.md"
  fi
fi

CHANNEL_PATH=""
if [[ -n "$CHANNEL" ]]; then
  if [[ -f "$CONFIG_ROOT/channels/$CHANNEL.md" ]]; then
    CHANNEL_PATH="$CONFIG_ROOT/channels/$CHANNEL.md"
  elif [[ "$PROJECT_OVERRIDE" == "true" && -f "$GLOBAL_CONFIG/channels/$CHANNEL.md" ]]; then
    CHANNEL_PATH="$GLOBAL_CONFIG/channels/$CHANNEL.md"
  fi
fi

# Resolve samples directory
SAMPLES_DIR=""
if [[ -n "$REGISTER" && -d "$CONFIG_ROOT/samples/$REGISTER" ]]; then
  SAMPLES_DIR="$CONFIG_ROOT/samples/$REGISTER"
elif [[ -n "$REGISTER" && "$PROJECT_OVERRIDE" == "true" && -d "$GLOBAL_CONFIG/samples/$REGISTER" ]]; then
  SAMPLES_DIR="$GLOBAL_CONFIG/samples/$REGISTER"
fi

# List available registers and channels for discovery
# Uses jq if available, falls back to manual JSON construction
list_md_files_as_json() {
  local dir="$1"
  if [[ ! -d "$dir" ]]; then
    echo "[]"
    return
  fi
  local names
  names=$(find "$dir" -name '*.md' -exec basename {} .md \; 2>/dev/null | sort)
  if [[ -z "$names" ]]; then
    echo "[]"
    return
  fi
  if command -v jq &>/dev/null; then
    echo "$names" | jq -R . | jq -s .
  else
    # Manual JSON array construction without jq
    local json="["
    local first=true
    while IFS= read -r name; do
      if [[ "$first" == "true" ]]; then
        first=false
      else
        json+=","
      fi
      json+="\"$name\""
    done <<< "$names"
    json+="]"
    echo "$json"
  fi
}

merge_json_arrays() {
  local arr1="$1" arr2="$2"
  if command -v jq &>/dev/null; then
    echo "$arr1 $arr2" | jq -s 'add | unique'
  else
    # Simple merge: strip brackets, combine, re-wrap, deduplicate
    local combined
    combined=$(echo "${arr1:1:${#arr1}-2},${arr2:1:${#arr2}-2}" | tr ',' '\n' | sort -u | tr '\n' ',' | sed 's/,$//')
    echo "[$combined]"
  fi
}

AVAILABLE_REGISTERS=$(list_md_files_as_json "$CONFIG_ROOT/registers")
AVAILABLE_CHANNELS=$(list_md_files_as_json "$CONFIG_ROOT/channels")

# Also check global config for additional registers/channels if using project override
if [[ "$PROJECT_OVERRIDE" == "true" && -d "$GLOBAL_CONFIG" ]]; then
  if [[ -d "$GLOBAL_CONFIG/registers" ]]; then
    GLOBAL_REGISTERS=$(list_md_files_as_json "$GLOBAL_CONFIG/registers")
    AVAILABLE_REGISTERS=$(merge_json_arrays "$AVAILABLE_REGISTERS" "$GLOBAL_REGISTERS")
  fi
  if [[ -d "$GLOBAL_CONFIG/channels" ]]; then
    GLOBAL_CHANNELS=$(list_md_files_as_json "$GLOBAL_CONFIG/channels")
    AVAILABLE_CHANNELS=$(merge_json_arrays "$AVAILABLE_CHANNELS" "$GLOBAL_CHANNELS")
  fi
fi

# Output JSON
cat <<EOF
{
  "config_root": "$CONFIG_ROOT",
  "global_config": "$GLOBAL_CONFIG",
  "project_override": $PROJECT_OVERRIDE,
  "style": "$STYLE_PATH",
  "register": "$REGISTER_PATH",
  "register_name": "$REGISTER",
  "channel": "$CHANNEL_PATH",
  "channel_name": "$CHANNEL",
  "samples_dir": "$SAMPLES_DIR",
  "available_registers": $AVAILABLE_REGISTERS,
  "available_channels": $AVAILABLE_CHANNELS
}
EOF
