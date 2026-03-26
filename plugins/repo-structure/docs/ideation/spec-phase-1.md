# Implementation Spec: repo-structure - Phase 1

**PRD**: ./prd-phase-1.md
**Estimated Effort**: S

## Technical Approach

This plugin is purely hooks-based — no commands, skills, or TypeScript runtime code needed. It uses Claude Code's PreToolUse prompt hooks, which intercept Bash tool calls matching specific patterns and inject a markdown prompt that instructs Claude how to handle the command.

We need three hook entries in `plugin.json`:

1. **git clone** — matches `git clone` in Bash commands
2. **gh repo clone** — matches `gh repo clone` in Bash commands
3. **project scaffolding** — matches `init` or `new` patterns for common scaffolding tools

Each hook points to a markdown prompt file in `./hooks/` that contains the full instructions for how Claude should validate the command and either allow it or block-and-suggest the correct path.

The key design decision is using a **single comprehensive hook prompt** for git clone and gh repo clone (since they share the same logic), and a **separate hook prompt** for scaffolding commands. This keeps the prompts focused and maintainable.

## File Changes

### New Files

| File Path                                               | Purpose                                      |
| ------------------------------------------------------- | -------------------------------------------- |
| `plugins/repo-structure/plugin.json`                    | Plugin manifest with hook definitions        |
| `plugins/repo-structure/package.json`                   | Workspace package config                     |
| `plugins/repo-structure/tsconfig.json`                  | TypeScript config (extends base)             |
| `plugins/repo-structure/src/index.ts`                   | Empty entry point (monorepo convention)      |
| `plugins/repo-structure/hooks/intercept-git-clone.md`   | Hook prompt for git clone and gh repo clone  |
| `plugins/repo-structure/hooks/intercept-scaffolding.md` | Hook prompt for project scaffolding commands |

### Modified Files

| File Path       | Changes                                                        |
| --------------- | -------------------------------------------------------------- |
| `tsconfig.json` | Add `{ "path": "plugins/repo-structure" }` to references array |

### Generated Files (via `bun run sync`)

| File Path                         | Changes                             |
| --------------------------------- | ----------------------------------- |
| `.claude-plugin/marketplace.json` | Will be auto-updated by sync script |

## Implementation Details

### plugin.json

**Pattern to follow**: `plugins/octoflow/plugin.json`

```json
{
  "name": "repo-structure",
  "version": "0.1.0",
  "description": "Enforces ~/Code/ORG/REPO directory convention for cloned repos and new projects",
  "hooks": [
    {
      "event": "PreToolUse",
      "tools": ["Bash"],
      "matcher": "git clone",
      "type": "prompt",
      "prompt": "./hooks/intercept-git-clone.md"
    },
    {
      "event": "PreToolUse",
      "tools": ["Bash"],
      "matcher": "gh repo clone",
      "type": "prompt",
      "prompt": "./hooks/intercept-git-clone.md"
    },
    {
      "event": "PreToolUse",
      "tools": ["Bash"],
      "matcher": "bun init",
      "type": "prompt",
      "prompt": "./hooks/intercept-scaffolding.md"
    },
    {
      "event": "PreToolUse",
      "tools": ["Bash"],
      "matcher": "npm init",
      "type": "prompt",
      "prompt": "./hooks/intercept-scaffolding.md"
    },
    {
      "event": "PreToolUse",
      "tools": ["Bash"],
      "matcher": "pnpm init",
      "type": "prompt",
      "prompt": "./hooks/intercept-scaffolding.md"
    },
    {
      "event": "PreToolUse",
      "tools": ["Bash"],
      "matcher": "uv init",
      "type": "prompt",
      "prompt": "./hooks/intercept-scaffolding.md"
    },
    {
      "event": "PreToolUse",
      "tools": ["Bash"],
      "matcher": "cargo init",
      "type": "prompt",
      "prompt": "./hooks/intercept-scaffolding.md"
    },
    {
      "event": "PreToolUse",
      "tools": ["Bash"],
      "matcher": "cargo new",
      "type": "prompt",
      "prompt": "./hooks/intercept-scaffolding.md"
    }
  ]
}
```

### intercept-git-clone.md

This is the core hook prompt. It must instruct Claude to:

1. Parse the GitHub URL from the command (HTTPS or SSH format)
2. Extract the org/user and repo name
3. Determine the expected path: `~/Code/ORG/REPO`
4. Check for exceptions (WorkOS SDKs, WorkOS Demo, underscore dirs)
5. If the command targets the correct path → ALLOW
6. If not → BLOCK and provide the corrected command

**Key content**:

```markdown
You are intercepting a git clone or gh repo clone command. Validate the target directory.

## Rules

The correct directory for any GitHub repository is:
~/Code/{ORG}/{REPO}

### URL Parsing

Extract ORG and REPO from:

- HTTPS: `https://github.com/{ORG}/{REPO}[.git]`
- SSH: `git@github.com:{ORG}/{REPO}[.git]`
- gh CLI: `gh repo clone {ORG}/{REPO}`

Strip any trailing `.git` from REPO.

### Expected Path

The repository MUST be cloned to: `~/Code/{ORG}/{REPO}`

If the command does not specify a target directory, or specifies one that doesn't match,
BLOCK the command and instruct to use:

mkdir -p ~/Code/{ORG} && git clone {URL} ~/Code/{ORG}/{REPO}

(or the gh equivalent)

### Exceptions — ALLOW these paths without modification

1. **WorkOS SDKs**: Paths matching `~/Code/workos/sdk/*` are allowed
2. **WorkOS Demo**: The path `~/Code/workos/demo` is allowed
3. **Underscore directories**: Paths under `~/Code/_*/` are allowed (e.g., \_learning, \_experiments)

### If path is correct

If the target directory already matches ~/Code/{ORG}/{REPO}, ALLOW the command to proceed.
```

### intercept-scaffolding.md

This hook prompt handles `bun init`, `npm init`, `uv init`, etc.

**Key content**:

```markdown
You are intercepting a project scaffolding command. Validate the target directory.

## Rules

New projects should be created under: ~/Code/{OWNER}/{PROJECT_NAME}

The default owner is: birdcar

### Validation

Check the working directory or target path of this command:

1. If it's under ~/Code/{any-owner}/{any-project}/ → ALLOW (already in correct structure)
2. If it's under ~/Code/\_\*/ → ALLOW (exception for experimental/learning dirs)
3. If it's under ~/Code/workos/sdk/\* → ALLOW (WorkOS SDK exception)
4. Otherwise → BLOCK

### When blocking

Tell Claude the project should be created under ~/Code/birdcar/{PROJECT_NAME}.

Provide the corrected commands:
mkdir -p ~/Code/birdcar/{PROJECT_NAME}
cd ~/Code/birdcar/{PROJECT_NAME}
{original scaffolding command}

If the user specified a different owner/org context, use that instead of birdcar.

### If path is correct

If the working directory already follows the convention, ALLOW the command to proceed.
```

### package.json

**Pattern to follow**: `plugins/octoflow/package.json`

```json
{
  "name": "@birdcar/claude-plugin-repo-structure",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts"
}
```

### tsconfig.json

**Pattern to follow**: other plugin tsconfig.json files

```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src"]
}
```

### src/index.ts

Empty file (monorepo convention):

```typescript
// repo-structure plugin - hooks only, no runtime exports
export {};
```

### Root tsconfig.json modification

Add to the references array:

```json
{ "path": "plugins/repo-structure" }
```

## Testing Requirements

### Manual Testing

- [ ] Run `bun run build` — should compile without errors
- [ ] Run `bun run typecheck` — should pass
- [ ] Run `bun run sync` — should add repo-structure to marketplace.json
- [ ] Run `bun run format:check` — should pass
- [ ] In a Claude Code session with the plugin loaded, test `git clone https://github.com/anthropics/claude-code` — should be intercepted and corrected to `~/Code/anthropics/claude-code`
- [ ] Test `git clone git@github.com:anthropics/claude-code.git` — same behavior
- [ ] Test `gh repo clone anthropics/claude-code` — same behavior
- [ ] Test `git clone https://github.com/anthropics/claude-code ~/Code/anthropics/claude-code` — should be allowed
- [ ] Test `bun init` from `~/Desktop` — should be blocked, suggested to use `~/Code/birdcar/`
- [ ] Test `bun init` from `~/Code/birdcar/my-project` — should be allowed
- [ ] Test clone targeting `~/Code/_learning/some-tutorial` — should be allowed
- [ ] Test clone targeting `~/Code/workos/sdk/node` — should be allowed

## Error Handling

| Error Scenario                       | Handling Strategy                                                                                              |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------------- |
| URL is not a GitHub URL              | Hook matcher won't fire (only matches `git clone` pattern, and the prompt instructs to only parse GitHub URLs) |
| Command has unusual flags before URL | Prompt instructs to find the URL argument regardless of flag position                                          |
| Multiple URLs in one command         | Prompt handles the first URL found                                                                             |

## Validation Commands

```bash
# Type checking
bun run typecheck

# Build
bun run build

# Sync marketplace
bun run sync

# Format check
bun run format:check
```

---

_This spec is ready for implementation. Follow the patterns and validate at each step._
