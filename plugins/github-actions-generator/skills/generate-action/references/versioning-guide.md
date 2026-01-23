# Action Versioning Guide

Best practices for versioning GitHub Actions.

## Semantic Versioning

Actions follow semver (Semantic Versioning):

| Type  | When to Use                                   | Example             |
| ----- | --------------------------------------------- | ------------------- |
| Major | Breaking changes to inputs, outputs, behavior | `v1` → `v2`         |
| Minor | New features, backward compatible             | `v1.0` → `v1.1`     |
| Patch | Bug fixes, no feature changes                 | `v1.0.0` → `v1.0.1` |

## Tag Strategy

### Full Version Tags

Always create full semver tags:

- `v1.0.0`, `v1.0.1`, `v1.1.0`, `v2.0.0`

These are immutable - once created, they should never change.

### Major Version Tags (Recommended)

Maintain floating major version tags for user convenience:

- `v1` points to latest `v1.x.x`
- `v2` points to latest `v2.x.x`

Users reference `@v1` to automatically get patches and minor updates.

### For Monorepos

Prefix tags with action name to avoid collisions:

| Tag Type | Format                   | Example            |
| -------- | ------------------------ | ------------------ |
| Full     | `{action-name}-v{x.y.z}` | `add-label-v1.2.0` |
| Major    | `{action-name}-v{x}`     | `add-label-v1`     |

## When to Bump Versions

### Major Version (Breaking)

Bump major version when you:

- Remove an input
- Remove an output
- Change input/output types or semantics
- Change default behavior in incompatible ways
- Upgrade Node.js runtime requirement (e.g., node16 → node20)
- Change required inputs to have different names

**Example**: Renaming `token` to `github-token` is a breaking change.

### Minor Version (Features)

Bump minor version when you:

- Add new optional inputs
- Add new outputs
- Add new functionality with backward compatibility
- Deprecate (but don't remove) inputs/outputs

**Example**: Adding a `dry-run` input that defaults to `false`.

### Patch Version (Fixes)

Bump patch version when you:

- Fix bugs without changing API
- Update documentation
- Update dependencies (non-breaking)
- Improve performance
- Fix typos in error messages

**Example**: Fixing a bug where the action failed on empty input.

## README Version Examples

### Good

Show real, stable version tags:

```yaml
- uses: owner/repo/action@v1.2.0
# or
- uses: owner/repo/action@v1
```

### Bad

Never use these in documentation:

```yaml
# DON'T DO THIS
- uses: owner/repo/action@latest # Doesn't exist
- uses: owner/repo/action@main # Unstable
- uses: owner/repo/action@master # Unstable
- uses: owner/repo/action@HEAD # Unpredictable
```

## Version in package.json

Keep `package.json` version in sync with tags:

```json
{
  "name": "@scope/add-label",
  "version": "1.2.0"
}
```

This isn't strictly required (users reference tags, not npm), but helps with:

- Tracking which version is deployed
- Automated release workflows
- Changelog generation

## First Release Checklist

For a new action's first release:

1. **Choose version**: Start with `v1.0.0` (stable) or `v0.1.0` (experimental)
2. **Update package.json**: Set matching version
3. **Build**: Run `bun run build`
4. **Commit**: `git commit -m "release: add-label v1.0.0"`
5. **Tag**: `git tag add-label-v1.0.0`
6. **Major tag**: `git tag add-label-v1`
7. **Push**: `git push origin main --tags`
8. **Create release**: Use GitHub UI or `gh release create`

## Version Lifecycle

```
v0.x.x → Experimental (breaking changes expected)
v1.0.0 → First stable release
v1.0.1 → Patch (bug fix)
v1.1.0 → Minor (new feature)
v1.1.1 → Patch
v2.0.0 → Major (breaking change)
```

## Deprecation Process

When planning breaking changes:

1. **Announce**: Add deprecation warnings in current version
2. **Document**: Update README with migration guide
3. **Wait**: Give users time to migrate (2+ weeks)
4. **Release**: Publish new major version
5. **Support**: Keep old major version for critical fixes

## Commit Message Convention

Use conventional commits for easy changelog generation:

```
feat(add-label): add dry-run option
fix(add-label): handle empty label list
docs(add-label): update usage examples
chore(add-label): update dependencies
BREAKING CHANGE: rename token input to github-token
```
