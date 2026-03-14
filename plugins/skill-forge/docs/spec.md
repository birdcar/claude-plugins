# Skill-Forge Harness Evolution — Spec

## Component Manifest

### New Files

| File | Purpose |
|---|---|
| `agents/retrospective.md` | Skill-forge's own retrospective agent. Analyzes forge/improve runs, appends to learnings, proposes knowledge base updates after repeated patterns. Sonnet model. Tools: Read, Glob, Grep, Write, Edit. |
| `shared/learnings.md` | Timestamped observations from retrospective runs. Accumulates patterns. When a pattern appears 3+ times, the retrospective proposes a concrete update to the relevant reference doc. |
| `shared/templates/contract-template.md` | Template for contract.md documents generated in created skills. Sections: Problem Statement, Goals, Success Criteria, Scope Boundaries, Design Decisions. |
| `shared/templates/spec-template.md` | Template for spec.md documents generated in created skills. Sections: Component Manifest, Skill Architecture, Per-Component Details, Execution Plan, Retrospective Configuration, Validation Strategy. |
| `shared/templates/retrospective-agent-template.md` | Template for retrospective agents generated in complex skills. Mirrors skill-forge's own retrospective pattern: analyze session, append to learnings, propose knowledge base updates. Sections: Role, Input (learnings file path, session context), Process (analyze, classify, append, propose), Output Format, Constraints (never modify target code, only knowledge base). |

### Modified Files

| File | Changes |
|---|---|
| `skills/create-skill/SKILL.md` | Pipeline restructured from 8 to 6 steps. Confidence gate replaced by spec formation loop. Generation plan approval removed. Name selection moved to step 2. Retrospective added as step 6. |
| `skills/improve-skill/SKILL.md` | Three-way analysis when spec exists. Spec-first updates. Retroactive spec generation offer. Score history to learnings.md. Retrospective as final step. |
| `agents/skill-generator.md` | Primary input becomes spec.md. Follows execution plan for ordering and parallelization. Reports deviations from spec. Still reads shared/ for writing quality guidance. |
| `agents/intake-analyst.md` | Adds retrospective complexity classification to output: full (agent + command + learnings), lightweight (learnings only), or none. Based on: multi-agent, external systems, evolving domain, state management. |
| `agents/skill-optimizer.md` | Reads spec alongside skill when spec exists. Three-way analysis (spec + skill + braindump). Updates spec before proposing skill changes. Offers retroactive spec generation when no spec found. |
| `agents/skill-researcher.md` | Timing change only: runs during spec formation (before spec is written) instead of after confidence gate. Agent instructions unchanged. |
| `agents/skill-validator.md` | Adds spec compliance checking: verifies generated artifacts match the spec's component manifest. Checks for files in the spec not created, or files created not in the spec. |
| `shared/quality-checklist.md` | Adds spec compliance checks: did generated artifacts match the spec's component manifest? Are there files in the spec not created, or files created not in the spec? |
| `shared/skill-anatomy.md` | Documents the `docs/` directory convention: contract.md (design intent), spec.md (execution plan), learnings.md (accumulated observations). Explains permanence and gitignore option. |
| `shared/anti-patterns.md` | New anti-patterns: spec drift (skill diverges from spec without updating it), empty learnings files (created but never written to), retrospective agents that modify target code instead of knowledge base, specs that describe implementation details instead of design intent. |
| `plugin.json` | Version bump 0.3.0 → 0.4.0. Register retrospective agent. |

All files not listed in New or Modified are unchanged (scaffold-writer, command entry points, and shared reference docs for description-engineering, agent-design, workflow-patterns, primitives-guide, and local-config-pattern).

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
  Tools: Edit, AskUserQuestion, TodoWrite
  Input: Selected improvements
  Process:
    - If spec updates approved: Edit contract.md and/or spec.md first
    - For each skill improvement:
      - AskUserQuestion shows old vs new text
      - User: Apply / Skip / Modify
      - If Apply: Edit tool (surgical, minimum change)
      - TodoWrite tracks applied/skipped
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
