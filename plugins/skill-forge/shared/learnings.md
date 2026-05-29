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

## Retrospective — 2026-05-20

### Run: improve — skill-forge (scope-expansion, v0.7.1 → 0.8.0, braindump: adopt harness-creator patterns)

### Scores

- Before: 91 total (Description 23, Structure 23, Instructions 23, Agents/Tools 22)
- After: 100 total (+9) — perfect score; deterministic validate-skill.mjs now covers structural checks

### Observations

- Scope-expansion vs defect-cleanup: this is the first improve run that added a net-new sibling skill (forge-harness) rather than fixing existing artifacts — existing contract.md/spec.md structure handled it but the contract revision felt bolted-on; contract templates assume scope is fixed at intake, not expanded mid-run
- Stealing-with-attribution workflow: 6 reference docs + 2 scripts ported from walkinglabs/learn-harness-engineering (MIT); no prior precedent in the plugin; no external-sources index exists — if ported content drifts from upstream, there is no mechanism to detect it or propose a sync
- Deterministic validator displacement: scripts/validate-skill.mjs now does structural checks that skill-validator agent previously did via LLM reasoning; this is the first occurrence of script-displacing-agent for mechanical validation
- Template-syntax landmine: `{{COMPONENT_MANIFEST}}` in validate-mjs-template.mjs broke Prettier because the unsubstituted file was not valid JS; workaround was wrapping placeholders in valid-syntax envelopes (e.g., `JSON.parse('{{...}}')`) — this class of bug will recur for any template containing object/array placeholder syntax
- forge-harness meta-level gap: plugin now has forge-skill (creates skills) + forge-harness (creates harnesses); "forge-meta" (creates harness creators) was discussed but not built; current assessment is forge-skill is sufficient — a harness creator is just a skill with a create-harness.mjs in its scripts/; no real gap at this time
- Phased execution plan (10 phases) correlated with zero generation deviations and zero skipped scope items — third run where phased spec structure correlates with single-pass generation fidelity

### Patterns Detected

- Phased execution plan correlating with single-pass generation: now at 3 occurrences (roost, 0.7.1, 0.8.0) — threshold reached; propose adding mandatory phased execution plan to spec template for multi-agent or multi-phase runs
- Scope-expansion via improve run (contract template friction): first logged occurrence — watch; if it recurs 2 more times, propose a scope-expansion contract section in the contract template
- Stealing-with-attribution workflow (no external-sources index): first logged occurrence — watch; if it recurs 2 more times, propose `shared/external-sources.md` tracking ported content + license + origin commit SHA
- Deterministic script displacing LLM agent for mechanical validation: first logged occurrence — watch; if it recurs 2 more times, propose Golden Rule addition to agentic-subsystems.md
- Template-syntax landmine (unsubstituted placeholders breaking formatter): first logged occurrence — watch; if it recurs 2 more times, propose new entry in anti-patterns.md Cluster 3

### Knowledge Base Updates

- PROPOSED (3-occurrence threshold reached): add mandatory phased execution plan guidance to spec template for multi-agent or multi-phase plugins — awaiting orchestrator approval before editing `shared/templates/spec-template.md`

## Retrospective — 2026-05-29

### Run: improve — forge-harness (capability-extension, v0.8.0 → 0.9.0, braindump: PHP/Laravel/Filament + Python FastAPI/FastMCP/Django/uv/Typer awareness)

### Scores

- Before: 84 total (Description 21, Structure 25, Instructions 16, Agents/Tools 22)
- After: 94 total (+10) (Description 24, Structure 25, Instructions 23, Agents/Tools 22)

### Observations

- The braindump targeted a capability that lives entirely in a **bundled deterministic script** (`scripts/lib/harness-utils.mjs` — `detectProject` + `verificationCommands`), not in SKILL.md prose. The four-dimension optimizer rubric (Description/Structure/Instructions/Agents) does not score script logic, so the standard "spawn skill-optimizer" step would have under-served this run. Analysis was done inline with runtime fixture proof instead.
- A **critical latent bug surfaced only because the work required executing the script**: `TEMPLATE_DIR` resolved to `<plugin>/templates` (the origin repo's layout) while skill-forge placed templates at `shared/templates/harness/`. `create-harness.mjs` had been failing with `ENOENT` on every `create` run since the 0.8.0 port. The per-skill `validate.mjs` reported 100/100 the whole time because it checks structure, never executes the script. This is occurrence 2 of the "ported-content drift" class first logged in 0.8.0 (stealing-with-attribution, no integration smoke test).
- Stack detection ordering matters more than expected: Laravel/Filament apps ship **both** `composer.json` and `package.json`. Naively checking `package.json` first misclassifies every Laravel app as Node. The fix (check `composer.json` first) is a domain insight that a language-agnostic detector misses.
- Library-level frameworks (FastAPI, FastMCP, Typer) have **no reliable filesystem fingerprint** distinct from "Python managed by uv." Serving them implicitly via the uv-aware baseline (`uv sync` + `uv run pytest` + ruff/ty) is the correct call; only Django earns a distinct branch because `manage.py` changes the test command. Detection granularity should track _what changes the verification command_, not _what the user names_.
- Description trigger-surface value: adding "PHP", "Laravel/Filament", "Django", "uv" to the SKILL.md description directly serves a user whose dominant stack was previously invisible to the trigger matcher.

### Patterns Detected

- **Improve run where the target behavior lives in a bundled script, not prose (occurrence 1).** The optimizer's prose rubric is blind to deterministic engine logic. If this recurs 2 more times: propose an explicit improve-skill step — "if the skill delegates behavior to a bundled script, read and run that script against a fixture as part of Step 2 analysis."
- **Ported scripts carry origin-repo path/layout assumptions, undetected by structural validators (occurrence 2 of ported-content drift).** 0.8.0 logged "no external-sources index"; this run found the concrete failure mode (broken runtime path shipped + survived a release). At occurrence 3, the case for a port-integration smoke test in CI becomes strong.
- **Stack detector ordering bugs for polyglot projects (occurrence 1).** Laravel-beats-Node is now encoded in an eval; watch for the same class with other backend+frontend combos (Rails+package.json, Django+package.json).

### Knowledge Base Updates

- No new updates proposed at threshold this run. The "ported-content drift" pattern is now at 2 logged occurrences — one more warrants proposing a `shared/external-sources.md` index **plus** a port-integration smoke-test Golden Rule in `agentic-subsystems.md` (Verification subsystem). The pre-existing phased-execution-plan proposal remains open.
