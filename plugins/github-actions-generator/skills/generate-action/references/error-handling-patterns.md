# Error Handling Patterns

Best practices for error handling in GitHub Actions.

## Standard Error Wrapper

Every action should wrap its main logic in a try-catch that calls `setFailed`:

```typescript
import * as core from '@actions/core';

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

run();
```

## Octokit Error Handling

Handle GitHub API errors with specific status codes:

```typescript
import { RequestError } from '@octokit/request-error';

try {
  await octokit.rest.issues.create({
    owner,
    repo,
    title: 'Issue title',
  });
} catch (error) {
  if (error instanceof RequestError) {
    switch (error.status) {
      case 401:
        core.setFailed('Authentication failed. Check your GITHUB_TOKEN.');
        break;
      case 403:
        if (error.response?.headers['x-ratelimit-remaining'] === '0') {
          core.setFailed('GitHub API rate limit exceeded. Try again later.');
        } else {
          core.setFailed('Permission denied. Ensure the token has required scopes.');
        }
        break;
      case 404:
        core.setFailed('Repository not found or no access.');
        break;
      case 422:
        core.setFailed(`Validation failed: ${error.message}`);
        break;
      default:
        core.setFailed(`GitHub API error (${error.status}): ${error.message}`);
    }
  } else {
    throw error; // Re-throw unexpected errors
  }
}
```

## Input Validation

Validate inputs early and fail with clear messages:

```typescript
interface ActionInputs {
  token: string;
  labelName: string;
  maxItems: number;
}

function validateInputs(): ActionInputs {
  const token = core.getInput('github-token', { required: true });
  if (!token) {
    throw new Error('github-token is required');
  }

  const labelName = core.getInput('label-name', { required: true });
  if (!labelName.match(/^[a-zA-Z0-9-_]+$/)) {
    throw new Error(
      'label-name must contain only alphanumeric characters, hyphens, and underscores'
    );
  }

  const maxItemsRaw = core.getInput('max-items') || '100';
  const maxItems = parseInt(maxItemsRaw, 10);
  if (isNaN(maxItems) || maxItems < 1 || maxItems > 1000) {
    throw new Error('max-items must be a number between 1 and 1000');
  }

  return { token, labelName, maxItems };
}
```

## Context Validation

Ensure the action runs in the correct context:

```typescript
function validateContext(): { prNumber: number } {
  if (github.context.eventName !== 'pull_request') {
    throw new Error(
      `This action only supports pull_request events, got: ${github.context.eventName}`
    );
  }

  const prNumber = github.context.payload.pull_request?.number;
  if (!prNumber) {
    throw new Error('Could not determine pull request number from context');
  }

  return { prNumber };
}
```

## Graceful Degradation

When optional features fail, continue with a warning:

```typescript
async function run(): Promise<void> {
  try {
    // Core functionality
    const result = await performMainAction();
    core.setOutput('result', result);

    // Optional enhancement - don't fail if this errors
    try {
      await addOptionalMetadata(result);
    } catch (error) {
      core.warning(`Optional metadata failed: ${error}`);
      // Continue without failing
    }

    // Another optional feature
    try {
      await notifySlack(result);
    } catch (error) {
      core.warning(`Slack notification failed: ${error}`);
      // Continue without failing
    }
  } catch (error) {
    handleError(error);
  }
}
```

## Retries for Transient Errors

Retry operations that might fail due to network issues:

```typescript
async function withRetry<T>(
  operation: () => Promise<T>,
  maxAttempts = 3,
  delayMs = 1000
): Promise<T> {
  let lastError: Error | undefined;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      // Don't retry on client errors (4xx except 429)
      if (error instanceof RequestError) {
        if (error.status >= 400 && error.status < 500 && error.status !== 429) {
          throw error;
        }
      }

      if (attempt < maxAttempts) {
        core.warning(`Attempt ${attempt} failed, retrying in ${delayMs}ms...`);
        await new Promise((resolve) => setTimeout(resolve, delayMs * attempt));
      }
    }
  }

  throw lastError;
}

// Usage
const result = await withRetry(() => octokit.rest.issues.create({ owner, repo, title: 'Issue' }));
```

## Error Messages for Users

Write error messages that help users fix the problem:

```typescript
// Bad - doesn't help user
core.setFailed('Error occurred');

// Good - tells user what went wrong and how to fix
core.setFailed(
  'Failed to add label: Label "needs-review" does not exist. ' +
    'Create the label in your repository settings first.'
);

// Good - includes context for debugging
core.setFailed(
  `Failed to create issue in ${owner}/${repo}. ` +
    `Ensure the GITHUB_TOKEN has 'issues: write' permission.`
);
```

## Structured Error Information

For complex errors, provide structured information:

```typescript
interface ActionError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

function createError(
  code: string,
  message: string,
  details?: Record<string, unknown>
): ActionError {
  return { code, message, details };
}

function handleStructuredError(error: ActionError): void {
  core.error(`[${error.code}] ${error.message}`);
  if (error.details) {
    core.debug(`Error details: ${JSON.stringify(error.details, null, 2)}`);
  }
  core.setFailed(error.message);
}

// Usage
if (!prNumber) {
  handleStructuredError(
    createError('MISSING_CONTEXT', 'Pull request number not found in context', {
      eventName: github.context.eventName,
      hasPayload: !!github.context.payload,
    })
  );
}
```

## Cleanup on Failure

Ensure cleanup happens even when the action fails:

```typescript
async function run(): Promise<void> {
  let tempFile: string | undefined;

  try {
    tempFile = await createTempFile();
    await performAction(tempFile);
  } catch (error) {
    handleError(error);
  } finally {
    // Cleanup always runs
    if (tempFile) {
      try {
        (await Bun.file(tempFile).exists()) && (await unlink(tempFile));
      } catch {
        core.warning('Failed to cleanup temporary file');
      }
    }
  }
}
```

## Error Boundaries for Parallel Operations

When running multiple operations, collect all errors:

```typescript
async function processItems(items: string[]): Promise<void> {
  const results = await Promise.allSettled(items.map((item) => processItem(item)));

  const failures = results.filter((r): r is PromiseRejectedResult => r.status === 'rejected');

  if (failures.length > 0) {
    const errorMessages = failures.map((f) => f.reason?.message || 'Unknown error');
    core.setFailed(`${failures.length}/${items.length} items failed:\n${errorMessages.join('\n')}`);
  } else {
    core.info(`Successfully processed all ${items.length} items`);
  }
}
```
