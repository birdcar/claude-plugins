# Spec: Phase 4 — Quality Pipeline

## Overview

Build the validation agent and trigger test infrastructure that both create and improve modes share. This phase adds the `skill-validator` agent and trigger test generation, completing the full quality pipeline: structural validation + trigger tests + anti-pattern scan.

## Technical Approach

The quality pipeline runs as the final step of both create and improve workflows. It's a single agent (`skill-validator`) that performs all checks and returns a structured report. Trigger tests are generated as a companion file that the user can run manually.

```
SKILL FILES → STRUCTURAL CHECK → ANTI-PATTERN SCAN → TRIGGER TEST GEN → REPORT
     ↓              ↓                    ↓                   ↓              ↓
  Read all      Validate:          Check against         Generate 20    Pass/fail
  artifacts     - frontmatter      anti-patterns.md      queries:       summary +
                - naming           with severity          10 should      details
                - line count       ratings                10 shouldn't
                - structure
                - tools
```

Key decisions:

- **Single agent** — validation is read-heavy analysis, not generation. One Haiku agent handles all checks efficiently.
- **Trigger tests as a file** — written alongside the skill as `trigger-tests.md`, not executed automatically (execution requires a separate Claude session to avoid self-evaluation bias)
- **Anti-pattern scan uses the shared checklist** — no duplicate knowledge, single source of truth

## File Changes

### New Files

| File                                                  | Purpose                                                                        |
| ----------------------------------------------------- | ------------------------------------------------------------------------------ |
| `plugins/skill-forge/agents/skill-validator.md`       | Validates skill quality across all dimensions, generates trigger tests (Haiku) |
| `plugins/skill-forge/shared/trigger-test-template.md` | Template for trigger test files                                                |

### Modified Files

| File                                                | Change                                                                          |
| --------------------------------------------------- | ------------------------------------------------------------------------------- |
| `plugins/skill-forge/plugin.json`                   | Add skill-validator agent                                                       |
| `plugins/skill-forge/skills/create-skill/SKILL.md`  | Update validation step to use skill-validator agent                             |
| `plugins/skill-forge/skills/improve-skill/SKILL.md` | Update validation step to reference skill-validator for trigger test generation |

## Implementation Details

### Component 1: `skill-validator` Agent

**File**: `agents/skill-validator.md`

```yaml
---
name: skill-validator
description: >-
  Validates skill quality through structural checks, anti-pattern scanning,
  and trigger test generation. Returns a structured pass/fail report.
  Use as the final quality gate in both create and improve workflows.
tools:
  - Read
  - Glob
  - Grep
model: haiku
---
```

**System prompt body**:

Role: You are a skill quality validator. You check skills against known standards and generate trigger tests.

Input: Path to a skill directory (containing SKILL.md and optionally agents/, commands/, references/, hooks/)

Process:

**1. Structural Validation**

Check each item and report pass/fail:

| Check                  | Rule                                                                       | Severity |
| ---------------------- | -------------------------------------------------------------------------- | -------- |
| File name              | Must be `SKILL.md` (exact case)                                            | CRITICAL |
| Directory name         | Must be kebab-case                                                         | CRITICAL |
| Frontmatter present    | YAML frontmatter with `---` delimiters                                     | CRITICAL |
| `name` field           | kebab-case, ≤64 chars, no "claude"/"anthropic", no XML                     | CRITICAL |
| `description` field    | Present, ≤1024 chars, no XML, third-person                                 | CRITICAL |
| Description triggers   | Contains explicit trigger phrases ("Use when...")                          | HIGH     |
| Description negatives  | Contains "Do NOT use" or similar negative case                             | MEDIUM   |
| Line count             | SKILL.md ≤500 lines                                                        | HIGH     |
| Progressive disclosure | Heavy content in references/, not inline                                   | MEDIUM   |
| Constraints placement  | Critical rules in first 100 lines                                          | MEDIUM   |
| Agent tools            | `tools:` list follows least-privilege principle                            | MEDIUM   |
| Agent model            | `model:` field set appropriately (not defaulting to opus for simple tasks) | LOW      |
| `allowed-tools`        | Commands have appropriate tool restrictions                                | MEDIUM   |
| Hooks location         | In hooks/hooks.json, not inline in plugin.json                             | HIGH     |

**2. Anti-Pattern Scan**

Read `${CLAUDE_PLUGIN_ROOT}/shared/anti-patterns.md` and check each item:

- Report any CRITICAL or HIGH severity matches
- Note MEDIUM matches as warnings
- Skip LOW matches unless specifically asked

**3. Trigger Test Generation**

Generate 20 queries using this methodology:

- 10 **should-trigger** queries: realistic user messages that should activate this skill
  - 3 exact trigger phrase matches (from description)
  - 3 paraphrased variants (same intent, different words)
  - 2 edge cases (minimal context, ambiguous but should still trigger)
  - 2 with additional context (embedded in a longer message)
- 10 **should-NOT-trigger** queries: similar but distinct requests
  - 3 adjacent domain queries (related topic but different skill)
  - 3 general programming queries (no skill should trigger)
  - 2 queries that mention keywords but wrong context
  - 2 queries for other known skills (if conflicts identified)

Write to `trigger-tests.md` alongside the skill using the template from `${CLAUDE_PLUGIN_ROOT}/shared/trigger-test-template.md`.

Output format:

```
## Validation Report: {skill-name}

### Structural Checks
- [x] PASS: File name is SKILL.md
- [ ] FAIL: Description exceeds 1024 characters (1,247 chars)
...

### Anti-Pattern Scan
- CRITICAL: None found
- HIGH: Constraints buried after line 200 — move to first 100 lines
- MEDIUM: No examples section
...

### Trigger Tests
Written to: {path}/trigger-tests.md
20 queries generated (10 should-trigger, 10 should-not-trigger)

### Summary
PASS: 12/14 structural checks
WARNINGS: 2 anti-patterns (0 critical, 1 high, 1 medium)
ACTION REQUIRED: Fix 2 structural failures before shipping
```

### Component 2: Trigger Test Template

**File**: `shared/trigger-test-template.md`

```markdown
# Trigger Tests: {skill-name}

## How to Use

Run these in a fresh Claude Code session (not the one that generated the skill).
For each query, note whether the skill activated or not.

Target: 90%+ activation on should-trigger, <10% activation on should-not-trigger.

## Should Trigger (expect skill to activate)

### Exact Matches

1. "{query}"
2. "{query}"
3. "{query}"

### Paraphrased

4. "{query}"
5. "{query}"
6. "{query}"

### Edge Cases

7. "{query}"
8. "{query}"

### Embedded Context

9. "{query}"
10. "{query}"

## Should NOT Trigger (expect skill to stay inactive)

### Adjacent Domain

11. "{query}"
12. "{query}"
13. "{query}"

### General Programming

14. "{query}"
15. "{query}"
16. "{query}"

### Keyword Overlap

17. "{query}"
18. "{query}"

### Other Skills

19. "{query}"
20. "{query}"

## Results

| #   | Expected | Actual | Pass? |
| --- | -------- | ------ | ----- |
| 1   | trigger  |        |       |
| 2   | trigger  |        |       |

...
| 20 | no trigger | | |

**Score**: **_/20 (_**%)
```

### Component 3: Integration with Create Mode

Update `skills/create-skill/SKILL.md` Step 7 (Validation) to:

1. Spawn `skill-forge:skill-validator` agent via Agent tool with the skill directory path
2. Present validation report via AskUserQuestion
3. If CRITICAL failures: block delivery until fixed
4. If HIGH failures: warn and recommend fixing
5. Trigger tests are always generated

### Component 4: Integration with Improve Mode

Update `skills/improve-skill/SKILL.md` Step 5 (Re-validate) to:

- After applying improvements, spawn `skill-forge:skill-validator` for the after-score
- If description was changed, regenerate trigger tests
- Include trigger test results in the before/after report

## Testing Requirements

- Validator correctly identifies known anti-patterns in test skills
- Trigger test generation produces 20 queries with the right distribution
- Structural checks catch: wrong file name, missing frontmatter, oversized descriptions, >500 line SKILL.md
- Integration with create-skill and improve-skill works end-to-end

## Validation Commands

```bash
cd /Users/birdcar/Code/birdcar/claude-plugins
bun run typecheck
bun run build
bun run format:check
```

## Open Items

- Trigger test execution could be automated in a future phase using context:fork to run the skill in an isolated subagent and check if it activates
- The validator could also check for description budget conflicts (if user has many skills, warn about context window pressure) — future enhancement
