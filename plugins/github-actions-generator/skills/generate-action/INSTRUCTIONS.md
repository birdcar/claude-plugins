# Generate GitHub Action

Generate TypeScript GitHub Actions for Bun workspace monorepos with full lifecycle support.

## When to Use

Use this skill when the user wants to:

- Create a new GitHub Action in their actions monorepo
- Scaffold an action with TypeScript, Bun, and Octokit
- Add a new action to an existing Bun workspace

## Prerequisites

Before starting, verify these requirements:

1. **Bun Workspace**: Current directory has a `package.json` with `"workspaces"` field
2. **Dependencies Available**: Root `package.json` includes `@actions/core`, `@actions/github`, and `@octokit/*` packages
3. **Bun Catalog**: Root `package.json` has a `"catalog"` section for shared dependency versions
4. **Actions Directory**: Identify where actions live (commonly `packages/`, `actions/`, or similar)

If prerequisites are missing, guide the user to set them up before proceeding.

## Workflow

### Step 1: Detect Workspace Structure

Read the root `package.json` to understand the workspace:

```typescript
// Check for workspace configuration
const pkg = await Bun.file('package.json').json();

// Verify it's a Bun workspace
if (!pkg.workspaces) {
  // Not a Bun workspace - inform user
}

// Check for Bun Catalog
if (!pkg.catalog) {
  // No catalog - may need to set one up
}

// Find actions directory from workspaces patterns
const actionsDir = pkg.workspaces.find((p) => p.includes('actions') || p.includes('packages'));
```

Examine existing actions to understand patterns:

- Package naming convention (scoped vs unscoped)
- Directory structure
- Existing dependencies

### Step 2: Gather Action Details

Use `AskUserQuestion` to collect information:

1. **Action Name** (kebab-case): What should the action be called?
2. **Description**: One-line description of what it does
3. **Primary Purpose**: What GitHub resources does it interact with? (Issues, PRs, Repos, etc.)

Example questions:

```
Question: "What should this action be named?"
Header: "Action Name"
Options:
- User provides kebab-case name (e.g., "add-label", "create-issue", "sync-files")
```

### Step 3: Check for Conflicts

Before creating files:

1. Check if `{actions-dir}/{action-name}/` already exists
2. If exists, ask user how to proceed:
   - Choose different name
   - Overwrite (requires explicit confirmation)

### Step 4: Handle Dependencies

When the action needs additional dependencies beyond the defaults:

Use `AskUserQuestion`:

```
Question: "Should {package-name} be a global dependency (shared across all actions) or local to this action only?"
Header: "Dependency"
Options:
- "Global" - Add to root package.json catalog, use catalog: in action
- "Local" - Add directly to action's package.json with pinned version
```

**For global dependencies**:

1. Add to root `package.json` dependencies
2. Add version to `catalog` section
3. Use `"package-name": "catalog:"` in action's package.json

**For local dependencies**:

1. Add directly to action's package.json with specific version

### Step 5: Generate Files

Create files in this order using the reference templates:

1. **package.json** - Use `references/package-template.md`
2. **tsconfig.json** - Use `references/tsconfig-template.md`
3. **action.yml** - Use `references/action-yml-template.md`
4. **src/index.ts** - Use `references/entrypoint-template.md`

File generation checklist:

- [ ] All `catalog:` references match root package.json catalog
- [ ] tsconfig extends root or has appropriate standalone config
- [ ] action.yml has placeholder inputs/outputs ready for Phase 2
- [ ] src/index.ts has basic structure with @actions/core imports

### Step 6: Workspace Integration

After generating files:

```bash
# Install dependencies and link the new package
bun install

# Verify TypeScript compiles
bun run build --filter=@{scope}/{action-name}
```

### Step 7: Validate

Run validation to ensure the scaffold is correct:

```bash
# From the new action directory
bun install
bun run build
biome check .
```

Report any errors and fix before completing.

### Step 8: Report Results

Provide a summary:

```markdown
## Action Created: {action-name}

**Location**: {actions-dir}/{action-name}/

**Files created**:

- package.json (using Bun Catalog dependencies)
- tsconfig.json
- action.yml
- src/index.ts

**Next steps**:

1. Implement action logic in src/index.ts
2. Define inputs/outputs in action.yml
3. Add unit tests
4. Generate README and CI workflow

Use this skill again to help with implementation (Phase 2).
```

## Default Dependencies

Actions are created with these dependencies via Bun Catalog:

**Dependencies**:

- `@actions/core` - GitHub Actions toolkit core
- `@actions/github` - GitHub context and Octokit
- `@octokit/rest` - GitHub REST API client

**Dev Dependencies**:

- `@biomejs/biome` - Linting and formatting
- `@types/bun` - Bun type definitions

## Implementation Assistance

When the user wants to implement the action logic after scaffolding:

### Step 1: Understand Requirements

Ask the user to describe:

- **Primary purpose**: What should the action do?
- **GitHub resources**: What does it interact with? (issues, PRs, repos, files, etc.)
- **Inputs needed**: What information does it need from users?
- **Outputs produced**: What should it return?
- **Edge cases**: Any special situations to handle?

### Step 2: Choose Implementation Pattern

Based on requirements, select appropriate patterns from:

- `references/implementation-patterns.md` - General action patterns
- `references/octokit-patterns.md` - GitHub API interactions
- `references/error-handling-patterns.md` - Error handling

### Step 3: Implement

1. Update `src/index.ts` with the implementation
2. Update `action.yml` with actual inputs/outputs and descriptions
3. Add JSDoc comments to exported functions and types
4. Only add clarifying comments for complex or non-obvious logic

### Step 4: Validate Implementation

Run these commands:

```bash
bun run build    # Verify compilation
biome check .    # Verify code quality
```

Fix any issues before proceeding.

## Test Generation

After implementation, generate unit tests:

### Step 1: Create Test File

Create `src/index.test.ts` (or `tests/index.test.ts` based on project convention).

### Step 2: Apply Testing Patterns

Use patterns from `references/testing-patterns.md`:

- Mock `@actions/core` (getInput, setOutput, setFailed, logging)
- Mock `@actions/github` (context, getOctokit)
- Mock Octokit client methods as needed

### Step 3: Write Test Cases

Required coverage for comprehensive testing:

**Happy path**:

- Valid inputs produce expected outputs
- API calls made with correct parameters

**Edge cases**:

- Empty optional inputs use defaults
- Missing optional context handled gracefully
- Boundary conditions (empty arrays, max values)

**Error cases**:

- API failures (rate limits, 404, 403)
- Invalid inputs (wrong format, out of range)
- Missing required inputs

### Step 4: Run Tests

```bash
bun test
```

All tests must pass before completing.

### Step 5: Report Test Results

```markdown
## Tests Created

**Test file**: src/index.test.ts

**Coverage**:

- Happy path: {number} tests
- Edge cases: {number} tests
- Error cases: {number} tests

**Run with**: `bun test`
```

## Documentation Generation

After implementation and tests are complete, generate documentation:

### Step 1: Gather Context

- Read `action.yml` for inputs/outputs
- Check git tags for latest version: `git describe --tags --abbrev=0`
- For monorepos: `git tag --list '{action-name}-v*' --sort=-version:refname | head -1`
- Identify repository owner/repo from git remote

### Step 2: Generate README

Use `references/readme-template.md` to create `README.md` in the action directory:

- Action name and description from action.yml
- Usage example with **actual version tag** (never `@latest` or `@main`)
- Inputs table matching action.yml exactly
- Outputs table matching action.yml exactly
- Example workflow showing real-world usage
- Development section with build/test commands

### Step 3: Validate README

- [ ] Version tag exists (or warn user to create release)
- [ ] Inputs table matches action.yml
- [ ] Outputs table matches action.yml
- [ ] Example workflow is syntactically valid

## CI Workflow Generation

### Step 1: Determine Workflow Strategy

Ask user preference via `AskUserQuestion`:

```
Question: "How should CI be structured for this action?"
Header: "CI Strategy"
Options:
- "Per-action workflow (Recommended)" - Create .github/workflows/test-{action-name}.yml
- "Add to existing monorepo workflow" - Update existing workflow with path filters
```

### Step 2: Generate CI Workflow

Use `references/ci-workflow-template.md`:

- Path filters for action directory
- Bun setup with latest version
- Install, lint, build, test steps
- Working directory scoped to action

### Step 3: Place Workflow File

Create at `.github/workflows/test-{action-name}.yml`

### Step 4: Report CI Setup

```markdown
## CI Workflow Created

**File**: `.github/workflows/test-{action-name}.yml`

**Triggers**:

- Pull requests modifying `{action-path}/**`
- Push to main modifying `{action-path}/**`

**Jobs**:

- Install dependencies
- Run linter
- Build action
- Run tests
```

## Release Guidance

When user is ready to release:

### Step 1: Versioning Strategy

Reference `references/versioning-guide.md`:

- **Major**: Breaking changes (removed inputs, changed behavior)
- **Minor**: New features (new optional inputs, new outputs)
- **Patch**: Bug fixes, documentation

### Step 2: Release Options

Ask user preference:

```
Question: "How would you like to handle releases?"
Header: "Release"
Options:
- "Manual releases" - Guide through manual tagging process
- "Automated workflow" - Generate release workflow from references/release-workflow-template.md
```

### Step 3: For Manual Releases

Guide through:

```bash
# 1. Update version in package.json
cd {action-path}
# Edit package.json version field

# 2. Build the action
bun run build

# 3. Commit changes
git add .
git commit -m "release: {action-name} v{version}"

# 4. Create tags
git tag {action-name}-v{version}
git tag -f {action-name}-v{major}

# 5. Push
git push origin main
git push origin {action-name}-v{version}
git push origin -f {action-name}-v{major}

# 6. Create GitHub release
gh release create {action-name}-v{version} --generate-notes
```

### Step 4: For Automated Releases

Use `references/release-workflow-template.md` to create `.github/workflows/release-{action-name}.yml`

## Important Rules

- **Always use Bun Catalog**: Dependencies should reference `catalog:` for version management
- **Follow existing patterns**: Match naming and structure conventions from other actions in the repo
- **Validate before reporting success**: Run build and lint, fix any issues
- **Use kebab-case everywhere**: Action names, package names, directory names
- **No unnecessary dependencies**: Prefer Bun runtime utilities over npm packages
- **Comments policy**: Only JSDoc for public APIs, or comments for genuinely complex code
- **Ask before overwriting**: Never replace existing files without explicit confirmation
- **Test coverage**: Every action should have unit tests covering happy path, edge cases, and errors
- **Use bun:test**: Always use bun:test for testing, not Jest or other frameworks
- **Real version tags**: Never use `@latest`, `@main`, or `@master` in documentation examples
- **Per-action CI**: Prefer per-action workflows with path filters for monorepo efficiency
