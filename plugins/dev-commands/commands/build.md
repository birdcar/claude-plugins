---
name: /build
description: Build the project
allowed-tools: [Bash, Read, Glob]
---

Build the project using the appropriate build system.

## Detection

Check for build configuration:
1. `package.json` - look for build script
2. `tsconfig.json` - TypeScript compilation
3. `Cargo.toml` - Rust build
4. `go.mod` - Go build
5. `pyproject.toml` - Python build

## Execution

Run the build command:
- **Node/Bun**: `npm run build` or `bun run build`
- **TypeScript only**: `tsc --build`
- **Rust**: `cargo build --release`
- **Go**: `go build ./...`
- **Python**: `python -m build` or `uv build`

Report build errors with suggestions for fixes.
