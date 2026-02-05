---
name: commit
description: Create a git commit with a well-crafted message
allowed-tools: [Bash, Read, Glob, Grep]
---

Generate well-crafted commit messages and create Git commits following best practices.

## Process

1. Run `git status` to check for staged and unstaged changes
2. Run `git diff` (unstaged) and `git diff --cached` (staged) to analyze ALL changes
3. **Evaluate if changes should be split** into multiple logical commits (see Splitting Commits below)
4. If splitting: guide user through staging and committing each logical unit separately
5. Run `git log --oneline -10` to understand the repository's commit message style
6. Generate a commit message following the rules below
7. Present the message to user for approval or editing
8. Execute the commit with the approved message
9. Repeat for remaining logical units if splitting
10. Show the final result

## Splitting Commits

**Every commit should represent ONE logical change.** Before committing, analyze whether changes should be split.

### When to Split

Split changes into separate commits when you see:

- **Multiple unrelated fixes** - Bug fix in auth AND bug fix in payments = 2 commits
- **Feature + refactor** - New feature AND cleanup of existing code = 2 commits
- **Multiple files for different purposes** - Config change AND code change = likely 2 commits
- **Distinct logical steps** - Add migration, then add model, then add API = 3 commits

### Chronological Ordering

Commits should follow the logical order of development:

1. **Infrastructure first** - Dependencies, config, migrations
2. **Core changes second** - Models, business logic, services
3. **Surface changes last** - UI, API endpoints, tests for new behavior
4. **Cleanup at the end** - Refactors, removals, formatting (if any)

### How to Split

1. Use `git add -p` or `git add <specific-files>` to stage only related changes
2. Commit that logical unit with a focused message
3. Stage the next logical unit
4. Repeat until all changes are committed

### Examples

**Bad**: One commit with message "Update auth and fix payment bug and add tests"

**Good**: Three commits:

```
fix(payments): Handle null amount in refund calculation
feat(auth): Add session timeout configuration
test(auth): Add tests for session timeout behavior
```

### When NOT to Split

Keep changes together when:

- They are tightly coupled (changing a function signature + all its callers)
- One change doesn't make sense without the other
- Splitting would leave the codebase in a broken intermediate state

## The Seven Rules of Great Commits

### 1. Separate Subject from Body with a Blank Line

```
type(scope): subject line here

Body starts after blank line. Explains the why, not the what.
```

### 2. Limit Subject to 50 Characters

- 50 characters is the target for readability
- 72 characters is the hard limit (GitHub truncates beyond this)
- Forces concise, meaningful summaries

### 3. Capitalize the Subject Line

- Write `feat: Add user authentication` not `feat: add user authentication`

### 4. Do Not End Subject with a Period

- Periods waste space and are unnecessary for headlines
- Write `fix: Resolve login timeout` not `fix: Resolve login timeout.`

### 5. Use Imperative Mood in Subject

Write commands, not descriptions of what happened:

- **Good**: `Add`, `Fix`, `Update`, `Remove`, `Refactor`
- **Bad**: `Added`, `Fixed`, `Updated`, `Removed`, `Refactored`

**Test**: "If applied, this commit will _[your subject line]_" should be grammatically correct.

### 6. Wrap Body at 72 Characters

- Manually wrap body text at 72 characters
- Allows room for Git's indentation in various tools
- Most editors can be configured to do this automatically

### 7. Use Body to Explain What and Why, Not How

- The code diff shows how
- The body explains:
  - Why was this change necessary?
  - What problem does it solve?
  - What side effects or consequences exist?

## Commit Message Format

```
type(scope): imperative subject under 50 chars

Optional body wrapped at 72 characters. Focus on explaining
WHY this change was made, not what was changed (the diff shows
that). Include context that future developers will need.

Optional footers like:
Fixes #123
BREAKING CHANGE: description of breaking change
```

## Commit Types

| Type       | Use For                                       |
| ---------- | --------------------------------------------- |
| `feat`     | New feature visible to users                  |
| `fix`      | Bug fix for existing functionality            |
| `docs`     | Documentation only changes                    |
| `style`    | Formatting, whitespace (no code logic change) |
| `refactor` | Code restructuring without behavior change    |
| `perf`     | Performance improvements                      |
| `test`     | Adding or updating tests                      |
| `build`    | Build system or external dependencies         |
| `ci`       | CI/CD configuration changes                   |
| `chore`    | Maintenance tasks (tooling, configs)          |
| `revert`   | Reverting a previous commit                   |

## Breaking Changes

For changes that break backward compatibility:

```
feat!: Remove deprecated authentication method

BREAKING CHANGE: The `legacyAuth()` function has been removed.
Migrate to `newAuth()` before upgrading. See migration guide
in docs/migration-v2.md.
```

## Examples

### Good Commit Messages

```
feat(auth): Add OAuth2 support for GitHub login

Enables users to authenticate via GitHub OAuth2. This reduces
friction for developers who already have GitHub accounts.

Closes #234
```

```
fix: Prevent crash when config file is missing

The app crashed on first run because it expected a config file.
Now creates a default config if none exists.
```

```
refactor: Extract validation logic into separate module

Validation was duplicated across 4 controllers. Centralizing it
reduces maintenance burden and ensures consistent behavior.
```

### Bad Commit Messages

```
fixed stuff                      # Too vague, not imperative
Updated the code.                # Says nothing useful
feat: added new feature.         # Not imperative, has period
WIP                              # Meaningless
```

## Important Rules

- Never commit without explicit user approval of the message
- Never add a Co-Authored-By line unless the user explicitly requests it
- Warn user if staging files that look like secrets (.env, credentials, tokens, keys, \*.pem, id_rsa)
- Match the existing commit style in the repository when possible
- For multi-file changes, follow the Splitting Commits section to create logical, focused commits
- If the diff is large, summarize the key changes in the body

## Edge Cases

### Amending Commits

Only offer to amend if:

- The previous commit was made in the current session
- It hasn't been pushed to remote
- User explicitly requests it

Otherwise, create a new commit.

### Empty Commits

Never create empty commits unless explicitly requested for CI triggers.

### Large Changesets

If there are many changed files, follow the Splitting Commits section above to break them into logical units.

### Generated Files

Warn if committing generated files (node_modules, dist/, build/, \*.min.js) that are typically gitignored.
