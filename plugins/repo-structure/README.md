# repo-structure

Enforces the `~/Code/ORG/REPO` directory convention for cloned repos. Implemented entirely as a `PreToolUse` hook — no skills or commands, just automatic interception.

Without a consistent layout, clones accumulate on the Desktop, in Downloads, or directly in `~`. This plugin intercepts `git clone` and `gh repo clone` before they run, so you don't have to remember a target path. If Claude tries to clone into the wrong place, the hook blocks the command and returns the corrected version with `mkdir -p` included.

It fires **only** on `git clone` and `gh repo clone`. Every other Bash command passes straight through untouched.

## Install

```bash
/plugin marketplace add birdcar/claude-plugins
/plugin install repo-structure@birdcar-plugins
```

## What it enforces

**Cloning** (`git clone`, `gh repo clone`): target must be `~/Code/{org}/{repo}`.

Parses GitHub HTTPS URLs, SSH URLs, and `gh` CLI shorthand. Strips `.git` suffixes. Preserves any flags you pass (`--depth 1`, `--branch main`, etc.). Non-GitHub URLs pass through without validation.

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

These clone targets always pass through:

- `~/Code/_*/` — underscore directories for experiments and learning
- `~/Code/workos/demo` — the single WorkOS demo app (distinct from `demos/`)
- Any non-GitHub clone target

## Implementation notes

Clone validation runs as a shell script (`hooks/validate-clone.sh`) so it can do fast regex extraction without spinning up a Node process. The script self-gates: it exits immediately (allowing the command) unless the command begins with `git clone` or `gh repo clone`, so the overhead on unrelated commands is negligible.

When a clone is blocked, the hook returns a corrected version with `mkdir -p` included so the target directory tree gets created automatically.

## Limitations

Org is always parsed from the clone URL; there is no default owner. The hook matches `git clone` / `gh repo clone` only at the start of a command, so a clone chained behind another command (e.g. `cd foo && git clone …`) passes through unvalidated — in that case you've already chosen an explicit location.
