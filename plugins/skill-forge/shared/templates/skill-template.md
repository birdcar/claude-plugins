# Skill Template

Generate SKILL.md files using this structure. Replace `{placeholders}` with actual values. Remove comments and conditional sections that don't apply.

## Frontmatter

```yaml
---
name: { skill-name }
description: >-
  {What it does — one sentence}. {Capabilities list}.
  Use when the user asks to "{trigger-phrase-1}", "{trigger-phrase-2}",
  "{trigger-phrase-3}", or {broader condition}.
  Do NOT use for {negative-case-1}, {negative-case-2}, or {negative-case-3}.


# -- Optional fields below. Include only if applicable. --
# allowed-tools: {tool1}, {tool2}, {tool3}
# disable-model-invocation: true        # Only if side-effects or timing-sensitive
# user-invocable: false                  # Only if background/reference skill
# context: fork                          # Only if isolated subagent execution needed
# agent: {Explore|Plan|general-purpose}  # Only with context: fork
# model: {sonnet|haiku}                  # Only to override default
# argument-hint: [{hint-text}]           # Only for slash commands with arguments
# metadata:
#   author: {author}
#   version: {version}
#   tags: [{tag1}, {tag2}]
---
```

## Body Structure

```markdown
# {Skill Title}

{One-line summary of what this skill does and its core value.}

## Critical Rules

{Non-negotiable constraints that MUST be in the first 100 lines.}
{Use bullet points, not prose.}
{Explain why, not just what: "Use AskUserQuestion for all decisions because plain text questions can't capture structured responses."}

## Workflow

### Step 1: {Name}

{What to do, in imperative form.}
{Which tools to use and how.}
{Validation: how to know this step succeeded.}

### Step 2: {Name}

{Continue for each step...}

### Step N: {Delivery}

{Final output, how to present results.}
{Next steps for the user.}

## Examples

### Example 1: {Scenario name}

**Input**: {What the user says or provides}
**Process**: {What the skill does, briefly}
**Output**: {What the user gets}

### Example 2: {Scenario name}

{Repeat for 2-3 examples total.}

## References

{Links to supporting files — only include if references/ directory exists.}

- `${CLAUDE_SKILL_DIR}/references/{file}.md` — {what it contains}
```

## Guidelines

- Total SKILL.md: ≤500 lines
- Critical rules: within first 100 lines
- Use imperative form ("Read the file", not "You should read the file")
- Explain rationale, don't use ALL CAPS directives
- Include at least 2 examples
- Move detailed reference material to `references/` directory
- Move output templates to `templates/` directory
- Reference scripts as execution targets, not reading material
