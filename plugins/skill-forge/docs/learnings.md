# Learnings — Skill-Forge Plugin

Accumulated observations from improve runs against the skill-forge plugin itself.

## 2026-05-20 — 0.7.0 modernization run

- **Trigger:** user-directed modernization — "use the claude references to update things and make use of modern features better like Hooks, Checkpointing, etc."
- **Before:** Description 22/25, Structure 19/25, Instructions 15/25, Agents/Tools 13/25 (Total: 69/100)
- **After:** Description 22/25, Structure 22/25, Instructions 23/25, Agents/Tools 22/25 (Total: 89/100)
- **Changes applied:**
  - Rewrote `hooks-json-template.md` to cover all 28 event types, all 5 handler types (`command`, `prompt`, `http`, `mcp_tool`, `agent`), the `if` filter, `asyncRewake`, `once`, `terminalSequence`, full universal output schema, and modern env vars
  - Rewrote `plugin-json-template.md` to cover all 18 manifest fields (added `displayName`, `userConfig`, `dependencies`, `monitors`, `channels`, `outputStyles`, `lspServers`, `experimental.themes`)
  - Replaced `TodoWrite` references with `Task*` family across `primitives-guide.md`, `agent-design.md`, `agent-template.md`, both SKILL.md files, and all four eval-pipeline commands
  - Added new tools section to `primitives-guide.md`: `Monitor`, `LSP`, `EnterPlanMode`/`ExitPlanMode`, `EnterWorktree`/`ExitWorktree`, `Cron*`, `RemoteTrigger`, `PushNotification`, `SendMessage`, `NotebookEdit`, `Skill`, `ShareOnboardingGuide`
  - Added `checkpointing.md` documenting when to embed Bash/checkpoint warnings in generated skills
  - Updated `skill-anatomy.md` to document the single-file plugin auto-loading pattern (v2.1.142+) and path-rule semantics (additive vs replacement)
  - Updated `agent-design.md` and `agent-template.md` with modern frontmatter (`effort`, `maxTurns`, `isolation`, `background`, `disallowedTools`) and current model IDs (Opus 4.7, Sonnet 4.6, Haiku 4.5)
  - Added `Write` to `tools:` lists of `analyzer`, `comparator`, `grader`, `skill-validator` agents (they write JSON/MD output)
  - Canonicalized `feedback.json` `next_action` enum to `"iterate" | "accept" | "reject"` — updated `generate_report.py` form to match the schema and command
  - Fixed `run_eval.py` ↔ `eval-skill.md` signature mismatch: added `--config-label` to invocations, removed unsupported `--skill-path`, corrected model ID drift (`claude-sonnet-4-5` → `claude-sonnet-4-6`)
  - Fixed `aggregate_history.py` to read schema-correct nested fields (`changes.applied`/`changes.skipped`, `scores.after.{dim}`, `description_changed`, `trigger_test_results.should_trigger_accuracy`) — falls back to legacy flat fields for compatibility
  - Raised `quick_validate.py` severity for `kebab_name_field` and `kebab_directory_name` from HIGH to CRITICAL (matches anti-patterns and quality-checklist)
  - Standardized command `allowed-tools` format on YAML list across `forge-skill.md`, `improve-skill.md`, `eval-skill.md`, `optimize-description.md`
  - Reconciled `local-config-pattern.md` variables (use `${CLAUDE_PLUGIN_ROOT}` for plugin scripts, `${CLAUDE_SKILL_DIR}` for project/global skills) and added a guidance preamble pointing at `userConfig` as the modern alternative for install-time prompts
  - Thinned `quality-checklist.md` — removed the duplicate 16-check table (now lives only in `skill-validator.md`) and the 20-query trigger spec (lives only in `trigger-test-template.md`)
  - Added a `Modern primitives` row to the skill-validator check table — scans generated content for deprecated `TodoWrite` references and stale model IDs
  - Reconciled the inline-hooks rule: re-tested on v2.1.146, inline `hooks: {...}` in `plugin.json` is now valid — updated `hooks-json-template.md` to document both placements and noted the historical "Invalid input" error has been fixed
  - Updated the project-level `MEMORY.md` to reflect the corrected inline-hooks support and the modern handler-type roster
  - Archived `docs/ideation/` (superseded by `docs/spec.md`) and `docs/2026-03-25-skill-forge-improvements-design.md` (shipped) under `docs/archive/`
  - Added a 0.7.0 modernization section to `docs/contract.md` recording the design intent
  - Bumped plugin version 0.6.0 → 0.7.0
- **Changes skipped:** none — all proposed buckets (Modernize / Bug fixes / Cleanup) were applied
- **Notes:**
  - The "Invalid input" inline-hooks error documented in the prior MEMORY note is no longer reproducible on v2.1.146 — verified with `claude plugin validate --strict`. The fix is undated in the docs, so older Claude Code installs may still hit it.
  - Verified `aggregate_history.py` reads schema-shape entries correctly against a synthetic 2-entry history (description trend 22→24, total 85→88, applied-change frequency counted)
  - Verified `quick_validate.py` reports `kebab_name_field` and `kebab_directory_name` as CRITICAL severity
  - Marketplace validates clean with `claude plugin validate --strict .` from repo root

## 2026-05-20 — 0.7.1 self-improvement run

- **Trigger:** systematic improvement (no braindump) — improve both create-skill and improve-skill sequentially
- **Scope:** both `create-skill` and `improve-skill` SKILL.md files, plus supporting agents/templates/spec
- **Before:** create-skill 84/100 (Description 22, Structure 21, Instructions 19, Agents/Tools 22); improve-skill 83/100 (Description 22, Structure 21, Instructions 18, Agents/Tools 22)
- **After:** create-skill 91/100 (Description 23, Structure 23, Instructions 23, Agents/Tools 22); improve-skill 90/100 (Description 23, Structure 23, Instructions 22, Agents/Tools 22)
- **Changes applied:**
  - **P0 — TodoWrite drift fix (5 files):**
    - `skills/improve-skill/SKILL.md` lines 160 + 219 → `TaskCreate/TaskUpdate`
    - `docs/spec.md` lines 158 + 166 → `TaskCreate/TaskUpdate`
    - `shared/workflow-patterns.md` lines 30, 101, 184 → `TaskCreate/TaskUpdate` in all three pattern descriptions
    - `shared/templates/command-template.md` rows 22–23 → `TaskCreate, TaskUpdate, TaskList` in both `allowed-tools` rows
    - `commands/eval-skill.md` line 99 → `TaskCreate ... TaskUpdate`
  - **P1 — Hook/Agent post-0.7.0 inconsistencies:**
    - `agents/skill-generator.md` Critical Rule and Constraint rewritten — inline hooks in plugin.json now permitted, matching validator and hooks-json-template
    - `agents/scaffold-writer.md` line 43 rewritten — same change
    - `agents/skill-generator.md` tools list gains `Agent` (its own line 56 requires it for parallel-phase spawning)
  - **P2 — Description tweaks:**
    - `create-skill` description adds "add a skill" trigger phrase and names `improve-skill` as the alternative for modification requests
    - `improve-skill` description tightens "points to..." → "references..." and names `code-review` as the alternative for non-skill review
  - **P3 — Step 4b structural fix:**
    - `skills/create-skill/SKILL.md` Step 4b folded into Step 4 as `### Optional: Eval Testing`
    - `skills/improve-skill/SKILL.md` Step 4b folded into Step 4 as `### Optional: Eval Comparison`
    - Re-aligns both SKILL.md files with the spec's stated 6-step pipeline
  - **Version:** plugin.json 0.7.0 → 0.7.1
- **Changes skipped:** none — all proposed buckets (P0/P1/P2/P3) were applied
- **Notes:**
  - The 0.7.0 modernization run's history-record claimed it had replaced `TodoWrite` across "both SKILL.md files" but two lines of `improve-skill/SKILL.md` and four other live references survived. This is a recurring drift pattern — see Pattern watch below.
  - Self-contradiction surfaced cleanly: the improve-skill Critical Rule (line 20) told the auditor to flag `TodoWrite` as outdated, while line 160 of the same file instructed the operator to use `TodoWrite`. Internal-consistency checks (Critical-Rules ↔ body) should be a first-class validator scan.
  - The hooks-placement rule still lived in two agent prompts (`skill-generator.md`, `scaffold-writer.md`) even after `hooks-json-template.md` was modernized. Agent prompts need their own audit pass when shared templates are modernized.

## Pattern watch

- **Cross-file drift survives "we updated all files" claims (now 2 occurrences).** 0.7.0 modernization claimed coverage of "both SKILL.md files" but 6 live `TodoWrite` references survived across 5 files. 0.7.1 modernization caught them. If this recurs in 0.7.2: add a grep-based CI check in the marketplace's CI to fail on `TodoWrite` outside known deprecation-doc contexts.
- The agent tools-list mismatch (Write missing on agents that wrote files) appeared in 4 of 10 agents. If this recurs after the 0.7.0 fix, consider a generator rule: when an agent's prompt contains "write `<filename>`", auto-grant `Write` in the tools list. **Update 0.7.1:** same class of bug recurred for `skill-generator` missing `Agent` despite its own instructions saying "spawn concurrent agents via the Agent tool" — generalize the rule: scan agent prompts for tool names and reconcile against the `tools:` frontmatter list.
- The eval pipeline accumulated 3 separate `next_action`-enum disagreements before being caught. Treat `eval-schemas.md` as the canonical source and add a CI check that grep'd source matches schema enums.
- **Agent-prompt drift after shared-template modernization (new in 0.7.1).** When `hooks-json-template.md` was modernized to allow inline `plugin.json` hooks, the validator was updated but `skill-generator.md` and `scaffold-writer.md` retained the old "never inline" rule. Modernization runs should treat agent-prompt scans as a required phase after shared-doc edits.
