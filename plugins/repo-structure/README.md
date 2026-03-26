# repo-structure

Enforces the `~/Code/ORG/REPO` directory convention for cloned repos and new projects. Implemented entirely as `PreToolUse` hooks — no skills or commands, just automatic interception.

Without a consistent layout, repos accumulate on the Desktop, in Downloads, or directly in `~`. This plugin intercepts Bash commands before they run, so you don't have to remember the convention or police it manually. If Claude tries to clone or scaffold in the wrong place, the hook blocks the command and returns the corrected version with `mkdir -p` included.

## Install

```bash
/plugin marketplace add birdcar/claude-plugins
/plugin install repo-structure@birdcar-plugins
```

## What it enforces

**Cloning** (`git clone`, `gh repo clone`): target must be `~/Code/{org}/{repo}`.

Parses GitHub HTTPS URLs, SSH URLs, and `gh` CLI shorthand. Strips `.git` suffixes. Preserves any flags you pass (`--depth 1`, `--branch main`, etc.). Non-GitHub URLs pass through without validation.

**Scaffolding** (`bun init`, `npm init`, `pnpm init`, `uv init`, `cargo init`, `cargo new`): target must be `~/Code/{owner}/{project}`. When no explicit owner is given, it defaults to `birdcar`.

## WorkOS repo routing

WorkOS repos get special-cased into subdirectories rather than landing directly under `~/Code/workos/`:

| Pattern                     | Target                          |
| --------------------------- | ------------------------------- |
| `workos-{lang}` (core SDK)  | `~/Code/workos/sdk/{lang}`      |
| `workos-{lang}-{framework}` | `~/Code/workos/sdk/{framework}` |
| `authkit-{lang}`            | `~/Code/workos/sdk/{lang}`      |
| `se-demo-{name}`            | `~/Code/workos/demos/{name}`    |
| anything else               | `~/Code/workos/{repo}`          |

## Exceptions

These paths always pass through:

- `~/Code/_*/` — underscore directories for experiments and learning
- `~/Code/workos/demo` — the single WorkOS demo app (distinct from `demos/`)
- Any non-GitHub clone target

## Implementation notes

Clone validation runs as a shell script (`hooks/validate-clone.sh`) to do fast regex extraction without spinning up a Node process. Scaffolding validation runs as a prompt hook since the path inference logic benefits from Claude's context awareness — for example, knowing the CWD when no explicit path is given.

When a command is blocked, the hook returns a corrected version with `mkdir -p` so the target directory tree is created automatically.

## Limitations

The default owner (`birdcar`) is hardcoded in the prompt hook. If you fork this plugin, update that string in `hooks/hooks.json`. The clone script has no equivalent default — org is always parsed from the URL.
