# creator

Generate new Claude Code plugin components from natural language descriptions.

## Why

Scaffolding a new plugin or adding a skill/command involves creating multiple files with the right structure, naming conventions, and workspace configuration. This plugin automates that so you can go from idea to working component in one step.

## Usage

```
/create-skill A command that formats JSON files with proper indentation
```

The command will:

1. Parse your description to determine what kind of component to create (command vs skill)
2. Generate kebab-case names for the plugin and component
3. Check for naming conflicts with existing plugins
4. Scaffold the full directory structure (package.json, tsconfig.json, plugin.json, src/index.ts, and the command/skill file)
5. Add the new workspace to root tsconfig.json
6. Run `bun run sync` to update marketplace.json
7. Validate with `bun run typecheck && bun run build`

If a suitable existing plugin already exists, it will offer to add the component there instead of creating a new plugin.

## Components

| Component       | Type    | Description                                                 |
| --------------- | ------- | ----------------------------------------------------------- |
| `/create-skill` | Command | Scaffold a new plugin or add a component to an existing one |
