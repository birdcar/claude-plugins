# dev-commands

Five slash commands that detect your project's tooling and run the right thing.

The friction isn't usually running a build or test suite — it's remembering which command this project uses. Is it `bun test` or `pytest` or `cargo test`? Does lint here mean `ruff` or `eslint` or `clippy`? These commands figure that out from your lockfiles and config files so you don't have to context-switch.

## Install

```sh
claude plugin install dev-commands
```

## Commands

`/build` — builds the project. Detects `package.json` build scripts, `tsconfig.json` for tsc, `Cargo.toml`, `go.mod`, `pyproject.toml`, and Deno. Falls back to `tsc --build` for TypeScript-only projects. Pass extra arguments through: `/build --debug`.

`/check` — runs the full pre-commit sequence: typecheck → lint → test, stopping on the first failure. Summarizes what passed and what broke.

`/deps` — installs dependencies using the detected package manager. Pass `update` or `upgrade` to upgrade instead: `/deps update`. Pass a package name to add it: `/deps zod`.

`/lint` — runs the linter with auto-fix enabled. Detects Biome, oxlint, ESLint, Prettier, Ruff, Black, Clippy, golangci-lint, and Deno lint. Reports anything it couldn't fix automatically. Pass a path to lint only that directory: `/lint src/`.

`/test` — runs the test suite. Pass an optional filter to narrow down: `/test auth`. Detects Bun, Vitest, Jest, pytest, `cargo test`, and `go test`. For pytest the filter uses `-k`; for Go it uses `-run`.

## Tooling detection

Each command reads lockfiles and config files rather than checking what's installed globally:

- Node/Bun: `bun.lock`, `bun.lockb`, `pnpm-lock.yaml`, `package-lock.json`, `yarn.lock`
- Deno: `deno.json`, `deno.jsonc`
- Python: `uv.lock`, `Pipfile.lock`, `requirements.txt`, `pyproject.toml`, `pytest.ini`
- Rust: `Cargo.toml`, `Cargo.lock`
- Go: `go.mod`, `go.sum`, `.golangci.yml`

When multiple Node package managers could apply, the detection order is bun > pnpm > npm > yarn.
