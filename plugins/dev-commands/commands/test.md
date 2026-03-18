---
name: test
description: Run the project's test suite
allowed-tools: [Bash, Read, Glob]
---

Run the test suite for this project.

## Detection

Identify the test runner by checking lockfiles and config files:

1. `bun.lock` or `bun.lockb` → `bun test`
2. `vitest.config.*` or vitest in devDependencies → `vitest`
3. `jest.config.*` or jest in devDependencies → `jest`
4. `package.json` with test script → use the package manager's `test` script
5. `deno.json` or `deno.jsonc` → `deno test`
6. `pyproject.toml` or `pytest.ini` → `pytest`
7. `Cargo.toml` → `cargo test`
8. `go.mod` → `go test ./...`

For Node-based projects, prefer the lockfile-detected package manager (bun > pnpm > npm) when running commands.

## Execution

Run the detected test command:

- **Bun**: `bun test`
- **Vitest**: `bunx vitest run` (or `npx` based on lockfile)
- **Jest**: `bunx jest` (or `npx` based on lockfile)
- **pnpm**: `pnpm test`
- **npm**: `npm test`
- **Deno**: `deno test`
- **Python**: `pytest` (or `uv run pytest` if `uv.lock` exists)
- **Rust**: `cargo test`
- **Go**: `go test ./...`

If `$ARGUMENTS` is provided, use it to filter tests:

- **Bun/Vitest/Jest**: pass as positional arg (e.g., `bun test auth`)
- **pytest**: pass with `-k` flag (e.g., `pytest -k auth`)
- **Rust**: pass as positional arg (e.g., `cargo test auth`)
- **Go**: pass with `-run` flag (e.g., `go test ./... -run Auth`)

If tests fail, analyze the output and suggest fixes.
