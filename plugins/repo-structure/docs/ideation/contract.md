# repo-structure Contract

**Created**: 2026-02-09
**Confidence Score**: 96/100
**Status**: Draft

## Problem Statement

When Claude Code clones repositories or scaffolds new projects, it uses whatever directory the user specifies or defaults to the current working directory. This leads to repositories ending up in inconsistent locations, breaking the user's established convention of organizing all code under `~/Code/[org-or-user]/[repo-name]`.

The user (birdcar) has a well-defined directory structure that maps GitHub ownership to filesystem paths. Without enforcement, Claude will clone repos to `~/` or the CWD, and new projects won't default to `~/Code/birdcar/`. Over time this creates a scattered codebase that's hard to navigate from memory.

## Goals

1. All `git clone` and `gh repo clone` commands intercepted and validated against the `~/Code/ORG/REPO` convention before execution
2. New project scaffolding commands (`bun init`, `npm init`, `uv init`, `cargo init`, etc.) default to `~/Code/birdcar/PROJECT_NAME`
3. Known exceptions (WorkOS SDKs, WorkOS Demo, underscore-prefixed directories) are allowed without interference
4. When a command targets the wrong path, block it and provide the corrected command so Claude re-executes properly

## Success Criteria

- [ ] `git clone https://github.com/anthropics/claude-code` is blocked if not targeting `~/Code/anthropics/claude-code`, with correct path suggested
- [ ] `git clone git@github.com:anthropics/claude-code.git` (SSH URL) is handled identically
- [ ] `gh repo clone anthropics/claude-code` is intercepted and validated
- [ ] `bun init` in a non-conforming directory is blocked with the correct path suggested
- [ ] New projects default to `~/Code/birdcar/` when no org is specified
- [ ] Cloning to `~/Code/workos/sdk/node` for a WorkOS SDK repo is allowed
- [ ] Operations in `~/Code/_learning/` or similar underscore-prefixed dirs are allowed
- [ ] Plugin integrates cleanly into the existing `birdcar/claude-plugins` monorepo
- [ ] `bun run sync` picks up the new plugin in marketplace.json

## Scope Boundaries

### In Scope

- PreToolUse hook on Bash tool to intercept `git clone` commands (HTTPS and SSH URLs)
- PreToolUse hook on Bash tool to intercept `gh repo clone` commands
- PreToolUse hook on Bash tool to intercept common scaffolding commands (`bun init`, `npm init`, `uv init`, `cargo init`)
- URL parsing to extract org/repo from GitHub URLs
- Exception handling for WorkOS SDK paths, WorkOS Demo path, and underscore-prefixed directories
- Block-and-suggest behavior (not silent rewrite)
- Plugin manifest, package.json, tsconfig.json following existing monorepo conventions

### Out of Scope

- Intercepting `cd` or navigation commands - only clone/create operations
- Intercepting `mkdir` generically - only scaffolding tool commands
- Non-GitHub hosting providers (GitLab, Bitbucket) - GitHub only for now
- Enforcement of structure on existing repos already in wrong locations
- Any UI or interactive prompts beyond the hook prompt

### Future Considerations

- Support for GitLab/Bitbucket URL parsing
- A `/relocate` command that moves misplaced repos to the correct location
- Navigation awareness (warn when working in a non-standard path)

---

_This contract was generated from brain dump input. Review and approve before proceeding to PRD generation._
