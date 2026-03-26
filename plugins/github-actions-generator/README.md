# github-actions-generator

Scaffolds TypeScript GitHub Actions in Bun workspace monorepos, from empty directory to tagged release.

Standing up a new action in a Bun monorepo means wiring together a `package.json` with catalog references, `tsconfig.json`, `action.yml`, a typed entrypoint, unit tests, a per-action CI workflow with path filters, and release tagging — before you've written a line of actual logic. This plugin handles that scaffolding through a single `generate-action` skill that covers the full lifecycle interactively.

## Installation

```bash
claude plugin install github-actions-generator@birdcar-plugins
```

## What it does

Trigger the skill by describing what you want to build:

> "Create a GitHub Action that labels issues based on their title"

The skill walks through the lifecycle in stages, stopping to ask questions when it needs input:

**Scaffold** — Reads your root `package.json` to detect workspace layout, Bun catalog entries, and existing action conventions. Asks for the action name, description, and what GitHub resources it touches. Generates `package.json` (with `catalog:` references), `tsconfig.json`, `action.yml`, and `src/index.ts`. Runs `bun install` and `bun run build` to verify the scaffold compiles before moving on.

**Implement** — Helps write the action logic using `@actions/core`, `@actions/github`, and `@octokit/rest`. Validates with build and lint after changes.

**Test** — Generates `bun:test` unit tests covering happy path, edge cases (empty inputs, boundary values), and API failure scenarios (rate limits, 404, 403).

**Document** — Generates a README with a real version tag (checked via `git describe`), inputs/outputs tables matching `action.yml` exactly, and an example workflow.

**CI** — Creates `.github/workflows/test-{action-name}.yml` with path filters scoped to the action directory so unrelated changes don't trigger the workflow.

**Release** — Guides through manual tagging or generates an automated release workflow at `.github/workflows/release-{action-name}.yml`.

## Requirements

Your repo needs to be a Bun workspace with `@actions/core`, `@actions/github`, and `@octokit/rest` in the root catalog. If any of these are missing, the skill will walk you through adding them before proceeding.

## Conventions

The skill follows these rules and matches them to whatever patterns already exist in your repo:

- `catalog:` for all shared dependency versions, never pinned duplicates in action packages
- `kebab-case` for action names, package names, and directories
- `bun:test` for testing, never Jest
- Real version tags in generated docs (`{action-name}-v1.0.0`, never `@latest` or `@main`)
- Per-action CI workflows with path filters rather than a single monorepo-wide workflow
- Asks before overwriting any existing file
