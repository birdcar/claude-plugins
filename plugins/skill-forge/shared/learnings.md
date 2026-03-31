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
