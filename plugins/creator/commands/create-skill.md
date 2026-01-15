---
name: create-skill
description: Generate new Claude Code skills from natural language descriptions
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
---

Generate new Claude Code skills from natural language descriptions with comprehensive validation and structure.

## Process

1. **Parse the Description**
   Analyze the user's skill description to extract:
   - **Primary action**: What the skill fundamentally does
   - **Inputs**: What information or arguments it needs
   - **Outputs**: What it produces or changes
   - **Scope**: Is this a single skill or should it be multiple skills?
   - **Complexity**: Simple (single step) vs complex (multi-step workflow)

2. **Determine Component Type**
   Decide whether this should be a command or skill:
   - **Command**: User invokes explicitly via `/command-name`, discrete action
   - **Skill**: Agent triggers proactively based on context, background behavior

3. **Generate Names**
   Create kebab-case names:
   - **Plugin name**: Descriptive of the domain (e.g., `json-formatter`, `test-runner`)
   - **Component name**: Action-oriented verb phrase (e.g., `format-json`, `run-tests`)

   If a suitable existing plugin exists, ask the user if they want to add the component there instead.

4. **Check for Conflicts**
   Before creating anything:
   - Check if `plugins/{plugin-name}/` already exists
   - Check if any plugin has a component with the same name
   - If conflicts exist, present options:
     - Use a different name
     - Add to existing plugin
     - Overwrite (requires explicit confirmation)

5. **Create Plugin Structure**
   Generate the complete directory structure:

   For commands:

   ```
   plugins/{plugin-name}/
   ├── package.json
   ├── tsconfig.json
   ├── plugin.json
   ├── src/
   │   └── index.ts
   └── commands/
       └── {command-name}.md
   ```

   For skills:

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

6. **Generate Files**

   **package.json**:

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

   **tsconfig.json**:

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

   **plugin.json** (for commands):

   ```json
   {
     "name": "{plugin-name}",
     "version": "0.1.0",
     "description": "{Generated description}",
     "commands": ["./commands/"]
   }
   ```

   **plugin.json** (for skills):

   ```json
   {
     "name": "{plugin-name}",
     "version": "0.1.0",
     "description": "{Generated description}",
     "skills": ["./skills/"]
   }
   ```

   **src/index.ts**:

   ```typescript
   // {Plugin name} plugin
   export const name = '{plugin-name}';
   ```

7. **Update Project Configuration**
   - Add reference to root `tsconfig.json`
   - Run `bun run sync` to update marketplace.json

8. **Validate Creation**
   After creating files, run:

   ```bash
   bun run typecheck
   bun run build
   ```

   If either fails, fix the issue before reporting success.

9. **Report Results**
   Provide:
   - Summary of what was created
   - File locations
   - How to test the new component
   - Suggested next steps for refinement

## Command Template

Generate command files with this structure:

```markdown
---
name: { command-name }
description: { One-line description }
allowed-tools: [{ Tool1 }, { Tool2 }, ...]
---

{Description of what this command does}

## Process

1. **{Step Title}**
   {Detailed description}

2. **{Step Title}**
   {Continue for all steps}

## Examples

### Example 1: Basic Usage

{Show input and result}

## Edge Cases

- **Case 1**: {Description} → {How handled}

## Important Rules

- {Rule 1}
- {Rule 2}
```

## Skill Template

Generate INSTRUCTIONS.md files with this structure:

```markdown
# {Skill Name in Title Case}

{One-line description}

## When to Use

{Describe when the agent should proactively invoke this skill}

## Process

1. **{Step Title}**
   {Detailed description}

## Arguments

| Argument | Required | Description |
| -------- | -------- | ----------- |
| `arg1`   | Yes      | Description |

## Examples

### Example 1

{Show scenario and result}

## Important Rules

- {Rule 1}
- {Rule 2}
```

## Examples

### Simple Command

User: `/create-skill A command that formats JSON files with proper indentation`

Creates:

- Plugin: `plugins/json-formatter/`
- Command: `commands/format-json.md`
- Detects JSON files, formats with configurable indent

### Adding to Existing Plugin

User: `/create-skill A command for creating release notes` (when `essentials` plugin exists)

Prompts: "Would you like to add this to the existing `essentials` plugin, or create a new plugin?"

If adding to existing:

- Only creates `commands/release-notes.md`
- Updates `plugin.json` if needed
- Runs sync

## Important Rules

- **Never overwrite without confirmation**: If a plugin or component exists, always ask before replacing
- **Follow conventions exactly**: Match the patterns in existing plugins for consistency
- **Generate comprehensive instructions**: Include process, examples, edge cases, and rules
- **Validate before reporting success**: Run typecheck and build, fix any issues
- **Use kebab-case everywhere**: Plugin names, component names, directory names, file names
- **Run sync after creation**: Always update marketplace.json
- **Suggest improvements**: After creation, suggest how the user might refine the component
- **Single responsibility**: Each component should do one thing well - suggest splitting if too complex
- **Commands for user actions**: Most `/invoke-name` patterns should be commands, not skills
