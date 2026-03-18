---
name: deps
description: Install or update project dependencies
allowed-tools: [Bash, Read, Glob]
---

Install or update project dependencies.

## Detection

Identify the package manager from lockfiles:

- `bun.lock` or `bun.lockb` → bun
- `pnpm-lock.yaml` → pnpm
- `package-lock.json` → npm
- `yarn.lock` → yarn
- `deno.json` or `deno.jsonc` (with imports) → deno
- `uv.lock` → uv
- `Pipfile.lock` → pipenv
- `requirements.txt` → pip
- `Cargo.lock` → cargo
- `go.sum` → go

## Execution

If `$ARGUMENTS` contains "update" or "upgrade":

- **bun**: `bun update`
- **npm**: `npm update`
- **pnpm**: `pnpm update`
- **yarn**: `yarn upgrade`
- **deno**: `deno outdated --update`
- **uv**: `uv lock --upgrade && uv sync`
- **cargo**: `cargo update`
- **go**: `go get -u ./...`

Otherwise install:

- **bun**: `bun install`
- **npm**: `npm install`
- **pnpm**: `pnpm install`
- **yarn**: `yarn install`
- **deno**: `deno install`
- **uv**: `uv sync`
- **cargo**: `cargo build`
- **go**: `go mod download`

If `$ARGUMENTS` contains a package name (not "update"/"upgrade"), add it:

- **bun**: `bun add <pkg>`
- **npm**: `npm install <pkg>`
- **pnpm**: `pnpm add <pkg>`
- **uv**: `uv add <pkg>`
- **cargo**: `cargo add <pkg>`
- **go**: `go get <pkg>`
