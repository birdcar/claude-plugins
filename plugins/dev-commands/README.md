# dev-commands

Five slash commands that detect your project's tooling and run the right thing.

The friction isn't usually running a build or test suite — it's remembering which command this project uses. Is it `bun test` or `pytest` or `cargo test`? Does lint here mean `ruff` or `eslint` or `clippy`? These commands figure that out from your lockfiles and config so you don't have to context-switch.

## Commands

`/build` — builds the project. Detects `package.json` build scripts, `tsconfig.json` for tsc, `Cargo.toml`, `go.mod`, and `pyproject.toml`. Falls back to `tsc --build` for TypeScript-only projects.

`/check` — runs the full pre-commit sequence: typecheck → lint → test, stopping on the first failure. Summarizes what passed and what broke.

`/deps` — installs dependencies. Pass `update` or `upgrade` as an argument to upgrade instead: `/deps update`.

`/lint` — runs the linter with auto-fix enabled. Detects ESLint, Biome, Prettier, Ruff, Clippy, and golangci-lint. Reports anything it couldn't fix automatically.

`/test` — runs the test suite. Accepts an optional filter argument: `/test auth` runs only tests matching "auth". Detects test runners from `package.json` scripts, `pytest.ini`, `Cargo.toml`, and `go.mod`.

## Tooling detection

Each command reads lockfiles and config files rather than just checking what's installed globally:

- Node/Bun: `bun.lock`, `pnpm-lock.yaml`, `package-lock.json`, `yarn.lock`
- Python: `uv.lock`, `Pipfile.lock`, `requirements.txt`, `pyproject.toml`, `pytest.ini`
- Rust: `Cargo.toml`, `Cargo.lock`
- Go: `go.mod`, `go.sum`, `.golangci.yml`

## Install

```sh
claude plugin install dev-commands
```
