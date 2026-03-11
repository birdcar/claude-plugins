# octoflow

Git workflow commands for well-structured commits and pull requests.

## Why

Raw `git commit` makes it easy to create unfocused commits — vague messages, unrelated changes bundled together, no explanation of why the change was needed. Over time these make `git log` useless and code archaeology painful.

This plugin installs two commands that enforce a disciplined workflow: `/commit` analyzes your changes and can split them into multiple logical commits with proper messages, and `/pr` generates structured PR descriptions with a summary and test plan checklist.

A `PreToolUse` hook backs this up — if Claude tries to run `git commit` directly without a conventional commit message already in the command, it gets blocked and redirected to `/commit`.

## Installation

```bash
claude plugin install octoflow
```

Requires the `gh` CLI for `/pr`.

## Commands

### `/commit`

Runs `git status`, `git diff`, and `git diff --cached` to analyze all changes, then evaluates whether they should be split into multiple logical commits. A bug fix in one module and a refactor in another should be two commits, not one. A tightly coupled change where splitting would leave the repo in a broken state should stay together.

When splitting is needed, `/commit` walks through staging and committing each logical unit in the right order: infrastructure first (deps, config, migrations), then core changes (models, business logic), then surface changes (API endpoints, UI), then cleanup.

Messages follow [Chris Beams' seven rules](https://cbea.ms/git-commit/) and conventional commit format:

```
feat(auth): Add OAuth2 support for GitHub login

Enables users to authenticate via GitHub OAuth2. Reduces friction
for developers who already have GitHub accounts.

Closes #234
```

The message is presented for approval before any commit is made.

### `/pr`

Analyzes all commits since diverging from main, generates a PR title and description, then creates the PR via `gh pr create`. If the branch hasn't been pushed to remote yet, it pushes first.

PR descriptions follow this structure:

```markdown
## Summary

- What changed and why, in 3-5 bullets

## Test plan

- [ ] Specific verification step
- [ ] Another thing to check
```

The description is presented for approval before the PR is created. Returns the PR URL when done.

## Hook behavior

The `intercept-git-commit` hook watches `Bash` tool calls for `git commit` commands. If the command already contains a properly formatted conventional commit message (e.g., Claude is following `/commit`'s own instructions), it passes through. If not, it blocks the commit and instructs Claude to use `/commit` instead.

This means the hook enforces the workflow without getting in the way of it.
