# bat-kol — Learnings

Accumulated observations from retrospective runs. Starts empty, grows over time.

<!-- Entries below this line are added by the retrospective agent. Do not edit manually. -->

## Retrospective — 2026-03-25

### Run: forge — bat-kol (contextual voice writer)

### Observations

- Intake accuracy: multi-skill-plugin / high complexity was correct — 7 agents + 3 commands + 1 skill + 1 script + 3 references + hooks confirmed the classification
- Spec formation: 2 rounds / 3 AskUserQuestion calls is appropriate depth for a high-complexity plugin; no over-questioning observed
- Retrospective Configuration section in spec.md named two components (agents/bat-kol-retrospective.md, commands/retrospect.md) that do not appear in the Component Manifest — generator correctly followed the manifest (manifest is authoritative), but this is a latent confusion point in the spec template
- Validation passed at zero CRITICAL/HIGH — explicit per-category validation strategy in the spec (channel-specific drafter checks, config resolution edge cases) appears to raise output fidelity
- Prettier fixes required on 15 of 23 generated files post-generation — expected overhead for bulk markdown generation, not a process failure
- No user corrections after generation — generator followed the spec accurately for all 16 execution-plan files

### Process Notes

- The independent channel/register dimension design decision was surfaced early in intake and shaped the entire agent structure cleanly — independent dimension patterns are worth flagging in spec formation to avoid entanglement
- Cascading config (.gitignore-style resolution) is a strong pattern for multi-context plugins; resolve-config.sh as a script rather than inline agent logic keeps it testable and reusable
