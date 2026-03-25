#!/usr/bin/env bash
set -euo pipefail

# scrape-github.sh — Scrapes GitHub communication history for bat-kol voice training
# Usage: scrape-github.sh <output-file>
# Requires: gh CLI (authenticated), jq

OUTPUT_FILE="${1:?Usage: scrape-github.sh <output-file>}"

if ! command -v gh &>/dev/null; then
  echo "ERROR: gh CLI not found. Install from https://cli.github.com/" >&2
  exit 1
fi

if ! gh auth status &>/dev/null 2>&1; then
  echo "ERROR: gh CLI not authenticated. Run 'gh auth login' first." >&2
  exit 1
fi

USERNAME=$(gh api /user --jq '.login' 2>/dev/null)
if [[ -z "$USERNAME" ]]; then
  echo "ERROR: Could not determine GitHub username." >&2
  exit 1
fi

echo "Scraping GitHub history for @${USERNAME}..."
echo "Output: ${OUTPUT_FILE}"

mkdir -p "$(dirname "$OUTPUT_FILE")"

# Start the output file
cat > "$OUTPUT_FILE" <<EOF
# GitHub Communication History — @${USERNAME}
# Scraped: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

EOF

PR_COUNT=0
ISSUE_COUNT=0
REVIEW_COUNT=0
COMMENT_COUNT=0

# PR bodies (authored)
echo "Scraping PR bodies..."
PR_DATA=$(gh api --paginate "search/issues?q=author:${USERNAME}+type:pr&sort=updated&per_page=100" --jq '.items[] | {title: .title, body: .body, url: .html_url, date: .updated_at}' 2>/dev/null || echo "")
if [[ -n "$PR_DATA" ]]; then
  echo "" >> "$OUTPUT_FILE"
  echo "## Pull Request Bodies" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  echo "$PR_DATA" | jq -r '"### PR: \(.title)\nURL: \(.url)\nDate: \(.date)\n\n\(.body // "(no body)")\n\n---\n"' >> "$OUTPUT_FILE" 2>/dev/null
  PR_COUNT=$(echo "$PR_DATA" | jq -s 'length' 2>/dev/null || echo "0")
  echo "  Found ${PR_COUNT} PRs"
fi

# Issue bodies (authored)
echo "Scraping issue bodies..."
ISSUE_DATA=$(gh api --paginate "search/issues?q=author:${USERNAME}+type:issue&sort=updated&per_page=100" --jq '.items[] | {title: .title, body: .body, url: .html_url, date: .updated_at}' 2>/dev/null || echo "")
if [[ -n "$ISSUE_DATA" ]]; then
  echo "" >> "$OUTPUT_FILE"
  echo "## Issue Bodies" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  echo "$ISSUE_DATA" | jq -r '"### Issue: \(.title)\nURL: \(.url)\nDate: \(.date)\n\n\(.body // "(no body)")\n\n---\n"' >> "$OUTPUT_FILE" 2>/dev/null
  ISSUE_COUNT=$(echo "$ISSUE_DATA" | jq -s 'length' 2>/dev/null || echo "0")
  echo "  Found ${ISSUE_COUNT} issues"
fi

# PR review comments (where user reviewed)
echo "Scraping PR review comments..."
REVIEWED_PRS=$(gh api --paginate "search/issues?q=reviewed-by:${USERNAME}+type:pr&sort=updated&per_page=50" --jq '.items[] | .pull_request.url' 2>/dev/null || echo "")
if [[ -n "$REVIEWED_PRS" ]]; then
  echo "" >> "$OUTPUT_FILE"
  echo "## PR Review Comments" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  while IFS= read -r pr_url; do
    [[ -z "$pr_url" ]] && continue
    COMMENTS=$(gh api "${pr_url}/comments" --jq '.[] | select(.user.login=="'"${USERNAME}"'") | {body: .body, path: .path, date: .created_at}' 2>/dev/null || echo "")
    if [[ -n "$COMMENTS" ]]; then
      echo "$COMMENTS" | jq -r '"### Review comment on \(.path // "general")\nDate: \(.date)\n\n\(.body)\n\n---\n"' >> "$OUTPUT_FILE" 2>/dev/null
      COUNT=$(echo "$COMMENTS" | jq -s 'length' 2>/dev/null || echo "0")
      REVIEW_COUNT=$((REVIEW_COUNT + COUNT))
    fi
  done <<< "$REVIEWED_PRS"
  echo "  Found ${REVIEW_COUNT} review comments"
fi

# Issue comments (where user commented)
echo "Scraping issue comments..."
COMMENTED_ISSUES=$(gh api --paginate "search/issues?q=commenter:${USERNAME}+type:issue&sort=updated&per_page=50" --jq '.items[] | {url: .url, title: .title}' 2>/dev/null || echo "")
if [[ -n "$COMMENTED_ISSUES" ]]; then
  echo "" >> "$OUTPUT_FILE"
  echo "## Issue Comments" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  echo "$COMMENTED_ISSUES" | jq -r '.url' | while IFS= read -r issue_url; do
    [[ -z "$issue_url" ]] && continue
    # Convert API URL to comments endpoint
    COMMENTS=$(gh api "${issue_url}/comments" --jq '.[] | select(.user.login=="'"${USERNAME}"'") | {body: .body, date: .created_at}' 2>/dev/null || echo "")
    if [[ -n "$COMMENTS" ]]; then
      echo "$COMMENTS" | jq -r '"### Issue comment\nDate: \(.date)\n\n\(.body)\n\n---\n"' >> "$OUTPUT_FILE" 2>/dev/null
      COUNT=$(echo "$COMMENTS" | jq -s 'length' 2>/dev/null || echo "0")
      COMMENT_COUNT=$((COMMENT_COUNT + COUNT))
    fi
  done
  echo "  Found ${COMMENT_COUNT} issue comments"
fi

# Summary
TOTAL=$((PR_COUNT + ISSUE_COUNT + REVIEW_COUNT + COMMENT_COUNT))
echo ""
echo "Done. Scraped ${TOTAL} items total:"
echo "  PRs: ${PR_COUNT}"
echo "  Issues: ${ISSUE_COUNT}"
echo "  Review comments: ${REVIEW_COUNT}"
echo "  Issue comments: ${COMMENT_COUNT}"
echo "  Output: ${OUTPUT_FILE}"
