#!/usr/bin/env bash
set -euo pipefail

# format-linkedin.sh — Formats raw LinkedIn post/comment data into structured samples file
# Usage: echo "$RAW_DATA" | format-linkedin.sh <output-file>
# Accepts raw text on stdin (post content), writes structured markdown.
# LinkedIn data comes from Glean search, data export files, or user-pasted content.

OUTPUT_FILE="${1:?Usage: echo \"\$DATA\" | format-linkedin.sh <output-file>}"

mkdir -p "$(dirname "$OUTPUT_FILE")"

# Write header
cat > "$OUTPUT_FILE" <<EOF
# LinkedIn Post/Comment History
# Scraped: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
# Source: Glean / LinkedIn Data Export / User-provided

EOF

COUNT=0

CURRENT_MSG=""
while IFS= read -r line; do
  if [[ "$line" == "---" ]]; then
    if [[ -n "$CURRENT_MSG" ]]; then
      echo "### LinkedIn Post" >> "$OUTPUT_FILE"
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

if [[ -n "$CURRENT_MSG" ]]; then
  echo "### LinkedIn Post" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  echo "$CURRENT_MSG" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  echo "---" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  COUNT=$((COUNT + 1))
fi

echo "" >> "$OUTPUT_FILE"
echo "# Total: ${COUNT} posts/comments" >> "$OUTPUT_FILE"

echo "Formatted ${COUNT} LinkedIn posts/comments to ${OUTPUT_FILE}"
