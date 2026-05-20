# Trigger Tests: create-skill

## How to Use

Run these in a fresh Claude Code session (not the one that generated the skill).
For each query, note whether the skill activated or not.

Target: 90%+ activation on should-trigger, <10% activation on should-not-trigger.

## Should Trigger (expect skill to activate)

### Exact Matches

1. "Create a skill for automated PR review"
2. "Build a skill that analyzes code quality"
3. "Add a skill to summarize meeting transcripts"

### Paraphrased

4. "I need you to generate a skill for managing project tasks"
5. "Can you write a skill that monitors log files?"
6. "Make a skill for extracting data from PDFs"

### Edge Cases

7. "Skill: markdown converter"
8. "Generate a thing that formats code"

### Embedded Context

9. "I've been thinking we need something reusable — can you create a skill that validates JSON files in bulk?"
10. "The team keeps asking me to do this manually. I want to make a skill to batch-rename files across directories"

## Should NOT Trigger (expect skill to stay inactive)

### Adjacent Domain

11. "Can you write a Python script for web scraping?"
12. "Build a Next.js component library"
13. "Create a GitHub Actions workflow for CI/CD"

### General Programming

14. "Write a function to sort arrays efficiently"
15. "Help me debug this JavaScript error"
16. "Refactor this class to use dependency injection"

### Keyword Overlap

17. "Improve this skill we already have"
18. "I want to generate documentation for my API"

### Other Skills

19. "Review my existing skill and tell me how to optimize it"
20. "Generate some code for a Claude Code command — not a full skill"

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
