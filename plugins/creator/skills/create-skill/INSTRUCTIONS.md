# Create Skill

Generate new Claude Code skills from natural language descriptions with comprehensive validation and structure.

## Trigger

Invoked via `/create-skill` followed by a description of what the skill should do.

## Process

### 1. Parse the Description

Analyze the user's skill description to extract:

- **Primary action**: What the skill fundamentally does
- **Inputs**: What information or arguments it needs
- **Outputs**: What it produces or changes
- **Scope**: Is this a single skill or should it be multiple skills?
- **Complexity**: Simple (single step) vs complex (multi-step workflow)

### 2. Generate Names

Create kebab-case names:

- **Plugin name**: Descriptive of the domain (e.g., `json-formatter`, `test-runner`)
- **Skill name**: Action-oriented verb phrase (e.g., `format-json`, `run-tests`)

If a suitable existing plugin exists, ask the user if they want to add the skill there instead.

### 3. Check for Conflicts

Before creating anything:

- Check if `plugins/{plugin-name}/` already exists
- Check if any plugin has a skill with the same name
- If conflicts exist, present options:
  - Use a different name
  - Add to existing plugin
  - Overwrite (requires explicit confirmation)

### 4. Create Plugin Structure

Generate the complete directory structure:

```
plugins/{plugin-name}/
├── package.json
├── tsconfig.json
├── plugin.json
├── src/
│   └── index.ts
└── skills/{skill-name}/
    └── INSTRUCTIONS.md
```

### 5. Generate Files

#### package.json

```json
{
  "name": "@birdcar/claude-plugin-{plugin-name}",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts"
}
```

#### tsconfig.json

```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "rootDir": "src",
    "outDir": "dist"
  },
  "include": ["src"]
}
```

#### plugin.json

```json
{
  "name": "{plugin-name}",
  "version": "0.1.0",
  "description": "{Generated description}",
  "skills": ["./skills/"]
}
```

#### src/index.ts

```typescript
// {Plugin name} plugin
export const name = '{plugin-name}';
```

#### INSTRUCTIONS.md

Generate comprehensive instructions following the template below.

### 6. Update Project Configuration

- Add reference to root `tsconfig.json`
- Run `bun run sync` to update marketplace.json

### 7. Validate Creation

After creating files, run:

```bash
bun run typecheck
bun run build
```

If either fails, fix the issue before reporting success.

### 8. Report Results

Provide:

- Summary of what was created
- File locations
- How to test the new skill
- Suggested next steps for refinement

## INSTRUCTIONS.md Template

Generate INSTRUCTIONS.md files following this comprehensive structure:

```markdown
# {Skill Name in Title Case}

{One-line description explaining what this skill does and its primary value}

## Trigger

Invoked via `/{skill-name}` {describe any arguments or options}

## Process

{Number each step. Be specific about what happens.}

1. **{Step Title}**
   {Detailed description of what this step does}
   {Include any decision points or branching logic}

2. **{Step Title}**
   {Continue for all major steps}

## Arguments

{If the skill accepts arguments, document them}

| Argument | Required | Description                  |
| -------- | -------- | ---------------------------- |
| `arg1`   | Yes      | Description                  |
| `arg2`   | No       | Description (default: value) |

## Examples

{Provide 2-3 concrete examples showing different use cases}

### Example 1: Basic Usage

User: `/{skill-name} basic input`

Result:
{Show what happens}

### Example 2: Advanced Usage

User: `/{skill-name} --option complex input`

Result:
{Show what happens}

## Edge Cases

{Document known edge cases and how they're handled}

- **Case 1**: {Description} → {How it's handled}
- **Case 2**: {Description} → {How it's handled}

## Important Rules

{Critical rules the skill must follow}

- {Rule 1}
- {Rule 2}
- {Rule 3}
```

## Examples

### Simple Skill

User: `/create-skill A skill that formats JSON files with proper indentation`

Creates:

- Plugin: `plugins/json-formatter/`
- Skill: `/format-json`
- INSTRUCTIONS.md with:
  - Process for finding and formatting JSON files
  - Options for indent size
  - Handling of invalid JSON
  - Examples with different file types

### Complex Skill

User: `/create-skill A skill that runs tests, collects coverage, and reports failures in a summary`

Creates:

- Plugin: `plugins/test-runner/`
- Skill: `/run-tests`
- INSTRUCTIONS.md with:
  - Multi-step process (run tests, collect coverage, generate report)
  - Arguments for test filtering
  - Output format options
  - Error handling for test failures
  - Examples for different test frameworks

### Adding to Existing Plugin

User: `/create-skill A skill for creating release notes` (when `essentials` plugin exists)

Prompts: "Would you like to add this to the existing `essentials` plugin, or create a new plugin?"

If adding to existing:

- Only creates `skills/release-notes/INSTRUCTIONS.md`
- Updates `plugin.json` if needed
- Runs sync

## Important Rules

- **Never overwrite without confirmation**: If a plugin or skill exists, always ask before replacing
- **Follow conventions exactly**: Match the patterns in existing plugins for consistency
- **Generate comprehensive instructions**: Don't be sparse - include process, examples, edge cases, and rules
- **Validate before reporting success**: Run typecheck and build, fix any issues
- **Use kebab-case everywhere**: Plugin names, skill names, directory names, file names
- **Run sync after creation**: Always update marketplace.json
- **Suggest improvements**: After creation, suggest how the user might want to refine the skill
- **Single responsibility**: Each skill should do one thing well - suggest splitting if too complex
