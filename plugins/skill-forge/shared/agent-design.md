## Agent File Structure

Agents are `.md` files in the plugin's `agents/` directory (auto-discovered) or referenced explicitly from `plugin.json`'s `"agents"` array.

```yaml
---
name: agent-name
description: >-
  One-line description of what this agent does and when to spawn it.
  Use when [specific condition].
tools:
  - Read
  - Glob
  - Grep
model: sonnet
effort: medium
maxTurns: 20
---
# Agent Name

System prompt body that defines the agent's role, constraints, and output format.
```

### Full frontmatter field reference

| Field             | Type          | Notes                                                                       |
| ----------------- | ------------- | --------------------------------------------------------------------------- | ------ | ------------------------------------ | ---- | ------------------------------------------------------------- |
| `name`            | string        | kebab-case, matches file name without .md                                   |
| `description`     | string        | Trigger-phrase rules same as skills; used for `subagent_type` matching      |
| `tools`           | YAML sequence | Tools the agent may use. Prefer over `disallowedTools` for least-privilege. |
| `disallowedTools` | YAML sequence | Subtractive — denies specific tools while inheriting others. Use sparingly. |
| `model`           | `opus         | sonnet                                                                      | haiku` | Right-sized for the task (see below) |
| `effort`          | `low          | medium                                                                      | high   | xhigh                                | max` | Compute budget. Opus 4.7/4.6 and Sonnet 4.6 support all five. |
| `maxTurns`        | integer       | Hard cap on agent turn count. Prevents runaway loops.                       |
| `skills`          | YAML sequence | Skills the agent has access to. Defaults to all.                            |
| `memory`          | string        | Path to an agent-scoped memory file.                                        |
| `background`      | boolean       | If `true`, agent runs in the background by default when spawned.            |
| `isolation`       | `worktree`    | Run agent in a git worktree (auto-cleanup if no changes).                   |

**Disallowed in plugin agents:** `hooks`, `mcpServers`, `permissionMode` — those live at the plugin manifest level, not on individual agents.

## Model Right-Sizing

Current model IDs (verified v2.1.146):

| Model    | Latest ID                   | Use for                                                                     | Token cost | Speed   |
| -------- | --------------------------- | --------------------------------------------------------------------------- | ---------- | ------- |
| `opus`   | `claude-opus-4-7`           | Complex reasoning, generation, multi-step analysis, skill content authoring | Highest    | Slowest |
| `sonnet` | `claude-sonnet-4-6`         | Research, analysis, code review, standard agent tasks, most subagents       | Medium     | Medium  |
| `haiku`  | `claude-haiku-4-5-20251001` | Validation, formatting, file writing, simple transformations, scaffolding   | Lowest     | Fastest |

Rules:

- Default to `sonnet` unless there's a specific reason for opus or haiku
- Use `opus` only for tasks requiring deep reasoning or creative generation
- Use `haiku` for mechanical tasks: writing boilerplate, running checklists, formatting output
- Never use `opus` for read-only research — sonnet is sufficient
- Consider haiku first for any task that doesn't require reasoning about trade-offs

## Tool Grants — Principle of Least Privilege

Only grant tools the agent actually needs:

| Agent role           | Typical tools                                              |
| -------------------- | ---------------------------------------------------------- |
| Read-only researcher | Read, Glob, Grep                                           |
| Codebase explorer    | Read, Glob, Grep, Bash (for git commands)                  |
| File generator       | Read, Write, Edit, Glob                                    |
| Full-stack builder   | Read, Write, Edit, Glob, Grep, Bash                        |
| Web researcher       | Read, WebFetch, WebSearch                                  |
| Interactive agent    | Read, Write, Edit, AskUserQuestion, TaskCreate, TaskUpdate |

Never grant:

- `Write`/`Edit` to read-only agents
- `Bash` to agents that don't need shell access
- `WebFetch`/`WebSearch` to agents working on local code only
- All tools "just in case" — overly broad grants lead to unexpected behavior

## Spawning Agents

From skills/commands, spawn agents using the `Agent` tool:

```
Agent tool with:
  subagent_type: "plugin-name:agent-name"
  description: "Short task description"
  prompt: "Detailed task instructions"
  model: "sonnet"  (optional override)
  run_in_background: true  (for parallel work)
```

From the Agent tool directly:

```
Agent tool with:
  subagent_type: "general-purpose" | "Explore" | "Plan" | etc.
  description: "Short task description"
  prompt: "Detailed task instructions"
```

Key patterns:

- Use `run_in_background: true` for agents that can work in parallel
- Use `isolation: "worktree"` when agents modify files and need git isolation
- Agent results are returned to the caller — summarize for the user since they can't see raw agent output
- Agents can be resumed with their `agentId` for follow-up work

## Agent Teams

When 2+ independent tasks can run in parallel, use agent teams:

1. Enable: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings
2. Enter delegate mode (Shift+Tab) — restricts lead to coordination-only tools
3. Lead spawns teammates automatically, each getting their own context window
4. Teammates load project context (CLAUDE.md, MCP servers, skills) independently

When to use teams:

- 2+ specs to implement with no shared file dependencies
- Research tasks that can run independently
- Testing different approaches in parallel

When NOT to use teams:

- Tasks that modify the same files
- Sequential dependencies (A must finish before B starts)
- Simple tasks that don't benefit from parallelization overhead

## context:fork

The `context` field in skill frontmatter:

```yaml
---
name: analyze-codebase
context: fork
agent: Explore
---
Analyze the codebase structure and report findings.
```

This runs the skill body as a task in an isolated subagent. The skill content becomes the task prompt.

Caveats:

- Only use for skills with explicit task instructions — if the skill is reference-only (guidelines, patterns), the subagent has no task to perform and returns nothing useful
- The `agent` field picks the subagent type (Explore for read-only, Plan for architecture, general-purpose for everything else)
- Subagent has its own context window — large reference files don't compete with the main conversation

## System Prompt Best Practices

Structure the agent's body (system prompt) with:

1. **Role definition** — one sentence: "You are a {role} that {does what}"
2. **Input specification** — what the agent receives: "Input: {description of expected input}"
3. **Process steps** — numbered steps the agent follows
4. **Output format** — exact structure of the response
5. **Constraints** — what the agent must NOT do

Keep agent prompts under 200 lines. If longer, the agent's own context gets crowded before it starts working.

Avoid:

- Vague role definitions ("You are helpful")
- Open-ended output ("Return whatever seems relevant")
- No constraints (every agent should have at least "never modify files you weren't asked to modify")
