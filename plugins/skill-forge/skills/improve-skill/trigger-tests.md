# Trigger Tests: improve-skill

## How to Use

Run these in a fresh Claude Code session (not the one that generated the skill).
For each query, note whether the skill activated or not.

Target: 90%+ activation on should-trigger, <10% activation on should-not-trigger.

## Should Trigger (expect skill to activate)

### Exact Matches

1. "Improve this skill — the triggers aren't firing correctly"
2. "Review my skill and audit its quality"
3. "Fix the triggers on this skill"

### Paraphrased

4. "This skill needs optimization — can you make it better?"
5. "Analyze this SKILL.md and tell me how to strengthen it"
6. "Optimize this skill for better accuracy and efficiency"

### Edge Cases

7. "My skill works but feels clunky — help me refine it"
8. "Audit: does this skill follow best practices?"

### Embedded Context

9. "I built this skill last month and it's been triggering on the wrong queries. Can you review it and update the description to be more precise?"
10. "Here's my skill code — the agent is running out of token budget and the instructions are too verbose. Help me tighten it up and make it work better"

## Should NOT Trigger (expect skill to stay inactive)

### Adjacent Domain

11. "Review my TypeScript codebase and suggest refactoring"
12. "Audit this Python library for security vulnerabilities"
13. "Check my API documentation for completeness"

### General Programming

14. "Help me write a function that validates email addresses"
15. "Debug this async/await issue in my code"
16. "Optimize this database query"

### Keyword Overlap

17. "Generate code that improves performance"
18. "Write tests to audit code coverage"

### Other Skills

19. "Create a new skill for markdown conversion"
20. "Build a skill to handle this request"

## Results

| #   | Expected   | Actual | Pass? |
| --- | ---------- | ------ | ----- |
| 1   | trigger    |        |       |
| 2   | trigger    |        |       |
| 3   | trigger    |        |       |
| 4   | trigger    |        |       |
| 5   | trigger    |        |       |
| 6   | trigger    |        |       |
| 7   | trigger    |        |       |
| 8   | trigger    |        |       |
| 9   | trigger    |        |       |
| 10  | trigger    |        |       |
| 11  | no trigger |        |       |
| 12  | no trigger |        |       |
| 13  | no trigger |        |       |
| 14  | no trigger |        |       |
| 15  | no trigger |        |       |
| 16  | no trigger |        |       |
| 17  | no trigger |        |       |
| 18  | no trigger |        |       |
| 19  | no trigger |        |       |
| 20  | no trigger |        |       |

**Score**: \_\_\_/20 (\_\_\_%)
