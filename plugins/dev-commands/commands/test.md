---
name: /test
description: Run the project's test suite
allowed-tools: [Bash, Read, Glob]
---

Run the test suite for this project.

## Detection

First, detect the test runner by checking:
1. `package.json` for test scripts (npm test, vitest, jest, etc.)
2. `pyproject.toml` or `pytest.ini` for pytest
3. `Cargo.toml` for Rust tests
4. `go.mod` for Go tests

## Execution

Run the appropriate test command:
- **Node/Bun**: `npm test` or `bun test` or `pnpm test`
- **Python**: `pytest` or `python -m pytest`
- **Rust**: `cargo test`
- **Go**: `go test ./...`

If tests fail, analyze the output and suggest fixes.

If $ARGUMENTS is provided, use it to filter tests (e.g., `/test auth` runs only auth-related tests).
