# github-actions-generator

Scaffold and implement TypeScript GitHub Actions within Bun workspace monorepos.

## Why

Creating a GitHub Action in a Bun workspace involves a lot of boilerplate: package.json with catalog references, tsconfig, action.yml, entry point, tests, CI workflow, and release tagging. This skill handles the full lifecycle so you can focus on the action's logic.

## Usage

The skill activates when you want to create or implement a GitHub Action. It walks you through the process interactively:

1. **Scaffold** — Detects workspace structure, asks for action name/description, generates all files (package.json, tsconfig.json, action.yml, src/index.ts)
2. **Implement** — Helps write the action logic using patterns for Octokit, error handling, and input/output management
3. **Test** — Generates unit tests with bun:test, mocking @actions/core and @actions/github
4. **Document** — Creates a README with usage examples, inputs/outputs tables, and real version tags
5. **CI** — Generates per-action CI workflows with path filters
6. **Release** — Guides through manual tagging or generates automated release workflows

## Components

| Component         | Type  | Description                                                |
| ----------------- | ----- | ---------------------------------------------------------- |
| `generate-action` | Skill | Full lifecycle GitHub Action generation and implementation |

## Conventions

- Uses Bun Catalog for shared dependency versions
- All dependencies reference `catalog:` in action package.json
- kebab-case for action names, package names, and directories
- bun:test for testing (not Jest)
- Real version tags in docs (never `@latest` or `@main`)
