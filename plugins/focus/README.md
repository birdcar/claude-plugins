# Focus

A personal productivity system for Claude Code that uses GitHub Issues as its data layer. Inspired by the [Full Focus Planner](https://fullfocusplanner.com/), it maps annual goals to quarterly outcomes to daily tasks -- and gives you a coached planning workflow to keep everything connected.

The mental model: GitHub Milestones hold your annual goals across 9 life domains. Issues labeled `type.goal` are your quarterly outcomes, assigned to those milestones. Tasks are sub-issues of goals. Every morning, a GitHub Action creates a daily thread where you pick your Big 3 tasks for the day. At night, the thread compiles into a journal entry and closes.

## Prerequisites

- [Claude Code](https://claude.com/download) with plugin support
- [`gh` CLI](https://cli.github.com/) authenticated (`gh auth login`)
- `jq` installed
- A GitHub repository to use as your data store (can be private)

## Install

```
claude plugin install focus@birdcar-plugins
```

## Quick start

Run `/focus:init` in any Claude Code session. It walks you through:

1. Configuring your target repo and timezone
2. Syncing 20 labels (status, type, domain) to the repo
3. Setting annual goals across all 9 life domains (Body, Mind, Spirit, Love, Family, Money, Community, Hobbies, Work)
4. Selecting 2-4 domains to focus on this quarter
5. Defining quarterly goals with coaching on vagueness, measurability, and overcommitment
6. Brain-dumping initial tasks for each goal
7. Defining daily rituals (morning, workday startup, workday shutdown, evening)
8. Generating 7 GitHub Actions workflows for automation

The whole thing takes 15-30 minutes depending on how many domains you set up. It's safe to re-run -- it warns before adding to existing data.

## Commands

| Command          | What it does                                                                        |
| ---------------- | ----------------------------------------------------------------------------------- |
| `/focus:init`    | One-time bootstrap: labels, milestones, goals, tasks, rituals, automation           |
| `/focus:plan`    | Score your goals and tasks, propose today's Big 3, update the daily thread          |
| `/focus:daily`   | View today's thread -- Big 3 status, ritual progress, recent activity               |
| `/focus:goal`    | Create a quarterly goal with coached interview and task decomposition               |
| `/focus:goals`   | View the full cascade (milestones -> goals -> tasks) or trace a specific issue      |
| `/focus:task`    | Create a task. Clear input creates directly; vague input triggers a short interview |
| `/focus:labels`  | Sync the 20-label taxonomy. Use `scan` argument to find non-canonical labels        |
| `/focus:rituals` | Define or update your 4 daily rituals with time budgets and coaching                |
| `/focus:review`  | Scan Slack, Granola, Gmail, and Google Calendar for missed action items             |

## Daily workflow

**Morning**: `/focus:plan` scores your active goals by due date proximity, task count, and recent activity, then proposes 3 tasks. You approve or adjust, and it updates the daily thread.

**During the day**: `/focus:daily` shows your thread. Pass a message to log activity as a comment. Use `/focus:task` to capture anything new.

**End of day**: `/focus:review` scans your external tools for commitments you made in Slack threads, meetings, and email. It creates tasks for new items and comments on existing tasks that look resolved (never auto-closes). The evening ritual checklist gets posted to your thread automatically.

**Overnight**: The journal-compile workflow archives the day's thread to `journals/YYYY/MM/DD.md` and closes the issue.

## Automation

Init generates 7 GitHub Actions workflows with cron schedules adjusted to your timezone:

- **daily-thread.yml** -- Creates a new daily thread at 6 AM with Big 3 placeholders and goal context
- **rituals.yml** -- Posts ritual checklists at 4 times: morning (6 AM), workday startup (8:30 AM weekdays), workday shutdown (5 PM weekdays), evening (9 PM)
- **journal-compile.yml** -- Compiles the day's thread + comments into a markdown journal at 11 PM, then closes the thread
- **weekly-review.yml** -- Generates a weekly review at 6 PM Sunday with completion stats, Big 3 hit rate, and goal progress. Includes a quarterly check-in on quarter boundaries
- **stale-cleanup.yml** -- Labels tasks with no activity for 30+ days as `status.stale` on Monday mornings. Posts a triage comment but never auto-closes
- **migration.yml** -- Fires when a task is closed. Updates parent goal progress and flags when all subtasks are complete
- **sync-labels.yml** -- Manual trigger to sync labels from `.github/labels.yml`

## The coaching model

Focus pushes back when your input is vague, unmeasurable, or overambitious. During goal creation, it will tell you "that's too vague to track" or "this sounds like 2-3 separate goals." During task creation, it scores your input on 4 dimensions (what, why, done criteria, scope) and only interviews you on the weak spots.

The coaching is firm but not blocking. If you say "I know, just create it," it moves on.

## Configuration

Focus stores config at `~/.config/focus/config.json`:

```json
{ "repo": "owner/repo", "timezone": "America/Chicago" }
```

Config resolution checks three locations in order: the `FOCUS_REPO` / `FOCUS_TZ` environment variables, a `.focus/config.json` walking up from cwd, then the global XDG config.

## Label taxonomy

20 labels across 3 categories:

- **Status** (6): `active`, `blocked`, `waiting`, `stale`, `done`, `cancelled`
- **Type** (5): `goal`, `task`, `daily-thread`, `review`, `note`
- **Domain** (9): `body`, `mind`, `spirit`, `love`, `family`, `money`, `community`, `hobbies`, `work`

Every issue gets exactly one type label, one status label, and one or more domain labels.

## Limitations

- The review skill requires MCP integrations for Slack, Granola, Gmail, and Google Calendar to be connected in your Claude Code session. If a source isn't available, it skips it.
- GitHub Actions cron is UTC-only, so DST shifts the effective local time by an hour twice a year.
- The weekly review workflow is large and references the `birdcar/home` repo's implementation during generation -- it's not fully self-contained in the template.
- Sub-issue linking uses the GitHub GraphQL API. If that fails, it falls back to posting a comment on the parent goal. The linkage is nice-to-have, not critical.
- This is a personal productivity tool. It has coaching opinions baked in (time budgets for rituals, pushback on vague goals, Big 3 limit). If you want a neutral task tracker, this isn't it.
