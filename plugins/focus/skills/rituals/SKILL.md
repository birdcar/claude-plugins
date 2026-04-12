---
name: rituals
description: Define, update, or view the 4 daily rituals (morning, workday startup, workday shutdown, evening). Interviews to create personalized checklists with time estimates. Use at the start of each quarter to re-evaluate, or anytime to update a single ritual.
disable-model-invocation: true
allowed-tools: Bash, AskUserQuestion
argument-hint: [morning|workday-startup|workday-shutdown|evening|view]
---

# /focus:rituals

Define, update, or view the 4 Full Focus daily rituals.

## Configuration

Before running any `gh` commands, resolve the target repository and timezone:

```bash
CONFIG_JSON=$(${CLAUDE_PLUGIN_ROOT}/scripts/resolve-config.sh)
```

If this fails, tell the user: "Focus is not configured. Run `/focus:init` to set up, or create `~/.config/focus/config.json` with `{\"repo\": \"owner/repo\", \"timezone\": \"America/Chicago\"}`."

Extract values:

```bash
REPO=$(echo "$CONFIG_JSON" | jq -r '.repo')
TZ_NAME=$(echo "$CONFIG_JSON" | jq -r '.timezone')
```

**All `gh` commands MUST use `-R $REPO`** instead of a hardcoded repo. All timezone-sensitive operations MUST use `TZ="$TZ_NAME"` instead of a hardcoded timezone.

## Step 1: Route on arguments

Parse `$ARGUMENTS`:

- **Empty or "all"** → Step 2 (full 4-ritual interview)
- **"view"** → Step 5 (display current rituals)
- **"morning"**, **"workday-startup"**, **"workday-shutdown"**, **"evening"** → Step 3 (single ritual update)
- **Anything else** → tell the user: "Usage: `/focus:rituals [morning|workday-startup|workday-shutdown|evening|view]`"

## Step 2: Full ritual interview

Walk through all 4 rituals in order. For each, run Step 4 (the interview for one ritual). After all 4, proceed to Step 6 (save).

Before starting, load existing rituals if they exist (Step 5 logic) and show them: "Here are your current rituals. We'll walk through each one — keep what works, change what doesn't."

If no rituals exist yet: "Let's set up your 4 daily rituals. Each one is a short checklist of activities with time estimates. The Full Focus system recommends re-evaluating these every quarter."

## Step 3: Single ritual update

Load existing rituals from repo. Run Step 4 for just the specified ritual. Save back with Step 6.

If no rituals exist yet: "No rituals configured yet. Run `/focus:rituals` with no arguments to set up all 4."

## Step 4: Interview one ritual

This step is called for each ritual type. Use AskUserQuestion throughout.

### 4a: Context and examples

Present the ritual type with its purpose and examples:

**Morning** — What you do when you first get up. Important but not urgent activities that make life rich. These set your mental and physical tone for the day.

- Examples: Meditate (10 min), Exercise (30 min), Journal (10 min), Read (15 min), Prayer (5 min), Healthy breakfast (15 min)
- Warning: "Take into account your season of life. If you have a newborn, 15 minutes to yourself is a win. Don't set yourself up for frustration by planning a 90-minute morning routine."

**Workday Startup** — What you do when you first sit down to work. Tasks that set you up to win for the day.

- Examples: Review calendar (5 min), Clear inbox to zero (15 min), Review Big 3 (5 min), Check Slack for urgent items (10 min), Set up workspace (5 min)

**Workday Shutdown** — What you do as you wrap up work and transition to evening. Prep to hit the ground running tomorrow.

- Examples: Process inbox (10 min), Review tomorrow's calendar (5 min), Update task status (5 min), Clear desk (3 min), Write tomorrow's Big 3 draft (5 min), Run `/focus:review` (10 min)

**Evening** — What you do right before bed. Activities that set you up for restful sleep.

- Examples: Read fiction (20 min), Gratitude journal (5 min), Prep clothes for tomorrow (5 min), Screen-free wind-down (15 min), Review wins and challenges (5 min)

### 4b: Collect items

Ask via AskUserQuestion:

> "What activities make up your **[Ritual Name]**? List each activity and roughly how many minutes it takes. For example: 'Meditate (10 min), Journal (5 min), Exercise (30 min)'"

The user types their list freely. Parse it into items with text and minutes.

### 4c: Coaching gate

Evaluate the list:

- **Too long** (>60 minutes total): "That's [N] minutes. For a [ritual type], that's ambitious. Can you trim to what you'll actually do consistently? It's better to have a 15-minute ritual you do every day than a 60-minute one you skip."
- **No time estimates**: "Each item needs a time estimate so you can budget your day. How long does each take?"
- **Too few items** (0-1): "A ritual works best with 2-5 items. What else would set you up for [purpose]?"
- **Good** (2-7 items, reasonable total): Proceed.

### 4d: Confirm

Show the formatted ritual:

```
Morning Ritual (~45 min)
  - Meditate (10 min)
  - Exercise (30 min)
  - Journal 3 gratitudes (5 min)
```

Ask: "Look good? Or adjust anything?"

If adjustments needed, loop back to 4b. Accept after 2 rounds max.

## Step 5: View current rituals

Fetch `.focus/rituals.json` from the repo:

```bash
gh api /repos/$REPO/contents/.focus/rituals.json --jq '.content' | base64 -d
```

If the file doesn't exist, report: "No rituals configured. Run `/focus:rituals` to set them up."

If it exists, parse and display all 4 rituals formatted as:

```
Your daily rituals (last updated: YYYY-MM-DD):

Morning Ritual (~15 min)
  - Meditate for 10 minutes (10 min)
  - Journal 3 gratitudes (5 min)

Workday Startup (~20 min)
  - Review calendar (5 min)
  - Clear inbox to zero (15 min)

Workday Shutdown (~15 min)
  - Process inbox (10 min)
  - Review tomorrow's calendar (5 min)

Evening Ritual (~7 min)
  - Wins today (3 min)
  - Tomorrow's #1 priority (2 min)
  - Gratitude (2 min)

Total daily ritual time: ~57 min

To update a single ritual: /focus:rituals morning
To redefine all: /focus:rituals
```

## Step 6: Save rituals to repo

Build the JSON object matching the schema in `${CLAUDE_PLUGIN_ROOT}/shared/rituals-schema.md`.

Write it to the repo. First check if `.focus/rituals.json` already exists:

```bash
EXISTING_SHA=$(gh api /repos/$REPO/contents/.focus/rituals.json --jq '.sha' 2>/dev/null || echo "")
```

If it exists, update:

```bash
CONTENT=$(echo '<JSON>' | base64)
gh api -X PUT /repos/$REPO/contents/.focus/rituals.json \
  -f message="focus: Update daily rituals" \
  -f content="$CONTENT" \
  -f sha="$EXISTING_SHA"
```

If it doesn't exist, create:

```bash
CONTENT=$(echo '<JSON>' | base64)
gh api -X PUT /repos/$REPO/contents/.focus/rituals.json \
  -f message="focus: Define daily rituals" \
  -f content="$CONTENT"
```

Report: "Rituals saved to `.focus/rituals.json` and committed to $REPO."

## Edge cases

- If `gh` commands fail with auth errors: report "gh CLI auth error — run `gh auth login` to fix."
- If `.focus/` directory doesn't exist in the repo: the GitHub Contents API creates it automatically when writing the file.
- If the user provides items without time estimates: prompt once for estimates. If they refuse, default each to 5 minutes with a note.
- If updating a single ritual and the file doesn't exist: tell user to run `/focus:rituals` (full setup) first.
