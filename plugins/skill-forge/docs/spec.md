# Skill-Forge Harness Evolution — Spec

## Component Manifest

### New Files

| File                                               | Purpose                                                                                                                                                                                                                                                                                                                                                                       |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `agents/retrospective.md`                          | Skill-forge's own retrospective agent. Analyzes forge/improve runs, appends to learnings, proposes knowledge base updates after repeated patterns. Sonnet model. Tools: Read, Glob, Grep, Write, Edit.                                                                                                                                                                        |
| `shared/learnings.md`                              | Timestamped observations from retrospective runs. Accumulates patterns. When a pattern appears 3+ times, the retrospective proposes a concrete update to the relevant reference doc.                                                                                                                                                                                          |
| `shared/templates/contract-template.md`            | Template for contract.md documents generated in created skills. Sections: Problem Statement, Goals, Success Criteria, Scope Boundaries, Design Decisions.                                                                                                                                                                                                                     |
| `shared/templates/spec-template.md`                | Template for spec.md documents generated in created skills. Sections: Component Manifest, Skill Architecture, Per-Component Details, Execution Plan, Retrospective Configuration, Validation Strategy.                                                                                                                                                                        |
| `shared/templates/retrospective-agent-template.md` | Template for retrospective agents generated in complex skills. Mirrors skill-forge's own retrospective pattern: analyze session, append to learnings, propose knowledge base updates. Sections: Role, Input (learnings file path, session context), Process (analyze, classify, append, propose), Output Format, Constraints (never modify target code, only knowledge base). |

### Modified Files

| File                            | Changes                                                                                                                                                                                                                                                                          |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `skills/create-skill/SKILL.md`  | Pipeline restructured from 8 to 6 steps. Confidence gate replaced by spec formation loop. Generation plan approval removed. Name selection moved to step 2. Retrospective added as step 6.                                                                                       |
| `skills/improve-skill/SKILL.md` | Three-way analysis when spec exists. Spec-first updates. Retroactive spec generation offer. Score history to learnings.md. Retrospective as final step.                                                                                                                          |
| `agents/skill-generator.md`     | Primary input becomes spec.md. Follows execution plan for ordering and parallelization. Reports deviations from spec. Still reads shared/ for writing quality guidance.                                                                                                          |
| `agents/intake-analyst.md`      | Adds retrospective complexity classification to output: full (agent + command + learnings), lightweight (learnings only), or none. Based on: multi-agent, external systems, evolving domain, state management.                                                                   |
| `agents/skill-optimizer.md`     | Reads spec alongside skill when spec exists. Three-way analysis (spec + skill + braindump). Updates spec before proposing skill changes. Offers retroactive spec generation when no spec found.                                                                                  |
| `agents/skill-researcher.md`    | Timing change only: runs during spec formation (before spec is written) instead of after confidence gate. Agent instructions unchanged.                                                                                                                                          |
| `agents/skill-validator.md`     | Adds spec compliance checking: verifies generated artifacts match the spec's component manifest. Checks for files in the spec not created, or files created not in the spec.                                                                                                     |
| `shared/quality-checklist.md`   | Adds spec compliance checks: did generated artifacts match the spec's component manifest? Are there files in the spec not created, or files created not in the spec?                                                                                                             |
| `shared/skill-anatomy.md`       | Documents the `docs/` directory convention: contract.md (design intent), spec.md (execution plan), learnings.md (accumulated observations). Explains permanence and gitignore option.                                                                                            |
| `shared/anti-patterns.md`       | New anti-patterns: spec drift (skill diverges from spec without updating it), empty learnings files (created but never written to), retrospective agents that modify target code instead of knowledge base, specs that describe implementation details instead of design intent. |
| `plugin.json`                   | Version bump 0.3.0 → 0.4.0. Register retrospective agent.                                                                                                                                                                                                                        |

All files not listed in New or Modified are unchanged (scaffold-writer, command entry points, and shared reference docs for description-engineering, agent-design, workflow-patterns, primitives-guide, and local-config-pattern).

### 0.8.0 Additions (Harness-Creator Integration)

**New files (Phase 1 — Knowledge base lift):**

| File                                               | Purpose                                                                                                                                                                                |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `shared/agentic-subsystems.md`                     | 5-subsystem mental model (Instructions / State / Verification / Scope / Lifecycle) ported from harness-creator. Shared mental framework for forge-skill and forge-harness. ~150 lines. |
| `shared/references/memory-persistence-pattern.md`  | Ported from harness-creator with attribution. Memory layers, two-step save, local-wins priority. ~110 lines.                                                                           |
| `shared/references/context-engineering-pattern.md` | Ported from harness-creator with attribution. SELECT / WRITE / COMPRESS / ISOLATE operations and context budgets. ~150 lines.                                                          |
| `shared/references/tool-registry-pattern.md`       | Ported from harness-creator with attribution. Tool permissions, concurrency safety per call, audit trail. ~200 lines.                                                                  |
| `shared/references/multi-agent-pattern.md`         | Ported from harness-creator with attribution. Coordinator / worker / reviewer roles, disjoint ownership. ~193 lines.                                                                   |
| `shared/references/lifecycle-bootstrap-pattern.md` | Ported from harness-creator with attribution. Hook trust gates, two-phase eviction, dependency-ordered bootstrap. ~264 lines.                                                          |
| `shared/references/gotchas.md`                     | Ported from harness-creator with attribution. Non-obvious failure modes. ~209 lines.                                                                                                   |
| `scripts/validate-skill.mjs`                       | Pure Node-built-ins deterministic skill validator. Ports harness-creator's `validate-harness.mjs` adapted to SKILL.md schema. Outputs JSON + HTML. ~200 lines.                         |

**New files (Phase 2 — Self-improving generated skills):**

| File                                         | Purpose                                                                                                                                                                                                  |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `shared/templates/evals-template.json`       | Template for `evals/evals.json` that the generator writes into every new skill. Schema mirrors harness-creator's evals.json. Contains placeholders the generator fills from the spec's success criteria. |
| `shared/templates/validate-mjs-template.mjs` | Template for per-skill `evals/validate.mjs` that the generator writes alongside the SKILL.md. Reads the skill's evals.json + component manifest, scores structural conformance.                          |

**New files (Phase 3 — forge-harness):**

| File                                                | Purpose                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `skills/forge-harness/SKILL.md`                     | New skill — scaffolds AGENTS.md/CLAUDE.md + feature_list.json + progress.md + init.sh + session-handoff.md into a target repo. ~250 lines.                                                                                                                                                                                                                                                                                                                                                                    |
| `skills/forge-harness/trigger-tests.md`             | 20 trigger queries for the new skill.                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `skills/forge-harness/evals/evals.json`             | First example of the new self-improving generated-skill pattern — eval cases for the harness-scaffolding flow.                                                                                                                                                                                                                                                                                                                                                                                                |
| `skills/forge-harness/evals/validate.mjs`           | Per-skill validator.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `commands/forge-harness.md`                         | Thin entry-point wrapper for `/forge-harness`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `shared/templates/harness/agents.md`                | Ported from harness-creator. Generator substitutes placeholders for target stack / verification commands.                                                                                                                                                                                                                                                                                                                                                                                                     |
| `shared/templates/harness/feature-list.json`        | Ported template with 5 placeholder features.                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `shared/templates/harness/feature-list.schema.json` | Ported JSON schema for feature-list validation.                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `shared/templates/harness/progress.md`              | Ported template.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `shared/templates/harness/init.sh`                  | Ported template.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `shared/templates/harness/session-handoff.md`       | Ported template.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `scripts/create-harness.mjs`                        | Ported from harness-creator with attribution. Detects target project stack (Node/Python/PHP/Go/Rust/Java/.NET) and synthesizes stack-appropriate verification commands — framework-aware for Laravel/Filament (`composer.json`), Django, and uv-managed Python (ruff/ty). PHP is detected before Node so Laravel/Filament apps (which ship both `composer.json` and `package.json`) resolve to the PHP backend. Templates resolve from `shared/templates/harness/`. Used by the forge-harness skill via Bash. |
| `scripts/validate-harness.mjs`                      | Ported from harness-creator with attribution. Scores the 5 subsystems of a harness in a target repo. Used by forge-harness for audits.                                                                                                                                                                                                                                                                                                                                                                        |

**Modified files (0.8.0):**

| File                            | Changes                                                                                                                                                                                                 |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `agents/intake-analyst.md`      | Adds harness-scaffolding intent recognition. New artifact type: `harness`. Routes "scaffold harness", "add AGENTS.md", "feature tracker for this repo" intents to forge-harness instead of forge-skill. |
| `agents/skill-generator.md`     | Updated component manifest: every generated skill now emits `evals/evals.json` + `evals/validate.mjs`. Reads the spec's success criteria to populate evals.json placeholders.                           |
| `agents/skill-validator.md`     | Delegates structural checks to `scripts/validate-skill.mjs`. Retains semantic checks (anti-pattern violations not grep-detectable, description-quality scoring).                                        |
| `agents/skill-optimizer.md`     | Step 2 (Analysis) now also reads the skill's `evals/validate.mjs` output if present. Deterministic structural scores feed into the four-dimension scorecard alongside semantic scores.                  |
| `skills/create-skill/SKILL.md`  | Step 4 generation manifest extended. Step 5 validation calls `scripts/validate-skill.mjs` before spawning the agent.                                                                                    |
| `skills/improve-skill/SKILL.md` | Step 5 re-validation runs `scripts/validate-skill.mjs` if present.                                                                                                                                      |
| `shared/anti-patterns.md`       | Restructured to Problem → Golden Rules → Trade-offs → Implementation Patterns → Gotchas → Related Patterns shape.                                                                                       |
| `shared/skill-anatomy.md`       | Documents `evals/` directory convention. Documents the 5-subsystem mental model as the design lens for new skills.                                                                                      |
| `plugin.json`                   | Version bump 0.7.1 → 0.8.0. No new agents (the new scripts are invoked via Bash, not via Agent).                                                                                                        |

## Skill Architecture

### New Forge Pipeline (6 Steps)

```
Step 1: Intake & Analysis
  Agent: intake-analyst (sonnet)
  Input: Brain dump text
  Output: Classification (skill type, workflow pattern, primitives, complexity,
          retrospective recommendation)
  Gate: None — always proceeds

Step 2: Target + Name Selection
  Tool: AskUserQuestion
  Input: Intake classification
  Output: Target location (project/global/marketplace), confirmed skill name,
          established skill directory path
  Gate: User confirms name and target
  Note: Name selection moved earlier because spec needs to be written to
        {skill-dir}/docs/

Step 3: Spec Formation Loop
  Tools: AskUserQuestion, Agent (skill-researcher during codebase exploration)
  Input: Intake classification, target directory, codebase research findings
  Process:
    - Score 5 dimensions (Trigger Clarity, Workflow Definition, Tool Requirements,
      Output Specification, Scope Boundaries) — 0-20 pts each
    - If < 90: ask clarifying questions via AskUserQuestion, re-score
    - Codebase research (skill-researcher agent) runs during this loop to inform
      the spec, not after it
    - When >= 90: write contract.md, spec.md, and learnings.md to {skill-dir}/docs/
      (learnings.md starts empty with a header explaining its purpose — created
      during spec formation, not during generation, so it exists before the
      skill does)
    - Present spec for approval via AskUserQuestion
      Options: Approved / Needs changes / Missing scope / Start over
    - If "Needs changes": iterate on documents (Edit), re-present
  Output: Approved contract.md + spec.md
  Gate: User approves spec (replaces both confidence gate exit AND generation
        plan approval)

Step 4: Execute Spec
  Agents: scaffold-writer (haiku, marketplace only), skill-generator (opus)
  Input: Approved spec.md, shared/ reference docs
  Process:
    - Phase 1 (marketplace only): scaffold-writer creates plugin.json,
      package.json, tsconfig.json per spec
    - Remaining phases: skill-generator reads spec and executes component
      manifest in execution plan order
    - Parallel phases dispatched concurrently via Agent tool
    - Generator reports any deviations from spec
  Output: All skill artifacts written to disk
  Gate: None — spec was already approved

Step 5: Validate
  Agent: skill-validator (haiku)
  Input: Skill directory path, spec.md
  Process:
    - Standard structural checks (frontmatter, line count, constraints placement)
    - Anti-pattern scan (76+ known patterns)
    - Spec compliance check (artifacts match component manifest)
    - Trigger test generation (20 queries to trigger-tests.md)
    - Build verification (marketplace: bun run typecheck && bun run build)
  Output: Validation report
  Gate: CRITICAL failures block delivery. HIGH failures warn. User decides
        whether to fix or ship.

Step 6: Retrospective
  Agent: retrospective (sonnet)
  Input: Spec (contract + spec), validator report, any user modifications
         during the run
  Process:
    - Analyze: Did intake classification match what was built? Did validator
      catch things the spec should have prevented? Did user manually change
      anything post-generation?
    - Append timestamped observations to shared/learnings.md
    - If a pattern appears 3+ times in learnings: propose concrete update to
      relevant reference doc via AskUserQuestion (user approves before
      modification)
  Output: Updated shared/learnings.md, optionally updated reference docs
  Gate: User approves any knowledge base modifications
```

### New Improve Pipeline (6 Steps)

```
Step 1: Locate & Gather Context
  Tools: Glob, Read
  Input: Skill path/name from command arguments
  Process:
    - Resolve skill path (direct path / project / global / marketplace / search)
    - Read SKILL.md, agents, commands, hooks, references, plugin.json
    - Read {skill-dir}/docs/ if it exists (contract.md, spec.md, learnings.md)
    - Store user's braindump for step 2
  Output: Full skill context + spec context (or flag: no spec exists)

Step 2: Analysis & Scoring
  Agent: skill-optimizer (sonnet)
  Input: Skill files, spec files (if they exist), user braindump
  Process:
    If spec exists:
      - Three-way analysis: spec vs current skill vs braindump
      - Flag spec drift (skill has diverged from spec)
      - Flag braindump-spec conflicts (user wants something spec excluded)
      - Score 4 dimensions (Description, Structure, Instructions, Agents/Tools)
      - Map braindump items to relevant dimensions
    If no spec exists:
      - Offer retroactive spec generation via AskUserQuestion
        Options: Generate spec from current skill / Skip, improve without spec
      - If accepted: reverse-engineer contract.md + spec.md from current state,
        write to {skill-dir}/docs/, then proceed with three-way analysis
      - If declined: standard scored analysis (current behavior)
  Output: Scored analysis with recommendations, spec alignment report

Step 3: Recommendations
  Tool: AskUserQuestion
  Input: Scorecard, spec alignment findings
  Process:
    - Present scorecard and spec alignment issues
    - If spec updates needed: present spec changes first
    - User selects: Improve all / specific dimensions / Update spec only /
      I'm satisfied
  Output: User's improvement selection

Step 4: Apply Changes
  Tools: Edit, AskUserQuestion, TaskCreate, TaskUpdate
  Input: Selected improvements
  Process:
    - If spec updates approved: Edit contract.md and/or spec.md first
    - For each skill improvement:
      - AskUserQuestion shows old vs new text
      - User: Apply / Skip / Modify
      - If Apply: Edit tool (surgical, minimum change)
      - TaskCreate/TaskUpdate tracks applied/skipped
  Output: Updated skill files, updated spec (if applicable)

Step 5: Re-validate & Report
  Agent: skill-validator (haiku, if description changed)
  Tools: Read
  Process:
    - Re-read and re-score all 4 dimensions
    - Present before/after scorecard
    - Append score history to {skill-dir}/docs/learnings.md:
        ## YYYY-MM-DD — Improvement Run
        - Trigger: <braindump summary>
        - Before: <scores>
        - After: <scores>
        - Changes applied: <list>
        - Changes skipped: <list>
    - If marketplace: bun run typecheck && bun run build
    - If description changed: generate new trigger tests
  Output: Final scorecard, updated learnings

Step 6: Retrospective
  Agent: retrospective (sonnet)
  Input: Before/after scores, applied vs skipped changes, braindump themes
  Process:
    - Analyze: Which dimensions consistently score low? What do users ask to
      improve most frequently? Are there common braindump themes suggesting
      generation is weak in a specific area?
    - Append to shared/learnings.md
    - Propose reference doc updates if patterns recur (3+ occurrences)
  Output: Updated shared/learnings.md, optionally updated reference docs
```

### Generated Skill Output (What Forge Creates)

For every skill:

```
{skill-dir}/
  docs/
    contract.md          # Design intent — problem, goals, scope, decisions
    spec.md              # Execution plan — components, architecture, phases
    learnings.md         # Starts empty, accumulates over time
  skills/{name}/
    SKILL.md             # Includes retrospective instructions (lightweight or full)
  ...                    # Other artifacts per spec
```

For complex skills (complexity-gated):

```
{skill-dir}/
  agents/
    {name}-retrospective.md    # Dedicated retrospective agent
  commands/
    {name}-retrospect.md       # User-invocable command (marketplace only)
```

## Execution Plan

### Phase 1: Templates and Knowledge Base (no dependencies)

Create the new template and reference files. These are standalone and don't depend on pipeline changes.

- Write `shared/templates/contract-template.md`
- Write `shared/templates/spec-template.md`
- Write `shared/templates/retrospective-agent-template.md`
- Write `shared/learnings.md` (empty with header)
- Update `shared/skill-anatomy.md` (add docs/ convention)
- Update `shared/quality-checklist.md` (add spec compliance checks)
- Update `shared/anti-patterns.md` (add spec-related anti-patterns)

### Phase 2: Retrospective Agent (depends on Phase 1)

Create skill-forge's own retrospective agent.

- Write `agents/retrospective.md`

### Phase 3: Intake Analyst Update (no dependencies)

Add retrospective complexity classification to intake output.

- Update `agents/intake-analyst.md`

Can run in parallel with Phase 2.

### Phase 4: Forge Pipeline Rewrite (depends on Phases 1, 2, 3)

Restructure the create-skill workflow.

- Rewrite `skills/create-skill/SKILL.md` (8 steps → 6 steps)
- Update `agents/skill-generator.md` (spec executor)
- Update `agents/skill-researcher.md` (timing change)

### Phase 5: Improve Pipeline Rewrite (depends on Phases 1, 2)

Restructure the improve-skill workflow.

- Rewrite `skills/improve-skill/SKILL.md` (add three-way analysis, retroactive spec, score history, retrospective)
- Update `agents/skill-optimizer.md` (spec-aware, three-way analysis)

Can run in parallel with Phase 4.

### Phase 6: Plugin Metadata and Validation (depends on Phases 4, 5)

Finalize the plugin.

- Update `plugin.json` (version bump, register retrospective agent)
- Update `agents/skill-validator.md` (add spec compliance instructions)
- Run `bun run typecheck && bun run build`
- Run `bun run sync`

### Dependency Graph

```
Phase 1 (templates + knowledge base)     Phase 3 (intake analyst)
        │                                       │
        ├──── Phase 2 (retrospective agent)     │
        │           │                           │
        │           ├───────────────────────────┤
        │           │                           │
        │           ├──── Phase 4 (forge pipeline) ←─┘
        │           │
        │           ├──── Phase 5 (improve pipeline)
        │           │           │
        └───────────┴───────────┴──── Phase 6 (metadata + validation)
```

- Phases 2 and 3 can run in parallel (both depend only on Phase 1)
- Phases 4 and 5 can run in parallel (both depend on 1 and 2; only 4 depends on 3)
- Phase 6 is sequential — must follow both 4 and 5

### Phase 7: 0.8.0 Knowledge Base Lift (no dependencies on prior phases — additive)

Port harness-creator reference docs and add the 5-subsystem mental model. All file writes are additive; no existing files are removed.

- Copy 6 reference docs into `shared/references/` with attribution header (Source: walkinglabs/learn-harness-engineering MIT license)
- Write `shared/agentic-subsystems.md` (new file documenting the 5-subsystem model)
- Restructure `shared/anti-patterns.md` to the Problem → Golden Rules → Trade-offs → Implementation → Gotchas → Related Patterns shape
- Write `scripts/validate-skill.mjs` — port of harness-creator's validate-harness.mjs adapted to SKILL.md schema

Phase 7 sub-tasks can run in parallel (all 4 are independent file writes).

### Phase 8: 0.8.0 Self-Improving Generation (depends on Phase 7's validate-skill.mjs)

Make every newly generated skill ship with its own deterministic structural validator.

- Write `shared/templates/evals-template.json`
- Write `shared/templates/validate-mjs-template.mjs`
- Update `agents/skill-generator.md` to add `evals/` to its component manifest
- Update `agents/skill-validator.md` to delegate structural checks to `scripts/validate-skill.mjs`
- Update `agents/skill-optimizer.md` to consume per-skill `evals/validate.mjs` output during Step 2 analysis
- Update `skills/create-skill/SKILL.md` Step 4 generation manifest + Step 5 validator delegation
- Update `skills/improve-skill/SKILL.md` Step 5 to run per-skill validate.mjs when present

### Phase 9: 0.8.0 forge-harness Skill (depends on Phase 7)

Create the sibling skill that scaffolds harnesses into target repos.

- Write `skills/forge-harness/SKILL.md`
- Write `commands/forge-harness.md` (thin entry point)
- Copy 6 templates into `shared/templates/harness/` (agents.md, feature-list.json, feature-list.schema.json, init.sh, progress.md, session-handoff.md)
- Port `scripts/create-harness.mjs` and `scripts/validate-harness.mjs` with attribution
- Update `agents/intake-analyst.md` to recognize harness intents and route correctly
- Write `skills/forge-harness/evals/evals.json` (first concrete example of the self-improving pattern)
- Write `skills/forge-harness/evals/validate.mjs`
- Write `skills/forge-harness/trigger-tests.md`

Phases 8 and 9 can run in parallel (both depend on Phase 7).

### Phase 10: 0.8.0 Plugin Metadata and Validation (depends on Phases 8, 9)

- Bump `plugin.json` version 0.7.1 → 0.8.0
- Run `bun run sync` to update marketplace.json
- Run `bun install && bun run format && bun run typecheck && bun run build`
- Run `node scripts/validate-skill.mjs --target plugins/skill-forge/skills/forge-skill` (self-test the new validator)

### 0.8.0 Dependency Graph

```
Phase 7 (knowledge base lift)
        │
        ├──── Phase 8 (self-improving generation)
        │           │
        │           │
        └──── Phase 9 (forge-harness skill)
                    │
                    │
              Phase 10 (metadata + sync + validation)
```

## Retrospective Configuration

Skill-forge itself gets the full retrospective treatment:

- `agents/retrospective.md` — dedicated agent
- `shared/learnings.md` — accumulation file
- Automatic execution as final pipeline step (no command needed — it's built into the workflow, not user-triggered)

## Validation Strategy

Beyond standard structural checks:

- Spec compliance: every file in the component manifest exists after generation
- Pipeline coherence: the 6-step forge pipeline and 6-step improve pipeline are internally consistent (step references, agent names, input/output contracts)
- Template completeness: contract, spec, and retrospective-agent templates contain all required sections
- Anti-pattern coverage: new spec-related anti-patterns are scannable by the validator
- Build verification: `bun run typecheck && bun run build && bun run sync` passes
- Formatting: `bun run format:check` passes
