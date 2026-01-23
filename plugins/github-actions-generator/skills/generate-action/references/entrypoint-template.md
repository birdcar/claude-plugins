# src/index.ts Template

Generate the entrypoint file for a GitHub Action.

## Template

```typescript
import * as core from '@actions/core';
import * as github from '@actions/github';

/**
 * Main entry point for the {Action Name} action.
 */
async function run(): Promise<void> {
  try {
    // Get inputs
    const token = core.getInput('github-token', { required: true });

    // Create Octokit client
    const octokit = github.getOctokit(token);

    // Get context
    const { owner, repo } = github.context.repo;

    // TODO: Implement action logic here

    // Set outputs
    // core.setOutput('result', value);

    core.info('Action completed successfully');
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

## Structure Explanation

### Imports

```typescript
import * as core from '@actions/core'; // Input/output handling, logging, failure
import * as github from '@actions/github'; // GitHub context, Octokit factory
```

### Input Handling

```typescript
// Required input - throws if not provided
const requiredInput = core.getInput('input-name', { required: true });

// Optional input with default
const optionalInput = core.getInput('optional-input') || 'default-value';

// Boolean input
const boolInput = core.getBooleanInput('bool-input');

// Multiline input (returns array)
const multilineInput = core.getMultilineInput('list-input');
```

### Octokit Client

```typescript
const token = core.getInput('github-token', { required: true });
const octokit = github.getOctokit(token);

// REST API calls
const { data } = await octokit.rest.issues.create({
  owner,
  repo,
  title: 'Issue title',
});

// GraphQL queries
const result = await octokit.graphql(
  `
  query($owner: String!, $repo: String!) {
    repository(owner: $owner, name: $repo) {
      name
    }
  }
`,
  { owner, repo }
);
```

### Context Access

```typescript
const { owner, repo } = github.context.repo;
const { eventName, payload, sha, ref } = github.context;

// For pull_request events
const prNumber = github.context.payload.pull_request?.number;

// For issue events
const issueNumber = github.context.payload.issue?.number;
```

### Output Setting

```typescript
// String output
core.setOutput('result', 'value');

// JSON output
core.setOutput('data', JSON.stringify(data));

// Export variable for subsequent steps
core.exportVariable('MY_VAR', 'value');
```

### Logging

```typescript
core.info('Information message');
core.warning('Warning message');
core.error('Error message');
core.debug('Debug message'); // Only shows when ACTIONS_STEP_DEBUG=true

// Grouped output
core.startGroup('Processing files');
core.info('File 1...');
core.info('File 2...');
core.endGroup();
```

### Error Handling

```typescript
try {
  await riskyOperation();
} catch (error) {
  if (error instanceof Error) {
    core.setFailed(error.message);
  } else {
    core.setFailed('An unexpected error occurred');
  }
}
```

## Notes

- Always wrap main logic in try/catch with `core.setFailed`
- Use `core.info` for user-visible progress messages
- Use `core.debug` for verbose debugging (hidden by default)
- Prefer async/await over callbacks
- The `run()` call at the end starts the action
