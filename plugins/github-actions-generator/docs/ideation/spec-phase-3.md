# Implementation Spec: GitHub Actions Generator Skill - Phase 3

**PRD**: ./prd-phase-3.md
**Estimated Effort**: M

## Technical Approach

Phase 3 completes the skill by adding documentation generation, CI workflow creation, and release guidance. This is implemented through additional sections in INSTRUCTIONS.md and new reference templates for README, CI workflows, and release workflows.

The README generation uses actual repository context (git tags, existing READMEs) to produce accurate, versioned documentation. CI workflows are generated as path-filtered workflows that only run for the specific action's directory changes.

Key technical decisions:

- README template pulls version from git tags or prompts user
- CI workflows use path filters for monorepo efficiency
- Release guidance is conversational (not automated publishing)
- Templates follow GitHub Actions community conventions

## File Changes

### New Files

| File Path                                                                                         | Purpose                          |
| ------------------------------------------------------------------------------------------------- | -------------------------------- |
| `plugins/github-actions-generator/skills/generate-action/references/readme-template.md`           | README.md template for actions   |
| `plugins/github-actions-generator/skills/generate-action/references/ci-workflow-template.md`      | CI workflow template             |
| `plugins/github-actions-generator/skills/generate-action/references/release-workflow-template.md` | Release workflow template        |
| `plugins/github-actions-generator/skills/generate-action/references/versioning-guide.md`          | Action versioning best practices |

### Modified Files

| File Path                                                                 | Changes                           |
| ------------------------------------------------------------------------- | --------------------------------- |
| `plugins/github-actions-generator/skills/generate-action/INSTRUCTIONS.md` | Add documentation and CI sections |

### Deleted Files

None.

## Implementation Details

### Extended INSTRUCTIONS.md

**New sections to add**:

```markdown
## Documentation Generation

After implementation and tests are complete:

### Step 1: Gather Context

- Read action.yml for inputs/outputs
- Check git tags for latest version (or ask user)
- Identify repository owner/name for usage examples

### Step 2: Generate README

Use `references/readme-template.md` to create README.md in action directory:

- Action name and description from action.yml
- Usage example with actual version tag
- Inputs table from action.yml
- Outputs table from action.yml
- Example workflow showing real-world usage
- Development section with build/test commands

### Step 3: Validate README

- Ensure version tag exists or warn user to create release
- Verify inputs/outputs tables match action.yml exactly

## CI Workflow Generation

### Step 1: Determine Workflow Strategy

Ask user preference:

- Per-action workflow (recommended for monorepos)
- Monorepo-wide workflow with path filters

### Step 2: Generate CI Workflow

Use `references/ci-workflow-template.md`:

- Trigger on PR to action directory
- Run install, build, test, lint
- Use Node.js version matching action runtime

### Step 3: Place Workflow File

Create at `.github/workflows/test-{action-name}.yml`

## Release Guidance

When user is ready to release:

### Versioning Strategy

Reference `references/versioning-guide.md`:

- Semantic versioning (v1.0.0, v1.0.1, v1.1.0)
- Major version tags (v1 points to latest v1.x.x)
- When to bump major vs minor vs patch

### Release Workflow (Optional)

If user wants automated releases, generate workflow from
`references/release-workflow-template.md`:

- Triggered on release creation
- Builds action
- Updates major version tag

### Manual Release Process

Guide through:

1. Update version in package.json
2. Build action
3. Commit changes
4. Create git tag
5. Push tag and create GitHub release
```

### README Template Reference

**references/readme-template.md**:

```markdown
# README Template

\`\`\`markdown

# {Action Name}

{Description from action.yml}

## Usage

\`\`\`yaml

- uses: {owner}/{repo}/{action-path}@v{version}
  with: # Required inputs
  {input-name}: {example-value} # Optional inputs
  {optional-input}: {example-value} # default: {default}
  \`\`\`

## Inputs

| Name             | Description   | Required | Default          |
| ---------------- | ------------- | -------- | ---------------- |
| \`{input-name}\` | {description} | {yes/no} | {default or N/A} |

## Outputs

| Name              | Description   |
| ----------------- | ------------- |
| \`{output-name}\` | {description} |

## Example Workflow

\`\`\`yaml
name: Example using {Action Name}

on:
pull_request:
types: [opened, synchronize]

jobs:
example:
runs-on: ubuntu-latest
steps: - uses: actions/checkout@v4

      - uses: {owner}/{repo}/{action-path}@v{version}
        with:
          github-token: \${{ secrets.GITHUB_TOKEN }}
          {other-inputs}

\`\`\`

## Development

\`\`\`bash

# Install dependencies

bun install

# Run tests

bun test

# Build

bun run build

# Lint

bun run lint
\`\`\`

## License

{License from root repo or MIT}
\`\`\`

## Template Variables

- \`{Action Name}\`: From action.yml name field
- \`{Description}\`: From action.yml description field
- \`{owner}\`: Repository owner (from git remote or user input)
- \`{repo}\`: Repository name
- \`{action-path}\`: Path to action in monorepo (e.g., \`actions/my-action\`)
- \`{version}\`: Latest git tag or user-provided version
- \`{input-name}\`: From action.yml inputs
- \`{output-name}\`: From action.yml outputs

## Version Detection

To get the latest version:

1. Run \`git describe --tags --abbrev=0\` to get latest tag
2. If no tags, ask user for intended first version
3. Never use "latest" or "@main" in examples
```

### CI Workflow Template Reference

**references/ci-workflow-template.md**:

```markdown
# CI Workflow Template

\`\`\`yaml
name: Test {action-name}

on:
pull_request:
paths: - '{action-path}/**' - '.github/workflows/test-{action-name}.yml'
push:
branches: - main
paths: - '{action-path}/**'

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
        working-directory: {action-path}

      - name: Lint
        run: bun run lint
        working-directory: {action-path}

      - name: Build
        run: bun run build
        working-directory: {action-path}

      - name: Test
        run: bun test
        working-directory: {action-path}

\`\`\`

## Template Variables

- \`{action-name}\`: Kebab-case action name
- \`{action-path}\`: Relative path to action (e.g., \`packages/my-action\`)

## Considerations

- Path filters ensure CI only runs for relevant changes
- Uses Bun for all operations (not Node.js directly)
- Working directory scoped to action for monorepo support
```

### Release Workflow Template Reference

**references/release-workflow-template.md**:

```markdown
# Release Workflow Template

\`\`\`yaml
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
        working-directory: {action-path}

      - name: Update major version tag
        uses: actions/publish-action@v0.2.2
        with:
          source-tag: \${{ github.event.release.tag_name }}

\`\`\`

## Tagging Convention for Monorepos

For monorepos with multiple actions, use prefixed tags:

- \`my-action-v1.0.0\` for full version
- \`my-action-v1\` for major version (floating)

## Manual Release Alternative

If not using automated releases:

\`\`\`bash

# 1. Update version in package.json

# 2. Build the action

bun run build

# 3. Commit the dist folder

git add .
git commit -m "release: {action-name} v{version}"

# 4. Create and push tags

git tag {action-name}-v{version}
git tag -f {action-name}-v{major} # Update major tag
git push origin {action-name}-v{version}
git push origin -f {action-name}-v{major}

# 5. Create GitHub release from tag

gh release create {action-name}-v{version} --generate-notes
\`\`\`
```

### Versioning Guide Reference

**references/versioning-guide.md**:

```markdown
# Action Versioning Guide

## Semantic Versioning

Actions follow semver:

- **Major (v1 → v2)**: Breaking changes to inputs, outputs, or behavior
- **Minor (v1.0 → v1.1)**: New features, backward compatible
- **Patch (v1.0.0 → v1.0.1)**: Bug fixes, no feature changes

## Tag Strategy

### Full Version Tags

Always create full semver tags:

- \`v1.0.0\`, \`v1.0.1\`, \`v1.1.0\`, \`v2.0.0\`

### Major Version Tags (Recommended)

Maintain floating major version tags for user convenience:

- \`v1\` points to latest \`v1.x.x\`
- \`v2\` points to latest \`v2.x.x\`

Users reference \`@v1\` to get latest patches automatically.

### For Monorepos

Prefix tags with action name:

- \`my-action-v1.0.0\`
- \`my-action-v1\`

## When to Bump Versions

### Major Version (Breaking)

- Removing an input or output
- Changing input/output types or semantics
- Changing default behavior in incompatible ways
- Upgrading Node.js runtime requirement

### Minor Version (Features)

- Adding new optional inputs
- Adding new outputs
- New functionality with backward compatibility

### Patch Version (Fixes)

- Bug fixes
- Documentation updates
- Dependency updates (non-breaking)

## README Version Examples

**Good**: \`@v1.2.0\` or \`@v1\`
**Bad**: \`@latest\`, \`@main\`, \`@master\`

Always show a real version tag in documentation.
```

**Implementation steps**:

1. Create readme-template.md
2. Create ci-workflow-template.md
3. Create release-workflow-template.md
4. Create versioning-guide.md
5. Update INSTRUCTIONS.md with documentation and CI sections

## Validation Commands

```bash
# Type checking
bun run typecheck

# Build plugin
bun run build

# Format check
bun run format:check

# Sync marketplace
bun run sync
```

## Testing Requirements

### Manual Testing

- [ ] Generate README for test action
- [ ] Verify README uses actual version tag
- [ ] Verify inputs/outputs tables match action.yml
- [ ] Generate CI workflow
- [ ] Verify CI workflow runs correctly in GitHub
- [ ] Test release workflow guidance
- [ ] Verify versioning guide is accurate

## Error Handling

| Error Scenario                     | Handling Strategy                                                     |
| ---------------------------------- | --------------------------------------------------------------------- |
| No git tags exist                  | Prompt user for intended version, warn about creating initial release |
| action.yml missing required fields | Report missing fields, guide user to complete action.yml              |
| Workflow file already exists       | Ask user if they want to replace or update existing                   |

## Open Items

- [ ] Decide if CI workflow should be per-action or monorepo-wide (currently per-action)
- [ ] Determine if actions/publish-action is the right tool for major tag updates
