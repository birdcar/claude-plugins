# Trigger Tests: bat-kol

## How to Use

Run these in a fresh Claude Code session (not the one that generated the skill).
For each query, note whether the skill activated or not.

Target: 90%+ activation on should-trigger, <10% activation on should-not-trigger.

## Should Trigger (expect skill to activate)

### Exact Matches

1. "draft an email about the project deadline"
2. "respond in slack with an update on the deploy"
3. "write a bluesky post about what I learned today"

### Paraphrased

4. "I need to write a message to the team on Slack about the migration"
5. "can you compose an email to the client about the timeline change"
6. "put together a bluesky thread about the new API design"

### Edge Cases

7. "write a reply" (no channel specified — should trigger and ask which channel)
8. "draft something for the team" (implicit Slack — should trigger)

### Embedded Context

9. "We just finished the sprint. Can you draft a slack message about it?"
10. "I need to tell the client about the delay — write an email"

## Should NOT Trigger (expect skill to stay inactive)

### Adjacent Domain

11. "Write a README for this project"
12. "Help me write better documentation"
13. "Draft a CLAUDE.md for this repo"

### General Programming

14. "Write a function that validates email addresses"
15. "Create a Python script to process these CSV files"
16. "Generate a shell script for the deploy pipeline"

### Keyword Overlap Wrong Context

17. "What's the best way to draft error messages in this UI?"
18. "How should I compose these database queries?"

### Other Skills

19. "Reply to the customer support ticket about the billing issue" (customer-reply)
20. "Create a commit message for these changes" (octoflow)

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

**Score**: **_/20 (_**)

## Description Quality Score

Evaluated against the description engineering formula: [what it does] + [when to use it] + [trigger phrases] + [negative cases].

| Criterion       | Score | Notes                                                                                          |
| --------------- | ----- | ---------------------------------------------------------------------------------------------- |
| What it does    | 5/5   | Clear: drafts messages in user's voice for channels                                            |
| When to use it  | 5/5   | "Use when the user asks to..." with 7 trigger phrases                                          |
| Trigger phrases | 4/5   | Good coverage but missing "write a LinkedIn post", "send a message"                            |
| Negative cases  | 4/5   | Covers code/docs/READMEs, customer support, monitoring. Could add "commit messages" (octoflow) |
| Conciseness     | 5/5   | ~290 chars, well under 1024 limit                                                              |
| Third-person    | 5/5   | Properly third-person throughout                                                               |

**Description quality: 28/30 (Excellent)**

### Suggested improvements

- Add "write a LinkedIn post" to trigger phrases (LinkedIn is a supported custom channel)
- Add "send a message" and "reply to this" as trigger phrases
- Add "commit messages" to negative cases (overlaps with octoflow)
