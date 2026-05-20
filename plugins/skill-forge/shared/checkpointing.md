# Checkpointing — what generators need to know

Claude Code automatically snapshots files before each edit. The user can `/rewind` (or press `Esc Esc` on an empty input) to revert. As a skill generator, you mostly don't need to do anything — but there are two situations where you should warn the user.

Verified against Claude Code v2.1.146.

## What's tracked

- Every user prompt creates a new checkpoint
- All file edits made by Claude's editing tools (`Write`, `Edit`, `NotebookEdit`) are captured
- Checkpoints persist across sessions, survive for 30 days (configurable)

## What's NOT tracked

- **File changes from Bash commands** — `rm`, `mv`, `cp`, `> file`, `sed -i`, build outputs, anything a shell command did
- External changes (manual edits, other concurrent sessions, IDE saves)
- Files that exist only in `$CLAUDE_PLUGIN_DATA` or `$CLAUDE_PROJECT_DIR` outside the edit-tool path

This is the biggest pitfall: if a skill uses `Bash` to move, delete, or rewrite files, those operations are **invisible to `/rewind`**. The user can't undo them through the normal rewind menu.

## The /rewind menu

When the user invokes `/rewind`, the menu lists each prompt sent during the session. Each entry offers:

- **Restore code and conversation** — revert both
- **Restore conversation** — keep current code, rewind chat
- **Restore code** — keep chat, revert files
- **Summarize from here** — compress chat after this point into a summary, freeing context
- **Summarize up to here** — compress chat before this point, keep recent messages intact
- **Never mind** — exit menu

`Summarize` is the targeted form of `/compact`: choose which side of a message to compress.

## Generator rules

1. **Prefer file-edit tools over Bash for any change you want to be rewindable.** If a skill creates a config file, use `Write` (rewindable) rather than `Bash(cat > file)` (not rewindable).

2. **When a skill MUST use Bash for file changes (running a generator, build script, codemod), include a warning.** Add a one-line note to the user that the operation won't appear in the rewind menu.

   Example skill text:

   ```markdown
   > Note: this step uses a shell script to rewrite the config. It won't appear in `/rewind` — commit before running if you want a recovery point.
   ```

3. **Don't replace version control.** Checkpoints are session-level undo, not a substitute for git. For irreversible operations, recommend the user commit first.

4. **Hooks don't trigger checkpoints.** Files modified by a `PreToolUse` or `PostToolUse` command hook are outside Claude's edit-tool path; they're not captured. If a hook rewrites files (linters, formatters), the user can't `/rewind` those changes.

## Sample warnings to embed in generated skills

For a skill that runs migrations / build scripts:

```markdown
## ⚠ Checkpoint caveat

This skill invokes `<command>` via Bash. The file changes it produces are **not captured by `/rewind`**. Commit before running if you need recovery.
```

For a skill with a destructive Bash step (rm/mv):

```markdown
## ⚠ Destructive operation

This step removes <files>. `/rewind` cannot undo Bash file deletions — use git if you need recovery.
```

For a skill that uses a hook to auto-format on save:

```markdown
> The auto-format hook rewrites files outside Claude's edit-tool path; those formatting changes won't appear in `/rewind`. Commit before triggering the format pass if you want a recovery point.
```

## Quick reference for generators

| Operation                            | Rewindable? | Generator action                                       |
| ------------------------------------ | ----------- | ------------------------------------------------------ |
| `Write` / `Edit` / `NotebookEdit`    | Yes         | Default — no warning needed                            |
| `Bash` rewriting files               | **No**      | Emit a checkpoint caveat warning                       |
| `Bash` running build/test (no edits) | N/A         | No warning needed                                      |
| Hook-driven file changes             | **No**      | Warn if the hook materially mutates user-visible files |
| MCP tools modifying files            | Depends     | Verify with the MCP server author; warn if uncertain   |
