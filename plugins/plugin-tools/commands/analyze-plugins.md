---
name: analyze-plugins
description: Analyze plugin repository to identify improvements and suggest enhancements
allowed-tools: [Bash, Read, Glob, Grep]
---

Analyze this plugin repository to identify improvements, discover patterns, and suggest enhancements.

## Process

1. **Scan Repository Structure**
   - Read all plugin directories under `plugins/`
   - Parse each `plugin.json` for metadata
   - Collect all skill INSTRUCTIONS.md and command files

2. **Analyze Plugin Quality**
   For each plugin, evaluate:
   - Completeness: Does it have all required files? (package.json, tsconfig.json, plugin.json, commands/ or skills/)
   - Consistency: Do naming conventions match? (kebab-case everywhere)
   - Documentation: Are instructions comprehensive?
   - Structure: Does it follow established patterns?

3. **Identify Improvement Opportunities**
   Look for:
   - Missing or sparse documentation
   - Inconsistent patterns between plugins
   - Components that could be more robust
   - Common patterns that could be extracted
   - Error handling gaps in instructions

4. **Check Against Best Practices**
   Compare components against:
   - Clear trigger/description documentation
   - Step-by-step process instructions
   - Important rules section
   - Example usage
   - Edge case handling

5. **Generate Report**
   Output a structured analysis with:
   - Summary of plugins found
   - Quality scores for each plugin
   - Specific improvement suggestions
   - Priority ranking of fixes

## Arguments

| Argument | Required | Description                                                                 |
| -------- | -------- | --------------------------------------------------------------------------- |
| focus    | No       | Focus area: `structure`, `documentation`, `consistency`, or `{plugin-name}` |

## Focus Areas

- `/analyze-plugins structure` - Focus on directory and file organization
- `/analyze-plugins documentation` - Focus on instruction quality
- `/analyze-plugins consistency` - Focus on pattern consistency across plugins
- `/analyze-plugins {plugin-name}` - Deep dive into a specific plugin

## Output Format

```markdown
## Plugin Analysis Report

### Summary

- Total plugins: N
- Total commands: N
- Total skills: N
- Overall health: Good/Needs Attention/Critical

### Plugin Details

#### {plugin-name}

- **Status**: Complete/Incomplete
- **Components**: command1, command2, skill1
- **Issues**:
  - Issue 1
  - Issue 2
- **Suggestions**:
  - Suggestion 1
  - Suggestion 2

### Priority Improvements

1. [High] Description of critical improvement
2. [Medium] Description of moderate improvement
3. [Low] Description of minor improvement
```

## Important Rules

- Never modify files during analysis - this is read-only
- Be specific in suggestions - point to exact files and lines
- Prioritize improvements by impact
- Compare against existing patterns in the repository, not external standards
- If a plugin is well-structured, say so - don't invent problems
