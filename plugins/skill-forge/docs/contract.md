# Skill-Forge Harness Evolution — Contract

## Problem Statement

Skill-forge generates and improves Claude Code skills through a pipeline of specialized agents. But the pipeline doesn't learn from its own runs. When a generated skill has problems — the description triggers too broadly, the agent model is oversized, the structure hits anti-patterns — that knowledge stays in the conversation and evaporates. The next forge run starts from zero.

Meanwhile, generated skills themselves have no mechanism for accumulating operational knowledge. A skill like home-server encodes domain expertise that evolves (new services, config gotchas, API changes), but that retrospective capability was hand-built. Skill-forge should produce skills that learn, not just skills that execute.

The creation flow also lacks documentation. The confidence gate decides "I know enough to generate" but doesn't capture *what* was decided or *why*. When `/improve-skill` runs later, it has no record of the original design intent — only the artifact. It can score structural quality but can't evaluate whether the skill still serves its original purpose or whether assumptions have changed.

## Goals

1. Skill-forge improves its own knowledge base (anti-patterns, quality checklist, description-engineering guidance) automatically after every forge and improve run
2. Every skill created by skill-forge ships with persistent design documentation (contract + spec) that future improve runs can reference
3. Complex skills get retrospective capability built in, gated by the intake analyst's complexity classification
4. The creation flow produces a spec that serves as both the design record and the execution plan for generation — replacing the confidence gate and generation plan approval with a single, documentable artifact
5. The improve flow performs three-way analysis (spec + current skill + braindump) when a spec exists, and offers retroactive spec generation for pre-existing skills

## Success Criteria

- [ ] `/forge-skill` produces `contract.md`, `spec.md`, and `learnings.md` in `{skill-dir}/docs/` for every created skill
- [ ] The spec includes a component manifest and phased execution plan that the generator follows mechanically
- [ ] The retrospective agent runs automatically after every forge and improve run
- [ ] After 3+ occurrences of the same pattern in `shared/learnings.md`, the retrospective proposes a concrete update to the relevant reference doc (user approves before modification)
- [ ] Complex skills (multi-agent, external systems, evolving domain knowledge) receive a retrospective agent and command
- [ ] Simple skills receive a `learnings.md` file with soft instructions to append observations
- [ ] `/improve-skill` reads existing spec alongside the skill and performs three-way analysis
- [ ] `/improve-skill` updates the spec before applying skill changes when design intent has shifted
- [ ] `/improve-skill` offers retroactive spec generation for skills that predate this feature
- [ ] Score history is appended to `{skill-dir}/docs/learnings.md` after every improve run
- [ ] Validator checks spec compliance (generated artifacts match the spec's component manifest)

## Scope Boundaries

### In Scope

- Restructuring the forge pipeline (8 steps to 6)
- Spec formation loop replacing the confidence gate and generation plan approval
- Spec-driven generation (generator becomes executor)
- Automatic retrospective as final step in both pipelines
- Complexity-gated retrospective generation in created skills
- Three-way analysis in improve pipeline
- Retroactive spec generation offer for pre-existing skills
- Score history persistence in learnings files
- New templates (contract, spec, retrospective agent)
- Updates to shared knowledge base docs (skill-anatomy, quality-checklist, anti-patterns)
- Version bump to 0.4.0

### Out of Scope

- Multi-document specs (phasing within a single spec is sufficient for skill-forge's bounded output)
- Task resumption / session persistence (most forge sessions complete in one sitting)
- Doom-loop detection (user is the circuit breaker via approval gates)
- Evidence markers / hash-verified testing (validator output is sufficient)
- Changes to scaffold-writer agent (unchanged role)
- Changes to command entry points (thin wrappers, unchanged)

### Future Considerations

- Visual companion for spec review (browser-based mockup of skill structure)
- Automated trigger testing against the spec's success criteria
- Cross-skill learning (patterns from one skill's retrospective informing another's)

## Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Single spec vs multi-spec | Single spec with phased execution plan | Skill-forge's output is bounded (SKILL.md + agents + commands). No single phase is large enough to warrant its own document. |
| Confidence threshold | 90 (unchanged) | Specs are executed by agents, not humans. Slightly lower confidence is acceptable because the validator catches structural issues. |
| Spec location | `{skill-dir}/docs/` | Lives alongside the skill permanently. Future improve runs read it. Users can gitignore if desired. |
| Retrospective trigger | Automatic (final pipeline step) | User-triggered means forgetting and losing learnings. The cost of always running it is low. |
| Retrospective complexity gate | Intake analyst classifies | Multi-agent, external systems, evolving domain = full retrospective. Single-skill, deterministic, stable scope = learnings file only. User can override. |
| Knowledge base update threshold | 3 occurrences in learnings | Prevents one-off edge cases from polluting shared docs. Requires user approval before modification. |
| Retroactive spec generation | Offered, not required | Gradual adoption. No regression for pre-existing skills. |
| Spec approval model | Single approval replaces confidence gate exit + generation plan approval | The spec *is* the evidence of confidence. Two approval gates for the same information is redundant. |
