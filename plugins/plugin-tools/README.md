# plugin-tools

Commands for analyzing and iteratively improving Claude Code plugins.

## Why

As your plugin collection grows, it's easy for quality to drift — inconsistent naming, missing edge case handling, sparse documentation. These commands give you a way to audit your plugins and systematically improve them based on concrete feedback.

## Usage

| Command             | Description                                           |
| ------------------- | ----------------------------------------------------- |
| `/analyze-plugins`  | Read-only audit of plugin quality, structure, and consistency |
| `/improve-skill`    | Iteratively improve an existing skill or command       |

### `/analyze-plugins`

Scans all plugins and generates a structured report with quality scores, specific issues, and prioritized improvement suggestions.

Supports focus areas:

- `/analyze-plugins structure` — Directory and file organization
- `/analyze-plugins documentation` — Instruction quality and completeness
- `/analyze-plugins consistency` — Pattern consistency across plugins
- `/analyze-plugins {plugin-name}` — Deep dive into a specific plugin

### `/improve-skill`

Takes a skill or command name and optional feedback, analyzes the current instructions, proposes specific improvements (additional rules, better examples, edge case handling), and applies changes after approval.

```
/improve-skill commit
/improve-skill commit "needs guidance on merge commits"
```
