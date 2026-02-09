You are intercepting a `git clone` or `gh repo clone` command. Validate the target directory before proceeding.

## Directory Convention

All GitHub repositories MUST be cloned to:

```
~/Code/{ORG}/{REPO}
```

Where `{ORG}` is the GitHub organization or user, and `{REPO}` is the repository name.

## Step 1: Parse the URL

Extract `{ORG}` and `{REPO}` from the command:

- **HTTPS**: `https://github.com/{ORG}/{REPO}` or `https://github.com/{ORG}/{REPO}.git`
- **SSH**: `git@github.com:{ORG}/{REPO}` or `git@github.com:{ORG}/{REPO}.git`
- **gh CLI**: `gh repo clone {ORG}/{REPO}`

Strip any trailing `.git` suffix from `{REPO}`.

If the URL is not a GitHub URL, ALLOW the command — this convention only applies to GitHub.

## Step 2: Determine target directory

Check if the command specifies a target directory:

- `git clone <url> <target>` — target is the last argument after the URL
- `git clone <url>` with no target — git defaults to CWD, which is likely wrong
- `gh repo clone ORG/REPO <target>` — target after the org/repo
- `gh repo clone ORG/REPO` — defaults to CWD

The **correct** target is: `~/Code/{ORG}/{REPO}`

## Step 3: Check exceptions

ALLOW the command without modification if the target path matches ANY of these:

1. **WorkOS SDKs**: `~/Code/workos/sdk/*` (e.g., `~/Code/workos/sdk/node`)
2. **WorkOS Demo**: `~/Code/workos/demo`
3. **Underscore directories**: `~/Code/_*/` (e.g., `~/Code/_learning/some-tutorial`, `~/Code/_experiments/foo`)

## Step 4: Validate or block

**If target matches `~/Code/{ORG}/{REPO}`** → ALLOW the command to proceed unchanged.

**If target is wrong or unspecified** → BLOCK the command and provide the corrected version:

For `git clone`:

```
mkdir -p ~/Code/{ORG} && git clone {ORIGINAL_URL} ~/Code/{ORG}/{REPO}
```

For `gh repo clone`:

```
mkdir -p ~/Code/{ORG} && gh repo clone {ORG}/{REPO} ~/Code/{ORG}/{REPO}
```

Preserve any flags from the original command (e.g., `--depth 1`, `--branch main`).

## Important

- BLOCK means: do NOT allow the original command. Instead, re-execute with the corrected path.
- Always use `mkdir -p` to ensure the parent directory exists.
- The `~/Code/` prefix uses the literal home directory path (`/Users/birdcar/Code/` or `$HOME/Code/`).
