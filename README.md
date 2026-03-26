# claude-plugins

A personal Claude Code plugin marketplace. These are the plugins I've built to make Claude Code fit how I actually work — git workflows, voice writing, plugin scaffolding, and enforcing conventions I care about.

The repo is a Bun workspace monorepo where each `plugins/` subdirectory is a self-contained plugin. A sync script generates the `marketplace.json` that Claude Code reads to install plugins.

## Using These Plugins

Register the marketplace, then install whatever you want:

```bash
/plugin marketplace add birdcar/claude-plugins
/plugin install octoflow@birdcar-plugins
/plugin install dev-commands@birdcar-plugins
```

To update after I've pushed changes:

```bash
/plugin marketplace update birdcar-plugins
/plugin update octoflow@birdcar-plugins
```

## Available Plugins

### octoflow `v0.3.0`

Git workflow commands: `/commit` and `/pr`.

`/commit` analyzes whether your changes should be split into multiple logical commits, proposes an ordering (infrastructure first, surface changes last), and shows you the message before doing anything. It follows the seven rules of good commits and warns if you're about to commit what looks like a secret.

`/pr` checks the current branch, compiles what's changed since main, generates a summary and test plan checklist, pushes if needed, then creates the PR via `gh pr create`. Returns the URL when done.

### dev-commands `v0.2.0`

Five language-agnostic slash commands for common development tasks: `/build`, `/test`, `/lint`, `/check`, and `/deps`. Each detects the project's tooling from lockfiles and config files — `/test` knows to run `bun test` in a Bun project, `pytest` in a Python project, or `cargo test` in a Rust project. `/check` chains all three validation steps (typecheck → lint → test) and stops on the first failure.

### skill-forge `v0.6.0`

Generate production-grade Claude Code plugins from a brain dump. `/forge-skill` takes a description — as rough or detailed as you like — and runs it through a pipeline of specialized agents (intake analyst, skill researcher, generator, validator, optimizer, scaffold writer) that turn it into a complete plugin with proper structure, optimized skill instructions, and passing type checks.

`/improve-skill` takes an existing skill or command and iteratively improves it based on feedback, showing proposed changes before applying them.

### github-actions-generator `v0.1.0`

Scaffold TypeScript GitHub Actions for Bun workspace monorepos. The `generate-action` skill handles the full lifecycle: `action.yml`, entrypoint, package.json, tsconfig, CI workflow, release workflow, Octokit patterns, error handling, and tests. It carries reference templates so the generated output follows established patterns rather than guessing.

### repo-structure `v0.1.0`

Enforces a `~/Code/ORG/REPO` directory convention for cloned repos and new projects. Implemented as a `PreToolUse` hook on Bash commands — when you run `git clone`, `gh repo clone`, or an init command (`bun init`, `cargo new`, etc.) in the wrong location, it blocks the command and gives you the corrected version.

### bat-kol `v0.8.0`

Contextual voice writer — drafts messages in your authentic voice for Slack, email, Bluesky, GitHub, and custom channels.

`/write-for <channel> [topic]` produces a draft in the right format and register for that channel. `/train-voice` walks through a guided interview, accepts writing samples, and can scrape communication history from channel APIs to build a voice profile. `/add-channel` creates custom channel definitions with their own format rules and default voice register.

Voice and channel are independent dimensions: channel handles formatting (mrkdwn for Slack, char limits for Bluesky, HTML for email), register handles tone (professional, internal, personal, social). Config cascades from project `.bat-kol/` down to global `$XDG_CONFIG_HOME/bat-kol/`, so voice profiles can vary per repo. bat-kol drafts only — no direct sending.

### github-profile `v0.1.0`

Generates a complete GitHub Profile README from your actual GitHub data. `/generate-github-profile` walks through a guided workflow: gathers your preferences (sections, style, integrations), researches your real repos and languages via the GitHub API, then generates the README, GitHub Actions workflows for dynamic content (blog feeds, contribution snake, WakaTime, Spotify), and SVG assets with dark/light mode support. Four style templates (Professional, Creative, Minimal, Playful) and a 300-line cap to keep things scannable.

### home-server `v0.2.1`

Manages a personal Coolify-based home server through four specialized agents. Describe what you want — deploy a service, fix a cert, tune Jellyfin transcoding — and it classifies the task and dispatches to the right specialist (coolify-specialist, networking-specialist, app-tuner, or retrospect). Covers the full stack: Coolify deployments, Traefik routing, Tailscale networking, Cloudflare DNS, and deployed services. The server config is specific to my setup but the architecture is reusable.

### customer-voice `v0.7.0` (DEPRECATED)

Superseded by the [ghostwriter](https://github.com/birdcar/ghostwriter) plugin, which is installed separately. customer-voice drafts customer responses in a specific voice with optional codebase and docs research, but ghostwriter handles this more generally and is actively maintained.

## Development

Prerequisites: [Bun](https://bun.sh) v1.0+

```bash
git clone https://github.com/birdcar/claude-plugins
cd claude-plugins
bun install
```

| Command                | Purpose                               |
| ---------------------- | ------------------------------------- |
| `bun run build`        | Compile TypeScript                    |
| `bun run typecheck`    | Type check without emit               |
| `bun run sync`         | Update marketplace.json from plugins/ |
| `bun run format`       | Format with Prettier                  |
| `bun run format:check` | Check formatting (CI)                 |
| `bun run clean`        | Remove build artifacts                |

CI requires type check, build, sync, and format check to all pass before merge.

## Adding a Plugin

The fastest path is `/forge-skill` if you have skill-forge installed. Otherwise manually:

1. Create `plugins/{name}/` with `package.json`, `tsconfig.json`, `plugin.json`
2. Add commands in `commands/{name}.md` or skills in `skills/{name}/SKILL.md`
3. Add a reference to the root `tsconfig.json`
4. Run `bun run sync`

Bump the version in `plugin.json` before running sync when shipping changes — without a version bump, `claude plugin update` won't detect that anything changed.

## Shipping a Plugin Change

```bash
# 1. Bump version in plugin.json, then:
bun run sync
bun install
bun run format && bun run format:check
bun run typecheck && bun run build
git add -p && git commit
git push

# 2. After CI passes, pull the local marketplace cache:
cd ~/.claude/plugins/marketplaces/birdcar-plugins && git pull
claude plugin update <plugin-name>@birdcar-plugins
```

## Local Configuration

Some plugins need machine-specific config that shouldn't be committed. These are stored in `*.local.md` files (gitignored) and plugins that need them will prompt on first use.
