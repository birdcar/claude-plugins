# Quality Checklist — Scoring & Rollup

This file defines the rollup scoring used at the end of `create-skill` and `improve-skill` runs. The mechanical structural checks themselves live in the validator agent (`agents/skill-validator.md`), the trigger-test spec lives in `trigger-test-template.md`, and the anti-pattern catalog lives in `anti-patterns.md`. This file references them — it does not duplicate.

## Pass criteria

A skill is ready to ship when:

- **All CRITICAL structural checks pass** — see the check table in `agents/skill-validator.md`
- **No more than 2 HIGH failures** in the same check table
- **Trigger test score ≥18/20** when trigger tests were generated — see `trigger-test-template.md`
- **No CRITICAL anti-pattern matches** — see `anti-patterns.md`

If any of these fail, the validator agent must report `ACTION REQUIRED` and block delivery.

## Spec compliance check

When a `docs/spec.md` exists, the validator additionally verifies:

- Every file in the component manifest was created
- No files were created that aren't in the manifest (reported as deviations)
- The execution plan's phases were followed in order
- The retrospective configuration matches the intake analyst's recommendation (`full`, `lightweight`, or `none`)

## Dry-run prompts (optional, qualitative)

Beyond mechanical checks, the validator can generate 3 realistic test prompts that exercise the skill's core workflow:

1. **Happy path** — standard use case with clear inputs
2. **Edge case** — unusual but valid input
3. **Boundary** — input at the limits of the skill's scope

For each, describe the prompt, the expected behavior, and the success criteria. Dry-run prompts are not auto-executed; they're shown to the user as suggestions for manual sanity-checking.

## Score rollup

| Dimension                | Weight | Source                                                                         |
| ------------------------ | ------ | ------------------------------------------------------------------------------ |
| Structural compliance    | 30%    | % of structural checks passing (see `agents/skill-validator.md`)               |
| Trigger precision        | 30%    | Trigger test score (out of 20) per `trigger-test-template.md`                  |
| Anti-pattern cleanliness | 20%    | Inverse of severity-weighted violations (CRITICAL=10, HIGH=5, MEDIUM=2, LOW=1) |
| Dry-run readiness        | 20%    | Subjective: are the dry-run prompts realistic and comprehensive?               |

### Rating scale

- **90–100**: Production-ready
- **75–89**: Good — minor improvements possible
- **60–74**: Functional but needs work
- **Below 60**: Not ready — significant issues

## Validator-Enforced Literals

`scripts/validate-skill.mjs` greps for these exact strings/patterns. Generator and
validator agents must copy the template snippets that contain them VERBATIM — a
paraphrase ("Rules", "Hard rules", a Status/✓ table) fails the deterministic score.
This pattern (restyled template text failing a literal check) has recurred across
three runs (wiz-kid ×2, wtfdyd ×2 — see `learnings.md` 2026-07-15).

| File (resolved from `--target`) | Enforced literal / pattern |
| --- | --- |
| `SKILL.md` body, first 100 lines | heading matching `/#+\s*Critical Rules\b/i` (body ≤500 lines) |
| `SKILL.md` frontmatter description | "Use when" trigger phrasing; a "Do NOT use" / "Do not use" clause; ≤1024 chars; third-person |
| `docs/contract.md` | heading matching `/#+\s*Problem Statement\b/i` |
| `docs/spec.md` | heading matching `/#+\s*Component Manifest\b/i` |
| `docs/learnings.md` | contains `/improve\|retrospective/i` or a dated `## YYYY-MM-DD` entry |
| `trigger-tests.md` | ≥10 numbered entries under a "should trigger" heading, ≥10 under "should not trigger"; a table row matching `/\|.*pass/i` (the template's "Pass?" column) |
| `scripts/*.mjs`, `scripts/*.py` | shebang on line 1 |

Path contract: `--target` is the SKILL directory (the one containing `SKILL.md`);
`docs/` is resolved at the plugin root (`skillDir/../..`), and `trigger-tests.md`
sits beside `SKILL.md`. Passing a plugin root as `--target` produces an all-false
cascade (~32/100) even when every file exists.

## Where to find the underlying checks

- **Structural check table (16 items)** → `agents/skill-validator.md` — the authoritative list. Don't duplicate here.
- **Trigger-test query distribution & scoring** → `trigger-test-template.md`
- **Anti-pattern catalog (CRITICAL/HIGH/MEDIUM/LOW)** → `anti-patterns.md`
- **Modern-feature audit (TodoWrite, model IDs, hooks handler types)** → cross-reference `primitives-guide.md`, `templates/hooks-json-template.md`, and `templates/plugin-json-template.md` during improve-skill scoring
