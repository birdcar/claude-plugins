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
