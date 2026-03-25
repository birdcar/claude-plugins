#!/usr/bin/env bash
set -euo pipefail

# format-slack.sh — Formats raw Slack message data into structured samples file
# Usage: echo "$RAW_DATA" | format-slack.sh <output-file>
# Accepts raw text on stdin (one message per line, or JSON), writes structured markdown.

OUTPUT_FILE="${1:?Usage: echo \"\$DATA\" | format-slack.sh <output-file>}"

mkdir -p "$(dirname "$OUTPUT_FILE")"

# Write header
cat > "$OUTPUT_FILE" <<EOF
# Slack Message History
# Scraped: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
# Source: Slack MCP

EOF

COUNT=0

# Read stdin and format each message
while IFS= read -r line; do
  [[ -z "$line" ]] && continue
  echo "### Message" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  echo "$line" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  echo "---" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  COUNT=$((COUNT + 1))
done

echo "" >> "$OUTPUT_FILE"
echo "# Total: ${COUNT} messages" >> "$OUTPUT_FILE"

echo "Formatted ${COUNT} Slack messages to ${OUTPUT_FILE}"
