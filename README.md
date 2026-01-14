# Claude Plugins

Personal Claude Code plugin marketplace.

## Installation

1. Register marketplace:

   ```
   /plugin marketplace add birdcar/claude-plugins
   ```

2. Install plugins:
   ```
   /plugin install essentials@birdcar
   /plugin install creator@birdcar
   ```

## Available Plugins

| Plugin     | Description                          | Skills                           |
| ---------- | ------------------------------------ | -------------------------------- |
| essentials | Core Git workflow skills             | /commit, /pr                     |
| creator    | Generate new skills from description | /create-skill                    |
| meta       | Self-improvement and analysis        | /analyze-plugins, /improve-skill |

## Development

### Prerequisites

- [Bun](https://bun.sh) v1.0+
- Git

### Setup

```bash
git clone https://github.com/birdcar/claude-plugins
cd claude-plugins
bun install
```

### Commands

```bash
bun run build      # Build all plugins
bun run typecheck  # Type check
bun run sync       # Update marketplace metadata
bun run format     # Format code
bun run clean      # Remove build artifacts
```

### Adding a Plugin

1. Create directory: `plugins/my-plugin/`
2. Add `plugin.json`, `package.json`, `tsconfig.json`
3. Create skills in `skills/` directory
4. Add reference to root `tsconfig.json`
5. Run `bun run sync` to register

## License

MIT
