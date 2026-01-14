# PR Skill

Create GitHub pull requests with structured descriptions.

## Trigger

Invoked via `/pr` or when user requests PR creation.

## Process

1. Check current branch is not main/master - if it is, ask user to create a feature branch
2. Run `git log main..HEAD --oneline` to see commits included in this PR
3. Run `git diff main...HEAD --stat` to see file changes
4. Analyze all changes and generate PR description:
   - Summary (3-5 bullet points of what changed and why)
   - Test plan (checklist of verification steps)
5. Check if branch is pushed to remote, push if needed (with user confirmation)
6. Create PR via `gh pr create` with the generated description
7. Return the PR URL to the user

## PR Template

```markdown
## Summary

- {bullet point 1}
- {bullet point 2}
- {bullet point 3}

## Test plan

- [ ] {verification step 1}
- [ ] {verification step 2}
```

## Important Rules

- Never create PR without user approval of the description
- Always push branch before creating PR
- Use HEREDOC syntax for PR body to preserve formatting
- Return the PR URL when complete so user can review
- If `gh` CLI is not installed, inform user how to install it
