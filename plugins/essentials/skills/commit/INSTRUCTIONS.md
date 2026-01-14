# Commit Skill

Generate semantic commit messages and create Git commits.

## Trigger

Invoked via `/commit` or when user requests a commit.

## Process

1. Run `git status` to check for staged changes
2. If no staged changes, ask user what to stage or offer to stage all modified files
3. Run `git diff --cached` to analyze staged changes
4. Run `git log --oneline -5` to understand the repository's commit message style
5. Generate a semantic commit message following conventional commits:
   - `feat`: new feature
   - `fix`: bug fix
   - `docs`: documentation changes
   - `refactor`: code refactoring
   - `test`: adding or updating tests
   - `chore`: maintenance tasks
6. Present the message to user for approval or editing
7. Execute the commit with the approved message
8. Show the commit result

## Commit Message Format

```
type(scope): short description

Longer description if needed, explaining the "why" not the "what".
```

## Important Rules

- Never commit without explicit user approval
- Never add a Co-Authored-By line unless the user explicitly requests it
- Warn user if staging files that look like secrets (.env, credentials, tokens, keys)
- Keep the commit message concise - focus on "why" not "what" (the diff shows what)
- Match the existing commit style in the repository when possible
