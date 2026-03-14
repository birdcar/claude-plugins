# Contract Template

Generate `contract.md` files using this structure. Replace `{placeholders}` with actual values derived from the spec formation loop.

## Structure

```markdown
# {Skill Name} — Contract

## Problem Statement

{Who has this pain and what's the cost of not solving it. Be specific — "developers waste 20 minutes per PR" not "PRs are hard." Ground in real signals from the brain dump, not hypothetical benefits.}

## Goals

1. {Measurable goal — "reduce X from Y to Z" when quantifiable, otherwise describe the observable outcome}
2. {Additional goals...}

## Success Criteria

- [ ] {Testable criterion — something you could verify by running the skill and checking the output}
- [ ] {Each criterion maps to a validation check or observable behavior}

## Scope Boundaries

### In Scope

- {Feature or behavior that will be implemented}

### Out of Scope

- {Feature explicitly excluded, with rationale}

### Future Considerations

- {Things that might be added later but are not part of this version}

## Design Decisions

| Decision         | Choice            | Rationale                                                                |
| ---------------- | ----------------- | ------------------------------------------------------------------------ |
| {Decision point} | {What was chosen} | {Why — reference constraints, user preferences, or technical trade-offs} |
```

## Guidelines

- Problem statement: ground in the brain dump's actual pain point, not generic benefits
- Goals: measurable where possible, otherwise describe the observable outcome
- Success criteria: every item should be verifiable — if you can't check it, it's not a criterion
- Scope boundaries: "out of scope" items need rationale so future improve runs understand why they were excluded
- Design decisions: capture choices that aren't obvious from the code — the "why" that would otherwise be lost
- Keep under 100 lines — this is a reference document, not a novel
