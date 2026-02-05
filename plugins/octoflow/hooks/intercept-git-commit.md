You are intercepting a `git commit` command. Do NOT proceed with the raw git commit.

Instead, you MUST use the `/commit` skill to handle this commit properly. This ensures:

1. **Logical commit splitting** - Changes are analyzed and split into separate, focused commits when appropriate
2. **Proper commit messages** - Following Chris Beams' seven rules of great commits
3. **User approval** - Commit messages are reviewed before execution

## Action Required

BLOCK this git commit and instead run: `/commit`

The commit skill will:

- Analyze what's staged (or help stage changes)
- Determine if changes should be split into multiple logical commits
- Generate proper commit messages
- Get user approval before committing

## Why This Matters

Raw `git commit` bypasses the workflow that ensures:

- Each commit represents ONE logical change
- Commits are ordered chronologically by when changes were conceptually made
- Messages explain WHY, not just WHAT
