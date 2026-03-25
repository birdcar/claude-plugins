# bat-kol — Spec

## Component Manifest

| File                                            | Purpose                                                      |
| ----------------------------------------------- | ------------------------------------------------------------ |
| `plugin.json`                                   | Plugin manifest with agents, commands, hooks                 |
| `package.json`                                  | Package metadata for Bun workspace                           |
| `tsconfig.json`                                 | TypeScript config                                            |
| `skills/bat-kol/SKILL.md`                       | Auto-trigger skill for drafting requests                     |
| `skills/bat-kol/references/voice-resolution.md` | How cascading config resolution works                        |
| `skills/bat-kol/references/channel-formats.md`  | Default format rules and constraints per channel             |
| `skills/bat-kol/references/style-frameworks.md` | Known writing style frameworks and how to apply them         |
| `skills/bat-kol/scripts/resolve-config.sh`      | Cascading config resolution script (cwd → parent → global)   |
| `commands/train-voice.md`                       | `/train-voice` — guided voice training command               |
| `commands/write-for.md`                         | `/write-for <channel> [topic]` — draft/summarize command     |
| `commands/add-channel.md`                       | `/add-channel <name>` — channel setup command                |
| `agents/voice-trainer.md`                       | Orchestrates training interview, samples, and API scraping   |
| `agents/config-resolver.md`                     | Resolves cascading config and returns active voice profile   |
| `agents/slack-drafter.md`                       | Drafts Slack messages with mrkdwn formatting                 |
| `agents/email-drafter.md`                       | Drafts emails with subject lines and HTML/plain text         |
| `agents/bluesky-drafter.md`                     | Drafts Bluesky posts with character constraints              |
| `agents/github-drafter.md`                      | Drafts PRs, issues, commit messages with GH conventions      |
| `agents/generic-drafter.md`                     | Fallback drafter for unrecognized channels                   |
| `shared/drafter-base.md`                        | Shared drafting instructions inherited by all channel agents |
| `hooks/hooks.json`                              | Plugin hooks (empty initially, future expansion)             |
| `docs/contract.md`                              | Design intent document                                       |
| `docs/spec.md`                                  | This file                                                    |
| `docs/learnings.md`                             | Retrospective observations                                   |

## Skill Architecture

**Workflow pattern**: Context-aware tool selection + iterative refinement. The skill detects the target channel from user intent, resolves the active voice profile via cascading config, selects the appropriate channel drafter agent, and enters a draft → review → refine loop until the user approves.

**Agent team structure**: A `config-resolver` agent (haiku) handles the deterministic config lookup. Channel-specific drafter agents (sonnet) handle the creative drafting work — each knows its channel's formatting rules and conventions. A `voice-trainer` agent (sonnet) handles the training flow, which is a separate entry point. All drafter agents inherit shared instructions from `shared/drafter-base.md`.

**Data flow**: User request → SKILL.md detects channel + register → spawns `config-resolver` to load voice profile → spawns channel drafter with voice profile + content prompt → drafter produces draft → SKILL.md presents via AskUserQuestion → user approves, edits, or regenerates.

**Config resolution**: The `resolve-config.sh` script walks the directory tree from cwd upward looking for `.bat-kol/`, then falls back to `$XDG_CONFIG_HOME/bat-kol/`. It outputs a JSON object with paths to the active style, register, and channel config files. The config-resolver agent reads these files and assembles the composite voice profile.

## Per-Component Details

### SKILL.md (`skills/bat-kol/SKILL.md`)

- **Purpose**: Auto-trigger skill that fires on natural language drafting requests
- **Key behaviors**:
  - Detects target channel from user message (explicit mention or inference)
  - Detects register from context or channel default
  - Spawns config-resolver to load voice profile
  - Spawns appropriate channel drafter agent with assembled voice
  - Presents draft via AskUserQuestion (clipboard / edit / regenerate)
  - If channel unclear, asks user via AskUserQuestion before drafting
- **Trigger phrases**: "draft an email", "respond in slack", "write a reply", "write a bluesky post", "draft a PR description", "write a commit message", "compose a message for", "summarize this for slack"
- **Negative cases**: Do NOT trigger for general writing tasks unrelated to communication channels (writing code, documentation, READMEs)

### resolve-config.sh (`skills/bat-kol/scripts/resolve-config.sh`)

- **Purpose**: Deterministic cascading config resolution
- **Key behaviors**:
  - Accepts optional `--channel` and `--register` flags
  - Checks `$BAT_KOL_CONFIG` env var first (explicit override)
  - Walks from cwd upward looking for `.bat-kol/` directory
  - Falls back to `${XDG_CONFIG_HOME:-$HOME/.config}/bat-kol/`
  - Outputs JSON: `{"config_root": "...", "style": "...", "register": "...", "channel": "...", "project_override": true|false}`
  - Exits non-zero with descriptive error if no config found

### config-resolver agent (`agents/config-resolver.md`)

- **Purpose**: Reads resolved config paths and assembles composite voice profile
- **Model**: haiku
- **Tools**: Read, Glob, Bash
- **Key behaviors**:
  - Runs resolve-config.sh to get paths
  - Reads style.md, register file, channel file
  - Merges layers: global style → register rules → channel format rules
  - Returns assembled voice profile as structured text

### voice-trainer agent (`agents/voice-trainer.md`)

- **Purpose**: Orchestrates the training flow for voice profiles
- **Model**: sonnet
- **Tools**: Read, Write, Edit, Glob, Bash, AskUserQuestion
- **Key behaviors**:
  - Guided interview: asks about tone, formality, sentence structure preferences per register
  - Sample analysis: reads provided writing samples and extracts patterns
  - API scraping: uses `gh` CLI for GitHub history, Slack MCP for message history, Bluesky AT Protocol for post history (when available)
  - Writes structured voice profile files to the config directory
  - Can train a single register, all registers, or add a new channel

### Channel drafter agents (`agents/{channel}-drafter.md`)

Each channel drafter follows the same structure with channel-specific adaptations:

- **Model**: sonnet
- **Tools**: Read, Glob, Bash (for clipboard via pbcopy)
- **Key behaviors**:
  - Receives assembled voice profile + content prompt from SKILL.md
  - Reads `shared/drafter-base.md` for shared drafting instructions
  - Applies channel-specific formatting (mrkdwn, HTML, char limits, etc.)
  - Produces a single draft as output text

Channel-specific details:

- **slack-drafter**: mrkdwn formatting, emoji conventions, thread vs channel awareness, link unfurling
- **email-drafter**: subject line generation, greeting/closing conventions, HTML vs plain text, CC/BCC suggestions
- **bluesky-drafter**: 300-char limit awareness, thread splitting for long content, hashtag conventions
- **github-drafter**: PR description templates, issue formatting, conventional commit messages, markdown
- **generic-drafter**: Plain text, adapts to any custom channel's format rules if present

### Commands

- **train-voice.md**: Spawns voice-trainer agent. Accepts optional `--register` or `--channel` flag. If no flags, asks via AskUserQuestion what to train.
- **write-for.md**: First arg is channel name (required). Remaining args are the topic. If no topic, summarizes current session context. Spawns config-resolver then appropriate drafter.
- **add-channel.md**: First arg is channel name. Walks user through format rules, default register, and optional API/MCP integration setup. Writes channel config file.

### shared/drafter-base.md

- **Purpose**: Shared instructions all drafter agents inherit
- **Key behaviors**:
  - Voice profile application rules (how to interpret register + style + channel layers)
  - Draft quality checklist (tone consistency, format compliance, length appropriateness)
  - Revision protocol (what to change when user asks to edit)

### References

- **voice-resolution.md**: Documents the full cascading config resolution algorithm for the SKILL.md to reference
- **channel-formats.md**: Default format constraints per built-in channel (char limits, markup syntax, conventions)
- **style-frameworks.md**: Descriptions of known writing style frameworks (Fish, Strunk & White, etc.) and how to apply them as a voice layer

## Execution Plan

### Phase 1: Foundation (no dependencies)

- `skills/bat-kol/scripts/resolve-config.sh`
- `skills/bat-kol/references/voice-resolution.md`
- `skills/bat-kol/references/channel-formats.md`
- `skills/bat-kol/references/style-frameworks.md`
- `shared/drafter-base.md`
- `docs/learnings.md`

### Phase 2: Agents (depends on Phase 1 for shared references)

Parallelizable — all agents can be generated simultaneously:

- `agents/config-resolver.md`
- `agents/voice-trainer.md`
- `agents/slack-drafter.md`
- `agents/email-drafter.md`
- `agents/bluesky-drafter.md`
- `agents/github-drafter.md`
- `agents/generic-drafter.md`

### Phase 3: Commands + Skill (depends on Phase 2 for agent references)

- `commands/train-voice.md`
- `commands/write-for.md`
- `commands/add-channel.md`
- `skills/bat-kol/SKILL.md`
- `hooks/hooks.json`

## Retrospective Configuration

- **Recommendation**: full
- **Rationale**: Voice profiles evolve over time, multi-agent coordination requires observation, training quality varies by channel/register, and the system interacts with external APIs that may change
- **Components**:
  - `agents/bat-kol-retrospective.md` — analyzes sessions, identifies voice drift or training patterns
  - `commands/retrospect.md` — user-invocable retrospective
  - `docs/learnings.md` — accumulated observations

## Validation Strategy

- Structural: frontmatter validity, naming conventions, line counts, tool restrictions per agent
- Anti-pattern scan: check against shared/anti-patterns.md
- Spec compliance: every file in manifest exists, no unexpected files
- Channel-specific: verify each drafter references drafter-base.md and channel-formats.md
- Config resolution: verify resolve-config.sh handles all cascade paths (env var, cwd, parent, global, missing)
- Build verification: `bun run typecheck && bun run build && bun run format:check`
