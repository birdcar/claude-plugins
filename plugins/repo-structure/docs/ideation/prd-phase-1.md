# PRD: repo-structure - Phase 1

**Contract**: ./contract.md
**Phase**: 1 of 1
**Focus**: Enforce ~/Code/ORG/REPO directory convention via PreToolUse hooks

## Phase Overview

This is a single-phase implementation that adds a new plugin to the `birdcar/claude-plugins` monorepo. The plugin uses PreToolUse prompt hooks on the Bash tool to intercept git clone operations and project scaffolding commands, validating that they target the correct directory path per the user's convention.

When a command targets the wrong path, the hook blocks execution and instructs Claude to re-execute with the corrected path. Known exceptions (WorkOS SDKs, WorkOS Demo, underscore-prefixed directories) are explicitly allowed.

## User Stories

1. As a developer, I want git clone commands to always place repos in `~/Code/ORG/REPO` so that I can find any repository by its GitHub ownership path
2. As a developer, I want new project scaffolding to default to `~/Code/birdcar/` so that my personal projects are consistently located
3. As a developer, I want my WorkOS SDK and experimental directory exceptions respected so that the hook doesn't interfere with my established special cases

## Functional Requirements

### Git Clone Interception

- **FR-1.1**: Intercept `git clone <url>` commands targeting the Bash tool
- **FR-1.2**: Parse HTTPS GitHub URLs (`https://github.com/ORG/REPO[.git]`) to extract org and repo name
- **FR-1.3**: Parse SSH GitHub URLs (`git@github.com:ORG/REPO[.git]`) to extract org and repo name
- **FR-1.4**: If the clone command doesn't specify a target directory, block and suggest `~/Code/ORG/REPO` with `mkdir -p` for parent dirs
- **FR-1.5**: If the clone command specifies a target directory that doesn't match `~/Code/ORG/REPO`, block and suggest the correct path
- **FR-1.6**: If the clone command correctly targets `~/Code/ORG/REPO`, allow it to proceed

### gh repo clone Interception

- **FR-1.7**: Intercept `gh repo clone ORG/REPO` commands
- **FR-1.8**: Extract org and repo from the `ORG/REPO` argument
- **FR-1.9**: Apply the same path validation as git clone

### Project Scaffolding Interception

- **FR-1.10**: Intercept `bun init`, `npm init`, `pnpm init`, `uv init`, `cargo init`, `cargo new` commands
- **FR-1.11**: Check if the current working directory or specified path follows the `~/Code/OWNER/PROJECT` convention
- **FR-1.12**: If not, suggest the correct path under `~/Code/birdcar/PROJECT_NAME`

### Exception Handling

- **FR-1.13**: Allow operations in `~/Code/_*` directories (underscore-prefixed) without interference
- **FR-1.14**: Allow operations in `~/Code/workos/sdk/*` for WorkOS SDK repos
- **FR-1.15**: Allow operations at `~/Code/workos/demo` for the WorkOS Demo repo
- **FR-1.16**: Allow operations in any path that already matches `~/Code/ORG/REPO` structure

## Non-Functional Requirements

- **NFR-1.1**: Hook prompt must be clear enough that Claude consistently follows the block-and-suggest pattern
- **NFR-1.2**: Hook matcher patterns must not produce false positives on unrelated Bash commands
- **NFR-1.3**: Plugin must follow existing monorepo conventions (package.json, tsconfig.json, plugin.json)

## Dependencies

### Prerequisites

- Existing `birdcar/claude-plugins` monorepo structure
- Understanding of PreToolUse hook prompt format and matcher syntax

### Outputs

- Fully functional `repo-structure` plugin registered in marketplace.json

## Acceptance Criteria

- [ ] HTTPS git clone URLs are parsed and validated
- [ ] SSH git clone URLs are parsed and validated
- [ ] `gh repo clone` commands are parsed and validated
- [ ] Scaffolding commands (`bun init`, `npm init`, `uv init`, `cargo init`) are intercepted
- [ ] Wrong-path commands are blocked with clear corrective instructions
- [ ] Correct-path commands pass through without interference
- [ ] WorkOS SDK exception paths are allowed
- [ ] WorkOS Demo exception path is allowed
- [ ] Underscore-prefixed directories are allowed
- [ ] Plugin builds and typechecks with `bun run build && bun run typecheck`
- [ ] `bun run sync` generates correct marketplace.json entry
- [ ] `bun run format:check` passes

---

_Review this PRD and provide feedback before spec generation._
