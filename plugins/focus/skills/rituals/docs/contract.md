# Rituals — Contract

## Problem Statement

The Focus system currently has 2 hardcoded rituals (morning embedded in daily thread body, evening as a comment). Full Focus defines 4 personalized rituals: Morning, Workday Startup, Workday Shutdown, and Evening. Each is a user-defined checklist with time estimates, reviewed quarterly. The current system has no way to define, store, or update rituals — they're baked into workflow YAML.

## Goals

1. Users define their own 4 rituals through a coached interview, stored as committed config in the repo
2. GitHub Actions post the right ritual at the right time as comments on the daily thread
3. All ritual comments (and all other daily thread comments) get compiled into the journal by the existing journal-compile workflow
4. Individual rituals can be updated without redefining all 4
5. The init skill includes ritual setup as part of onboarding

## Success Criteria

- [ ] `/focus:rituals` with no args walks through all 4 rituals with examples and coaching
- [ ] `/focus:rituals morning` updates only the morning ritual
- [ ] `/focus:rituals view` displays current ritual definitions
- [ ] Rituals stored as `.focus/rituals.json` committed to the repo (readable by Actions)
- [ ] `rituals.yml` workflow posts 4 rituals at correct times as daily thread comments
- [ ] All ritual comments appear in journal-compile output (already works — comments are compiled)
- [ ] Init skill includes ritual definition in onboarding flow

## Scope Boundaries

### In Scope

- `/focus:rituals` skill (define, update, view)
- `.focus/rituals.json` schema and storage
- Updated `rituals.yml` workflow (4 crons, reads from config)
- Updated `daily-thread.yml` (no longer embeds morning ritual in body — all rituals are comments)
- Updated init skill (adds ritual definition stage)
- Updated `workflows-reference.md` in the plugin

### Out of Scope

- Modifying `/focus:daily` display logic — it already reads comments
- Ritual tracking/analytics (how often completed) — future consideration
- Reminder notifications beyond the Actions cron posts

### Future Considerations

- Quarterly ritual review prompt (detect quarter boundary, suggest re-evaluation)
- Ritual completion tracking (parse checkbox state from comments)

## Design Decisions

| Decision                 | Choice                                                 | Rationale                                                               |
| ------------------------ | ------------------------------------------------------ | ----------------------------------------------------------------------- |
| Storage location         | `.focus/rituals.json` committed to repo                | Actions need to read it; committed file works like `.github/labels.yml` |
| Morning ritual placement | Comment on daily thread (not embedded in body)         | Consistent with other 3 rituals; all are comments that get journaled    |
| Ritual posting times     | Morning=6AM, Startup=8:30AM, Shutdown=5PM, Evening=9PM | Matches typical workday boundaries; configurable via cron               |
| Coaching approach        | Per-ritual examples + "season of life" warning         | Directly from Full Focus methodology                                    |
