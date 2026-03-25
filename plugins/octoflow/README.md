# octoflow

Git workflow commands for Claude Code that enforce well-structured commits and pull requests.

## The problem

Left to its own devices, Claude will run `git commit -m "Update files"` and move on. You end up with vague messages, unrelated changes bundled together, and no record of _why_ anything was done. Six months later, `git log` is useless and code archaeology is painful.

I wanted Claude to commit the way I would: one logical change per commit, conventional commit format, a body that explains motivation instead of restating the diff, and a check before anything gets committed. This plugin installs two commands and a hook that enforce that workflow.

## Installation

```bash
claude plugin install octoflow
```

The `/pr` command requires the [`gh` CLI](https://cli.github.com/).

## Commands

### `/commit`

Analyzes staged and unstaged changes, evaluates whether they should be split into multiple logical commits, and walks you through staging and committing each one.

The interesting part is the splitting logic. If you have a bug fix in auth and a refactor in payments, `/commit` proposes two separate commits and asks you to pick a strategy via `AskUserQuestion`. If the changes are tightly coupled and splitting would leave the repo broken, it keeps them together.

When splitting is needed, commits are ordered by dependency: infrastructure first (deps, config, migrations), then core changes (models, business logic), then surface changes (API, UI), then cleanup. For multi-commit workflows, each commit gets tracked as a Task so the plan survives context compaction at end of session.

Every commit message follows [Chris Beams' seven rules](https://cbea.ms/git-commit/) and conventional commit format. The body must explain _why_ the change was made, never _what_ changed -- the diff already shows that. If the motivation isn't clear from session context, the command asks you directly rather than guessing.

Nothing gets committed without your explicit approval. The command presents each draft message via `AskUserQuestion` with options to approve, edit the subject, edit the body, or skip. For multi-commit batches, there's a final review step where you can combine, reorder, or start over.

```
feat(auth): Add OAuth2 support for GitHub login

GitHub is the primary VCS for 90% of our users. Supporting
OAuth2 login eliminates the separate account creation step
that was causing 40% drop-off during onboarding.

Closes #234
```

### `/pr [base-branch]`

Analyzes all commits since diverging from the base branch (defaults to main), generates a PR title and structured description, then creates the PR via `gh pr create`. If the branch hasn't been pushed to remote, it pushes first.

Before generating anything, it checks edge cases: are you on main (stop), are there zero commits ahead (stop), does an open PR already exist for this branch (ask whether to update or create new).

PR descriptions follow a consistent structure:

```markdown
## Summary

- What changed and why, in 3-5 bullets

## Test plan

- [ ] Specific verification step
- [ ] Another thing to check
```

Like `/commit`, the description is presented for approval before the PR is created. The full workflow is tracked as a Task so the PR URL survives compaction. Returns the PR URL when done.

## Hook

The `intercept-git-commit` hook watches all `Bash` tool calls for `git commit` commands. If the command already contains a properly formatted conventional commit type prefix (e.g., `feat:`, `fix(scope):`) it passes through -- this lets `/commit`'s own generated commands work normally. If not, it blocks the commit and redirects to `/commit`.

This means raw `git commit -m "update stuff"` gets caught, but the plugin's own workflow isn't interrupted.
