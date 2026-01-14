# Architecture

## Directory Structure

```
claude-plugins/
├── .claude-plugin/           # Marketplace metadata
│   └── marketplace.json      # Lists all available plugins
├── .github/
│   └── workflows/
│       └── ci.yml            # CI workflow
├── plugins/                  # Plugin packages (Bun workspace)
│   ├── essentials/           # Core Git workflows
│   ├── creator/              # Skill generator
│   └── hello/                # Example plugin
├── scripts/
│   └── sync.ts               # Plugin discovery script
├── package.json              # Workspace root
├── tsconfig.json             # TypeScript project references
└── tsconfig.base.json        # Shared TypeScript config
```

## Plugin Structure

Each plugin follows this structure:

```
plugins/{name}/
├── package.json              # Name, version, dependencies
├── tsconfig.json             # Extends ../../tsconfig.base.json
├── plugin.json               # Claude Code metadata
├── skills/                   # Skill definitions
│   └── {skill-name}/
│       └── INSTRUCTIONS.md   # Skill prompt/instructions
└── src/                      # TypeScript source (optional)
    └── index.ts
```

## How It Works

### 1. Registration

```
/plugin marketplace add birdcar/claude-plugins
```

- Claude Code fetches `.claude-plugin/marketplace.json` from GitHub
- Registers available plugins from the `plugins` array

### 2. Installation

```
/plugin install essentials@birdcar
```

- Pulls plugin files from the `source` path in marketplace.json
- Caches plugin locally in Claude Code's plugin directory
- Makes skills available for invocation

### 3. Invocation

```
/commit
```

- Claude Code reads the skill's `INSTRUCTIONS.md`
- Follows the instructions to complete the task
- Skills are prompt-based - no runtime code execution

## Sync Script

`scripts/sync.ts` auto-discovers plugins:

1. Scans `plugins/` directory for subdirectories
2. Reads `plugin.json` from each valid plugin
3. Updates `.claude-plugin/marketplace.json` with discovered plugins

Run after adding or removing plugins:

```bash
bun run sync
```

## Build System

- **Bun workspaces**: Manages multiple packages from single root
- **TypeScript project references**: Type checking across plugins
- **tsc --build**: Compiles all plugins respecting dependencies

## CI Pipeline

On every push/PR to main:

1. Install dependencies (`bun install --frozen-lockfile`)
2. Type check (`bun run typecheck`)
3. Build (`bun run build`)
4. Verify sync is current (no uncommitted marketplace changes)
5. Check formatting (`bun run format:check`)
