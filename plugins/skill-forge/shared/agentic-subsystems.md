> **Source:** Adapted from walkinglabs/learn-harness-engineering harness-creator (MIT).

# The Five Agentic Subsystems

## Problem

Every agentic tool — a Claude Code skill, an in-repo harness, a CLI plugin, an MCP server — fails the same way when it's missing one of five concerns. The agent forgets why it's running (no instructions), loses where it is (no state), claims false success (no verification), drifts off-task (no scope), or can't resume tomorrow (no lifecycle). Building any of these tools without all five guarantees recurrence of the same incident class.

This doc is the shared mental model used by `forge-skill`, `forge-harness`, and `improve-skill` to decide what a generated artifact must contain and to score what an existing one is missing.

## Golden Rules

### Every reliable agentic tool implements all five subsystems

The subsystems are not optional layers — they are the minimum surface area an agent runtime expects. Skipping one does not produce a smaller tool; it produces a broken one with a delayed symptom.

### The artifact differs by surface; the contract does not

A harness materializes the five subsystems as repo files. A skill materializes them as frontmatter, body sections, scripts, and retrospective hooks. The contract is identical: instruct, persist, verify, bound, resume.

### The lowest-scoring subsystem is the bottleneck

When scoring an artifact, the weakest subsystem determines the failure mode. Raising the average by improving an already-strong subsystem does not change the observed failure rate.

## The Five Subsystems

| Subsystem        | Harness manifestation                                        | Skill manifestation                                                              | Purpose                                             |
| ---------------- | ------------------------------------------------------------ | -------------------------------------------------------------------------------- | --------------------------------------------------- |
| **Instructions** | `AGENTS.md` / `CLAUDE.md` — startup path, working rules      | `SKILL.md` frontmatter + body — name, description, body steps                    | Tell the agent what it's doing and how              |
| **State**        | `feature_list.json`, `progress.md` — current feature, status | TaskCreate task list, intermediate scratch files in cwd                          | Survive turns; know where you are                   |
| **Verification** | `init.sh` or documented test commands                        | `scripts/` (e.g., `quick_validate.py`) and "before claiming done" body section   | Prove the work actually works before declaring done |
| **Scope**        | Feature dependencies + done criteria                         | Description negative cases ("Do NOT use for...") + explicit out-of-scope section | Prevent overreach and half-finished work            |
| **Lifecycle**    | `session-handoff.md`, end-of-session routine                 | Retrospective agent + `docs/learnings.md` append                                 | Make the next session restartable                   |

## Why Five

Empirically derived, not theoretical. These five are the failure modes that show up in production agent runtimes; other concerns (telemetry, cost accounting, multi-agent coordination) are real but not load-bearing for correctness. The set is not exhaustive — it is the minimum that covers the failure modes that actually cause incidents.

## Per-Subsystem Deep Dives

### 1. Instructions

**What it solves.** The cold-start problem: an agent with no instructions improvises, and improvisation is unaudited.

**Minimum viable artifact.** A single discoverable file telling the agent (a) what this tool is for, (b) how to start, (c) the definition of done. For skills, that file is `SKILL.md` with valid frontmatter and a body. For harnesses, `AGENTS.md` at the repo root.

**How forge-skill checks for it.** `scripts/quick_validate.py:70-99` enforces frontmatter presence, `name`, `description`, and the absence of XML tags. Missing → CRITICAL.

**How forge-harness emits it.** Writes `AGENTS.md` with a startup section that points at `feature_list.json` and the verification command.

**Common omission failure.** "No frontmatter" or "description is a label, not a trigger." The agent never activates, or activates on the wrong prompts.

### 2. State

**What it solves.** Multi-turn coherence. Without explicit state, the agent re-derives its position on every turn and inevitably re-derives it wrong.

**Minimum viable artifact.** A structured representation of "where am I now" that survives across turns. Harnesses use `feature_list.json` + `progress.md`. Skills use TaskCreate task lists during a session and `docs/learnings.md` across sessions.

**How forge-skill checks for it.** Looks for a `docs/learnings.md` placeholder and (for complex skills) a retrospective agent that writes to it. See `shared/skill-anatomy.md`.

**How forge-harness emits it.** Initializes `feature_list.json` with the feature graph and `progress.md` with a single "no feature started" marker.

**Common omission failure.** Skill restarts from scratch every turn. Or, conversely, the skill writes state into the conversation context and loses it on compaction.

### 3. Verification

**What it solves.** False completion claims. An agent saying "done" without evidence is the single most common production failure.

**Minimum viable artifact.** A command — runnable, deterministic, with a non-zero exit code on failure — that the agent MUST run before declaring done. For harnesses, `init.sh`. For skills, the validation scripts under `scripts/` plus an explicit "before claiming done" instruction in the body.

**How forge-skill checks for it.** `scripts/quick_validate.py` runs against the generated SKILL.md and exits non-zero on any CRITICAL failure. The forge-skill skill is required to surface this output to the user before declaring success.

**How forge-harness emits it.** Generates `init.sh` that runs the project's existing test suite (discovered via package.json / pyproject.toml / Cargo.toml) and exits non-zero on failure.

**Common omission failure.** Agent says "I've implemented X and all tests pass" without running tests. The repo is silently broken until a human catches it days later.

### 4. Scope

**What it solves.** Overreach and adjacent-feature drift. Without explicit bounds, the agent expands the task to its natural-language interpretation rather than the user's intent.

**Minimum viable artifact.** Negative cases in the description (skills) or feature dependencies + acceptance criteria (harnesses). The artifact must explicitly state what is NOT in scope, not only what is.

**How forge-skill checks for it.** Description-engineering review (see `shared/description-engineering.md`) requires negative-case anti-triggers. The forge-skill spec phase forces the user to articulate scope before generation.

**How forge-harness emits it.** Each feature entry in `feature_list.json` declares `dependencies: []` and `done_when: ""` fields. Missing either → CRITICAL.

**Common omission failure.** "While I was at it I also refactored X." The user wanted a 50-line change; they got a 500-line PR touching unrelated subsystems.

### 5. Lifecycle

**What it solves.** Session non-resumability. The work between today and tomorrow is invisible if it isn't materialized somewhere readable on next bootstrap.

**Minimum viable artifact.** A handoff file the next session reads before doing anything else. For harnesses, `session-handoff.md` written at end-of-session. For skills, a retrospective agent that appends to `docs/learnings.md` and (optionally) emits a session summary.

**How forge-skill checks for it.** Complex skills (multi-agent, external systems, evolving domain) get a dedicated retrospective agent and command by default. See `shared/skill-anatomy.md`.

**How forge-harness emits it.** Writes `session-handoff.md` template and an end-of-session prompt that fills it in.

**Common omission failure.** Every new session re-discovers the same blockers, re-makes the same decisions, and re-litigates the same trade-offs.

## Validation Heuristic

Score each subsystem 0-5. The artifact's effective quality is `min(scores)`, not the average.

| Score | Meaning                                                    |
| ----- | ---------------------------------------------------------- |
| 0     | Absent. No artifact exists for this subsystem.             |
| 1     | Stub. File exists but has no content the agent can act on. |
| 2     | Partial. Some content; missing one of the required fields. |
| 3     | Acceptable. Meets minimum viable artifact.                 |
| 4     | Strong. Includes negative cases / failure handling.        |
| 5     | Exemplary. Matches the references in this directory.       |

`scripts/quick_validate.py` is the deterministic implementation for skills; it grades Instructions and Scope directly via frontmatter checks. `improve-skill` extends this with State, Verification, and Lifecycle scoring by inspecting `docs/`, `scripts/`, and agent definitions. The equivalent for harnesses is a `validate-harness` script that walks `feature_list.json`, `init.sh`, and `session-handoff.md`.

## Anti-patterns: Skipping a Subsystem

| Skipped subsystem | Observed symptom                                                                                          |
| ----------------- | --------------------------------------------------------------------------------------------------------- |
| Instructions      | Skill never triggers, or triggers on the wrong prompts. Agent improvises a workflow.                      |
| State             | Agent re-discovers context every turn; loses progress on compaction; re-asks the user the same questions. |
| Verification      | False "done" claims. Broken code lands. Test suite is never run.                                          |
| Scope             | Scope creep. Unrelated files modified. PRs balloon. User intent gets relitigated.                         |
| Lifecycle         | Each session starts from zero. Same blockers re-litigated. Learnings never accumulate.                    |

## Related Patterns

- [skill-anatomy.md](skill-anatomy.md) — Concrete directory structure for the skill manifestation
- [references/lifecycle-bootstrap-pattern.md](references/lifecycle-bootstrap-pattern.md) — Deeper treatment of Lifecycle and bootstrap ordering
- [references/memory-persistence-pattern.md](references/memory-persistence-pattern.md) — How State persists across sessions
- [references/context-engineering-pattern.md](references/context-engineering-pattern.md) — Budget operations for Instructions and State
- [references/multi-agent-pattern.md](references/multi-agent-pattern.md) — Scope boundaries between delegated agents
- [references/tool-registry-pattern.md](references/tool-registry-pattern.md) — How Verification commands are registered
- [references/gotchas.md](references/gotchas.md) — Cross-cutting failure modes
