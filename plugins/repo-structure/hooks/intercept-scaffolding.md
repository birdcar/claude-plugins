You are intercepting a project scaffolding command (e.g., `bun init`, `npm init`, `uv init`, `cargo init`, `cargo new`). Validate the target directory before proceeding.

## Directory Convention

New projects MUST be created under:

```
~/Code/{OWNER}/{PROJECT_NAME}
```

The **default owner** is `birdcar`. If the user has specified a different owner or org in conversation context, use that instead.

## Step 1: Determine the target directory

Check where this command will create the project:

- If the command specifies a path argument (e.g., `cargo new ~/Desktop/my-app`), that's the target
- If no path is specified, the **current working directory** is the target
- For `cargo new <name>`, the name argument becomes a subdirectory of CWD

## Step 2: Check if the target is valid

ALLOW the command if the target directory matches ANY of these patterns:

1. **Standard structure**: `~/Code/{any-owner}/{any-project}` or a subdirectory thereof
2. **Underscore directories**: `~/Code/_*/` (e.g., `~/Code/_learning/`, `~/Code/_experiments/`)
3. **WorkOS SDKs**: `~/Code/workos/sdk/*`

## Step 3: Block if invalid

If the target does NOT match the above patterns, BLOCK the command.

Provide corrected instructions:

```
mkdir -p ~/Code/birdcar/{PROJECT_NAME} && cd ~/Code/birdcar/{PROJECT_NAME} && {ORIGINAL_COMMAND}
```

Where `{PROJECT_NAME}` is inferred from:

- The directory name argument if provided
- The project name from conversation context
- The current directory name as a fallback

If the user mentioned a specific org/owner in conversation, use that instead of `birdcar`.

## Important

- BLOCK means: do NOT allow the original command. Instead, re-execute in the correct directory.
- Always use `mkdir -p` to ensure the parent directory exists.
- The `~/Code/` prefix uses the literal home directory path (`/Users/birdcar/Code/` or `$HOME/Code/`).
