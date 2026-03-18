---
name: build
description: Build the project
allowed-tools: [Bash, Read, Glob]
---

Build the project using the appropriate build system.

## Detection

Identify the build system by checking for these files in order:

1. `bun.lock` or `bun.lockb` → Bun project
2. `pnpm-lock.yaml` → pnpm project
3. `package-lock.json` → npm project
4. `yarn.lock` → Yarn project
5. `deno.json` or `deno.jsonc` → Deno project
6. `Cargo.toml` → Rust project
7. `go.mod` → Go project
8. `pyproject.toml` → Python project

For Node-based projects, also check `package.json` for a `build` script.

## Execution

Run the build command based on detected tooling:

- **Bun**: `bun run build` (if build script exists), else `bun build`
- **pnpm**: `pnpm run build`
- **npm**: `npm run build`
- **Yarn**: `yarn build`
- **Deno**: `deno task build` (if task exists), else `deno compile`
- **TypeScript only** (no build script): `tsc --build`
- **Rust**: `cargo build --release`
- **Go**: `go build ./...`
- **Python**: `uv build` (if `uv.lock` exists), else `python -m build`

If `$ARGUMENTS` is provided, pass it through to the build command (e.g., `/build --debug` → `cargo build`).

## Error Handling

If the build fails:
- Show the first error clearly
- For TypeScript errors, suggest the fix
- For missing dependencies, suggest running `/deps` first
- Do not retry automatically
