#!/usr/bin/env bash
set -euo pipefail

# scrape-bluesky.sh — Scrapes Bluesky post history for bat-kol voice training
# Usage: scrape-bluesky.sh <handle> <output-file>
# Requires: curl, jq

HANDLE="${1:?Usage: scrape-bluesky.sh <handle> <output-file>}"
OUTPUT_FILE="${2:?Usage: scrape-bluesky.sh <handle> <output-file>}"

if ! command -v jq &>/dev/null; then
  echo "ERROR: jq not found. Install with: brew install jq" >&2
  exit 1
fi

echo "Scraping Bluesky posts for @${HANDLE}..."
echo "Output: ${OUTPUT_FILE}"

mkdir -p "$(dirname "$OUTPUT_FILE")"

API_BASE="https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed"
TOTAL=0
CURSOR=""

cat > "$OUTPUT_FILE" <<EOF
# Bluesky Post History — @${HANDLE}
# Scraped: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

EOF

while true; do
  URL="${API_BASE}?actor=${HANDLE}&limit=100"
  if [[ -n "$CURSOR" ]]; then
    URL="${URL}&cursor=${CURSOR}"
  fi

  RESPONSE=$(curl -sf "$URL" 2>/dev/null || echo "")
  if [[ -z "$RESPONSE" ]]; then
    if [[ $TOTAL -eq 0 ]]; then
      echo "ERROR: Could not fetch posts for @${HANDLE}. Check the handle is correct." >&2
      exit 1
    fi
    break
  fi

  POSTS=$(echo "$RESPONSE" | jq -r '.feed[]? | .post | "### Post (\(.record.createdAt // "unknown date"))\n\n\(.record.text // "(no text)")\n\n---\n"' 2>/dev/null || echo "")
  if [[ -z "$POSTS" ]]; then
    break
  fi

  echo "$POSTS" >> "$OUTPUT_FILE"
  PAGE_COUNT=$(echo "$RESPONSE" | jq '.feed | length' 2>/dev/null || echo "0")
  TOTAL=$((TOTAL + PAGE_COUNT))

  CURSOR=$(echo "$RESPONSE" | jq -r '.cursor // empty' 2>/dev/null || echo "")
  if [[ -z "$CURSOR" ]]; then
    break
  fi

  echo "  Fetched ${TOTAL} posts so far..."
done

echo ""
echo "Done. Scraped ${TOTAL} posts."
echo "  Output: ${OUTPUT_FILE}"
