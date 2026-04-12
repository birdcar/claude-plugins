#!/usr/bin/env bash
set -euo pipefail

# sync-labels.sh — Sync the canonical Focus label taxonomy to GitHub
# Usage: sync-labels.sh <REPO>

REPO="${1:?Usage: sync-labels.sh <REPO>}"

ERRORS=0

sync_label() {
  local name="$1" color="$2" description="$3"
  if gh label create "$name" -R "$REPO" --color "$color" --description "$description" --force 2>/dev/null; then
    echo "  $name: ok"
  else
    echo "  $name: FAILED" >&2
    ERRORS=$((ERRORS + 1))
  fi
}

echo "Syncing status labels..."
sync_label "status.active"    "0075ca" "Actively being worked on"
sync_label "status.blocked"   "d73a4a" "Blocked by something external"
sync_label "status.waiting"   "e4e669" "Waiting on someone else"
sync_label "status.stale"     "e4e669" "No activity in 14+ days"
sync_label "status.done"      "0e8a16" "Completed"
sync_label "status.cancelled" "cfd3d7" "Cancelled — no longer relevant"

echo "Syncing type labels..."
sync_label "type.goal"         "a2eeef" "Quarterly goal"
sync_label "type.task"         "d4c5f9" "Actionable task"
sync_label "type.daily-thread" "f9d0c4" "Daily planning thread"
sync_label "type.review"       "fef2c0" "Review (weekly, quarterly)"
sync_label "type.note"         "bfd4f2" "Reference note"

echo "Syncing domain labels..."
sync_label "domain.body"      "bfd4f2" "Physical health and fitness"
sync_label "domain.mind"      "bfd4f2" "Mental health, learning, growth"
sync_label "domain.spirit"    "bfd4f2" "Spiritual practice and inner life"
sync_label "domain.love"      "bfd4f2" "Romantic relationship"
sync_label "domain.family"    "bfd4f2" "Family relationships"
sync_label "domain.money"     "bfd4f2" "Finances and financial goals"
sync_label "domain.community" "bfd4f2" "Community involvement and service"
sync_label "domain.hobbies"   "bfd4f2" "Hobbies, recreation, creative pursuits"
sync_label "domain.work"      "bfd4f2" "Career and professional work"

if [ "$ERRORS" -gt 0 ]; then
  echo "Sync complete with $ERRORS errors." >&2
  exit 1
fi

echo "Labels synced: 20 created/updated."
