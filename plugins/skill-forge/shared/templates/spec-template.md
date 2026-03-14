# Spec Template

Generate `spec.md` files using this structure. Replace `{placeholders}` with actual values derived from the spec formation loop.

## Structure

```markdown
# {Skill Name} — Spec

## Component Manifest

| File             | Purpose                                       |
| ---------------- | --------------------------------------------- |
| `{path/to/file}` | {One-line description of what this file does} |

{List every file that will be created. This is the execution plan's source of truth — the generator creates exactly these files.}

## Skill Architecture

{2-3 paragraphs describing: workflow pattern (sequential, iterative-refinement, context-aware, etc.), agent team structure if multi-agent, key data flow between components.}

## Per-Component Details

### {Component Name} ({file path})

- **Purpose**: {What this component does}
- **Key behaviors**: {Critical behaviors, not exhaustive — the generator fills in implementation details}
- **Model**: {opus|sonnet|haiku — agents only}
- **Tools**: {Tool list — agents only}

{Repeat for each component. Focus on WHAT and WHY, not HOW — the generator handles implementation.}

## Execution Plan

### Phase 1: {Phase Name} ({dependency note})

- {File to create/modify}
- {File to create/modify}

### Phase 2: {Phase Name} (depends on Phase 1)

- {File to create/modify}

{Continue for each phase. Note dependencies and which phases can run in parallel.}

## Retrospective Configuration

- **Recommendation**: {full | lightweight | none}
- **Rationale**: {Why this level — multi-agent? external systems? evolving domain? stable scope?}
- **Components** (if full):
  - `agents/{name}-retrospective.md`
  - `commands/{name}-retrospect.md` (marketplace only)
  - `docs/learnings.md`
- **Components** (if lightweight):
  - `docs/learnings.md`
  - Soft instructions in SKILL.md to append observations

## Validation Strategy

- {What to check beyond standard structural compliance}
- {Spec compliance: artifacts match component manifest}
- {Domain-specific checks if applicable}
```

## Guidelines

- Component manifest is exhaustive — every file listed, no surprises during generation
- Per-component details focus on WHAT and WHY, not HOW — the generator handles implementation
- Execution plan defines ordering and parallelization — phases with no dependencies between them should be noted as parallelizable
- Retrospective configuration is informed by the intake analyst's complexity classification
- Keep under 150 lines — detailed implementation belongs in the generated artifacts, not the spec
- The spec is both a design record and an execution plan — it should be useful to both the generator (as instructions) and to future improve runs (as context)
