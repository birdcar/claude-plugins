Your `git commit` command was blocked by the octoflow hook.

## What to do

### First time here?

Run `/commit` instead. It handles staging, message generation, and committing for you.

### Already running `/commit`?

If you were executing `/commit` and this block fired, the generated `git commit` command was missing a conventional commit type prefix. This is unexpected — the `/commit` command should always produce compliant messages.

Make sure your commit message includes a valid conventional commit type prefix. Valid types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert` — followed by an optional scope in parentheses, an optional `!` for breaking changes, then a colon.

Examples:

- `feat(auth): Add login flow`
- `fix: Resolve null pointer in payments`
- `feat(api)!: Remove deprecated endpoint`

Any format works (inline `-m`, heredoc, etc.) as long as the type prefix is present in the command.
