# claude-plugins

A personal Claude Code plugin marketplace. These are the plugins I've built to make Claude Code fit how I actually work — git workflows, customer communication, plugin scaffolding, and enforcing conventions I care about.

The repo is a Bun workspace monorepo where each `plugins/` subdirectory is a self-contained plugin. A sync script generates the `marketplace.json` that Claude Code reads to install plugins.

## Using These Plugins

Register the marketplace, then install whatever you want:

```bash
/plugin marketplace add birdcar/claude-plugins
/plugin install octoflow@birdcar
/plugin install dev-commands@birdcar
```

To update after I've pushed changes:

```bash
/plugin marketplace update birdcar-plugins
/plugin update octoflow
```

## Available Plugins

### octoflow `v0.2.0`

Git workflow commands: `/commit` and `/pr`.

`/commit` does more than just stage and write a message. It analyzes whether your changes should be split into multiple logical commits, proposes an ordering (infrastructure first, surface changes last), and shows you the message before doing anything. It follows the seven rules of good commits and warns if you're about to commit what looks like a secret.

`/pr` checks the current branch, compiles what's changed since main, generates a summary and test plan checklist, pushes if needed, then creates the PR via `gh pr create`. Returns the URL when done.

### dev-commands `v0.1.0`

Five language-agnostic slash commands for common development tasks: `/build`, `/test`, `/lint`, `/check`, and `/deps`. Each one detects the project's tooling from lockfiles and config files — so `/test` knows to run `bun test` in a Bun project, `pytest` in a Python project, or `cargo test` in a Rust project. `/check` chains all three validation steps (typecheck → lint → test) and stops on the first failure.

### skill-forge `v0.4.0`

Generate production-grade Claude Code plugins from a brain dump. `/forge-skill` takes a description — as rough or detailed as you like — and runs it through a pipeline of specialized agents (intake analyst, skill researcher, generator, validator, optimizer, scaffold writer) that turn it into a complete plugin with proper structure, optimized skill instructions, and passing type checks.

There's also `/improve-skill` which takes an existing skill or command and iteratively improves it based on feedback, showing proposed changes before applying them.

### github-actions-generator `v0.1.0`

Scaffold TypeScript GitHub Actions for Bun workspace monorepos. The `generate-action` skill handles the full lifecycle: `action.yml`, entrypoint, package.json, tsconfig, CI workflow, release workflow, Octokit patterns, error handling, and tests. It carries a set of reference templates so the generated output follows established patterns rather than guessing.

### repo-structure `v0.1.0`

Enforces a `~/Code/ORG/REPO` directory convention for cloned repos and new projects. Implemented as a `PreToolUse` hook on Bash commands — when you run `git clone`, `gh repo clone`, or an init command (`bun init`, `cargo new`, etc.) in the wrong location, it blocks the command and gives you the corrected version.

### customer-voice `v0.7.0`

Drafts customer responses in a specific voice. Takes an incoming customer message, optionally researches the relevant codebase and documentation, and produces a reply draft. This one is fairly personal — the voice and context are tuned for a specific person's communication style — but the structure is reusable if you want to adapt it.

### github-profile `v0.1.0`

Generates a complete GitHub Profile README from your actual GitHub data. `/generate-github-profile` walks through a guided workflow: gathers your preferences (sections, style, integrations), researches your real repos and languages via the GitHub API, then generates the README, GitHub Actions workflows for dynamic content (blog feeds, contribution snake, WakaTime, Spotify), and SVG assets with dark/light mode support. Four style templates (Professional, Creative, Minimal, Playful) and a 300-line cap to keep things scannable.

### home-server `v0.2.1`

Manages a personal Coolify-based home server through four specialized agents. Describe what you want — deploy a service, fix a cert, tune Jellyfin transcoding — and it classifies the task and dispatches to the right specialist (coolify-specialist, networking-specialist, app-tuner, or retrospect). Covers the full stack: Coolify deployments, Traefik routing, Tailscale networking, Cloudflare DNS, and 14 deployed services. The server config is specific but the architecture is reusable.

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

The fastest path is `/forge-skill` if you have the skill-forge plugin installed. Otherwise manually:

1. Create `plugins/{name}/` with `package.json`, `tsconfig.json`, `plugin.json`
2. Add commands in `commands/{name}.md` or skills in `skills/{name}/SKILL.md`
3. Add a reference to the root `tsconfig.json`
4. Run `bun run sync`

After pushing changes, bump the version in `plugin.json` before running sync — without a version bump, `claude plugin update` won't detect that anything changed.

## Local Configuration

Some plugins need machine-specific config that shouldn't be committed. These are stored in `*.local.md` files (gitignored) and plugins that need them will prompt on first use.

| Plugin         | Config File     | Values                 |
| -------------- | --------------- | ---------------------- |
| customer-voice | config.local.md | `workos_monorepo_path` |

## License

MIT
