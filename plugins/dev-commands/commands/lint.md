---
name: lint
description: Run linter and fix issues
allowed-tools: [Bash, Read, Glob, Edit]
---

Run the project's linter with auto-fix enabled.

## Detection

Identify the linter by checking config files and `package.json` devDependencies:

**JavaScript/TypeScript** (check in this order, use first match):

1. `biome.json` or `biome.jsonc` → Biome
2. `.oxlintrc.json` or oxlint in devDependencies → oxlint
3. `.eslintrc.*` or `eslint.config.*` → ESLint
4. `.prettierrc*` or prettier in devDependencies → Prettier

**Python**:

- `ruff.toml` or `[tool.ruff]` in `pyproject.toml` → Ruff
- `[tool.black]` in `pyproject.toml` → Black

**Rust**: `cargo clippy` (always available)

**Go**: `.golangci.yml` → golangci-lint, else `go vet`

**Deno**: `deno.json` → `deno lint`

## Execution

Run the linter with auto-fix:

- **Biome**: `bunx biome check --write .` (or `npx` based on lockfile)
- **oxlint**: `bunx oxlint --fix`
- **ESLint**: `npx eslint . --fix`
- **Prettier**: `npx prettier --write .`
- **Ruff**: `ruff check --fix . && ruff format .`
- **Black**: `black .`
- **Clippy**: `cargo clippy --fix --allow-dirty`
- **golangci-lint**: `golangci-lint run --fix`
- **go vet**: `go vet ./...` (no auto-fix)
- **Deno**: `deno lint`

If `$ARGUMENTS` contains a path, lint only that path instead of `.`.

Report any issues that couldn't be auto-fixed.
