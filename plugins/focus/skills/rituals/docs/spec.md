# Rituals — Spec

## Component Manifest

| File                                              | Purpose                                                         |
| ------------------------------------------------- | --------------------------------------------------------------- |
| `plugins/focus/skills/rituals/SKILL.md`           | `/focus:rituals` — define, update, and view the 4 daily rituals |
| `plugins/focus/shared/rituals-schema.md`          | JSON schema reference for `.focus/rituals.json`                 |
| `birdcar/home/.focus/rituals.json`                | Committed ritual definitions (readable by Actions)              |
| `birdcar/home/.github/workflows/rituals.yml`      | Updated: 4 crons, reads from `.focus/rituals.json`              |
| `birdcar/home/.github/workflows/daily-thread.yml` | Updated: remove embedded morning ritual from body               |
| `plugins/focus/shared/workflows-reference.md`     | Updated: new rituals.yml template with 4 crons                  |
| `plugins/focus/skills/init/SKILL.md`              | Updated: add ritual definition stage after Stage 7              |

## Skill Architecture

Context-aware single-skill. Branches on `$ARGUMENTS`:

- No args → full 4-ritual interview
- `morning` / `workday-startup` / `workday-shutdown` / `evening` → single ritual update
- `view` → display current rituals

Config stored as `.focus/rituals.json` in the target repo (committed). Skill reads/writes via `gh api` to fetch file contents and commit updates. No local-only config — Actions must read the same data.

The rituals.yml workflow runs 4 cron jobs (one per ritual time). Each reads `.focus/rituals.json`, extracts the relevant ritual's checklist, and posts it as a comment on today's daily thread. The journal-compile workflow already compiles all comments — no changes needed there.

## rituals.json Schema

```json
{
  "version": 1,
  "updated": "2026-04-11",
  "rituals": {
    "morning": {
      "items": [
        { "text": "Meditate for 10 minutes", "minutes": 10 },
        { "text": "Journal 3 gratitudes", "minutes": 5 }
      ],
      "total_minutes": 15
    },
    "workday-startup": {
      "items": [
        { "text": "Review Big 3 for today", "minutes": 5 },
        { "text": "Clear inbox to zero", "minutes": 15 }
      ],
      "total_minutes": 20
    },
    "workday-shutdown": {
      "items": [
        { "text": "Process inbox", "minutes": 10 },
        { "text": "Review tomorrow's calendar", "minutes": 5 }
      ],
      "total_minutes": 15
    },
    "evening": {
      "items": [
        { "text": "Wins today", "minutes": 3 },
        { "text": "Gratitude", "minutes": 2 },
        { "text": "Tomorrow's #1 priority", "minutes": 2 }
      ],
      "total_minutes": 7
    }
  }
}
```

## Per-Component Details

### SKILL.md (`plugins/focus/skills/rituals/SKILL.md`)

- **Purpose**: Define, update, and view the 4 Full Focus daily rituals
- **Key behaviors**:
  - Resolves config via `resolve-config.sh` (same preamble as all focus skills)
  - `view` mode: fetches `.focus/rituals.json` from repo via `gh`, displays formatted
  - Single-ritual mode: fetches current config, interviews for just that ritual, writes back
  - Full mode: interviews for all 4 rituals sequentially with coaching
  - Coaching: season-of-life warning, time-budget realism, examples per ritual type
  - Writes `.focus/rituals.json` to repo via `gh api` (commit to main)
- **Tools**: Bash, AskUserQuestion

### rituals-schema.md (`plugins/focus/shared/rituals-schema.md`)

- **Purpose**: Reference doc for the JSON schema, loaded by SKILL.md via `references/` convention
- **Key behaviors**: Documents the schema, field meanings, constraints

### rituals.yml (`birdcar/home/.github/workflows/rituals.yml`)

- **Purpose**: Post ritual checklists as comments on the daily thread at 4 times
- **Key behaviors**:
  - 4 cron schedules (morning 6AM, startup 8:30AM, shutdown 5PM, evening 9PM CT)
  - Reads `.focus/rituals.json` from repo using `cat` after checkout
  - Extracts the relevant ritual using `jq`
  - Formats as markdown checklist with time column
  - Posts as comment on today's daily thread via `gh issue comment`
  - `workflow_dispatch` with ritual type input for manual triggers

### daily-thread.yml (`birdcar/home/.github/workflows/daily-thread.yml`)

- **Purpose**: Remove the embedded `## Morning Ritual` section from the thread body
- **Key behaviors**: The morning ritual is now a comment (posted by rituals.yml), not part of the body. Body keeps: Big 3 + Goal Context only.

### init/SKILL.md (edit)

- **Purpose**: Add ritual definition to onboarding
- **Key behaviors**: New stage between current Stage 7 (summary) and Stage 8 (automation) that runs the `/focus:rituals` interview pattern inline

## Execution Plan

### Phase 1: Foundation (no deps)

- `plugins/focus/shared/rituals-schema.md`
- `plugins/focus/skills/rituals/SKILL.md`

### Phase 2: Repo config + workflow updates (depends on Phase 1 for schema)

- `birdcar/home/.focus/rituals.json` (initial placeholder)
- `birdcar/home/.github/workflows/rituals.yml` (rewrite with 4 crons)
- `birdcar/home/.github/workflows/daily-thread.yml` (remove morning ritual from body)

### Phase 3: Plugin updates (depends on Phase 1)

- `plugins/focus/skills/init/SKILL.md` (add ritual stage)
- `plugins/focus/shared/workflows-reference.md` (update rituals template)

Phases 2 and 3 are parallelizable.

## Retrospective Configuration

- **Recommendation**: lightweight
- **Rationale**: Single skill, no agents, but evolving domain (ritual content changes quarterly). Learnings file sufficient.
- **Components**: `docs/learnings.md`

## Validation Strategy

- SKILL.md <=500 lines, correct frontmatter, config preamble present
- rituals.json matches schema
- rituals.yml has 4 cron expressions, reads from `.focus/rituals.json`
- daily-thread.yml no longer has `## Morning Ritual` section
- init/SKILL.md has ritual stage
- `bun run typecheck && bun run format:check` pass in marketplace repo
