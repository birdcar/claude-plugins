---
name: deps
description: Install or update project dependencies
allowed-tools: [Bash, Read, Glob]
---

Install or update project dependencies.

## Detection

Identify package manager:
- `bun.lock` or `bun.lockb` -> bun
- `pnpm-lock.yaml` -> pnpm
- `package-lock.json` -> npm
- `yarn.lock` -> yarn
- `uv.lock` -> uv
- `Pipfile.lock` -> pipenv
- `requirements.txt` -> pip
- `Cargo.lock` -> cargo
- `go.sum` -> go

## Execution

If $ARGUMENTS contains "update" or "upgrade":
- **bun**: `bun update`
- **npm**: `npm update`
- **pnpm**: `pnpm update`
- **uv**: `uv lock --upgrade && uv sync`
- **cargo**: `cargo update`
- **go**: `go get -u ./...`

Otherwise install:
- **bun**: `bun install`
- **npm**: `npm install`
- **pnpm**: `pnpm install`
- **uv**: `uv sync`
- **cargo**: `cargo build`
- **go**: `go mod download`
