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

## 2026-05-20 — 0.8.0 harness-creator integration

- **Trigger:** braindump — "steal from harness-creator to improve our creation of skills and make it possible for skills to be self improving and even full harnesses / harness creators"
- **Scope:** major. Three phases of net-new work.
- **Before:** create-skill 91/100, improve-skill 90/100, forge-harness did not exist (this was a scope-expansion run, not a self-improvement of existing skills)
- **After:** create-skill 100/100, improve-skill 100/100, forge-harness 100/100 (all per `scripts/validate-skill.mjs`)
- **Changes applied:**
  - **Phase 7 — Knowledge base lift:**
    - Copied 6 reference docs from `walkinglabs/learn-harness-engineering` harness-creator (MIT) into `shared/references/` with attribution: `memory-persistence-pattern.md`, `context-engineering-pattern.md`, `tool-registry-pattern.md`, `multi-agent-pattern.md`, `lifecycle-bootstrap-pattern.md`, `gotchas.md`
    - Wrote `shared/agentic-subsystems.md` — the 5-subsystem mental model (Instructions / State / Verification / Scope / Lifecycle) shared between forge-skill and forge-harness
    - Restructured `shared/anti-patterns.md` to the Problem → Golden Rules → Trade-offs → Implementation Patterns → Gotchas → Related Patterns shape used by the ported reference docs. All 36 original anti-patterns preserved with their severity tags.
    - Wrote `scripts/validate-skill.mjs` — pure Node-built-ins deterministic structural validator that scores any skill across the 5 subsystems. Outputs JSON or HTML. Self-tests against all three existing skills pass.
  - **Phase 8 — Self-improving generated skills:**
    - Wrote `shared/templates/evals-template.json` and `shared/templates/validate-mjs-template.mjs`. Every skill generated by skill-forge now ships with `evals/evals.json` and `evals/validate.mjs`.
    - Updated `agents/skill-generator.md` to emit the new `evals/` artifacts (new Process step 10)
    - Updated `agents/skill-validator.md` to delegate structural checks to `scripts/validate-skill.mjs`. Removed the 18-row inline structural check table. Validator retains only semantic checks not detectable by grep.
    - Updated `agents/skill-optimizer.md` to consume per-skill `evals/validate.mjs` output during Step 2 analysis. Structural Compliance dimension sourced from the deterministic script.
    - Updated `skills/create-skill/SKILL.md` Step 4 to mention the evals/ artifacts; Step 5 to run validate-skill.mjs before spawning the validator agent
    - Updated `skills/improve-skill/SKILL.md` Step 5 to run per-skill validate.mjs when present
  - **Phase 9 — `forge-harness` sibling skill:**
    - Wrote `skills/forge-harness/SKILL.md` — scaffolds AGENTS.md/CLAUDE.md + feature_list.json + progress.md + init.sh + session-handoff.md into a target repo. Three intents: create, audit, report.
    - Wrote `commands/forge-harness.md` (thin entry-point wrapper)
    - Copied 6 templates into `shared/templates/harness/` from harness-creator
    - Ported `scripts/create-harness.mjs` and `scripts/validate-harness.mjs` (with `scripts/lib/harness-utils.mjs`) from harness-creator with attribution
    - Updated `agents/intake-analyst.md` to recognize harness-scaffolding intents and route to forge-harness. New artifact type: `harness-scaffold`. New required `Routing:` output field.
    - Wrote `skills/forge-harness/trigger-tests.md` (20 queries: 10 should-trigger, 10 should-not-trigger with cross-sibling-skill redirects)
    - Wrote `skills/forge-harness/evals/evals.json` (6 eval cases covering the 5-subsystem scaffolding flow + a misuse case)
    - Wrote `skills/forge-harness/evals/validate.mjs` (per-skill validator that wraps the plugin-level script + asserts evals.json shape)
  - **Phase 10 — Plugin metadata:**
    - Bumped `plugin.json` version 0.7.1 → 0.8.0
    - Updated plugin description to acknowledge harness scaffolding
    - Updated `docs/contract.md` with 0.8.0 problem statement extension, new goals 6 and 7, new success criteria, and a 0.8.0 in-scope section
    - Updated `docs/spec.md` with new component manifest tables, Phase 7/8/9/10 execution plan, and dependency graph
    - Ran `bun run sync`, `bun install` (no lockfile drift), `bun run format` (reformatted the .mjs files Prettier-style), `bun run format:check` (clean), `bun run typecheck` (clean), `bun run build` (clean)
- **Changes skipped:** none — every approved scope item shipped
- **Notes:**
  - Cross-agent compatibility (claude-code/codex/cursor/windsurf) was REAFFIRMED as out-of-scope despite harness-creator's `metadata.json` modeling it. skill-forge stays Claude-Code-targeted.
  - The 5-subsystem mental model from harness-creator now lives in `shared/agentic-subsystems.md` and is the framework BOTH forge-skill and forge-harness use to reason about output. This eliminated the need for separate quality frameworks per generator.
  - `scripts/validate-skill.mjs` (344 lines) and `scripts/validate-harness.mjs` (44 lines + 407-line shared lib) are now the deterministic backstops. Future runs of `improve-skill` source the Structural Compliance dimension directly from validate-skill.mjs output instead of LLM-re-scoring.
  - One Prettier hiccup discovered during Phase 10: `{{COMPONENT_MANIFEST}}` placeholder in `validate-mjs-template.mjs` produced invalid JS for the linter. Fix: replaced with `JSON.parse('{{COMPONENT_MANIFEST_JSON}}')` so the file is valid syntax even before substitution. Pattern for future templates: every placeholder must keep the surrounding file syntactically valid.
  - The Phase 9 background agent independently confirmed the validate-skill.mjs score for forge-harness moved from 84/100 (missing trigger-tests.md) to 100/100 after it wrote the trigger-tests, evals.json, and evals/validate.mjs files. This is the eval loop working end-to-end on a brand-new skill.
- **Validation:**
  - All three skills (create-skill, improve-skill, forge-harness) score 100/100 on `scripts/validate-skill.mjs`
  - forge-harness's per-skill `evals/validate.mjs` returns PASS with 6 well-formed eval cases
  - `bun run typecheck && bun run build && bun run format:check` all clean
  - Marketplace sync updated (`bun run sync` discovered all 11 plugins including the version bump)

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

## 2026-05-29 — 0.9.0 forge-harness stack-coverage run

- **Target skill:** `forge-harness`
- **Trigger:** user braindump — "make forge-harness aware of PHP (Laravel, Filament) and Python (FastAPI, FastMCP, Django, uv, Typer)."
- **Before:** Description 21/25, Structure 25/25, Instructions 16/25, Agents/Tools 22/25 (Total: 84/100)
- **After:** Description 24/25, Structure 25/25, Instructions 23/25, Agents/Tools 22/25 (Total: 94/100)
- **Changes applied:**
  - **Critical bug fix:** `harness-utils.mjs` `TEMPLATE_DIR` pointed at `<plugin>/templates`, but the harness templates live at `shared/templates/harness/`. `create-harness.mjs` died with `ENOENT … templates/agents.md` on every run — the entire `create` intent was non-functional and had been since the 0.8.0 port. Found only because the PHP/Python work required running the script against fixtures.
  - **PHP/Laravel/Filament detection:** `detectProject` now reads `composer.json` and resolves `php-laravel` (when `laravel/framework` or `artisan` is present) or `php`. Checked **before** `package.json` because Laravel/Filament apps ship both manifests (Vite assets) and the PHP backend is the primary verification stack.
  - **Python granularity:** `python-django` when `manage.py`/`django` present; reads `pyproject.toml` as raw text (no TOML dependency — keeps the "pure Node built-ins" constraint).
  - **Verification commands:** PHP = `composer install` + composer-scripts-first (`lint`/`analyse`/`test`) with framework fallback (`pint --test`, `php artisan test`, `pest`/`phpunit`); Python = uv-aware (`uv sync` + `uv run` prefix on `uv.lock`/`[tool.uv]`), `ruff check`, `ty check`, `manage.py test` for Django else `pytest`.
  - SKILL.md description gained PHP + framework keywords (trigger surface); contract.md/spec.md updated spec-first; two eval cases (Laravel-beats-Node, Python-uv-Django) and two stack-specific trigger queries added; `plugin.json` 0.8.0 → 0.9.0.
- **Changes skipped:** did not spawn skill-optimizer/skill-validator sub-agents — the defect lived in the deterministic `.mjs` engine, which the optimizer's four-dimension _prose_ rubric does not score; inline analysis with runtime fixture proof was higher-fidelity.
- **Notes:**
  - The braindump named FastAPI, FastMCP, and Typer specifically, but those are libraries with no reliable filesystem fingerprint distinct from "a Python project using uv." They are now served implicitly: a FastAPI/FastMCP/Typer app managed with uv gets `uv sync` + `uv run pytest` (+ ruff/ty), which is the correct baseline. Only Django earns a distinct branch because `manage.py` changes the test command.

## Pattern watch

- **Cross-file drift survives "we updated all files" claims (now 2 occurrences).** 0.7.0 modernization claimed coverage of "both SKILL.md files" but 6 live `TodoWrite` references survived across 5 files. 0.7.1 modernization caught them. If this recurs in 0.7.2: add a grep-based CI check in the marketplace's CI to fail on `TodoWrite` outside known deprecation-doc contexts.
- The agent tools-list mismatch (Write missing on agents that wrote files) appeared in 4 of 10 agents. If this recurs after the 0.7.0 fix, consider a generator rule: when an agent's prompt contains "write `<filename>`", auto-grant `Write` in the tools list. **Update 0.7.1:** same class of bug recurred for `skill-generator` missing `Agent` despite its own instructions saying "spawn concurrent agents via the Agent tool" — generalize the rule: scan agent prompts for tool names and reconcile against the `tools:` frontmatter list.
- The eval pipeline accumulated 3 separate `next_action`-enum disagreements before being caught. Treat `eval-schemas.md` as the canonical source and add a CI check that grep'd source matches schema enums.
- **Agent-prompt drift after shared-template modernization (new in 0.7.1).** When `hooks-json-template.md` was modernized to allow inline `plugin.json` hooks, the validator was updated but `skill-generator.md` and `scaffold-writer.md` retained the old "never inline" rule. Modernization runs should treat agent-prompt scans as a required phase after shared-doc edits.
- **Ported scripts carry origin-repo path assumptions (new in 0.9.0).** The 0.8.0 harness-creator port left `TEMPLATE_DIR` pointing at `<root>/templates` (correct in the origin repo) while skill-forge placed the templates at `shared/templates/harness/`. No eval or validator exercised the script's runtime path, so the broken `create` flow shipped silently and survived two releases. **Lesson:** when porting a bundled script, the integration step must run it end-to-end against a fixture, not just validate that the files exist. If this recurs: add a smoke test (`node create-harness.mjs --target <tmp-fixture>` asserting non-zero files written) to the marketplace CI rather than relying on structural validators that never execute the script.
