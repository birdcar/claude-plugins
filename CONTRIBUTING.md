# Contributing

Guide for adding new plugins to the marketplace.

## Plugin Structure

```
plugins/my-plugin/
├── package.json        # Package metadata
├── tsconfig.json       # TypeScript config (extends ../../tsconfig.base.json)
├── plugin.json         # Claude Code plugin metadata
├── skills/
│   └── my-skill/
│       └── INSTRUCTIONS.md
└── src/                # TypeScript source (optional)
    └── index.ts
```

## Adding a New Plugin

1. Create the directory structure under `plugins/`
2. Create `package.json` with name and version
3. Create `tsconfig.json` extending the base config
4. Create `plugin.json` with skills array pointing to `./skills/`
5. Write `INSTRUCTIONS.md` for each skill
6. Add reference to root `tsconfig.json`
7. Run `bun run sync` to update marketplace
8. Test with Claude Code

Or use the creator skill:

```
/create-skill A skill that does XYZ
```

## Conventions

- **Plugin names**: kebab-case (e.g., `my-plugin`)
- **Skill names**: kebab-case (e.g., `my-skill`)
- **TypeScript**: strict mode, ES2022 target
- **Formatting**: Prettier (run `bun run format`)

## Checklist

Before submitting:

- [ ] `plugin.json` is valid JSON with name, version, description, skills
- [ ] `INSTRUCTIONS.md` is comprehensive (trigger, process, rules)
- [ ] `bun run typecheck` passes
- [ ] `bun run build` succeeds
- [ ] `bun run sync` discovers the plugin
- [ ] `bun run format:check` passes
- [ ] Skills work when tested in Claude Code
