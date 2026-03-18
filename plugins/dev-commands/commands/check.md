---
name: check
description: Run all checks (typecheck, lint, test)
allowed-tools: [Bash, Read, Glob]
---

Run all validation checks for the project, stopping on first failure.

## Detection

Identify the project's tooling by checking lockfiles and config files (same detection as `/build`, `/lint`, `/test`).

## Workflow

Execute checks in this order, stopping immediately on first failure:

### 1. Type Check

- **TypeScript (Bun)**: `bunx tsc --noEmit`
- **TypeScript (pnpm)**: `pnpm exec tsc --noEmit`
- **TypeScript (npm)**: `npx tsc --noEmit`
- **Python**: `ty check` (if `ty` available), else `pyright`, else `mypy`
- **Rust**: `cargo check`
- **Go**: `go vet ./...`

### 2. Lint

Run the project's linter using the same detection as `/lint`.

### 3. Test

Run the project's test suite using the same detection as `/test`.

## Output

After all checks complete (or one fails):

- List each check with pass/fail status
- If a check failed, show the error details and stop
- If all pass, confirm the project is ready to commit
