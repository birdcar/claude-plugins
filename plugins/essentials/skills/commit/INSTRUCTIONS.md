# Commit Skill

Generate well-crafted commit messages and create Git commits following best practices.

## Trigger

Invoked via `/commit` or when user requests a commit.

## Process

1. Run `git status` to check for staged changes
2. If no staged changes, ask user what to stage or offer to stage all modified files
3. Run `git diff --cached` to analyze staged changes
4. Run `git log --oneline -10` to understand the repository's commit message style
5. Generate a commit message following the rules below
6. Present the message to user for approval or editing
7. Execute the commit with the approved message
8. Show the commit result

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

## Merge Commits

When committing a merge:

```
merge: Integrate feature-branch into main
```

## Revert Commits

When reverting:

```
revert: Remove broken feature X

This reverts commit abc123.

The feature caused regression in Y. Will re-implement after
fixing the underlying issue.
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
- For multi-file changes, consider whether they should be separate commits
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

If staging many files, ask user if changes should be split into multiple focused commits.

### Generated Files

Warn if committing generated files (node_modules, dist/, build/, \*.min.js) that are typically gitignored.
