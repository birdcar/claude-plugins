# hooks.json Template

Generate `hooks/hooks.json` files using this structure. Only create hooks when the skill workflow requires tool interception.

## Structure

```json
{
  "hooks": {
    "{EventType}": [
      {
        "matcher": "{ToolNamePattern}",
        "hooks": [
          {
            "type": "{prompt|command}",
            ...hook-specific-fields
          }
        ]
      }
    ]
  }
}
```

## Event Types

| Event         | When it fires                  | Common use                           |
| ------------- | ------------------------------ | ------------------------------------ |
| `PreToolUse`  | Before a tool executes         | Validate, intercept, redirect        |
| `PostToolUse` | After a tool executes          | Log, transform output, chain actions |
| `Stop`        | Before Claude stops responding | Final checks, cleanup                |

## Hook Types

### Prompt Hook

Injects a message into Claude's context:

```json
{
  "type": "prompt",
  "prompt": "Check if this operation follows our conventions before proceeding."
}
```

### Command Hook

Runs a shell command. Receives tool input as JSON on stdin. Must return JSON on stdout.

```json
{
  "type": "command",
  "command": "bash hooks/validate.sh"
}
```

**Command hook responses:**

Allow (proceed normally):

```json
{}
```

Block (prevent tool execution):

```json
{
  "decision": "block",
  "reason": "Human-readable explanation of why this was blocked"
}
```

Modify (change the tool input):

```json
{
  "decision": "modify",
  "tool_input": { "modified": "input" }
}
```

## Matcher Patterns

The `matcher` field matches **tool names**, not command content:

| Pattern               | Matches              |
| --------------------- | -------------------- |
| `"Bash"`              | All Bash tool calls  |
| `"Write"`             | All Write tool calls |
| `"Write\|Edit"`       | Write OR Edit calls  |
| `"Bash\|Write\|Edit"` | Any of the three     |

For filtering on command content within Bash, use a command hook that reads stdin JSON and inspects `tool_input.command`.

## Examples

### Intercept git commits

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash hooks/check-commit.sh"
          }
        ]
      }
    ]
  }
}
```

### Validate file writes

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Before writing, verify the file path follows project conventions and the content matches the expected format."
          }
        ]
      }
    ]
  }
}
```

## Rules

- Hooks MUST go in `hooks/hooks.json` — never inline in plugin.json
- The `hooks` field in plugin.json is not supported and causes validation errors
- Command hooks must handle their own errors — a crashing script blocks the tool
- Keep prompt hooks concise — they consume context on every matched tool call
- Test hooks locally before committing — a bad hook can make Claude unusable
