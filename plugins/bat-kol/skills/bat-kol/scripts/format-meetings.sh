#!/usr/bin/env bash
set -euo pipefail

# format-meetings.sh — Formats meeting transcript/notes data into structured samples file
# Usage: echo "$RAW_DATA" | format-meetings.sh <output-file> [source-label]
# Accepts raw text on stdin (transcripts, meeting notes), writes structured markdown.
# source-label defaults to "Meeting Transcripts" — use "Gong", "Granola", "Zoom", etc.

OUTPUT_FILE="${1:?Usage: echo \"\$DATA\" | format-meetings.sh <output-file> [source-label]}"
SOURCE_LABEL="${2:-Meeting Transcripts}"

mkdir -p "$(dirname "$OUTPUT_FILE")"

cat > "$OUTPUT_FILE" <<EOF
# ${SOURCE_LABEL}
# Scraped: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
# Source: ${SOURCE_LABEL}
#
# Voice analysis note: meeting transcripts capture spoken voice which
# is more informal, uses filler words, and has different rhythm than
# written communication. Use to inform the "internal" and "professional"
# registers but recognize spoken patterns don't transfer 1:1 to writing.

EOF

COUNT=0

CURRENT_MSG=""
while IFS= read -r line; do
  if [[ "$line" == "---" ]]; then
    if [[ -n "$CURRENT_MSG" ]]; then
      echo "### Transcript Segment" >> "$OUTPUT_FILE"
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
  echo "### Transcript Segment" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  echo "$CURRENT_MSG" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  echo "---" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  COUNT=$((COUNT + 1))
fi

echo "" >> "$OUTPUT_FILE"
echo "# Total: ${COUNT} transcript segments" >> "$OUTPUT_FILE"

echo "Formatted ${COUNT} transcript segments to ${OUTPUT_FILE}"
