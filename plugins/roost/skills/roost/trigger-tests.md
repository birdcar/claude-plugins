# Trigger Tests: roost

## How to Use

Run these in a fresh Claude Code session (not the one that generated the skill).
For each query, note whether the skill activated or not.

Target: 90%+ activation on should-trigger, <10% activation on should-not-trigger.

## Should Trigger (expect skill to activate)

### Exact Matches

1. "Build a SaaS app for project collaboration"
2. "Create a new SaaS project with auth and billing"
3. "Generate a full-stack app on Cloudflare"

### Paraphrased

4. "I need to start a greenfield SaaS application for team productivity"
5. "Set up auth and billing for a new web application"
6. "Generate a full-stack application on Cloudflare Workers with authentication"

### Edge Cases

7. "Build a SaaS"
8. "Create SaaS app"

### Embedded Context

9. "We're launching next month and need to build a SaaS app for appointment scheduling with subscription billing"
10. "I'm starting a new project that's a full-stack app on Cloudflare with WorkOS auth and Stripe payments"

## Should NOT Trigger (expect skill to stay inactive)

### Adjacent Domain

11. "Build a React frontend for a SaaS application"
12. "Set up Stripe billing integration in my existing app"
13. "Configure WorkOS authentication for my current project"

### General Programming

14. "Write a function to calculate subscription pricing"
15. "Create a database schema for user management"
16. "Build an API endpoint for user registration"

### Keyword Overlap

17. "What's the best way to architect a SaaS business?"
18. "How do I choose between Stripe and other payment processors?"

### Other Skills

19. "Fix the Cloudflare deployment in my existing project"
20. "Inspect my app for missing integrations"

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
