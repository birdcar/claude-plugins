# Tool Primitives Reference

## AskUserQuestion

The ONLY way to ask users questions in skills. Never use plain text questions.

**When to use**: Every decision point, clarification, approval gate, or choice.

**Effective patterns**:

- Provide 2-4 options (required: minItems 2, maxItems 4)
- Use `multiSelect: true` when choices aren't mutually exclusive
- Keep headers to ≤12 characters
- Add descriptions explaining implications of each choice
- Use `preview` field for comparing code snippets, ASCII mockups, or config examples
- "(Recommended)" suffix on the best option — make it the first in the list

**Anti-patterns**:

- Asking questions in plain text output (user can't respond structurally)
- Too many options (max 4, plus automatic "Other" option)
- Vague option labels ("Option A", "Option B")
- Missing descriptions (user can't make informed choice)
- Using it for simple acknowledgments — only for real decisions

---

## TaskCreate / TaskGet / TaskList / TaskUpdate / TaskStop

For tracking multi-step progress within a session. **`TodoWrite` is deprecated** — disabled by default in Claude Code v2.1.142+ and replaced by this `Task*` family.

**When to use**:

- Complex workflows with 5+ steps where losing track is likely
- Checklists that need visible progress tracking
- Before context compaction might erase progress state
- Coordinating work across subagents (tasks can be claimed via `owner` field)

**API surface**:

| Tool         | Purpose                                                          |
| ------------ | ---------------------------------------------------------------- |
| `TaskCreate` | Add a task with `subject`, `description`, optional `activeForm`  |
| `TaskGet`    | Read full details (description + comments) for a single task     |
| `TaskList`   | Summary of all tasks: id, subject, status, owner, blockedBy      |
| `TaskUpdate` | Change status, owner, dependencies (`addBlocks`, `addBlockedBy`) |
| `TaskStop`   | Stop a running task                                              |

Status flow: `pending` → `in_progress` → `completed` (or `deleted`).

**Effective patterns**:

- Create tasks at the START of a multi-step workflow, not mid-way
- Set `status: "in_progress"` when starting, `"completed"` only when fully done
- Use clear, specific subjects in imperative form ("Run database migration")
- Use `addBlockedBy` to encode sequential dependencies
- Set `owner` to claim a task when working as a teammate; check `TaskList` for available work

**Anti-patterns**:

- Creating tasks for 2-3 step workflows (overkill)
- Marking `completed` while errors are unresolved or tests are failing
- Using tasks as a communication channel (they're internal state, not chat)
- Calling `TodoWrite` — it's not loaded by default; fall back to `Task*`

> **For skill generators:** Always emit `Task*` references in generated skills. Older skills that still reference `TodoWrite` will silently fail to track progress on v2.1.142+ unless the user has explicitly re-enabled the legacy tool.

---

## Agent Tool

For spawning subagents to handle parallel or specialized work.

**When to use**:

- 2+ independent tasks that can run in parallel
- Tasks requiring a different model than the current context
- Heavy research that would bloat the main context
- Specialized work matching a defined agent type

**Parameters**:

```
subagent_type: "plugin-name:agent-name" | "Explore" | "Plan" | "general-purpose"
description: "3-5 word summary"
prompt: "Detailed task instructions with all needed context"
model: "opus" | "sonnet" | "haiku" (optional override)
run_in_background: true | false
isolation: "worktree" (for git-safe file modifications)
```

**Effective patterns**:

- Include ALL needed context in the prompt — agents don't share the parent's conversation
- Use `run_in_background: true` for parallel agents, wait for results before proceeding
- Use `isolation: "worktree"` when the agent modifies files in a git repo
- Summarize agent results for the user — they can't see raw agent output
- Use `resume` with `agentId` for follow-up work on the same task

**Model selection**:

| Task                                              | Model  |
| ------------------------------------------------- | ------ |
| Most agents                                       | sonnet |
| Validation, formatting, scaffolding               | haiku  |
| Complex multi-step reasoning, creative generation | opus   |

**Anti-patterns**:

- Spawning an agent for a task you could do with a single Read/Grep
- Forgetting to include context in the prompt (agent starts blind)
- Using opus for simple research (wasteful)
- Spawning sequential agents when tasks have dependencies (use one agent or do inline)

---

## Read / Write / Edit

**Read**: Inspect file contents. Supports images, PDFs (with `pages` parameter), notebooks.

- Specify `offset`/`limit` for large files
- Read multiple files in parallel when independent

**Write**: Create new files or complete rewrites.

- MUST Read the file first if it exists (tool enforces this)
- Use for NEW files only — prefer Edit for modifications

**Edit**: Surgical modifications to existing files.

- Requires `old_string` to be unique in the file
- If not unique, provide more surrounding context
- Use `replace_all: true` for find-and-replace operations
- Prefer over Write for any existing file modification

**Anti-patterns**:

- Using Write to modify existing files (loses ability to review diff)
- Using `Bash(cat/sed/awk)` instead of Read/Edit
- Reading files you don't need (wastes context)

---

## Glob / Grep

**Glob**: Find files by name pattern.

```
pattern: "**/*.ts"          # all TypeScript files
pattern: "src/**/*.test.*"  # test files in src
path: "/specific/dir"       # scope the search
```

**Grep**: Search file contents.

```
pattern: "function\\s+\\w+"          # regex pattern
output_mode: "content" | "files_with_matches" | "count"
glob: "*.ts"                          # filter to specific file types
type: "ts"                            # shorthand for file type
```

**Effective patterns**:

- Use Glob to find files, then Read to inspect them
- Use Grep with `output_mode: "files_with_matches"` for discovery, then `"content"` for details
- Combine `glob` filter with `pattern` for precise searches
- Run multiple Glob/Grep in parallel when searching for different things

**Anti-patterns**:

- Using `Bash(find)` or `Bash(grep)` instead of Glob/Grep
- Reading entire directories instead of using Glob to find specific files
- Not using `type` filter when file type is known

---

## WebFetch / WebSearch

**WebFetch**: Fetch a specific URL's content.
**WebSearch**: Search the web for information.

**When to use**:

- Researching external APIs or documentation
- Checking current library versions
- Finding best practices or examples not already known

**Effective patterns**:

- Delegate to a research agent (sonnet) rather than doing inline — keeps main context clean
- Use WebFetch for known URLs, WebSearch for discovery
- Cache stable results in the skill's `references/` directory

**Anti-patterns**:

- Fetching URLs when local docs exist
- Searching the web for things Claude already knows
- Inline research that bloats the main conversation context

---

## Scripts

Scripts are the right primitive for deterministic, repeatable operations that would be unreliable or wasteful to perform with LLM reasoning. Place them in the skill's `scripts/` directory.

**When to use scripts instead of inline instructions**:

- **Deterministic transformations**: parsing, formatting, data extraction where the logic is fixed
- **Validation checks**: linting, schema validation, structural checks with known rules
- **Multi-step shell operations**: sequences of commands that must run in exact order
- **Operations with external tools**: calling `jq`, `yq`, `python`, or other CLI tools
- **Repeatable commands**: anything you'd run the same way every time (sync scripts, build verification, file generation from templates)
- **Sourcing local configuration**: loading credentials, paths, or other sensitive values from `$XDG_CONFIG_HOME` without exposing full config files to LLM context (see `local-config-pattern.md`)

**How to integrate scripts in skills**:

```markdown
## Step 3: Validate Output

Run `bash ${CLAUDE_SKILL_DIR}/scripts/validate.sh <target-file>` and check its exit code.

- Exit 0: proceed to next step
- Non-zero: show the script's stderr output and ask the user how to proceed
```

**Key principles**:

- Execute scripts, don't read them — only the output consumes context tokens
- Scripts handle the "how" deterministically; the skill handles the "what" and "when" with LLM judgment
- Include error handling: check exit codes, capture stderr, specify fallback behavior
- Use `${CLAUDE_SKILL_DIR}/scripts/` for skill-scoped scripts, `${CLAUDE_PLUGIN_ROOT}/scripts/` for shared ones

**Anti-patterns**:

- Reading a script into context to "understand" it, then reimplementing its logic inline
- Using LLM reasoning for fixed transformations that a script would do identically every time
- Skipping error handling on script execution

---

## Bash

Use ONLY for operations without a dedicated tool.

**Appropriate uses**:

- Running scripts: `bash scripts/validate.sh`
- Git operations: `git status`, `git log`
- Package management: `bun install`
- Build/test commands: `bun run test`

**Anti-patterns**:

| Don't                         | Do instead                     |
| ----------------------------- | ------------------------------ |
| `Bash(cat file.txt)`          | Read                           |
| `Bash(grep pattern file)`     | Grep                           |
| `Bash(find . -name "*.ts")`   | Glob                           |
| `Bash(echo "text" > file)`    | Write                          |
| `Bash(sed 's/old/new/' file)` | Edit                           |
| Inline multi-step shell logic | Script in `scripts/` directory |

---

## Monitor

For reactive watches over background processes (logs, file changes, CI runs). Each stdout line of the watched command becomes a notification to Claude.

**When to use**:

- "Wait until X" loops — use Monitor with an `until <check>; do sleep 2; done` shell pattern
- Tail logs while implementing a fix
- Watch CI status without polling

**Effective patterns**:

- Pair with `monitors/monitors.json` declarative monitors in plugins for automatic startup
- Prefer over `Bash(run_in_background: true)` when you need streaming notifications, not just an exit signal

## LSP

Language-server intelligence: go-to-definition, find-references, type info. Use over Grep when the question is semantic ("where is this function called from?") rather than textual.

## EnterPlanMode / ExitPlanMode

Programmatic control over plan mode. Use when a skill should force a planning gate before implementation. The skill can call `EnterPlanMode`, present analysis, and require user approval via `ExitPlanMode` before any edits land.

## EnterWorktree / ExitWorktree

Native git worktree creation/teardown. Use when a skill needs git-isolated work without invoking the Agent tool's `isolation: "worktree"` parameter — for example, when the main thread (not a subagent) needs to make changes in isolation.

## CronCreate / CronList / CronDelete

Session-scoped scheduled prompts. The cron schedule fires the prompt as if the user typed it.

**When to use**:

- Recurring polls within a long session (CI status checks, deploy monitoring)
- Use with caution — every fire consumes context

## RemoteTrigger / PushNotification / ShareOnboardingGuide

- `RemoteTrigger` — invokes a claude.ai Routine remotely
- `PushNotification` — sends a push to the user's phone/desktop
- `ShareOnboardingGuide` — uploads a local `ONBOARDING.md` and returns a shareable link

## SendMessage

Used in agent-teams contexts to message a named teammate, or to resume a stopped subagent by id. The first call with `to: "<agentId>"` resumes that agent with full context preserved.

## NotebookEdit

Jupyter notebook cell-level editing. Use instead of Read/Edit when working with `.ipynb` files.

## Skill

The entry point that runs other skills. Calling `Skill` with `skill: "<name>"` loads and runs that skill. Use when one skill needs to delegate to another (the called skill's content is presented to you to follow).

## Model Selection Guide

Current model IDs (as of Claude Code v2.1.146):

| Tier   | Latest ID                   | Use for                                                                  |
| ------ | --------------------------- | ------------------------------------------------------------------------ |
| opus   | `claude-opus-4-7`           | Complex reasoning, creative generation, multi-step orchestration         |
| sonnet | `claude-sonnet-4-6`         | Research, analysis, code review, standard agent tasks, most subagents    |
| haiku  | `claude-haiku-4-5-20251001` | Validation, formatting, scaffolding, prompt hooks, mechanical transforms |

Effort levels (Opus 4.7 / 4.6, Sonnet 4.6): `low | medium | high | xhigh | max`. Set per-agent via `effort:` frontmatter or per-skill via `effort:` frontmatter.

| Task                  | Model  | Rationale                                          |
| --------------------- | ------ | -------------------------------------------------- |
| Main skill workflow   | opus   | Full reasoning for complex orchestration           |
| Research agents       | sonnet | Good analysis without opus cost                    |
| Code review agents    | sonnet | Pattern matching, not creative generation          |
| Validation agents     | haiku  | Checklist execution, fast and cheap                |
| Scaffold/file writers | haiku  | Template filling, no reasoning needed              |
| Creative generation   | opus   | Quality matters, cost justified                    |
| Formatting/cleanup    | haiku  | Mechanical transformation                          |
| Prompt-hook handlers  | haiku  | Hooks fire on every matched event; latency matters |
