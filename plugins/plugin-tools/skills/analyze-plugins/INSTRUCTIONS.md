# Analyze Plugins

Analyze this plugin repository to identify improvements, discover patterns, and suggest enhancements.

## Trigger

Invoked via `/analyze-plugins` with an optional focus area.

## Process

1. **Scan Repository Structure**
   - Read all plugin directories under `plugins/`
   - Parse each `plugin.json` for metadata
   - Collect all skill INSTRUCTIONS.md files

2. **Analyze Plugin Quality**
   For each plugin, evaluate:
   - Completeness: Does it have all required files? (package.json, tsconfig.json, plugin.json, skills/)
   - Consistency: Do naming conventions match? (kebab-case everywhere)
   - Documentation: Are INSTRUCTIONS.md files comprehensive?
   - Structure: Does it follow the established patterns?

3. **Identify Improvement Opportunities**
   Look for:
   - Missing or sparse documentation
   - Inconsistent patterns between plugins
   - Skills that could be more robust
   - Common patterns that could be extracted
   - Error handling gaps in skill instructions

4. **Check Against Best Practices**
   Compare skills against:
   - Clear trigger documentation
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

## Focus Areas

When invoked with a focus area, narrow analysis to:

- `/analyze-plugins structure` - Focus on directory and file organization
- `/analyze-plugins documentation` - Focus on INSTRUCTIONS.md quality
- `/analyze-plugins consistency` - Focus on pattern consistency across plugins
- `/analyze-plugins {plugin-name}` - Deep dive into a specific plugin

## Output Format

```markdown
## Plugin Analysis Report

### Summary

- Total plugins: N
- Total skills: N
- Overall health: Good/Needs Attention/Critical

### Plugin Details

#### {plugin-name}

- **Status**: Complete/Incomplete
- **Skills**: skill1, skill2
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
