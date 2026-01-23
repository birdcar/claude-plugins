# Package.json Template

Generate `package.json` for a new GitHub Action.

## Template

```json
{
  "name": "@{scope}/{action-name}",
  "version": "0.0.0",
  "private": true,
  "type": "module",
  "main": "dist/index.js",
  "scripts": {
    "build": "bun build src/index.ts --outdir dist --target node",
    "test": "bun test",
    "lint": "biome check .",
    "format": "biome format --write ."
  },
  "dependencies": {
    "@actions/core": "catalog:",
    "@actions/github": "catalog:",
    "@octokit/rest": "catalog:"
  },
  "devDependencies": {
    "@biomejs/biome": "catalog:",
    "@types/bun": "catalog:"
  }
}
```

## Variables

| Variable        | Source                                                  | Example                     |
| --------------- | ------------------------------------------------------- | --------------------------- |
| `{scope}`       | Organization scope from root package.json or user input | `birdcar`, `workos`         |
| `{action-name}` | Kebab-case action name from user input                  | `add-label`, `create-issue` |

## Determining Scope

1. Check root `package.json` for existing package names with scopes
2. If multiple scopes exist, ask user which to use
3. If no scope pattern, ask user for preferred scope

## Adding Dependencies

When user needs additional dependencies:

**Global (Catalog)**:

```json
{
  "dependencies": {
    "new-package": "catalog:"
  }
}
```

Also add to root package.json catalog section.

**Local (Pinned)**:

```json
{
  "dependencies": {
    "new-package": "^1.2.3"
  }
}
```

## Notes

- Version starts at `0.0.0` - will be set properly on first release
- `private: true` prevents accidental npm publish
- Build target is `node` for GitHub Actions runtime
- All shared dependencies use `catalog:` protocol
