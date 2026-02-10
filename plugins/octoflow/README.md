# octoflow

Git workflow commands for well-structured commits and pull requests.

## Why

Good commits tell a story. Raw `git commit` makes it easy to create unfocused commits with vague messages. This plugin enforces a disciplined workflow: logical commit splitting, imperative messages following Chris Beams' seven rules, and structured PR descriptions that explain what changed and how to verify it.

The hook ensures this workflow is always used — even when Claude tries to run `git commit` directly, it gets intercepted and redirected to `/commit`.

## Usage

| Component             | Type    | Description                                              |
| --------------------- | ------- | -------------------------------------------------------- |
| `/commit`             | Command | Analyze changes, split into logical commits, generate proper messages |
| `/pr`                 | Command | Create GitHub PRs with structured summary and test plan  |
| `intercept-git-commit` | Hook   | Blocks raw `git commit` and redirects to `/commit`       |

### `/commit`

Analyzes staged and unstaged changes, determines if they should be split into multiple logical commits (e.g., bug fix + refactor = 2 commits), generates messages following conventional commit format, and asks for approval before committing.

Commits are ordered logically: infrastructure first, core changes second, surface changes last, cleanup at the end.

### `/pr`

Checks you're on a feature branch, analyzes all commits since diverging from main, generates a PR description with a summary and test plan checklist, then creates the PR via `gh pr create`.

### Hook: intercept-git-commit

A `PreToolUse` hook on `Bash` commands matching `git commit`. Blocks the raw commit and instructs Claude to use `/commit` instead.
