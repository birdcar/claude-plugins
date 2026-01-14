# Create Skill

Generate new Claude Code skills from natural language descriptions.

## Trigger

Invoked via `/create-skill` followed by a description of what the skill should do.

## Process

1. Parse the user's skill description to understand:
   - What the skill should do
   - What inputs it needs
   - What outputs it produces
2. Generate a plugin name in kebab-case from the description
3. Generate a skill name in kebab-case
4. Create the complete plugin directory structure:

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

5. Generate each file with appropriate content:
   - `package.json`: Standard package config with @birdcar scope
   - `tsconfig.json`: Extends ../../tsconfig.base.json
   - `plugin.json`: Plugin metadata with skills array pointing to ./skills/
   - `src/index.ts`: Placeholder export
   - `INSTRUCTIONS.md`: Comprehensive skill instructions based on the description

6. Add the new plugin to root `tsconfig.json` references
7. Run `bun run sync` to update marketplace.json
8. Report success with next steps for testing

## INSTRUCTIONS.md Template

Generate INSTRUCTIONS.md files following this structure:

```markdown
# {Skill Name}

{One-line description of what this skill does}

## Trigger

Invoked via `/{skill-name}` {plus any arguments}

## Process

1. {Step 1}
2. {Step 2}
3. {Step 3}
   ...

## Important Rules

- {Rule 1}
- {Rule 2}
```

## Example

User: `/create-skill A skill that formats JSON files with proper indentation`

Creates:

- Plugin: `plugins/json-formatter/`
- Skill: `/format-json`
- INSTRUCTIONS.md with JSON formatting logic

## Important Rules

- Always create valid, installable plugin structures
- Follow existing plugin conventions exactly (check other plugins for reference)
- Generate comprehensive INSTRUCTIONS.md - don't be sparse
- Run sync after generating to register the new plugin
- Never overwrite existing plugins without explicit user confirmation
- Use kebab-case for all names (plugin names, skill names, directory names)
