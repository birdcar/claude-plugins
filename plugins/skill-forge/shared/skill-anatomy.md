# Skill Anatomy Reference

## Directory Structure

```
skill-name/
├── SKILL.md           # Required. Exact name, case-sensitive.
├── references/        # Optional. Detailed docs loaded on demand.
├── scripts/           # Optional. Executed, not loaded into context.
├── templates/         # Optional. Output templates.
└── assets/            # Optional. Static files.

# External (not in repo):
~/.config/{skill-name}/
├── credentials.env    # API keys, tokens (chmod 600)
├── paths.env          # Machine-specific paths
└── config.env         # User preferences
```

- Sensitive or machine-specific data belongs in `$XDG_CONFIG_HOME/{skill-name}/`, not in the repo
- Skills access local config through scripts that source env files and output specific values
- See `local-config-pattern.md` for the full pattern

- Folder name: kebab-case only
- File MUST be `SKILL.md` — not `INSTRUCTIONS.md`, not `Skill.md`, not `README.md`
- No `README.md` inside skill folders

---

## Frontmatter Fields

| Field                      | Type    | Constraints                                                                                                | Default                 | Example                                                                                    |
| -------------------------- | ------- | ---------------------------------------------------------------------------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------ |
| `name`                     | string  | kebab-case, ≤64 chars, no XML tags, no "claude"/"anthropic"                                                | directory name          | `process-pdfs`                                                                             |
| `description`              | string  | ≤1024 chars, no XML tags, third-person, include trigger phrases                                            | first paragraph of body | `"Extracts text from PDF files. Use when working with .pdf files or document extraction."` |
| `allowed-tools`            | string  | Space or comma-separated tool names. MCP tools: `ServerName:tool_name`. Bash subcommands: `Bash(python:*)` | all tools               | `"Read, Grep, Glob, Bash(python:*)"`                                                       |
| `disable-model-invocation` | boolean | Prevents Claude from auto-loading. Only manual `/name` invocation.                                         | `false`                 | `true`                                                                                     |
| `user-invocable`           | boolean | `false` hides from `/` menu. Claude can still auto-trigger.                                                | `true`                  | `false`                                                                                    |
| `context`                  | string  | `fork` runs in isolated subagent                                                                           | (inline)                | `fork`                                                                                     |
| `agent`                    | string  | Subagent type when `context: fork`. Built-ins: `Explore`, `Plan`, `general-purpose`                        | `general-purpose`       | `Explore`                                                                                  |
| `model`                    | string  | Override model for this skill                                                                              | (inherits)              | `sonnet`                                                                                   |
| `argument-hint`            | string  | Autocomplete hint shown after `/name`                                                                      | (none)                  | `[file-path]`                                                                              |
| `hooks`                    | object  | Skill-scoped lifecycle hooks                                                                               | (none)                  | See hooks docs                                                                             |
| `metadata`                 | object  | Arbitrary key-value pairs                                                                                  | (none)                  | `author: "your-name"`                                                                      |

---

## Invocation Control Matrix

| Configuration                    | User can invoke via `/` | Claude auto-triggers |
| -------------------------------- | ----------------------- | -------------------- |
| Default (both absent)            | Yes                     | Yes                  |
| `disable-model-invocation: true` | Yes                     | No                   |
| `user-invocable: false`          | No                      | Yes                  |
| Both set                         | No                      | No (useless)         |

---

## Progressive Disclosure

| Level               | What loads                               | When                          | Token cost           |
| ------------------- | ---------------------------------------- | ----------------------------- | -------------------- |
| 1. Metadata         | `name` + `description` only              | Always at startup             | Minimal (~50 tokens) |
| 2. SKILL.md body    | Full instructions                        | When skill triggers           | Full file size       |
| 3. Supporting files | `references/` content, `scripts/` output | When Claude navigates to them | On demand            |

Rules:

- Keep `SKILL.md` under 500 lines (hard limit for effectiveness)
- Place non-negotiable rules in the first 100 lines
- One-level-deep rule: all reference files must be linked directly from `SKILL.md`. Files referenced from within `references/` (two levels deep) may only get partial reads
- Large reference files have zero startup cost — put extensive docs in `references/` freely
- Scripts: execute them, don't read them into context. Only output consumes tokens
- Use `scripts/` for deterministic operations (validation, formatting, data extraction) — scripts produce consistent results without spending LLM reasoning tokens on fixed logic

---

## Variable Substitution

| Variable                | Value                            | Example usage                                 |
| ----------------------- | -------------------------------- | --------------------------------------------- |
| `$ARGUMENTS`            | All arguments as string          | `Process the file: $ARGUMENTS`                |
| `$0`, `$1`, `$N`        | Positional args (0-based)        | `Migrate $0 from $1 to $2`                    |
| `$ARGUMENTS[N]`         | Same as `$N`                     | `$ARGUMENTS[0]`                               |
| `${CLAUDE_SESSION_ID}`  | Current session UUID             | Log files, session correlation                |
| `${CLAUDE_SKILL_DIR}`   | Absolute path to skill directory | `Read ${CLAUDE_SKILL_DIR}/references/api.md`  |
| `${CLAUDE_PLUGIN_ROOT}` | Absolute path to plugin root     | `Read ${CLAUDE_PLUGIN_ROOT}/shared/config.md` |

---

## Dynamic Injection

Shell commands run before the skill is sent to Claude. Output replaces the placeholder inline.

```yaml
---
name: review-pr
---
Review this PR:
  - Diff: !`gh pr diff`
  - Changed files: !`gh pr diff --name-only`
```

Claude only sees the rendered result, not the original command.

---

## Skill Locations (Priority Order)

| Scope      | Path                               | Applies to              |
| ---------- | ---------------------------------- | ----------------------- |
| Enterprise | Managed settings                   | All org users           |
| Personal   | `~/.claude/skills/{name}/SKILL.md` | All your projects       |
| Project    | `.claude/skills/{name}/SKILL.md`   | This project only       |
| Plugin     | `{plugin}/skills/{name}/SKILL.md`  | Where plugin is enabled |

- Plugin skills are namespaced as `plugin-name:skill-name`
- Nested `.claude/skills/` directories in monorepos are auto-discovered
- The `--add-dir` flag enables live reloading without restarting

### Capability Matrix by Location

Not all features are available at every location. Plugins unlock the full feature set:

| Feature                           | Project/Global Skill | Plugin Skill |
| --------------------------------- | -------------------- | ------------ |
| SKILL.md (auto-trigger)           | Yes                  | Yes          |
| `references/` directory           | Yes                  | Yes          |
| `scripts/` directory              | Yes                  | Yes          |
| Slash commands (`/command`)       | No                   | Yes          |
| Custom agent definitions          | No                   | Yes          |
| `hooks/hooks.json`                | No                   | Yes          |
| Shared files (`PLUGIN_ROOT`)      | No                   | Yes          |
| Namespaced (avoids conflicts)     | No                   | Yes          |
| Versioned updates via marketplace | No                   | Yes          |

**Rule of thumb**: if the skill needs more than a SKILL.md and references, it belongs in a plugin.

---

## Description Context Budget

All skill descriptions compete for ~2% of the context window (~16,000 chars by default). With many installed skills, lower-priority descriptions get excluded. Override via `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var.

Descriptions must be concise AND precise — every character counts. Use third-person phrasing with explicit trigger phrases so Claude knows when to invoke the skill automatically.
