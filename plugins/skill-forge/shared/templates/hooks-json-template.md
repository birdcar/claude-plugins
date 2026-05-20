# hooks-json Template

Generate `hooks/hooks.json` (or inline `hooks` in `plugin.json`) using this reference. Only create hooks when the skill workflow requires lifecycle interception.

Verified against Claude Code v2.1.146.

## Placement: inline vs file

Both forms are supported. Pick based on size and reuse:

| Form                                                                        | When to use                                                        |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| `hooks/hooks.json` file with `"hooks": "./hooks/hooks.json"` in plugin.json | Default. Easier to read once hooks grow past a handful of entries. |
| Inline `hooks: {...}` object in plugin.json                                 | Compact alternative for 1-2 small hooks. Valid in v2.1.146+.       |

> **Historical note:** Earlier Claude Code versions rejected inline hooks with "Invalid input". Re-tested on v2.1.146 and inline now passes `claude plugin validate --strict`. The dedicated `hooks/hooks.json` form remains the more readable default.

When the `hooks` field is a string path, the referenced file MUST wrap events in a top-level `"hooks"` key:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "echo init" }]
      }
    ]
  }
}
```

## Top-level structure

```json
{
  "disableAllHooks": false,
  "hooks": {
    "{EventName}": [
      {
        "matcher": "{ToolNamePattern}",
        "hooks": [
          { "type": "command|prompt|http|mcp_tool|agent", ...handler-fields }
        ]
      }
    ]
  }
}
```

`matcher` (and `if` on individual hooks) are optional. When omitted, the entry matches all invocations of the event.

## Hook events

The full event surface in v2.1.146:

| Event                 | When it fires                                                    | Decision controls                                  |
| --------------------- | ---------------------------------------------------------------- | -------------------------------------------------- |
| `SessionStart`        | Session begin (matcher: `startup`, `resume`, `clear`, `compact`) | `additionalContext`, `$CLAUDE_ENV_FILE`            |
| `Setup`               | First-time plugin setup                                          | `$CLAUDE_ENV_FILE`                                 |
| `UserPromptSubmit`    | User pressed Enter                                               | `decision: "block"` to reject the prompt           |
| `UserPromptExpansion` | After `!`/`@` substitution, before send                          | `decision: "block"`                                |
| `PreToolUse`          | Before any tool runs                                             | `permissionDecision`, `updatedInput`               |
| `PermissionRequest`   | Tool needs permission                                            | `decision.behavior` is `"allow"` or `"deny"`       |
| `PermissionDenied`    | Permission was denied                                            | `retry: true`                                      |
| `PostToolUse`         | After a tool succeeds                                            | `decision: "block"`                                |
| `PostToolUseFailure`  | After a tool errors                                              | `decision: "block"`                                |
| `PostToolBatch`       | After a batch of parallel tool calls                             | `decision: "block"`                                |
| `Notification`        | Claude needs attention (`waiting_for_input`, `idle`, etc.)       | none                                               |
| `SubagentStart`       | A subagent (Agent tool, agent-team teammate) begins              | none — context only                                |
| `SubagentStop`        | A subagent completes                                             | `decision: "block"`                                |
| `TaskCreated`         | TaskCreate fired                                                 | `decision: "block"`                                |
| `TaskCompleted`       | A task moved to completed                                        | none                                               |
| `Stop`                | Claude is about to stop responding                               | `decision: "block"` (force continue)               |
| `StopFailure`         | Stop hook itself failed                                          | none                                               |
| `TeammateIdle`        | Agent-team teammate hit idle                                     | none                                               |
| `InstructionsLoaded`  | CLAUDE.md / rules loaded                                         | none                                               |
| `ConfigChange`        | Settings changed mid-session                                     | `decision: "block"`                                |
| `CwdChanged`          | Working directory changed                                        | `$CLAUDE_ENV_FILE`                                 |
| `FileChanged`         | A watched file (literal name in matcher) changed on disk         | none — context only                                |
| `WorktreeCreate`      | Before EnterWorktree creates                                     | `worktreePath`, non-zero exit aborts               |
| `WorktreeRemove`      | Before ExitWorktree removes                                      | none                                               |
| `PreCompact`          | Before context compaction                                        | `decision: "block"`                                |
| `PostCompact`         | After context compaction                                         | none                                               |
| `Elicitation`         | MCP elicitation request                                          | `action` is `"accept"`, `"decline"`, or `"cancel"` |
| `ElicitationResult`   | After user responded to elicitation                              | none                                               |
| `SessionEnd`          | Session is ending                                                | none                                               |

## Matcher rules

`matcher` matches **tool names** (not command content):

- `""`, `"*"`, or omitted — match all invocations of the event
- `"Bash"` — exact tool name
- `"Edit\|Write"` — OR-list (allowed characters: letters, digits, `_`, `\|`). Example renders as `"Edit|Write"`.
- `"^Notebook"` — JavaScript regex (triggered by any non-list character)
- `"mcp__memory__.*"` — regex matching MCP tool names

For `FileChanged`, the matcher is a literal filename OR-list: `".env|.envrc"`.

To filter Bash by **command content**, use the `if` field on the inner hook (see below).

## The `if` field — cheap filtering

Available on individual hook handlers for tool events (`PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied`). Uses permission-rule syntax:

```json
{ "if": "Bash(git commit *)" }
{ "if": "Bash(rm -rf *)" }
{ "if": "Edit(*.ts)" }
{ "if": "Write(**/.env)" }
```

The hook process only spawns when the rule matches. This is **much cheaper** than a command hook that reads stdin then exits early. Prefer `if` over runtime filtering wherever possible.

## Handler types — 5 variants

### 1. `command` — shell handler

Receives the event JSON on stdin, returns optional JSON on stdout. Exit 0 = success, 2 = blocking error.

**Shell form** (everything in one string, shell-interpreted):

```json
{
  "type": "command",
  "command": "bash \"${CLAUDE_PLUGIN_ROOT}\"/scripts/validate.sh"
}
```

**Exec form** (preferred when args contain spaces or path placeholders):

```json
{
  "type": "command",
  "command": "node",
  "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/format.js", "--fix"]
}
```

**Async variants:**

```json
{ "type": "command", "command": "...", "async": true }
{ "type": "command", "command": "...", "asyncRewake": true }
```

`asyncRewake: true` implies `async: true`. The hook runs in the background; if it exits 2, Claude is woken with the hook's stderr/stdout as a system reminder. Use for long-running validators that need to interrupt mid-conversation.

**Shell selection:**

```json
{ "type": "command", "command": "...", "shell": "powershell" }
```

### 2. `prompt` — LLM evaluation

A one-shot Claude call. The model receives the event JSON in context and outputs a hook response. Use for soft policy checks too nuanced for shell logic.

```json
{
  "type": "prompt",
  "prompt": "Is this Bash command safe given $ARGUMENTS? Block if it modifies user data without confirmation.",
  "model": "claude-haiku-4-5-20251001",
  "timeout": 30
}
```

Default to `claude-haiku-4-5` for prompt hooks — they fire on every matched event and a slower model multiplies latency. Reserve Sonnet for hooks that genuinely need reasoning.

### 3. `http` — webhook handler

POSTs the event JSON to a URL and reads a JSON response back.

```json
{
  "type": "http",
  "url": "http://localhost:8080/hooks/pre-tool-use",
  "timeout": 30,
  "headers": {
    "Authorization": "Bearer $MY_TOKEN",
    "Content-Type": "application/json"
  },
  "allowedEnvVars": ["MY_TOKEN"]
}
```

`allowedEnvVars` lists which env vars the hook's URL/headers may interpolate. Use for security-policy services running outside Claude Code.

### 4. `mcp_tool` — MCP tool handler

Calls an MCP tool with a templated input payload:

```json
{
  "type": "mcp_tool",
  "server": "my_server",
  "tool": "security_scan",
  "input": {
    "file_path": "${tool_input.file_path}",
    "config_id": "${user_config.scan_profile}"
  },
  "timeout": 600
}
```

Supports `${tool_input.*}`, `${user_config.*}`, and `${CLAUDE_PLUGIN_DATA}` interpolation in `input` values. Use to push verification through your existing MCP infrastructure.

### 5. `agent` — verification subagent

Spawns a full subagent to investigate before letting the tool proceed:

```json
{
  "type": "agent",
  "prompt": "Verify the following action: $ARGUMENTS. Return a JSON object with {decision: 'block'|'allow', reason: '...'}.",
  "timeout": 60
}
```

Heaviest of the five — use sparingly, only when shell + prompt aren't expressive enough.

### Common fields on all handler types

| Field           | Type             | Effect                                                                 |
| --------------- | ---------------- | ---------------------------------------------------------------------- | ------ | ---- | -------- | ------ |
| `type`          | string, required | `command                                                               | prompt | http | mcp_tool | agent` |
| `if`            | string           | Permission-rule filter (see above). Only on tool events.               |
| `timeout`       | integer (sec)    | Default 600                                                            |
| `statusMessage` | string           | Shown in the status line while the hook runs                           |
| `once`          | boolean          | If `true`, runs once per session then unregisters. Skills/agents only. |

## Universal output schema

When a hook returns JSON on stdout (exit 0), the JSON is interpreted with these fields:

```json
{
  "continue": true,
  "stopReason": "Optional message when continue is false",
  "suppressOutput": false,
  "systemMessage": "Shown to user as warning",
  "terminalSequence": "]777;notify;Title;Message",
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "additionalContext": "Injected into Claude's context",
    "permissionDecision": "allow|deny|ask|defer",
    "permissionDecisionReason": "Why",
    "updatedInput": { "command": "sanitized command" }
  }
}
```

Top-level `decision: "block"` works on `UserPromptSubmit`, `UserPromptExpansion`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `Stop`, `SubagentStop`, `ConfigChange`, `PreCompact`, `TaskCreated`. Pair with `reason` to explain.

`terminalSequence` emits an OSC notification to the user's terminal without writing to `/dev/tty` directly. Useful for SessionStart welcome notifications, Stop completion pings, etc.

## Exit codes

| Code  | Behavior                                                                |
| ----- | ----------------------------------------------------------------------- |
| `0`   | Success. JSON on stdout (if any) is processed.                          |
| `1`   | Non-blocking error (most events). Tool / action still proceeds.         |
| `2`   | Blocking error. stderr is shown to the user. Tool / action is rejected. |
| other | Same as exit 1.                                                         |

`WorktreeCreate` is special: any non-zero exit aborts creation.

## Environment variables available to hook processes

| Variable              | Lifetime / scope                                                                                                                       |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | -------- | ------ | ------- | ------------------------------------------------------------------ |
| `$CLAUDE_PROJECT_DIR` | Project root.                                                                                                                          |
| `$CLAUDE_PLUGIN_ROOT` | Plugin install dir. **Ephemeral** — changes on update (~7-day grace period).                                                           |
| `$CLAUDE_PLUGIN_DATA` | **Persistent** plugin data dir. Survives updates. Use for caches, state.                                                               |
| `$CLAUDE_CODE_REMOTE` | `"true"` on Claude Code on the Web, unset in CLI.                                                                                      |
| `$CLAUDE_ENV_FILE`    | Available to `SessionStart`, `Setup`, `CwdChanged`, `FileChanged`. Append `export FOO=bar` lines to persist env vars into the session. |
| `$CLAUDE_EFFORT`      | `"low"                                                                                                                                 | "medium" | "high" | "xhigh" | "max"`. Available to Bash commands run after `SessionStart` hooks. |

When writing scripts that read tool input, source them from `$CLAUDE_PLUGIN_ROOT/scripts/` and write any state to `$CLAUDE_PLUGIN_DATA`, never `$CLAUDE_PLUGIN_ROOT` (which can be deleted on update).

## Common patterns

### Intercept `git commit` and route through `/commit`

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "prompt",
            "if": "Bash(git commit *)",
            "prompt": "The user requires conventional commits via the /commit skill.\n\nBLOCK this command. Tell the user to use /commit instead of raw git commit. The ONLY exception: if the message already follows conventional commits (feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(scope)?: description — then ALLOW it."
          }
        ]
      }
    ]
  }
}
```

### Persist env vars at SessionStart

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "once": true,
            "command": "bash \"${CLAUDE_PLUGIN_ROOT}\"/scripts/load-env.sh"
          }
        ]
      }
    ]
  }
}
```

`load-env.sh` writes `export FOO=bar` to `$CLAUDE_ENV_FILE`.

### MCP-driven security scan on file writes

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "mcp_tool",
            "server": "security",
            "tool": "scan_path",
            "input": { "path": "${tool_input.file_path}" }
          }
        ]
      }
    ]
  }
}
```

### Background validator that interrupts Claude

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "asyncRewake": true,
            "command": "bash \"${CLAUDE_PLUGIN_ROOT}\"/scripts/typecheck.sh"
          }
        ]
      }
    ]
  }
}
```

## Rules for generators

- Prefer `if` over runtime filtering — it short-circuits before spawning the hook process
- Default to `command` for deterministic checks, `prompt` (haiku) for nuanced policy, `mcp_tool` for delegation, `agent` only when reasoning is required
- Match by tool name in the outer `matcher`; filter by command content in the inner `if`
- Use `$CLAUDE_PLUGIN_DATA` for any state that should outlive a plugin update; treat `$CLAUDE_PLUGIN_ROOT` as ephemeral
- `once: true` is for SessionStart-style init work; ignored outside skills/agents context
- A crashing `command` hook with exit 2 blocks the tool — handle errors explicitly inside the script
- Keep `prompt` hooks small — they consume tokens on every matched call
- Test hooks against `claude plugin validate --strict` before shipping
