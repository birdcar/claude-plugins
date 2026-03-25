#!/usr/bin/env bash
set -euo pipefail

# format-email.sh — Formats raw email data into structured samples file
# Usage: echo "$RAW_DATA" | format-email.sh <output-file>
# Accepts raw text on stdin (email content), writes structured markdown.

OUTPUT_FILE="${1:?Usage: echo \"\$DATA\" | format-email.sh <output-file>}"

mkdir -p "$(dirname "$OUTPUT_FILE")"

# Write header
cat > "$OUTPUT_FILE" <<EOF
# Email History
# Scraped: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
# Source: Glean Gmail Search

EOF

COUNT=0

# Read stdin — expects messages separated by a delimiter line (---)
CURRENT_MSG=""
while IFS= read -r line; do
  if [[ "$line" == "---" ]]; then
    if [[ -n "$CURRENT_MSG" ]]; then
      echo "### Email" >> "$OUTPUT_FILE"
      echo "" >> "$OUTPUT_FILE"
      echo "$CURRENT_MSG" >> "$OUTPUT_FILE"
      echo "" >> "$OUTPUT_FILE"
      echo "---" >> "$OUTPUT_FILE"
      echo "" >> "$OUTPUT_FILE"
      COUNT=$((COUNT + 1))
      CURRENT_MSG=""
    fi
  else
    if [[ -n "$CURRENT_MSG" ]]; then
      CURRENT_MSG="${CURRENT_MSG}"$'\n'"${line}"
    else
      CURRENT_MSG="$line"
    fi
  fi
done

# Flush last message if no trailing delimiter
if [[ -n "$CURRENT_MSG" ]]; then
  echo "### Email" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  echo "$CURRENT_MSG" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  echo "---" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  COUNT=$((COUNT + 1))
fi

echo "" >> "$OUTPUT_FILE"
echo "# Total: ${COUNT} emails" >> "$OUTPUT_FILE"

echo "Formatted ${COUNT} emails to ${OUTPUT_FILE}"
