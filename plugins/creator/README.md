# creator

A single command that scaffolds new Claude Code plugin components from a natural language description.

## The problem it solves

Adding a skill or command to this repo means creating 5-6 files in the right places, following naming conventions, updating `tsconfig.json`, running sync, and verifying typecheck passes. It's not hard, but it's tedious enough that the friction slows down adding new tools.

`/create-skill` handles all of that from one sentence.

## Usage

```
/create-skill A command that formats JSON files with proper indentation
```

The command parses your description, decides whether it fits better as a command (user-invoked via `/name`) or a skill (agent-triggered by context), generates kebab-case names, and scaffolds everything. It checks for naming conflicts with existing plugins first and will offer to add the component to an existing plugin if one fits.

Once files are written, it runs `bun run typecheck && bun run build` and fixes any issues before reporting success.

## What gets created

For a new command:

```
plugins/{plugin-name}/
├── package.json
├── tsconfig.json
├── plugin.json
├── src/index.ts
└── commands/{command-name}.md
```

For a new skill:

```
plugins/{plugin-name}/
├── package.json
├── tsconfig.json
├── plugin.json
├── src/index.ts
└── skills/{skill-name}/
    └── SKILL.md
```

It also adds the new workspace reference to the root `tsconfig.json` and runs `bun run sync` to update `marketplace.json`.

## Adding to an existing plugin

If a plugin already exists that's a natural fit for the new component, the command will ask whether to add it there instead of creating a whole new plugin directory. In that case it only creates the command or skill file and updates `plugin.json` if needed.

## Commands

| Command | Description |
| --- | --- |
| `/create-skill` | Scaffold a new plugin or add a component to an existing one |
