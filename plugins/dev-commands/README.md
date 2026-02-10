# dev-commands

Slash commands for common development workflows that auto-detect your project's tooling.

## Why

Every project uses different build tools, test runners, and linters. Instead of remembering whether this project uses `bun test`, `pytest`, `cargo test`, or `go test`, these commands detect the right tool and run it. They work across Node/Bun, Python, Rust, and Go projects.

## Usage

| Command  | Description                                  |
| -------- | -------------------------------------------- |
| `/build` | Build the project using the detected build system |
| `/check` | Run all checks in order: typecheck, lint, test (stops on first failure) |
| `/deps`  | Install dependencies (`/deps`) or update them (`/deps update`) |
| `/lint`  | Run the project's linter with auto-fix       |
| `/test`  | Run the test suite (supports filtering: `/test auth`) |

## Detection

Each command scans project files to determine the right tool:

- **Node/Bun**: package.json scripts, bun.lock, pnpm-lock.yaml, package-lock.json
- **Python**: pyproject.toml, pytest.ini, uv.lock, requirements.txt
- **Rust**: Cargo.toml, Cargo.lock
- **Go**: go.mod, go.sum, .golangci.yml
