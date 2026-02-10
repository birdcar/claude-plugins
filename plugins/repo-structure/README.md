# repo-structure

Enforces the `~/Code/ORG/REPO` directory convention for cloned repos and new projects.

## Why

Without a consistent directory structure, repos end up scattered across Desktop, Downloads, random home directories. This plugin ensures every GitHub clone and every scaffolded project lands in the right place: `~/Code/{org}/{repo}`.

It works passively through hooks — no commands to remember. If Claude tries to clone a repo to the wrong directory or scaffold a project outside the convention, the hook blocks it and provides the corrected command.

## How It Works

The plugin registers `PreToolUse` hooks on `Bash` commands that match cloning and scaffolding patterns. When triggered, the hook validates the target directory and blocks the command if it doesn't match the convention.

### Cloning (`git clone`, `gh repo clone`)

Enforces: `~/Code/{ORG}/{REPO}`

- Parses GitHub URLs (HTTPS, SSH) and `gh` CLI syntax to extract org and repo
- Blocks clones to wrong directories and provides corrected command with `mkdir -p`
- Preserves original flags (`--depth 1`, `--branch main`, etc.)
- Only applies to GitHub URLs — non-GitHub clones are allowed anywhere

### Scaffolding (`bun init`, `npm init`, `uv init`, `cargo init`, `cargo new`, `pnpm init`)

Enforces: `~/Code/{OWNER}/{PROJECT}` (defaults owner to `birdcar`)

- Checks the target directory of the scaffolding command
- Blocks if not under `~/Code/{owner}/{project}`
- Provides corrected command with `mkdir -p` and `cd`

### Exceptions

These paths are always allowed:

- `~/Code/workos/sdk/*` — WorkOS SDK workspace
- `~/Code/workos/demo` — WorkOS demo app
- `~/Code/_*/` — Underscore directories for learning, experiments, etc.
