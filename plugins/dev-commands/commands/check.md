---
name: check
description: Run all checks (typecheck, lint, test)
allowed-tools: [Bash, Read, Glob]
---

Run all validation checks for the project before committing.

## Workflow

Execute checks in order, stopping on first failure:

1. **Type Check**
   - TypeScript: `tsc --noEmit` or `npx tsc --noEmit`
   - Python: `pyright` or `mypy`
   - Rust: `cargo check`

2. **Lint**
   - Run project's configured linter (see /lint)

3. **Test**
   - Run project's test suite (see /test)

## Output

Summarize results:
- Total checks run
- Pass/fail status for each
- First error details if any failed

If all checks pass, confirm the project is ready to commit.
