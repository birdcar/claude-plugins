# plugin-tools

Two commands for auditing and improving the plugins in this repo.

As a plugin collection grows, quality tends to drift in quiet ways — a command missing edge case handling here, inconsistent naming there, a skill whose trigger description is vague enough that Claude never uses it. `plugin-tools` gives you a structured way to catch those issues and fix them without manually reading every file.

## Commands

### `/analyze-plugins`

Read-only audit of all plugins in the repo. Scans every `plugin.json`, command file, and skill definition, then produces a structured report with quality scores and prioritized improvement suggestions. It compares plugins against each other rather than against some external standard, so the suggestions reflect what's actually inconsistent in your repo.

```
/analyze-plugins                    # full audit of everything
/analyze-plugins structure          # directory and file organization only
/analyze-plugins documentation      # instruction quality and completeness
/analyze-plugins consistency        # naming and pattern consistency across plugins
/analyze-plugins skill-forge        # deep dive into a specific plugin
```

The report format is:

```markdown
## Plugin Analysis Report

### Summary
- Total plugins: N
- Overall health: Good / Needs Attention / Critical

### Plugin Details
#### {plugin-name}
- Status: Complete / Incomplete
- Issues: ...
- Suggestions: ...

### Priority Improvements
1. [High] ...
2. [Medium] ...
```

### `/improve-skill`

Takes a skill or command name, reads the current instruction file, and proposes specific changes — additional rules, better examples, edge case handling, clearer language. Changes are shown as a diff-style preview before anything is written.

```
/improve-skill commit
/improve-skill commit "needs guidance on merge commits"
```

If you pass feedback, it incorporates that directly. Without feedback, it prompts you for what's not working. After you approve the changes, it applies them and verifies the build still passes.

The command also checks whether the component is the right type for its usage pattern. If something is a skill but should be a command (or vice versa), it'll flag that with a recommendation to convert.

## Installation

```bash
claude plugin install plugin-tools
```

## What it doesn't do

`/analyze-plugins` is strictly read-only. It won't touch any files. `/improve-skill` won't rewrite components from scratch — it makes incremental improvements while preserving the original intent of what the component does.
