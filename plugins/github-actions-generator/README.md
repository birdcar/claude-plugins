# github-actions-generator

Scaffolds and implements TypeScript GitHub Actions in Bun workspace monorepos, from empty directory to tagged release.

Writing a new GitHub Action in a Bun monorepo means wiring together package.json with catalog references, tsconfig, action.yml, an entrypoint, tests, a per-action CI workflow with path filters, and release tagging. This plugin handles that entire lifecycle so you only need to write the action logic itself.

## Installation

```bash
claude plugin install github-actions-generator
```

## What it does

The `generate-action` skill walks through the full lifecycle interactively. Trigger it by describing what you want to build:

> "Create a GitHub Action that labels issues based on their title"

It will:

1. Read your workspace's `package.json` to detect the Bun catalog, workspace layout, and existing action conventions
2. Ask for the action name, description, and what GitHub resources it touches
3. Generate `package.json` (using `catalog:` references), `tsconfig.json`, `action.yml`, and `src/index.ts`
4. Run `bun install` and `bun run build` to verify the scaffold compiles cleanly
5. Help implement the action logic using Octokit, then validate with build and lint
6. Generate unit tests with `bun:test` covering happy path, edge cases, and API failures
7. Write a README with real version tags (never `@latest`), inputs/outputs tables, and an example workflow
8. Create `.github/workflows/test-{action-name}.yml` with path filters scoped to the action directory
9. Guide through manual tagging or generate an automated release workflow

## Requirements

Your repo needs to be a Bun workspace with `@actions/core`, `@actions/github`, and `@octokit/rest` in the root catalog. If any of these are missing, the skill will walk you through adding them before proceeding.

## Conventions

The skill follows these rules consistently, matching them to whatever patterns already exist in your repo:

- `catalog:` for all shared dependency versions, never pinned duplicates
- `kebab-case` for action names, package names, and directories
- `bun:test` for testing, not Jest
- Real version tags in generated docs (`{action-name}-v1.0.0`, not `@latest`)
- Per-action CI workflows with path filters rather than a single monorepo-wide workflow
- Ask before overwriting any existing file
