# Claude Plugins Repository

Personal Claude Code plugin marketplace using Bun workspaces and TypeScript.

## Structure

```
claude-plugins/
├── .claude-plugin/       # Marketplace metadata
│   └── plugin.json       # Lists all available plugins
├── plugins/              # Plugin packages (Bun workspace)
│   └── {plugin-name}/
│       ├── package.json
│       ├── tsconfig.json
│       ├── plugin.json   # Claude Code plugin metadata
│       ├── skills/       # Skill definitions
│       │   └── {skill}/
│       │       └── INSTRUCTIONS.md
│       └── src/          # TypeScript source (if needed)
├── scripts/              # Build utilities
├── package.json          # Workspace root
├── tsconfig.json         # Project references
└── tsconfig.base.json    # Shared TS config
```

## Conventions

- Plugin names: kebab-case
- Skill names: kebab-case
- TypeScript: strict mode, ES2022 target, NodeNext modules
- Formatting: Prettier with defaults from .prettierrc

## Commands

- `bun run build` - Compile TypeScript
- `bun run typecheck` - Type check without emit
- `bun run sync` - Update marketplace from plugins/
- `bun run format` - Format code with Prettier

## Adding a New Plugin

1. Create `plugins/{name}/` with package.json, tsconfig.json, plugin.json
2. Add skills in `skills/{skill-name}/INSTRUCTIONS.md`
3. Add TypeScript in `src/` if runtime code needed
4. Add reference to root tsconfig.json
5. Run `bun run sync`
