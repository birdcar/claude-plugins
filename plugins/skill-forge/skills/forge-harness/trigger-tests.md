# Trigger Tests: forge-harness

## How to Use

Run these in a fresh Claude Code session (not the one that generated the skill).
For each query, note whether the skill activated or not.

Target: 90%+ activation on should-trigger, <10% activation on should-not-trigger.

## Should Trigger (expect skill to activate)

### Exact Matches

1. "Scaffold a harness in /Users/me/projects/my-app"
2. "Add AGENTS.md to this project"
3. "Set up CLAUDE.md for the agent in /repo/path"

### Paraphrased

4. "Create a feature tracker for /Users/me/code/widget"
5. "Make this repo agent-ready: /Users/me/code/api-server"
6. "Add session-handoff support to /repo so I can resume work tomorrow"

### Edge Cases

7. "Audit the harness in /repo and tell me what's missing"
8. "Score my AGENTS.md against the 5 subsystems"

### Embedded Context

9. "I've got a Node + React project at /Users/me/code/store and I want to generate a harness assessment HTML report so I can share my agent setup with the team"
10. "My init.sh in /repo isn't verifying anything useful — set up init.sh verification for /repo with the right commands for our stack"

## Should NOT Trigger (expect skill to stay inactive)

### Adjacent Domain

11. "Set up a CI workflow in .github/workflows for type-checking"
12. "Add a pre-commit hook that runs lint and tests"
13. "Write me a project README explaining how to onboard a new contributor"

### General Programming

14. "Refactor my Express server to use async/await everywhere"
15. "Debug this TypeScript build error about missing module declarations"
16. "Help me wire up Tailwind in this Next.js app"

### Keyword Overlap

17. "Audit my React component library for accessibility issues"
18. "Set up a feature flag system in this repo so we can ship behind a toggle"

### Other Skills

19. "Create a Claude Code skill for extracting tables from PDFs"
20. "Review the harness-creator skill in our codebase and tell me how to optimize it"

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
