---
name: lint
description: Run linter and fix issues
allowed-tools: [Bash, Read, Glob, Edit]
---

Run the project's linter and optionally fix issues.

## Detection

Check for linting tools:

1. `package.json` - eslint, biome, prettier, oxlint
2. `pyproject.toml` - ruff, black, flake8
3. `Cargo.toml` - clippy
4. `.golangci.yml` - golangci-lint

## Execution

Run the linter:

- **ESLint**: `npx eslint . --fix`
- **Biome**: `npx biome check --write`
- **Prettier**: `npx prettier --write .`
- **Ruff**: `ruff check --fix . && ruff format .`
- **Clippy**: `cargo clippy --fix`
- **Go**: `golangci-lint run --fix`

Report any issues that couldn't be auto-fixed.
