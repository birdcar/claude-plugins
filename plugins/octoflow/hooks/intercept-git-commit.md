Your `git commit` command was blocked by the octoflow hook.

## What to do

Run `/commit` instead. It will handle staging, message generation, and committing for you.

If you were already executing `/commit` and this block fired, it means your `git commit` command was missing a conventional commit type prefix. Make sure your commit message starts with one of: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, or `revert` — followed by an optional scope in parentheses, then a colon. For example: `feat(auth): Add login flow`.

The hook allows `git commit` through when the command already contains a valid conventional commit type. Any format works (inline `-m`, heredoc, etc.) as long as the type prefix is present.
