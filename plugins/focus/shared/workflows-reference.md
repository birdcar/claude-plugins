# Focus Workflows Reference

When `/focus:init` Stage 8 generates workflows, use this reference. All workflows need the user's timezone to compute correct cron schedules.

## Timezone → Cron Mapping

The cron schedules below assume **America/Chicago (UTC-6 standard / UTC-5 daylight)**. For other timezones, compute the UTC offset and adjust. GitHub Actions cron is always UTC.

| Local time target | America/Chicago (UTC-6) | America/New_York (UTC-5) | America/Denver (UTC-7) | America/Los_Angeles (UTC-8) |
| ----------------- | ----------------------- | ------------------------ | ---------------------- | --------------------------- |
| 6 AM daily        | `0 12 * * *`            | `0 11 * * *`             | `0 13 * * *`           | `0 14 * * *`                |
| 6 PM weekdays     | `0 0 * * 2-6`           | `0 23 * * 1-5`           | `0 1 * * 2-6`          | `0 2 * * 2-6`               |
| 11 PM daily       | `0 5 * * *`             | `0 4 * * *`              | `0 6 * * *`            | `0 7 * * *`                 |
| 6 PM Sunday       | `0 0 * * 1`             | `0 23 * * 0`             | `0 1 * * 1`            | `0 2 * * 1`                 |
| 9 AM Monday       | `0 15 * * 1`            | `0 14 * * 1`             | `0 16 * * 1`           | `0 17 * * 1`                |

For timezones not listed, compute: `UTC_hour = local_hour + UTC_offset` (negative offset means add, e.g., UTC-6 at 6 AM local = 12 UTC). Handle day wrapping for evening times.

Note: DST causes the effective local time to shift by 1 hour twice a year. This is acceptable — the cron stays fixed in UTC.

## Workflow 1: daily-thread.yml

**Cron target**: 6 AM local, daily
**Permissions**: `contents: read`, `issues: write`
**Needs checkout**: Yes (for repo context, though current impl doesn't read files)

Creates a daily thread issue with Big 3 placeholders, morning ritual checklist, and goal context.

```yaml
name: Daily Thread

on:
  schedule:
    - cron: '<6AM_CRON>'
  workflow_dispatch:

jobs:
  create:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
    steps:
      - uses: actions/checkout@v4
      - name: Create daily thread issue
        run: |
          TODAY=$(TZ="<TIMEZONE>" date +%Y-%m-%d)
          WEEKDAY=$(TZ="<TIMEZONE>" date +%A)

          GOAL_CONTEXT=""
          while IFS= read -r goal; do
            GOAL_NUM=$(echo "$goal" | jq -r '.number')
            GOAL_TITLE=$(echo "$goal" | jq -r '.title')
            MILESTONE=$(echo "$goal" | jq -r '.milestone.title // "no milestone"')

            TASKS=$(gh api "/repos/$GITHUB_REPOSITORY/issues/$GOAL_NUM/sub_issues" \
              --jq '[.[] | select(.state == "open") | "  - #\(.number) \(.title)"] | join("\n")' 2>/dev/null)

            if [ -z "$TASKS" ]; then
              TASKS="  - (no open tasks)"
            fi

            GOAL_CONTEXT="${GOAL_CONTEXT}
          **#${GOAL_NUM} ${GOAL_TITLE}** (${MILESTONE})
          ${TASKS}
          "
          done < <(gh issue list \
            --label "type.goal,status.active" \
            --state open \
            --limit 20 \
            --json number,title,milestone \
            --jq '.[]' | jq -c '.')

          BODY_FILE=$(mktemp)
          cat > "$BODY_FILE" <<EOF
          # ${WEEKDAY}, ${TODAY}

          ## Big 3

          - [ ] _[to be selected]_
          - [ ] _[to be selected]_
          - [ ] _[to be selected]_

          ## Morning Ritual

          - [ ] Energy check: ___/10
          - [ ] Top blocker today: ___
          - [ ] Big 3 confirmed

          ## Goal Context

          _Active quarterly goals and open tasks for reference:_
          ${GOAL_CONTEXT}
          EOF

          gh issue create \
            --title "Daily Thread — ${TODAY}" \
            --body-file "$BODY_FILE" \
            --label "type.daily-thread,status.active"
          rm "$BODY_FILE"
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Workflow 2: rituals.yml

**Cron target**: 6 PM local, Monday-Friday (cron fires Tue-Sat UTC for CT)
**Permissions**: `issues: write`
**Needs checkout**: No

Posts evening ritual checklist to today's daily thread.

```yaml
name: Rituals

on:
  schedule:
    - cron: '<6PM_WEEKDAY_CRON>'
  workflow_dispatch:
    inputs:
      ritual:
        description: 'Ritual to run manually'
        required: false
        default: 'evening'
        type: choice
        options:
          - morning
          - evening

jobs:
  run:
    runs-on: ubuntu-latest
    permissions:
      issues: write
    steps:
      - name: Determine ritual type
        id: ritual-type
        env:
          EVENT_NAME: ${{ github.event_name }}
          INPUT_RITUAL: ${{ github.event.inputs.ritual }}
        run: |
          if [ "$EVENT_NAME" = "workflow_dispatch" ]; then
            echo "ritual=$INPUT_RITUAL" >> "$GITHUB_OUTPUT"
          else
            echo "ritual=evening" >> "$GITHUB_OUTPUT"
          fi

      - name: Morning ritual (no-op)
        if: steps.ritual-type.outputs.ritual == 'morning'
        run: echo "Morning ritual content is embedded in the daily thread issue body."

      - name: Evening ritual
        if: steps.ritual-type.outputs.ritual == 'evening'
        run: |
          TODAY=$(TZ="<TIMEZONE>" date +%Y-%m-%d)

          THREAD_NUMBER=$(gh issue list \
            --label "type.daily-thread" \
            --state open \
            --search "\"Daily Thread — $TODAY\" in:title" \
            --limit 5 \
            --json number \
            --jq '.[0].number // empty')

          if [ -z "$THREAD_NUMBER" ]; then
            echo "::warning::No open daily thread found for $TODAY"
            exit 0
          fi

          COMMENT_FILE=$(mktemp)
          printf '%s\n' \
            '## Evening Ritual' \
            '' \
            '- [ ] Wins: ___' \
            '- [ ] Challenges: ___' \
            '- [ ] Gratitude: ___' \
            "- [ ] Tomorrow's #1 priority: ___" \
            > "$COMMENT_FILE"

          gh issue comment "$THREAD_NUMBER" --body-file "$COMMENT_FILE"
          rm "$COMMENT_FILE"
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Workflow 3: journal-compile.yml

**Cron target**: 11 PM local, daily
**Permissions**: `issues: write`, `contents: write`
**Needs checkout**: Yes (commits journal files)

Compiles daily thread + comments into `journals/YYYY/MM/DD.md`, commits, and closes the thread.

```yaml
name: Journal Compile

on:
  schedule:
    - cron: '<11PM_CRON>'
  workflow_dispatch:

jobs:
  compile:
    runs-on: ubuntu-latest
    permissions:
      issues: write
      contents: write
    steps:
      - uses: actions/checkout@v4

      - name: Compile daily journal
        run: |
          TODAY=$(TZ="<TIMEZONE>" date +%Y-%m-%d)
          YEAR=$(TZ="<TIMEZONE>" date +%Y)
          MONTH=$(TZ="<TIMEZONE>" date +%m)
          DAY=$(TZ="<TIMEZONE>" date +%d)

          THREAD_NUMBER=$(gh issue list \
            --label "type.daily-thread" \
            --state open \
            --search "\"Daily Thread — $TODAY\" in:title" \
            --limit 5 \
            --json number \
            --jq '.[0].number // empty')

          if [ -z "$THREAD_NUMBER" ]; then
            echo "::warning::No open daily thread found for $TODAY"
            exit 0
          fi

          ISSUE_BODY=$(gh issue view "$THREAD_NUMBER" --json body --jq '.body')
          COMMENTS=$(gh issue view "$THREAD_NUMBER" \
            --json comments \
            --jq '.comments[] | "### \(.createdAt)\n\n\(.body)\n"')

          JOURNAL_PATH="journals/$YEAR/$MONTH/$DAY.md"
          mkdir -p "journals/$YEAR/$MONTH"

          {
            echo "# Daily Journal — $TODAY"
            echo ""
            echo "## Plan"
            echo ""
            echo "$ISSUE_BODY"
            echo ""
            echo "## Activity Log"
            echo ""
            echo "$COMMENTS"
          } > "$JOURNAL_PATH"

          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add "$JOURNAL_PATH"
          git commit -m "journal: $TODAY daily journal"
          git push

          gh issue close "$THREAD_NUMBER" \
            --comment "Journal compiled: [\`$JOURNAL_PATH\`](../blob/main/$JOURNAL_PATH)"
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Workflow 4: weekly-review.yml

**Cron target**: 6 PM Sunday local
**Permissions**: `issues: write`, `contents: write`
**Needs checkout**: Yes (commits review files, uses git log)

Generates weekly review + conditional quarterly check-in.

This is the largest workflow. It queries closed issues, daily threads, goal progress, and journal files from the past week. On quarter boundaries (first Sunday of Jan/Apr/Jul/Oct), it also generates a quarterly milestone progress report with off-track detection.

**Too large to template inline.** When generating this workflow, read the full implementation from the birdcar/home repo as reference and adapt the timezone. The key structure is:

1. Weekly review job with `fetch-depth: 0` for git log
2. Backward section: completion count, Big 3 hit rate, goal progress, journal highlights
3. Forward section: upcoming priorities from open goals
4. Conditional quarterly check-in (month in {1,4,7,10} AND day <= 7)
5. Quarterly report: milestone progress table with off-track detection via Python

## Workflow 5: stale-cleanup.yml

**Cron target**: 9 AM Monday local
**Permissions**: `issues: write`
**Needs checkout**: No

Labels tasks with no activity for 30+ days as `status.stale`. Posts triage comment. Never auto-closes.

```yaml
name: Stale Cleanup

on:
  schedule:
    - cron: '<9AM_MONDAY_CRON>'
  workflow_dispatch:

jobs:
  cleanup:
    runs-on: ubuntu-latest
    permissions:
      issues: write
    steps:
      - name: Label stale tasks and post triage comment
        run: |
          STALE_DATE=$(date -d "30 days ago" +%Y-%m-%d)

          STALE_ISSUES=$(gh issue list \
            --label "type.task" \
            --state open \
            --search "updated:<${STALE_DATE}" \
            --json number,title,updatedAt \
            --jq '.[]')

          if [ -z "$STALE_ISSUES" ]; then
            echo "No stale tasks found."
            exit 0
          fi

          LABELED=0
          while IFS= read -r issue; do
            ISSUE_NUM=$(echo "$issue" | jq -r '.number')
            ISSUE_TITLE=$(echo "$issue" | jq -r '.title')

            gh issue edit "$ISSUE_NUM" --add-label "status.stale"

            COMMENT=$(mktemp)
            printf '%s\n' \
              '**Stale task check-in** — no activity for 30+ days.' \
              '' \
              'Please take one action to keep this task current:' \
              '- **Close** — if this is no longer relevant' \
              '- **Add a comment** — with updated context to reset the stale clock' \
              '- **Reprioritize** — update labels or link to an active goal' \
              '' \
              '_This task will remain labeled `status.stale` until one of the above actions is taken._' \
              > "$COMMENT"
            gh issue comment "$ISSUE_NUM" --body-file "$COMMENT"
            rm "$COMMENT"

            LABELED=$((LABELED + 1))
          done < <(echo "$STALE_ISSUES")

          echo "Stale cleanup complete. $LABELED tasks labeled."
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Workflow 6: migration.yml

**Trigger**: `issues: closed` event + `workflow_dispatch`
**Permissions**: `issues: write`
**Needs checkout**: No

Updates parent goal progress when tasks close. Posts "all subtasks complete" note when applicable.

```yaml
name: Task Migration

on:
  issues:
    types: [closed]
  workflow_dispatch:

jobs:
  migrate:
    runs-on: ubuntu-latest
    permissions:
      issues: write
    steps:
      - name: Handle task lifecycle transition
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          ISSUE_NUM: ${{ github.event.issue.number }}
        run: |
          if [ -z "$ISSUE_NUM" ]; then
            echo "No issue context (workflow_dispatch). Nothing to do."
            exit 0
          fi

          ISSUE_TITLE=$(gh issue view "$ISSUE_NUM" --json title --jq '.title')
          LABELS=$(gh issue view "$ISSUE_NUM" --json labels --jq '[.labels[].name] | join(",")')

          if echo "$LABELS" | grep -q "type.daily-thread"; then
            echo "Daily thread — handled by journal-compile."
            exit 0
          fi

          if echo "$LABELS" | grep -q "type.goal"; then
            echo "Goal closed — no migration action."
            exit 0
          fi

          if echo "$LABELS" | grep -q "type.task"; then
            PARENT=$(gh api "/repos/$GITHUB_REPOSITORY/issues/${ISSUE_NUM}/parent" \
              --jq '.number // empty' 2>/dev/null || true)

            if [ -n "$PARENT" ]; then
              OPEN=$(gh api "/repos/$GITHUB_REPOSITORY/issues/${PARENT}/sub_issues" \
                --jq '[.[] | select(.state == "open")] | length' 2>/dev/null || echo "?")
              CLOSED=$(gh api "/repos/$GITHUB_REPOSITORY/issues/${PARENT}/sub_issues" \
                --jq '[.[] | select(.state == "closed")] | length' 2>/dev/null || echo "?")

              if [ "$OPEN" = "0" ] && [ "$CLOSED" != "?" ] && [ "$CLOSED" != "0" ]; then
                gh issue comment "$PARENT" \
                  --body "All sub-tasks complete (${CLOSED}/${CLOSED}). This goal may be ready to close."
              fi
            fi

            if echo "$LABELS" | grep -q "status.stale"; then
              gh issue edit "$ISSUE_NUM" --remove-label "status.stale"
            fi
          fi
```

## Workflow 7: sync-labels.yml

**Trigger**: `workflow_dispatch` only (manual)
**Permissions**: `contents: read`, `issues: write`
**Needs checkout**: Yes (reads `.github/labels.yml`)

Syncs labels from the YAML file. Uses Python to parse YAML and call `gh label create --force`.

```yaml
name: Sync Labels

on:
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
    steps:
      - uses: actions/checkout@v4
      - name: Sync labels from .github/labels.yml
        run: |
          python3 - <<'EOF'
          import yaml, subprocess, os, sys
          token = os.environ['GITHUB_TOKEN']
          with open('.github/labels.yml') as f:
              config = yaml.safe_load(f)
          env = {**os.environ, 'GH_TOKEN': token}
          errors = []
          for label in config['labels']:
              result = subprocess.run([
                  'gh', 'label', 'create', label['name'],
                  '--color', label['color'],
                  '--description', label.get('description', ''),
                  '--force'
              ], env=env, capture_output=True, text=True)
              status = 'ok' if result.returncode == 0 else f'error: {result.stderr.strip()}'
              print(f"  {label['name']}: {status}")
              if result.returncode != 0:
                  errors.append(label['name'])
          if errors:
              print(f'\nFailed labels: {errors}', file=sys.stderr)
              sys.exit(1)
          print(f'\nSynced {len(config["labels"])} labels successfully.')
          EOF
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## .gitignore addition

The repo also needs `.qmd/` in `.gitignore` for the ephemeral context cache:

```
.qmd/
```
