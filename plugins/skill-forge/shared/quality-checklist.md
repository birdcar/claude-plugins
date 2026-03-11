# Structural Compliance Checks

| #   | Check                  | Rule                                                   | Severity | Auto-fixable                 |
| --- | ---------------------- | ------------------------------------------------------ | -------- | ---------------------------- |
| 1   | File name              | Must be exactly `SKILL.md`                             | CRITICAL | No                           |
| 2   | Directory name         | kebab-case only                                        | CRITICAL | Yes                          |
| 3   | Frontmatter present    | YAML `---` delimiters at top of file                   | CRITICAL | No                           |
| 4   | `name` field           | kebab-case, ≤64 chars, no XML, no "claude"/"anthropic" | CRITICAL | Yes                          |
| 5   | `description` field    | Present, ≤1024 chars, no XML, third-person             | CRITICAL | No                           |
| 6   | Description triggers   | Contains "Use when" or equivalent trigger phrases      | HIGH     | No                           |
| 7   | Description negatives  | Contains "Do NOT use" or similar exclusion             | MEDIUM   | No                           |
| 8   | Line count             | SKILL.md ≤500 lines                                    | HIGH     | Yes (extract to references/) |
| 9   | Constraints placement  | Non-negotiable rules in first 100 lines                | MEDIUM   | Yes (reorder)                |
| 10  | Progressive disclosure | Heavy content in references/, not inline               | MEDIUM   | Yes (extract)                |
| 11  | Agent tools            | `tools:` list follows least-privilege                  | MEDIUM   | No                           |
| 12  | Agent model            | `model:` field set, right-sized for task               | LOW      | Yes                          |
| 13  | Command allowed-tools  | Appropriate tool restrictions                          | MEDIUM   | No                           |
| 14  | Hooks location         | hooks/hooks.json, not inline in plugin.json            | HIGH     | Yes                          |

## Pass criteria: All CRITICAL checks pass, no more than 2 HIGH failures.

# Trigger Test Protocol

## Generation

Produce 20 queries per skill:

**10 should-trigger:**

- 3 exact trigger phrase matches (directly from description)
- 3 paraphrased variants (same intent, different wording)
- 2 edge cases (minimal context, slightly ambiguous)
- 2 embedded (trigger buried in a longer message)

**10 should-NOT-trigger:**

- 3 adjacent domain (related but different skill territory)
- 3 general programming (no skill should activate)
- 2 keyword overlap (shares words but wrong context)
- 2 other-skill targets (if known competing skills exist)

## Execution

Run in a fresh Claude Code session — NOT the session that created the skill:

1. Paste each query as a user message
2. Note whether the skill activated (check if skill name appears in tool use)
3. Record pass/fail in the results table

## Scoring

| Metric                       | Target       | Action if missed                        |
| ---------------------------- | ------------ | --------------------------------------- |
| Should-trigger hit rate      | ≥90% (9/10)  | Add more trigger phrases to description |
| Should-NOT-trigger miss rate | <10% (≤1/10) | Add negative cases, narrow scope        |
| Combined score               | ≥18/20       | Iterate on description                  |

# Anti-Pattern Scan

Read `anti-patterns.md` and check every item at CRITICAL and HIGH severity. Report:

- CRITICAL matches: must fix before shipping
- HIGH matches: should fix, warn user
- MEDIUM matches: note as suggestions
- LOW matches: skip unless user requests full audit

# Dry-Run Test

Generate 3 realistic test prompts that exercise the skill's core workflow:

1. **Happy path**: Standard use case with clear inputs
2. **Edge case**: Unusual but valid input
3. **Boundary**: Input at the limits of the skill's scope

For each, describe:

- The prompt to use
- Expected behavior (what Claude should do)
- Success criteria (how to know it worked)

# Quality Score Rollup

| Dimension                | Weight | Source                                                    |
| ------------------------ | ------ | --------------------------------------------------------- |
| Structural compliance    | 30%    | Checklist above (% of checks passing)                     |
| Trigger precision        | 30%    | Trigger test score (out of 20)                            |
| Anti-pattern cleanliness | 20%    | Inverse of severity-weighted violations                   |
| Dry-run readiness        | 20%    | Subjective: are test prompts realistic and comprehensive? |

**Rating scale:**

- 90-100: Production-ready
- 75-89: Good, minor improvements possible
- 60-74: Functional but needs work
- Below 60: Not ready — significant issues
