---
name: init
description: Bootstraps the Focus productivity system from scratch — labels, annual milestones across all 9 life domains, quarterly goals with coaching, initial task backlog, daily rituals, and GitHub Actions automation. Use when the user asks to "set up focus", "initialize the system", "get started with focus", or "bootstrap my productivity system". Run once on first setup; safe to re-run (warns before adding to existing data). Do NOT use to add a single goal — use focus:goal. Do NOT use to update rituals only — use focus:rituals.
disable-model-invocation: true
allowed-tools: Bash, AskUserQuestion
---

# /focus:init

Bootstrap the Focus productivity system in one session: labels, annual milestones, quarterly goals, and an initial task backlog.

## Stage 0: Configuration

First, check if focus is already configured:

```bash
CONFIG_JSON=$(${CLAUDE_PLUGIN_ROOT}/scripts/resolve-config.sh 2>/dev/null) && echo "configured" || echo "not configured"
```

**If not configured**, set it up interactively before anything else:

1. Ask via AskUserQuestion: "Which GitHub repository should Focus manage? This is where your goals, tasks, and daily threads live."
   - Options: "Other" (user types `owner/repo`)
   - If you can detect the current repo via `gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null`, offer it as the first option

2. Ask via AskUserQuestion: "What timezone are you in?"
   - Options: "America/Chicago (Central)", "America/New_York (Eastern)", "America/Denver (Mountain)", "America/Los_Angeles (Pacific)", "Other"

3. Write the config:

```bash
mkdir -p "${XDG_CONFIG_HOME:-$HOME/.config}/focus"
cat > "${XDG_CONFIG_HOME:-$HOME/.config}/focus/config.json" << EOF
{"repo": "<REPO>", "timezone": "<TIMEZONE>"}
EOF
```

4. Confirm: "Focus configured: repo=`<REPO>`, timezone=`<TIMEZONE>`. Config saved to `~/.config/focus/config.json`."

**If already configured**, load the values:

```bash
CONFIG_JSON=$(${CLAUDE_PLUGIN_ROOT}/scripts/resolve-config.sh)
REPO=$(echo "$CONFIG_JSON" | jq -r '.repo')
TZ_NAME=$(echo "$CONFIG_JSON" | jq -r '.timezone')
```

Report: "Using repo `$REPO` (timezone: `$TZ_NAME`). Change with `~/.config/focus/config.json`."

Always use `-R $REPO` in `gh` commands — omitting it silently targets whatever repo `gh` infers from the current directory, which may not be the configured Focus repo. Similarly, use `TZ="$TZ_NAME"` for all timezone-sensitive operations.

---

## Stage 1: System check

Check whether the system already has data.

```bash
gh api /repos/$REPO/milestones --jq 'length'
gh issue list -R $REPO --label "type.goal" --json number --jq 'length'
```

If milestones > 0 OR goals > 0, ask via AskUserQuestion before continuing:

> "This repo already has N milestones and M goals. /focus:init is designed for first-time setup. Running it again will create new milestones and goals alongside existing ones. What would you like to do?"

Options:

- "Continue with init (add alongside existing data)"
- "Switch to /focus:goal to add one goal at a time"
- "Cancel"

If the user selects "Switch to /focus:goal" or "Cancel", stop and tell them to run the relevant command. Do not proceed.

If the repo is clean (0 milestones, 0 goals) OR the user chooses "Continue", proceed to Stage 2.

---

## Stage 2: Labels

Sync the canonical 20-label taxonomy to the repo:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/sync-labels.sh $REPO
```

If the script exits non-zero, report which labels failed but continue to Stage 3. Label sync failure is non-fatal.

---

## Stage 3: Annual milestones

Walk through all 9 life domains one at a time. Every domain is visited — skipping is allowed but the user must actively choose to skip so nothing is forgotten.

Determine the current year for milestone titles and due dates (e.g., `2026-12-31T23:59:59Z`).

### 3a: Per-domain interview (repeat for each of the 9 domains in this order)

**Domains**: Body, Mind, Spirit, Love, Family, Money, Community, Hobbies, Work

For each domain, use AskUserQuestion:

> "What's your annual goal for **[Domain]**? This is the big-picture outcome you want to reach by end of year. Examples: [domain-specific examples below]."

Provide these domain-specific examples:

- **Body**: "Run a marathon", "Lose 20 lbs and keep it off", "Establish a consistent gym routine (3x/week)"
- **Mind**: "Read 24 books (2/month)", "Complete a certification", "Learn Spanish to conversational level"
- **Spirit**: "Establish daily meditation practice", "Attend 2 retreats", "Read 5 spiritual texts"
- **Love**: "Go on 2 trips together", "Establish weekly date night", "Write 12 love letters"
- **Family**: "Visit parents monthly", "Start family game night", "Plan summer reunion"
- **Money**: "Save $20K", "Pay off student loans", "Max out 401K"
- **Community**: "Volunteer 100 hours", "Join a board", "Mentor 2 people"
- **Hobbies**: "Ship a side project", "Learn woodworking", "Play 50 rounds of golf"
- **Work**: "Get promoted to senior", "Launch product X", "Build team to 8 people"

Options:

- The user types their annual goal as free text
- "Skip this domain for now"

Record each response (goal text or "skipped") before moving to the next domain.

### 3b: Coaching gate — cross-domain summary

After collecting all 9 responses, present a summary and provide cross-domain observations. This is the only moment in the system where the full picture is visible — use it.

Format the summary like this:

```
Here's your annual plan:

Body: [goal or "(skipped)"]
Mind: [goal or "(skipped)"]
Spirit: [goal or "(skipped)"]
Love: [goal or "(skipped)"]
Family: [goal or "(skipped)"]
Money: [goal or "(skipped)"]
Community: [goal or "(skipped)"]
Hobbies: [goal or "(skipped)"]
Work: [goal or "(skipped)"]

Observations:
- [coaching notes — see rules below]
```

**Cross-domain coaching rules** (apply all that are relevant):

- If a domain was skipped: note it once, gently. "You skipped [domain]. That's fine if intentional — just noting it."
- If 3+ domains were skipped: "You skipped N domains. That leaves big parts of your life unplanned. Is that intentional, or do you want to go back and fill any in?"
- If Body + Work + Hobbies are all ambitious: "Body, Work, and Hobbies each have ambitious goals. Together they're a lot. Are you sure about the timeline across all three?"
- If a goal is vague ("be healthier", "do better", "improve X"): call it out by name. "The [domain] goal is vague — how would you know at year-end if you hit it?"
- If all goals are specific and well-scoped: "All 9 goals look specific and measurable. Nice."
- If Work is the only non-skipped domain: "Every non-skipped goal is in Work. A life well-lived has more dimensions — consider adding at least one personal domain."

After the coaching summary, ask via AskUserQuestion:

> "Any adjustments before I create the milestones? You can revise any domain's goal, add a skipped domain, or proceed as-is."

Options:

- "Proceed — create milestones"
- "Revise [domain]: [user types new goal]" — accept free text. After revision, re-present the full summary and ask again. Allow up to 2 revision rounds, then proceed regardless.

### 3c: Create milestones

For each domain with a non-skipped goal, create a milestone:

```bash
gh api -X POST /repos/$REPO/milestones \
  -f title="<YEAR> <Domain>: <Annual goal>" \
  -f description="Annual goal for <domain>" \
  -f due_on="<YEAR>-12-31T23:59:59Z"
```

Example: `2026 Body: Run a marathon`

Capture the milestone number for each domain — you'll need it in Stage 5.

Report: "Milestones created: N (M domains skipped)." Then proceed to Stage 4.

---

## Stage 4: Quarterly focus selection

Ask the user which domains to focus on this quarter. This is where the annual plan narrows to what's actionable now.

Build the options list from domains with milestones (exclude skipped domains). Show the annual goal as context for each option.

Use AskUserQuestion with multi-select:

> "Which domains do you want to focus on THIS QUARTER? Pick 2–4. Focusing on everything is focusing on nothing."

Options (one per non-skipped domain):

- "[Domain] — [annual goal]"

**Coaching gate**:

- If the user selects exactly 1 domain: "That's a tight focus — which is fine if intentional. Confirm you want to go deep on just [domain] this quarter?"
- If the user selects 5+ domains: "That's N domains. Most people make real progress on 2–4 per quarter. Which are the highest priority right now? Consider dropping [the lower-priority ones you can infer from the goals]." Ask again. If the user still selects 5+, accept it with a note: "Noted — that's ambitious. We'll proceed with all N."

Record the selected domains. Proceed to Stage 5.

---

## Stage 5: Quarterly goals (per selected domain)

For each selected domain, run the full goal interview pattern from `/focus:goal`. Do NOT invoke the skill — embed the same logic inline.

Process each domain in order. For each:

### 5a: Define the quarterly outcome

Ask via AskUserQuestion (open-ended):

> "What do you want to achieve in **[Domain]** this quarter? Be specific — this should advance your annual goal of '[annual goal]'."

Provide 2–3 domain-specific examples calibrated to the annual goal context:

- **Body**: "Run 3x/week for 12 consecutive weeks", "Lose 8 lbs by eating 1800 cal/day"
- **Mind**: "Read 3 books on [topic]", "Complete 6 of 12 certification modules"
- **Spirit**: "Meditate daily for 20 minutes for 12 weeks", "Attend one retreat this quarter"
- **Love**: "Complete 6 consecutive weekly date nights", "Plan and book anniversary trip"
- **Family**: "Have monthly family dinner (3 this quarter)", "Call parents every Sunday"
- **Money**: "Save $5K by cutting discretionary spending by 30%", "Pay off $2K on credit card"
- **Community**: "Volunteer 25 hours at food bank", "Onboard and meet with mentee 6 times"
- **Hobbies**: "Ship v1 of side project with 3 core features", "Complete beginner woodworking course"
- **Work**: "Launch feature X to production", "Complete 3 phases of platform migration"

### Coaching gate: Evaluate the quarterly outcome

Apply these checks. Push back directly — not apologetically.

**Vague** ("get better at X", "work on my health", "focus on money"):

> "That's too vague to track. What's the specific, observable outcome at the end of 13 weeks? For example, instead of 'work on my health,' try 'Run 3x/week for 12 consecutive weeks.'"

**Unmeasurable** ("improve my relationship", "be more productive"):

> "How would you know at the end of the quarter that you achieved this? What's the concrete evidence? Add a number or a deliverable."

**Overambitious** (multiple major outcomes, cross-domain dependencies, or clearly spans more than 13 weeks):

> "This sounds like it might be 2–3 separate goals, or might take longer than a quarter. What's the most critical piece you can complete in ~13 weeks?"

**Good** (specific, measurable, achievable in a quarter): proceed to 5b.

If the user pushes back on coaching ("I know, just create it"), accept and proceed.

### 5b: Create the goal issue

```bash
gh issue create -R $REPO \
  --title "<Specific quarterly goal title>" \
  --body "## Outcome
<What success looks like — specific and measurable>

## Measurement
<How progress is tracked — observable evidence>

## Timeline
Q<N> <Year>

## Tasks
_Sub-issues linked below_" \
  --label "type.goal,status.active,domain.<domain>" \
  --milestone "<milestone title>"
```

Capture the goal issue number. Then fetch its node ID:

```bash
gh issue view <GOAL_NUMBER> -R $REPO --json id --jq '.id'
```

Store both the issue number and node ID — needed for sub-issue linkage in Stage 6.

---

## Stage 6: Task brain dump

For each quarterly goal, collect an initial set of concrete tasks. Then offer a freeform brain dump for orphan tasks.

### 6a: Per-goal task collection

For each goal created in Stage 5, ask via AskUserQuestion:

> "What are the first 3–5 concrete steps for: **[goal title]**? Don't overthink — brain dump what comes to mind."

**Coaching gate: Evaluate tasks**

- **Too few** (fewer than 2): "This goal needs more concrete steps to be actionable. What's the very first thing you'd do? What comes after that?"
- **Too many** (more than 7): "That's a lot for one quarter. Which 3–5 are most critical to making real progress? The rest can be added later via `/focus:task`."
- **Too vague** ("think about X", "look into Y", "figure out Z"): "'Think about X' isn't a task — 'Research X and write a 1-page summary' is. Can you sharpen any of these?"

After coaching, accept what the user provides. Iterate at most once per goal — don't block progress.

### 6b: Create task issues and link as sub-issues

For each task in the list:

```bash
gh issue create -R $REPO \
  --title "<Clear imperative task title>" \
  --body "## What
<Clear description of what needs to happen>

## Why
Supports goal #<GOAL_NUMBER>: <goal title>

## Done when
<Acceptance criteria — specific, testable>" \
  --label "type.task,status.active,domain.<domain>"
```

After creating each task, link it as a sub-issue of the goal using the shared script (handles fallback automatically):

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/link-sub-issue.sh <GOAL_NUMBER> <TASK_NUMBER> $REPO
```

### 6c: Freeform orphan brain dump

After all goals have tasks, ask via AskUserQuestion:

> "Any other tasks floating in your head that don't belong to a specific goal? Things you need to do but haven't categorized yet? List them, or say 'none' to skip."

If the user provides tasks:

- Create each as a standalone task issue with `type.task,status.active` labels
- Infer the domain label from the task content. If ambiguous, show your best guess to the user inline and let them confirm or correct before creating the issue
- Do NOT link as sub-issues (these are orphan tasks by definition)

If the user says "none" or similar, skip.

---

## Stage 7: Summary and next steps

Present a final summary of everything created during this session.

```
System bootstrapped successfully.

Labels: 20 synced

Milestones: N created
  [list each: "YEAR Domain: Annual goal"]
  [list any skipped: "(Spirit — skipped)"]

Quarterly goals: N active
  [for each: "- #<N> [Domain]: <goal title> (<task count> tasks)"]

Standalone tasks: N created

Next steps:
- Define your daily rituals in Stage 8
- Complete the automation setup in Stage 9
- Run /focus:plan tomorrow morning to select your daily Big 3
- Use /focus:task anytime to add new tasks to any goal
- Use /focus:goal at the start of next quarter to set new quarterly goals
- Use /focus:review to scan Slack and meetings for missed tasks
```

---

## Stage 8: Ritual definition

Ask via AskUserQuestion:

> "The system includes 4 daily rituals (morning, workday startup, workday shutdown, evening) that get posted to your daily thread automatically. Want to define them now?"

Options: "Yes, define my rituals", "Skip for now (I'll run /focus:rituals later)"

**If the user skips**, note: "You can define them anytime with `/focus:rituals`. The automation will post empty placeholders until you do." Then proceed to Stage 9.

**If the user chooses to define rituals**, follow the full interview and save logic from `${CLAUDE_PLUGIN_ROOT}/skills/rituals/SKILL.md` — specifically Steps 2 (full ritual interview), 4 (interview one ritual), and 6 (save to repo). Walk through all 4 rituals in order using that skill's coaching gates and time budgets, then save the result.

---

## Stage 9: Automation setup

The Focus system needs GitHub Actions workflows to automate the daily loop. Without these, no daily threads get created, no journals get compiled, and no reviews get generated.

Ask via AskUserQuestion:

> "The goals, labels, tasks, and rituals are set up. The last step is automation — GitHub Actions that create your daily thread each morning, post ritual checklists at the right times, compile journals at night, and generate weekly reviews. Want me to set this up now?"

Options: "Yes, set up automation", "Skip for now (I'll do it manually)"

**If the user skips**, report what they'll need to do later and move to Stage 10.

**If the user chooses to set up automation**:

### 9a: Check for existing workflows

```bash
gh api /repos/$REPO/contents/.github/workflows --jq '.[].name' 2>/dev/null
```

The 7 expected workflows: `daily-thread.yml`, `rituals.yml`, `journal-compile.yml`, `weekly-review.yml`, `stale-cleanup.yml`, `migration.yml`, `sync-labels.yml`.

If all 7 exist, report: "All workflows already present. No action needed." and skip to Stage 10. If some exist, only generate the missing ones.

### 9b: Locate the repo on disk

Find the local checkout of `$REPO`. Try `gh repo view -R $REPO --json path` first, then check `$HOME/Code/` and `$HOME/code/` for a directory matching the repo name with a `.git/` subdirectory.

If not found, ask via AskUserQuestion: "I can't find a local checkout of $REPO. Where is it cloned on this machine?" with options including "Clone it for me" (runs `gh repo clone $REPO` in `$HOME/Code/`).

### 9c–9d: Generate workflow files

Read `${CLAUDE_PLUGIN_ROOT}/shared/workflows-reference.md` for:

1. The timezone-to-cron mapping table — look up `$TZ_NAME` to get UTC cron expressions for each local time target
2. Complete workflow templates for all 7 workflows

For each workflow template, replace `<TIMEZONE>` with `$TZ_NAME` and replace the cron placeholders (`<6AM_CRON>`, `<830AM_WEEKDAY_CRON>`, etc.) with the computed values. Write each to `<repo-path>/.github/workflows/<filename>.yml`.

For `weekly-review.yml`, the reference doc notes it is too large to template inline — use the birdcar/home repo's implementation as reference and adapt the timezone.

### 9e: Commit, push, and gitignore

```bash
cd <repo-path>
git add .github/workflows/
git commit -m "feat: Add Focus system automation workflows

7 GitHub Actions workflows for the daily productivity loop.
Cron schedules configured for $TZ_NAME."
git push
```

Also add `.qmd/` to `.gitignore` if not already present (the Focus plugin's session-start hook caches goals/tasks there with a 1-hour TTL):

```bash
if ! grep -q '.qmd/' .gitignore 2>/dev/null; then
  echo '.qmd/' >> .gitignore
  git add .gitignore
  git commit -m "chore: Gitignore .qmd/ ephemeral context cache"
  git push
fi
```

Report: "Automation setup complete. N workflows created and pushed. QMD cache gitignored."

---

## Stage 10: Final report

Update the summary from Stage 7 to include rituals and automation status:

```
Automation: 7 workflows created and pushed
  daily-thread.yml     — 6 AM $TZ_NAME daily
  rituals.yml          — 4 cron targets: morning (6 AM), workday startup (8:30 AM weekdays),
                         workday shutdown (5 PM weekdays), evening (9 PM daily)
  journal-compile.yml  — 11 PM $TZ_NAME daily
  weekly-review.yml    — 6 PM $TZ_NAME Sundays
  stale-cleanup.yml    — 9 AM $TZ_NAME Mondays
  migration.yml        — on task close
  sync-labels.yml      — manual trigger

Your first daily thread will appear tomorrow morning at 6 AM.
Run /focus:plan when it arrives to set your Big 3.
```

---

## Edge cases

- **Long session / context pressure**: Keep each domain's interview to 2–3 exchanges. The skill prioritizes breadth (covering all 9 domains) over depth. If a domain's coaching loop is going long, accept what the user has and move on.
- **User skips all domains in Stage 3**: Every domain was skipped. Ask: "You skipped all 9 domains. There's nothing to set up. Would you like to go back and set at least one annual goal?" If the user still declines, report "No milestones created. Run /focus:init again when you're ready." and exit.
- **User selects 0 domains in Stage 4**: Ask: "You didn't select any quarterly focus domains. Would you like to select at least one, or skip quarterly goal setup entirely?" If they skip, jump to Stage 7 with summary reflecting only labels and milestones.
- **gh auth error**: Report "gh CLI auth error — run `gh auth login` and then re-run /focus:init." Stop immediately.
- **Milestone creation failure**: Report the error, note which milestone failed, and continue. Summarize failures in Stage 7.
- **Sub-issue API failure**: The `link-sub-issue.sh` script handles its own fallback (posts a comment). Do not stop — task linkage failure is non-fatal.
- **User runs init on a repo with existing data and chooses "Continue"**: Stage 1 warned them. Proceed normally. New milestones will be created alongside existing ones.
