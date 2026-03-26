# Implementation Spec: GitHub Actions Generator Skill - Phase 2

**PRD**: ./prd-phase-2.md
**Estimated Effort**: L

## Technical Approach

Phase 2 extends the skill to assist with implementing action logic and generating unit tests. This is accomplished through additional sections in INSTRUCTIONS.md that guide Claude through implementation patterns, Octokit usage, and test generation.

The approach emphasizes pattern-following: the skill provides reference patterns for common GitHub Action scenarios (API calls, input handling, error handling) and instructs Claude to apply these patterns based on the user's description. Testing uses bun:test with mocking patterns for @actions/core and Octokit clients.

Key technical decisions:

- Extend existing INSTRUCTIONS.md rather than creating separate skill
- Reference files for common implementation patterns
- Test templates use bun:test's built-in mocking capabilities
- Focus on unit tests only (no integration/e2e)

## File Changes

### New Files

| File Path                                                                                       | Purpose                                   |
| ----------------------------------------------------------------------------------------------- | ----------------------------------------- |
| `plugins/github-actions-generator/skills/generate-action/references/implementation-patterns.md` | Common patterns for action implementation |
| `plugins/github-actions-generator/skills/generate-action/references/octokit-patterns.md`        | Patterns for Octokit SDK usage            |
| `plugins/github-actions-generator/skills/generate-action/references/testing-patterns.md`        | Unit test patterns with bun:test          |
| `plugins/github-actions-generator/skills/generate-action/references/error-handling-patterns.md` | Error handling best practices             |

### Modified Files

| File Path                                                                 | Changes                                 |
| ------------------------------------------------------------------------- | --------------------------------------- |
| `plugins/github-actions-generator/skills/generate-action/INSTRUCTIONS.md` | Add implementation and testing sections |

### Deleted Files

None.

## Implementation Details

### Extended INSTRUCTIONS.md

**Overview**: Add sections for implementation assistance and test generation.

**New sections to add**:

```markdown
## Implementation Assistance

When the user wants to implement the action logic:

### Step 1: Understand Requirements

Ask the user to describe:

- What should the action do? (primary purpose)
- What GitHub resources does it interact with? (issues, PRs, repos, etc.)
- What inputs does it need from the user?
- What outputs should it produce?
- Are there any edge cases to handle?

### Step 2: Choose Implementation Pattern

Based on requirements, select appropriate patterns from:

- `references/implementation-patterns.md` - General patterns
- `references/octokit-patterns.md` - GitHub API interactions
- `references/error-handling-patterns.md` - Error handling

### Step 3: Implement

1. Update src/index.ts with implementation
2. Update action.yml with actual inputs/outputs
3. Add JSDoc comments to exported functions
4. Only add clarifying comments for complex logic

### Step 4: Validate Implementation

Run:

- `bun run build` - Verify compilation
- `biome check .` - Verify code quality

## Test Generation

After implementation, generate unit tests:

### Step 1: Create Test File

Create src/index.test.ts (or tests/index.test.ts based on project convention)

### Step 2: Apply Testing Patterns

Use patterns from `references/testing-patterns.md`:

- Mock @actions/core (getInput, setOutput, setFailed)
- Mock @actions/github (context, getOctokit)
- Mock Octokit client methods

### Step 3: Write Test Cases

Required coverage:

- Happy path with valid inputs
- Edge cases (empty inputs, optional params)
- Error cases (API failures, invalid inputs)

### Step 4: Run Tests

`bun test`
```

**Implementation steps**:

1. Write implementation assistance section
2. Write test generation section
3. Ensure sections reference appropriate pattern files

### Implementation Patterns Reference

**references/implementation-patterns.md**:

```markdown
# Implementation Patterns

## Basic Action Structure

\`\`\`typescript
import _ as core from '@actions/core';
import _ as github from '@actions/github';

async function run(): Promise<void> {
try {
const result = await performAction();
core.setOutput('result', result);
} catch (error) {
if (error instanceof Error) {
core.setFailed(error.message);
} else {
core.setFailed('An unexpected error occurred');
}
}
}

run();
\`\`\`

## Input Handling

\`\`\`typescript
// Required input
const requiredInput = core.getInput('required-input', { required: true });

// Optional input with default
const optionalInput = core.getInput('optional-input') || 'default-value';

// Boolean input
const boolInput = core.getBooleanInput('bool-input');

// Multiline input
const multilineInput = core.getMultilineInput('multiline-input');
\`\`\`

## Output Setting

\`\`\`typescript
// String output
core.setOutput('result', 'value');

// JSON output
core.setOutput('data', JSON.stringify(data));

// Export variable for subsequent steps
core.exportVariable('MY_VAR', value);
\`\`\`

## Logging

\`\`\`typescript
// Prefer Bun-native logging for development
console.log('Info message');
console.error('Error message');

// Use core logging for action output
core.info('Info message');
core.warning('Warning message');
core.error('Error message');
core.debug('Debug message'); // Only shown when ACTIONS_STEP_DEBUG=true

// Group output
core.startGroup('Group name');
// ... grouped output
core.endGroup();
\`\`\`
```

### Octokit Patterns Reference

**references/octokit-patterns.md**:

```markdown
# Octokit Patterns

## Getting Authenticated Client

\`\`\`typescript
import \* as github from '@actions/github';

// Using GITHUB_TOKEN from action input
const token = core.getInput('github-token', { required: true });
const octokit = github.getOctokit(token);

// Access context
const { owner, repo } = github.context.repo;
const { eventName, payload } = github.context;
\`\`\`

## Common API Operations

### Issues

\`\`\`typescript
// Create issue
const { data: issue } = await octokit.rest.issues.create({
owner,
repo,
title: 'Issue title',
body: 'Issue body',
labels: ['bug'],
});

// Add comment
await octokit.rest.issues.createComment({
owner,
repo,
issue_number: issueNumber,
body: 'Comment body',
});

// List issues
const { data: issues } = await octokit.rest.issues.listForRepo({
owner,
repo,
state: 'open',
});
\`\`\`

### Pull Requests

\`\`\`typescript
// Get PR from event context
const pr = github.context.payload.pull_request;
const prNumber = pr?.number;

// Get PR details
const { data: pullRequest } = await octokit.rest.pulls.get({
owner,
repo,
pull_number: prNumber,
});

// List PR files
const { data: files } = await octokit.rest.pulls.listFiles({
owner,
repo,
pull_number: prNumber,
});

// Create review comment
await octokit.rest.pulls.createReviewComment({
owner,
repo,
pull_number: prNumber,
body: 'Comment',
commit_id: commitSha,
path: 'file.ts',
line: 10,
});
\`\`\`

### Repository Operations

\`\`\`typescript
// Get file contents
const { data: file } = await octokit.rest.repos.getContent({
owner,
repo,
path: 'path/to/file.ts',
ref: 'main',
});

// Create or update file
await octokit.rest.repos.createOrUpdateFileContents({
owner,
repo,
path: 'path/to/file.ts',
message: 'Commit message',
content: Buffer.from(content).toString('base64'),
sha: existingFileSha, // Required for updates
});
\`\`\`

### GraphQL Queries

\`\`\`typescript
// For complex queries, use GraphQL
const { repository } = await octokit.graphql<{
repository: { pullRequest: { title: string } };
}>(\`
query($owner: String!, $repo: String!, $number: Int!) {
repository(owner: $owner, name: $repo) {
pullRequest(number: $number) {
title
}
}
}
\`, {
owner,
repo,
number: prNumber,
});
\`\`\`
```

### Testing Patterns Reference

**references/testing-patterns.md**:

```markdown
# Testing Patterns

## Basic Test Structure

\`\`\`typescript
import { describe, it, expect, mock, beforeEach, afterEach } from 'bun:test';

// Import the module under test
import { run } from './index';

describe('action', () => {
beforeEach(() => {
// Reset mocks before each test
});

afterEach(() => {
// Cleanup
});

it('should succeed with valid inputs', async () => {
// Arrange
// Act
// Assert
});
});
\`\`\`

## Mocking @actions/core

\`\`\`typescript
import { mock } from 'bun:test';
import \* as core from '@actions/core';

// Mock getInput
const mockGetInput = mock((name: string) => {
const inputs: Record<string, string> = {
'my-input': 'test-value',
'github-token': 'fake-token',
};
return inputs[name] ?? '';
});
mock.module('@actions/core', () => ({
getInput: mockGetInput,
setOutput: mock(() => {}),
setFailed: mock(() => {}),
info: mock(() => {}),
warning: mock(() => {}),
error: mock(() => {}),
debug: mock(() => {}),
}));

// In tests
it('should get input correctly', () => {
expect(mockGetInput).toHaveBeenCalledWith('my-input');
});
\`\`\`

## Mocking @actions/github

\`\`\`typescript
import { mock } from 'bun:test';

const mockOctokit = {
rest: {
issues: {
create: mock(() => Promise.resolve({ data: { number: 1 } })),
createComment: mock(() => Promise.resolve({ data: {} })),
},
pulls: {
get: mock(() => Promise.resolve({ data: { title: 'Test PR' } })),
},
},
};

mock.module('@actions/github', () => ({
context: {
repo: { owner: 'test-owner', repo: 'test-repo' },
eventName: 'pull_request',
payload: {
pull_request: { number: 123 },
},
},
getOctokit: mock(() => mockOctokit),
}));
\`\`\`

## Test Cases to Cover

### Happy Path

\`\`\`typescript
it('should create issue when triggered', async () => {
await run();
expect(mockOctokit.rest.issues.create).toHaveBeenCalledWith(
expect.objectContaining({
owner: 'test-owner',
repo: 'test-repo',
})
);
expect(core.setOutput).toHaveBeenCalledWith('issue-number', 1);
});
\`\`\`

### Edge Cases

\`\`\`typescript
it('should handle empty optional input', async () => {
mockGetInput.mockImplementation((name) =>
name === 'optional-input' ? '' : 'value'
);
await run();
// Verify default behavior
});

it('should handle missing context', async () => {
// Test when PR context is undefined
});
\`\`\`

### Error Cases

\`\`\`typescript
it('should fail gracefully on API error', async () => {
mockOctokit.rest.issues.create.mockRejectedValue(
new Error('API rate limited')
);
await run();
expect(core.setFailed).toHaveBeenCalledWith('API rate limited');
});

it('should fail on missing required input', async () => {
mockGetInput.mockImplementation(() => '');
await run();
expect(core.setFailed).toHaveBeenCalled();
});
\`\`\`
```

### Error Handling Patterns Reference

**references/error-handling-patterns.md**:

```markdown
# Error Handling Patterns

## Standard Error Wrapper

\`\`\`typescript
async function run(): Promise<void> {
try {
await performAction();
} catch (error) {
handleError(error);
}
}

function handleError(error: unknown): void {
if (error instanceof Error) {
core.setFailed(error.message);
} else if (typeof error === 'string') {
core.setFailed(error);
} else {
core.setFailed('An unexpected error occurred');
}
}
\`\`\`

## Octokit Error Handling

\`\`\`typescript
import { RequestError } from '@octokit/request-error';

try {
await octokit.rest.issues.create({ ... });
} catch (error) {
if (error instanceof RequestError) {
if (error.status === 404) {
core.setFailed('Repository not found or no access');
} else if (error.status === 403) {
core.setFailed('Rate limited or insufficient permissions');
} else {
core.setFailed(\`GitHub API error: \${error.message}\`);
}
} else {
throw error; // Re-throw unexpected errors
}
}
\`\`\`

## Input Validation

\`\`\`typescript
function validateInputs(): { input1: string; input2: number } {
const input1 = core.getInput('input1', { required: true });
if (!input1.match(/^[a-z-]+$/)) {
throw new Error('input1 must be kebab-case');
}

const input2Raw = core.getInput('input2');
const input2 = parseInt(input2Raw, 10);
if (isNaN(input2) || input2 < 0) {
throw new Error('input2 must be a positive number');
}

return { input1, input2 };
}
\`\`\`

## Graceful Degradation

\`\`\`typescript
// When an optional feature fails, continue with warning
try {
await optionalEnhancement();
} catch (error) {
core.warning(\`Optional feature failed: \${error}\`);
// Continue with main functionality
}
\`\`\`
```

**Implementation steps**:

1. Create implementation-patterns.md
2. Create octokit-patterns.md
3. Create testing-patterns.md
4. Create error-handling-patterns.md
5. Update INSTRUCTIONS.md with implementation and testing sections

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

- [ ] Create test action in workspace
- [ ] Use skill to implement simple action (e.g., add label to PR)
- [ ] Verify generated code compiles
- [ ] Verify generated code uses correct Octokit patterns
- [ ] Verify generated tests pass
- [ ] Test edge case handling
- [ ] Test error handling patterns

## Error Handling

| Error Scenario                                 | Handling Strategy                                |
| ---------------------------------------------- | ------------------------------------------------ |
| User description unclear                       | Ask clarifying questions about specific behavior |
| Requested feature outside Octokit capabilities | Explain limitation, suggest alternatives         |
| Test mocking fails                             | Reference testing-patterns.md, adjust mock setup |

## Open Items

- [ ] Determine if bun:test mock.module works for all @actions/\* packages
- [ ] Test bun:test compatibility with @octokit/\* packages
