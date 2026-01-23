# Release Workflow Template

Template for automated release workflows for GitHub Actions in a monorepo.

## Template

```yaml
name: Release {action-name}

on:
  release:
    types: [published]

jobs:
  release:
    runs-on: ubuntu-latest
    if: startsWith(github.event.release.tag_name, '{action-name}-v')

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Bun
        uses: oven-sh/setup-bun@v2

      - name: Install and build
        run: |
          bun install
          bun run build
        working-directory: { action-path }

      - name: Update major version tag
        uses: actions/publish-action@v0.2.2
        with:
          source-tag: ${{ github.event.release.tag_name }}
```

## Template Variables

| Variable        | Source                          | Example              |
| --------------- | ------------------------------- | -------------------- |
| `{action-name}` | Kebab-case action name          | `add-label`          |
| `{action-path}` | Relative path to action package | `packages/add-label` |

## Tagging Convention for Monorepos

For monorepos with multiple actions, use prefixed tags:

| Tag Type | Format                   | Example            |
| -------- | ------------------------ | ------------------ |
| Full     | `{action-name}-v{x.y.z}` | `add-label-v1.2.0` |
| Major    | `{action-name}-v{x}`     | `add-label-v1`     |

The workflow's `if` condition filters releases to only run for the specific action:

```yaml
if: startsWith(github.event.release.tag_name, '{action-name}-v')
```

## Manual Release Process

If not using automated releases, follow these steps:

```bash
# 1. Update version in package.json
cd {action-path}
bun pkg set version=1.2.0

# 2. Build the action
bun run build

# 3. Commit the changes (including dist folder)
git add .
git commit -m "release: {action-name} v1.2.0"

# 4. Create full version tag
git tag {action-name}-v1.2.0

# 5. Update major version tag (force push to move the tag)
git tag -f {action-name}-v1

# 6. Push everything
git push origin main
git push origin {action-name}-v1.2.0
git push origin -f {action-name}-v1

# 7. Create GitHub release
gh release create {action-name}-v1.2.0 \
  --title "{Action Name} v1.2.0" \
  --generate-notes
```

## Alternative: Single Release Workflow for All Actions

For repos that prefer one workflow:

```yaml
name: Release Action

on:
  release:
    types: [published]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Parse release tag
        id: parse
        run: |
          TAG="${{ github.event.release.tag_name }}"
          # Extract action name: "add-label-v1.2.0" -> "add-label"
          ACTION_NAME=$(echo "$TAG" | sed 's/-v[0-9].*//')
          echo "action_name=$ACTION_NAME" >> $GITHUB_OUTPUT
          echo "action_path=packages/$ACTION_NAME" >> $GITHUB_OUTPUT

      - name: Setup Bun
        uses: oven-sh/setup-bun@v2

      - name: Install and build
        run: |
          bun install
          bun run build
        working-directory: ${{ steps.parse.outputs.action_path }}

      - name: Update major version tag
        uses: actions/publish-action@v0.2.2
        with:
          source-tag: ${{ github.event.release.tag_name }}
```

## Major Version Tag Updates

The `actions/publish-action` handles updating the major version tag:

- From `add-label-v1.2.0`, it updates `add-label-v1` to point to the same commit
- Users referencing `@add-label-v1` automatically get the latest patch

## Permissions Required

The release workflow needs these permissions:

```yaml
permissions:
  contents: write # To push tags
```

Or ensure the `GITHUB_TOKEN` has write access to the repository.

## Pre-Release vs Release

For pre-releases (alpha, beta, rc):

```yaml
on:
  release:
    types: [published]

jobs:
  release:
    runs-on: ubuntu-latest
    # Skip major tag update for pre-releases
    if: |
      startsWith(github.event.release.tag_name, '{action-name}-v') &&
      !github.event.release.prerelease
```

## Verifying Release

After releasing, verify:

1. **Tag exists**: `git tag -l '{action-name}-v*'`
2. **Major tag updated**: `git rev-parse {action-name}-v1` matches full tag
3. **Release visible**: Check GitHub Releases page
4. **Action usable**: Test in another repo with the new version
