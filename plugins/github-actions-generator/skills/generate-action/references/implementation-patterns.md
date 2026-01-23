# Implementation Patterns

Common patterns for implementing GitHub Actions with TypeScript.

## Basic Action Structure

```typescript
import * as core from '@actions/core';
import * as github from '@actions/github';

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
```

## Input Handling

```typescript
// Required input - throws if not provided
const requiredInput = core.getInput('required-input', { required: true });

// Optional input with default
const optionalInput = core.getInput('optional-input') || 'default-value';

// Boolean input (handles 'true', 'false', 'yes', 'no', etc.)
const boolInput = core.getBooleanInput('bool-input');

// Multiline input (returns array of lines)
const multilineInput = core.getMultilineInput('multiline-input');

// Trimmed whitespace (default is true)
const untrimmedInput = core.getInput('input', { trimWhitespace: false });
```

## Output Setting

```typescript
// String output
core.setOutput('result', 'value');

// JSON output (consumer needs to parse)
core.setOutput('data', JSON.stringify(data));

// Export variable for subsequent steps
core.exportVariable('MY_VAR', value);

// Add to PATH
core.addPath('/path/to/tool');
```

## Logging

```typescript
// Standard logging (always visible)
core.info('Information message');
core.warning('Warning message');
core.error('Error message');

// Debug logging (only when ACTIONS_STEP_DEBUG=true)
core.debug('Debug message');

// Notice (creates annotation)
core.notice('Notice message', {
  title: 'Notice Title',
  file: 'src/index.ts',
  startLine: 10,
});

// Group output for readability
core.startGroup('Processing files');
core.info('File 1...');
core.info('File 2...');
core.endGroup();

// Mask sensitive values from logs
core.setSecret(sensitiveValue);
```

## Conditional Execution

```typescript
// Check event type
if (github.context.eventName === 'pull_request') {
  // PR-specific logic
}

// Check action type within event
const action = github.context.payload.action;
if (action === 'opened' || action === 'synchronize') {
  // Handle new or updated PR
}

// Check if running in a specific context
const isPR = !!github.context.payload.pull_request;
const isIssue = !!github.context.payload.issue;
```

## Working with Files

```typescript
// Read file using Bun (preferred over Node.js fs)
const content = await Bun.file('path/to/file.ts').text();

// Write file using Bun
await Bun.write('path/to/output.json', JSON.stringify(data, null, 2));

// Check if file exists
const file = Bun.file('path/to/file.ts');
const exists = await file.exists();
```

## Environment Variables

```typescript
// Access environment variables
const token = process.env.GITHUB_TOKEN;
const workspace = process.env.GITHUB_WORKSPACE;
const repository = process.env.GITHUB_REPOSITORY;

// Common GitHub Actions environment variables:
// - GITHUB_TOKEN: Authentication token
// - GITHUB_WORKSPACE: Working directory
// - GITHUB_REPOSITORY: owner/repo
// - GITHUB_SHA: Commit SHA
// - GITHUB_REF: Branch or tag ref
// - GITHUB_ACTOR: Username who triggered the action
// - GITHUB_RUN_ID: Unique workflow run ID
```

## Async Operations

```typescript
// Sequential operations
const result1 = await operation1();
const result2 = await operation2(result1);

// Parallel operations (when independent)
const [issues, prs] = await Promise.all([
  octokit.rest.issues.listForRepo({ owner, repo }),
  octokit.rest.pulls.list({ owner, repo }),
]);

// Handle pagination
const allIssues = await octokit.paginate(octokit.rest.issues.listForRepo, {
  owner,
  repo,
  per_page: 100,
});
```

## State Management

```typescript
// Save state for post action
core.saveState('previousValue', currentValue);

// Retrieve state in post action
const previousValue = core.getState('previousValue');

// Check if in post action
const isPost = !!core.getState('isPost');
core.saveState('isPost', 'true');
```
