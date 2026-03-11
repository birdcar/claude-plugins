# plugin.json Template

Generate plugin.json files using this structure. Include only fields that apply.

## Structure

```json
{
  "name": "{plugin-name}",
  "version": "{semver}",
  "description": "{One-line plugin description}",
  "commands": ["./commands/"],
  "agents": ["./agents/{agent-1}.md", "./agents/{agent-2}.md"]
}
```

## Field Reference

| Field         | Required          | Type     | Notes                                          |
| ------------- | ----------------- | -------- | ---------------------------------------------- |
| `name`        | Yes               | string   | kebab-case, matches directory name             |
| `version`     | Yes               | string   | semver (e.g., "0.1.0")                         |
| `description` | Yes               | string   | One-line summary                               |
| `commands`    | If commands exist | string[] | Directory path(s) containing command .md files |
| `agents`      | If agents exist   | string[] | Explicit paths to each agent .md file          |

## Rules

- Skills are auto-discovered from `skills/` directory — do NOT add a `"skills"` field
- Commands use directory discovery: `["./commands/"]` finds all .md files in that directory
- Agents require explicit file paths — no directory discovery
- Hooks go in `hooks/hooks.json`, NOT in plugin.json
- The `"hooks"` field in plugin.json is NOT supported and causes validation errors
- Start at version `"0.1.0"` for new plugins
- Bump version for every functional change (patch for fixes, minor for features)

## Companion Files

Every plugin.json needs these siblings:

**package.json**:

```json
{
  "name": "{package-scope}/claude-plugin-{plugin-name}",
  "version": "{same-version}",
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
    "outDir": "./dist",
    "rootDir": "."
  },
  "include": [],
  "files": []
}
```

**Root tsconfig.json** — add a project reference:

```json
{ "path": "plugins/{plugin-name}" }
```

After creating all files, run:

```bash
bun run sync    # Updates marketplace.json
bun run typecheck  # Verify TypeScript
bun run build      # Compile
```
