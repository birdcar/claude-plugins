# Skill-Forge Learnings

Accumulated observations from retrospective runs. The retrospective agent appends timestamped entries after every forge and improve run. When a pattern appears 3+ times, the retrospective proposes a concrete update to the relevant reference doc in `shared/`.

<!-- Entries below this line are added by the retrospective agent. Do not edit manually. -->

## Retrospective — 2026-03-25

### Run: forge — bat-kol (contextual voice writer)

### Observations

- Intake accuracy: multi-skill-plugin / high complexity was correct — 7 agents + 3 commands + 1 skill + 1 script + 3 references matched the classification exactly
- Spec formation: 2 rounds / 3 AskUserQuestion calls for a high-complexity plugin is appropriate; no over-questioning observed
- Retrospective Configuration section in spec named two components (agents/bat-kol-retrospective.md, commands/retrospect.md) absent from the Component Manifest — generator correctly followed the manifest, but the spec has a structural ambiguity: the section implies generated artifacts without listing them
- Validation: PASS, zero CRITICAL/HIGH — explicit per-category validation strategy in spec (channel-specific checks, config resolution edge cases) correlates with clean output
- Prettier fixes required on 15 of 23 files post-generation — consistent expectation for multi-file forge runs; not a failure, just overhead
- No user corrections after generation — generator fidelity was high for this run

### Patterns Detected

- Retrospective Configuration section vs Component Manifest gap: first occurrence — watch for recurrence; if pattern reaches 3 runs, propose spec template update to require retrospective components be added to manifest or explicitly labeled "not generated"
- Prettier post-generation cleanup on bulk markdown output: first logged occurrence — monitor for 3+ occurrences before proposing action

## Retrospective — 2026-03-31

### Run: forge — roost (SaaS scaffold builder)

### Observations

- Intake accuracy: classified multi-skill-plugin / 6 agents; ended up with 7 (retrospective agent added) — intake undercounts by 1 when retrospective config is "full" because the retrospective agent itself is not in the initial classification count
- Spec formation: 4 clarifying questions in 1 round covered frontend framework, scope boundary (greenfield only), bootstrap depth, and deployment target — efficient; all 4 were load-bearing for design decisions recorded in contract
- Research enrichment: existing MCPs (Stripe MCP, Resend MCP) and CLI skills (WorkOS CLI) discovered during research and propagated into reference docs — research phase has high ROI for integrations-heavy plugins
- Generation: single-pass, no iterations, 31/31 manifest files — the explicit phased execution plan in the spec (Phases 1-6 with dependency ordering) is likely responsible for eliminating generation order ambiguity
- Validation: 16/16 structural, 0 anti-patterns, 100% spec compliance — clean run with no corrective loops
- User corrections: zero post-generation modifications — clarifying question round successfully front-loaded all consequential decisions
- Spec included domain-specific validation strategy (reference doc coverage check, shellcheck on scripts) alongside structural checks — correlated with validator thoroughness
- Retrospective Configuration section listed its components explicitly (agent, command, learnings.md) — no gap vs Component Manifest, unlike bat-kol run

### Patterns Detected

- Retrospective Configuration section vs Component Manifest gap: bat-kol had the gap; roost did NOT — pattern did not recur. Still at 1 occurrence. Watch for next run.
- Prettier post-generation cleanup: roost had 0 fixes needed (markdown-only output) vs bat-kol's 15 fixes (mixed TypeScript/markdown) — issue may be language-specific rather than a bulk-generation problem. Monitor by artifact type.
- Research phase discovering existing MCPs/CLI tools that enrich reference docs: first logged occurrence — if pattern recurs in 2 more runs, propose adding "discover existing integrations" as an explicit step in the forge intake checklist
- Phased execution plan in spec correlating with single-pass generation: first logged occurrence — if pattern holds across 2 more runs, propose making phased execution plan mandatory in spec template for multi-agent plugins

### Knowledge Base Updates

- No updates proposed (no pattern has reached 3 occurrences)

## Retrospective — 2026-05-20

### Run: improve — skill-forge (self-improvement, v0.7.0 → 0.7.1, no braindump)

### Scores

- Before: 84 total (Description 22, Structure 21, Instructions 19 avg, Agents/Tools 22)
- After: 91 total (+7) (Description 23, Structure 23, Instructions 23 avg, Agents/Tools 22)

### Observations

- Cross-file drift [P0]: 0.7.0 modernization history claimed "TodoWrite eliminated from both SKILL.md files" — 6 live references survived across 5 files; caught by improve auditor, not by the 0.7.0 validator
- Agent-prompt drift after shared-template update [P1]: hooks-json-template.md modernized (inline hooks permitted), validator updated, but skill-generator.md and scaffold-writer.md retained old hook-placement rule — gap persisted through a full version cycle
- Missing tool in agent's own tooling list [P1]: skill-generator Step 4 instructs spawning concurrent agents but tools list omitted the Agent tool — agent was instructing behavior it was not configured to perform
- Self-contradiction surface [P3]: improve-skill Critical Rules told auditor to flag TodoWrite as outdated while the same file's body told operators to use TodoWrite — internal Critical-Rules vs body consistency is not a validator check
- Description trigger phrases and negative-case alternatives added on improve pass — these patterns should be caught during initial spec formation, not discovered at improve time
- Step numbering drift: Step 4b folded into Step 4 to match spec's stated 6-step pipeline — agent prompt step counts can drift from spec without detection

### Patterns Detected

- Cross-file drift after "all files updated" claims: first logged occurrence (prior 0.7.0 occurrence was referenced in run context but not logged in learnings) — watch; at 2 total occurrences if counting unlogged 0.7.0 case
- Agent-prompt drift after shared-template modernization: first logged occurrence — when a shared doc is updated, agent prompts referencing that doc are not automatically reviewed
- Self-contradiction (Critical Rules vs body): first logged occurrence — generator and validator do not check intra-file consistency between Critical Rules and body prose
- Missing tool for behavior agent instructs (occurrence 2): 0.7.0 fixed 4 agents; this run caught 1 more — at 2 logged occurrences; one more occurrence warrants proposing a validator grep check against each agent's step instructions vs its tools list

### Knowledge Base Updates

- No updates proposed (no pattern has reached 3 logged occurrences; missing-tool pattern is at 2)
