# plugin.json Template

Generate `plugin.json` files using this reference. Include only the fields the plugin actually uses — `name` is the only required field, all others are optional.

Verified against Claude Code v2.1.146.

## Minimal example

```json
{
  "name": "my-plugin",
  "version": "0.1.0",
  "description": "One-line plugin description",
  "author": { "name": "Your Name" }
}
```

## Maximal example

```json
{
  "name": "my-plugin",
  "displayName": "My Plugin",
  "version": "1.2.0",
  "description": "Brief plugin description",
  "author": {
    "name": "Author Name",
    "email": "author@example.com",
    "url": "https://github.com/author"
  },
  "homepage": "https://docs.example.com/plugin",
  "repository": "https://github.com/author/plugin",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"],

  "skills": "./custom/skills/",
  "commands": ["./commands/"],
  "agents": ["./agents/reviewer.md"],
  "hooks": "./hooks/hooks.json",
  "mcpServers": "./mcp-config.json",
  "outputStyles": "./styles/",
  "lspServers": "./.lsp.json",
  "experimental": {
    "themes": "./themes/",
    "monitors": "./monitors.json"
  },

  "dependencies": ["helper-lib", { "name": "secrets-vault", "version": "~2.1.0" }],
  "userConfig": {
    "api_endpoint": {
      "type": "string",
      "title": "API endpoint",
      "description": "Your team's API endpoint"
    },
    "api_token": {
      "type": "string",
      "title": "API token",
      "description": "API authentication token",
      "sensitive": true
    }
  },
  "channels": [
    {
      "server": "telegram",
      "userConfig": {
        "bot_token": {
          "type": "string",
          "title": "Bot token",
          "description": "Telegram bot token",
          "sensitive": true
        }
      }
    }
  ]
}
```

## Field reference

| Field                   | Required | Type               | Notes                                                                                              |
| ----------------------- | -------- | ------------------ | -------------------------------------------------------------------------------------------------- |
| `name`                  | Yes      | string             | kebab-case, no spaces. Used for namespacing (`plugin-name:component-name`).                        |
| `displayName`           | No       | string             | Human-readable name shown in UI. v2.1.143+.                                                        |
| `version`               | No       | string             | semver. Required for marketplace cache to detect updates.                                          |
| `description`           | No       | string             | One-line summary.                                                                                  |
| `author`                | No       | object             | `{ name, email?, url? }`. Strict-mode validation warns when missing.                               |
| `homepage`              | No       | string             | URL.                                                                                               |
| `repository`            | No       | string             | URL.                                                                                               |
| `license`               | No       | string             | SPDX identifier.                                                                                   |
| `keywords`              | No       | string[]           | Discovery hints.                                                                                   |
| `skills`                | No       | string \| string[] | Custom skill dirs. **Additive** — `./skills/` is always scanned in addition.                       |
| `commands`              | No       | string \| string[] | Custom command dirs/files. **Replaces** `./commands/` default.                                     |
| `agents`                | No       | string \| string[] | Custom agent dirs/files. **Replaces** `./agents/` default.                                         |
| `hooks`                 | No       | string \| object   | Path to `hooks.json`, or an inline hooks object. Both forms valid in v2.1.146+.                    |
| `mcpServers`            | No       | string \| object   | Path to MCP config, or inline.                                                                     |
| `outputStyles`          | No       | string \| string[] | Custom output style dirs/files. Replaces default.                                                  |
| `lspServers`            | No       | string \| object   | LSP server config.                                                                                 |
| `experimental.themes`   | No       | string \| string[] | Color theme dirs. Schema may change.                                                               |
| `experimental.monitors` | No       | string             | Path to `monitors.json` for background watches. Schema may change.                                 |
| `dependencies`          | No       | array              | Other plugins this one requires. Strings = any version; objects = `{ name, version }` with semver. |
| `userConfig`            | No       | object             | Install-time prompts. See User configuration below.                                                |
| `channels`              | No       | array              | Bind MCP servers to channels for message injection. See Channels below.                            |

## Auto-discovery rules

**Skills** are additive — the default `./skills/` directory is always scanned, even when `skills` is set. List additional dirs to extend.

**Commands**, **agents**, **outputStyles**, **experimental.themes**, and **experimental.monitors** are _replacement_: when you set the manifest field, the default folder is **not** scanned. To keep the default plus add more, include it explicitly:

```json
{ "commands": ["./commands/", "./extras/"] }
```

**Single-file plugin auto-loading (v2.1.142+):** a plugin with `SKILL.md` at the root, no `skills/` subdir, and no `skills` manifest field loads automatically as a single-skill plugin. No `plugin.json` is strictly required for this layout, though one with at least `name` is recommended.

**Hooks**, **MCP servers**, **LSP servers** have their own merge semantics — see the individual references.

When a plugin has both a default folder and a matching manifest key, `/doctor`, `claude plugin list`, and the `/plugin` detail view flag the ignored folder in v2.1.140+.

## Companion files (for marketplace plugins)

Every marketplace `plugin.json` needs these siblings:

**package.json**:

```json
{
  "name": "{package-scope}/claude-plugin-{plugin-name}",
  "version": "{same-version}",
  "private": true,
  "type": "module",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts"
}
```

**tsconfig.json**:

```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "."
  },
  "include": [],
  "files": []
}
```

**Root `tsconfig.json`** — add a project reference:

```json
{ "path": "plugins/{plugin-name}" }
```

After creating all files, run:

```bash
bun install            # may update bun.lock — CI uses --frozen-lockfile
bun run sync           # updates marketplace.json
bun run typecheck      # verify TypeScript
bun run build          # compile
bun run format:check   # CI check
```

## userConfig — install-time prompts

The `userConfig` field declares values Claude Code prompts the user for when the plugin is enabled. Use this instead of hand-edited `settings.json`.

```json
{
  "userConfig": {
    "api_endpoint": {
      "type": "string",
      "title": "API endpoint",
      "description": "Your team's API endpoint"
    },
    "api_token": {
      "type": "string",
      "title": "API token",
      "description": "API authentication token",
      "sensitive": true
    },
    "retries": {
      "type": "number",
      "title": "Max retries",
      "description": "Retry budget per request",
      "min": 0,
      "max": 10,
      "default": 3
    },
    "log_dir": {
      "type": "directory",
      "title": "Log directory",
      "description": "Where to write rotating logs",
      "required": true
    }
  }
}
```

Each option supports:

| Field         | Required | Notes                                                                            |
| ------------- | -------- | -------------------------------------------------------------------------------- |
| `type`        | Yes      | `"string"` \| `"number"` \| `"boolean"` \| `"directory"` \| `"file"`             |
| `title`       | Yes      | Label in the prompt dialog                                                       |
| `description` | Yes      | Help text                                                                        |
| `sensitive`   | No       | If `true`, masks input and stores in keychain (or `~/.claude/.credentials.json`) |
| `required`    | No       | If `true`, validation fails on empty                                             |
| `default`     | No       | Default if user provides nothing                                                 |
| `multiple`    | No       | For `string`, allow array input                                                  |
| `min` / `max` | No       | Bounds for `number`                                                              |

Values are available for substitution as `${user_config.KEY}` in:

- MCP and LSP server configs
- Hook commands and headers
- Monitor commands
- Skill and agent content (non-sensitive values only)

They are also exported to plugin subprocesses as `CLAUDE_PLUGIN_OPTION_<KEY>`.

**Storage:** non-sensitive values go to `settings.json` under `pluginConfigs[<plugin-id>].options`. Sensitive values go to the system keychain (or `~/.claude/.credentials.json` as a fallback). The keychain is shared with OAuth tokens and has a ~2 KB total limit, so keep sensitive values small.

Use `userConfig` instead of hand-rolling the `$XDG_CONFIG_HOME/{name}/credentials.env` pattern for any value the user would have to supply during install. Reserve the env-file pattern for machine-specific runtime config that varies per session.

## channels — message injection from external sources

The `channels` field declares one or more message channels that inject content into the conversation. Each channel binds to an MCP server the plugin also provides.

```json
{
  "channels": [
    {
      "server": "telegram",
      "userConfig": {
        "bot_token": {
          "type": "string",
          "title": "Bot token",
          "description": "Telegram bot token",
          "sensitive": true
        },
        "owner_id": {
          "type": "string",
          "title": "Owner ID",
          "description": "Your Telegram user ID"
        }
      }
    }
  ]
}
```

`server` must match a key in the plugin's `mcpServers`. The per-channel `userConfig` uses the same schema as the top-level field — letting the plugin prompt for tokens or IDs when enabled.

Channels require Claude Code v2.1.80+ and (during the experimental window) the `--dangerously-load-development-channels` flag. Not available on Bedrock/Vertex/Foundry deployments.

## dependencies — semver constraints

Declare other plugins this one requires:

```json
{
  "dependencies": ["helper-lib", { "name": "secrets-vault", "version": "~2.1.0" }]
}
```

- String entries = any version
- Object entries = `{ name, version }` with semver constraints (`~`, `^`, exact, ranges)

## Environment variables for substitution

Both inline in manifest values and exported to subprocesses (hooks, MCP servers, LSP servers, monitor commands):

- `${CLAUDE_PROJECT_DIR}` — project root. Wrap in quotes when used in commands: `"${CLAUDE_PROJECT_DIR}/scripts/foo.sh"`
- `${CLAUDE_PLUGIN_ROOT}` — plugin install dir. **Ephemeral** — changes on plugin update (~7-day grace period before old version cleanup). Use exec-form args to avoid quoting issues.
- `${CLAUDE_PLUGIN_DATA}` — **persistent** plugin data dir. Survives updates. Use for `node_modules`, caches, generated code, anything that should persist across versions.
- `${user_config.KEY}` — user-config values declared in `userConfig`

When a plugin updates mid-session, hooks, monitors, MCP servers, and LSP servers keep using the previous version's path. Run `/reload-plugins` to switch hooks/MCP/LSP to the new path; monitors require a session restart.

## Strict validation

Run `claude plugin validate --strict <plugin-dir>` before committing. Strict mode treats warnings (like missing `author`) as errors. Use this in CI.

## Rules for generators

- Always set `name`; everything else is optional but `description`, `version`, and `author` are strongly recommended
- For new plugins, start at `"version": "0.1.0"`. Bump per the [marketplace versioning rules](../../CLAUDE.md): patch for fixes, minor for features, major for breaking changes
- Prefer `userConfig` over hand-rolling the `$XDG_CONFIG_HOME/{name}/credentials.env` pattern for install-time values. Reserve env-file config for runtime/machine-specific values.
- For `hooks`, default to the file path form (`"hooks": "./hooks/hooks.json"`) when more than a handful of entries. Inline is fine for tiny plugins.
- For skills, prefer the additive `skills/` default — only set `skills` in the manifest when you also want extra directories.
- When generating a single-skill plugin, the auto-loading layout (`SKILL.md` at root, no `skills/`, no `skills` field) is the most compact form (v2.1.142+).
- Write any cache or state path the plugin needs to `$CLAUDE_PLUGIN_DATA`, never `$CLAUDE_PLUGIN_ROOT`.
- Run `claude plugin validate --strict` in CI; do not ship with warnings.
