# CI Workflow Template

Template for generating GitHub Actions CI workflows to test actions in a monorepo.

## Template

```yaml
name: Test {action-name}

on:
  pull_request:
    paths:
      - '{action-path}/**'
      - '.github/workflows/test-{action-name}.yml'
  push:
    branches:
      - main
    paths:
      - '{action-path}/**'

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Bun
        uses: oven-sh/setup-bun@v2
        with:
          bun-version: latest

      - name: Install dependencies
        run: bun install
        working-directory: { action-path }

      - name: Lint
        run: bun run lint
        working-directory: { action-path }

      - name: Build
        run: bun run build
        working-directory: { action-path }

      - name: Test
        run: bun test
        working-directory: { action-path }
```

## Template Variables

| Variable        | Source                          | Example              |
| --------------- | ------------------------------- | -------------------- |
| `{action-name}` | Kebab-case action name          | `add-label`          |
| `{action-path}` | Relative path to action package | `packages/add-label` |

## File Placement

The workflow should be created at:

```
.github/workflows/test-{action-name}.yml
```

For example: `.github/workflows/test-add-label.yml`

## Path Filter Strategy

The workflow uses path filters to:

1. **Only run on relevant changes** - Won't trigger for unrelated code
2. **Include workflow file itself** - Changes to the CI config trigger a run
3. **Run on main push** - Verify merged changes

```yaml
paths:
  - '{action-path}/**' # Any file in the action
  - '.github/workflows/test-{action-name}.yml' # The workflow itself
```

## Alternative: Monorepo-Wide Workflow

For repos that prefer a single workflow for all actions:

```yaml
name: Test Actions

on:
  pull_request:
    paths:
      - 'packages/**'
  push:
    branches:
      - main
    paths:
      - 'packages/**'

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      actions: ${{ steps.changes.outputs.actions }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: changes
        with:
          filters: |
            add-label:
              - 'packages/add-label/**'
            create-issue:
              - 'packages/create-issue/**'

  test:
    needs: detect-changes
    if: ${{ needs.detect-changes.outputs.actions != '[]' }}
    strategy:
      matrix:
        action: ${{ fromJson(needs.detect-changes.outputs.actions) }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
      - run: bun install
        working-directory: packages/${{ matrix.action }}
      - run: bun test
        working-directory: packages/${{ matrix.action }}
```

## Bun Setup Notes

- Uses `oven-sh/setup-bun@v2` (latest stable)
- `bun-version: latest` ensures newest Bun
- Working directory scoped to action for proper lockfile resolution

## Adding Type Checking (Optional)

If the action has TypeScript type checking:

```yaml
- name: Type Check
  run: bun run typecheck
  working-directory: { action-path }
```

## Adding Integration Tests (Optional)

If the action has integration tests that run the action itself:

```yaml
- name: Integration Test
  uses: ./{action-path}
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    # test inputs
```

## Caching Dependencies (Optional)

For faster CI runs:

```yaml
- name: Setup Bun
  uses: oven-sh/setup-bun@v2
  with:
    bun-version: latest

- name: Cache dependencies
  uses: actions/cache@v4
  with:
    path: ~/.bun/install/cache
    key: ${{ runner.os }}-bun-${{ hashFiles('{action-path}/bun.lockb') }}
    restore-keys: |
      ${{ runner.os }}-bun-
```
