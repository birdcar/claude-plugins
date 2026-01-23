# Testing Patterns

Unit testing patterns for GitHub Actions using bun:test.

## Basic Test Structure

```typescript
import { describe, it, expect, mock, beforeEach, afterEach, spyOn } from 'bun:test';

describe('action', () => {
  beforeEach(() => {
    // Reset mocks before each test
  });

  afterEach(() => {
    // Cleanup after each test
  });

  it('should succeed with valid inputs', async () => {
    // Arrange - set up test data and mocks
    // Act - call the function under test
    // Assert - verify the results
  });
});
```

## Mocking @actions/core

```typescript
import { mock, beforeEach } from 'bun:test';

// Create mock functions
const mockGetInput = mock((name: string, options?: { required?: boolean }) => {
  const inputs: Record<string, string> = {
    'github-token': 'fake-token',
    'label-name': 'bug',
  };
  const value = inputs[name] ?? '';
  if (options?.required && !value) {
    throw new Error(`Input required and not supplied: ${name}`);
  }
  return value;
});

const mockSetOutput = mock(() => {});
const mockSetFailed = mock(() => {});
const mockInfo = mock(() => {});
const mockWarning = mock(() => {});
const mockError = mock(() => {});
const mockDebug = mock(() => {});

// Mock the module
mock.module('@actions/core', () => ({
  getInput: mockGetInput,
  getBooleanInput: mock((name: string) => mockGetInput(name) === 'true'),
  getMultilineInput: mock((name: string) => mockGetInput(name).split('\n')),
  setOutput: mockSetOutput,
  setFailed: mockSetFailed,
  info: mockInfo,
  warning: mockWarning,
  error: mockError,
  debug: mockDebug,
  startGroup: mock(() => {}),
  endGroup: mock(() => {}),
  saveState: mock(() => {}),
  getState: mock(() => ''),
  exportVariable: mock(() => {}),
  setSecret: mock(() => {}),
}));

// Reset mocks between tests
beforeEach(() => {
  mockGetInput.mockClear();
  mockSetOutput.mockClear();
  mockSetFailed.mockClear();
  mockInfo.mockClear();
});
```

## Mocking @actions/github

```typescript
import { mock } from 'bun:test';

// Create mock Octokit client
const mockOctokit = {
  rest: {
    issues: {
      create: mock(() =>
        Promise.resolve({ data: { number: 1, html_url: 'https://github.com/...' } })
      ),
      createComment: mock(() => Promise.resolve({ data: { id: 123 } })),
      addLabels: mock(() => Promise.resolve({ data: [] })),
      listForRepo: mock(() => Promise.resolve({ data: [] })),
    },
    pulls: {
      get: mock(() => Promise.resolve({ data: { title: 'Test PR', mergeable: true } })),
      listFiles: mock(() => Promise.resolve({ data: [] })),
      requestReviewers: mock(() => Promise.resolve({ data: {} })),
    },
    repos: {
      getContent: mock(() => Promise.resolve({ data: { content: '', sha: 'abc123' } })),
      createOrUpdateFileContents: mock(() => Promise.resolve({ data: {} })),
    },
  },
  graphql: mock(() => Promise.resolve({})),
  paginate: mock(() => Promise.resolve([])),
};

// Mock context
const mockContext = {
  repo: { owner: 'test-owner', repo: 'test-repo' },
  eventName: 'pull_request',
  sha: 'abc123def456',
  ref: 'refs/heads/main',
  payload: {
    pull_request: {
      number: 123,
      title: 'Test PR',
      body: 'Test body',
      head: { ref: 'feature-branch' },
      base: { ref: 'main' },
    },
    issue: null,
    action: 'opened',
  },
};

// Mock the module
mock.module('@actions/github', () => ({
  context: mockContext,
  getOctokit: mock(() => mockOctokit),
}));

// Helper to change context for specific tests
function setContext(overrides: Partial<typeof mockContext>) {
  Object.assign(mockContext, overrides);
}

function setPayload(overrides: Partial<typeof mockContext.payload>) {
  Object.assign(mockContext.payload, overrides);
}
```

## Test Case Patterns

### Happy Path

```typescript
it('should create issue when triggered', async () => {
  // Arrange
  mockGetInput.mockImplementation((name) => {
    if (name === 'github-token') return 'fake-token';
    if (name === 'title') return 'New Issue';
    return '';
  });

  // Act
  await run();

  // Assert
  expect(mockOctokit.rest.issues.create).toHaveBeenCalledWith(
    expect.objectContaining({
      owner: 'test-owner',
      repo: 'test-repo',
      title: 'New Issue',
    })
  );
  expect(mockSetOutput).toHaveBeenCalledWith('issue-number', 1);
  expect(mockSetFailed).not.toHaveBeenCalled();
});
```

### Edge Cases

```typescript
it('should handle empty optional input', async () => {
  mockGetInput.mockImplementation((name) => {
    if (name === 'github-token') return 'fake-token';
    if (name === 'optional-input') return ''; // Empty
    return 'value';
  });

  await run();

  // Verify default behavior is used
  expect(mockOctokit.rest.issues.create).toHaveBeenCalledWith(
    expect.objectContaining({
      body: 'Default body', // Should use default
    })
  );
});

it('should handle missing PR context', async () => {
  // Set up context without PR
  setPayload({ pull_request: undefined, issue: { number: 456 } });
  setContext({ eventName: 'issues' });

  await run();

  // Verify appropriate behavior
  expect(mockSetFailed).toHaveBeenCalledWith(expect.stringContaining('pull_request'));
});

it('should handle pagination correctly', async () => {
  // Return multiple pages worth of data
  mockOctokit.paginate.mockResolvedValue([{ number: 1 }, { number: 2 }, { number: 3 }]);

  await run();

  expect(mockOctokit.paginate).toHaveBeenCalled();
});
```

### Error Cases

```typescript
it('should fail gracefully on API error', async () => {
  mockOctokit.rest.issues.create.mockRejectedValue(new Error('API rate limited'));

  await run();

  expect(mockSetFailed).toHaveBeenCalledWith('API rate limited');
});

it('should fail on missing required input', async () => {
  mockGetInput.mockImplementation((name, options) => {
    if (options?.required) {
      throw new Error(`Input required and not supplied: ${name}`);
    }
    return '';
  });

  await run();

  expect(mockSetFailed).toHaveBeenCalled();
});

it('should handle 404 errors appropriately', async () => {
  const notFoundError = new Error('Not Found');
  (notFoundError as any).status = 404;
  mockOctokit.rest.repos.getContent.mockRejectedValue(notFoundError);

  await run();

  expect(mockSetFailed).toHaveBeenCalledWith(expect.stringContaining('not found'));
});

it('should handle rate limiting', async () => {
  const rateLimitError = new Error('Rate limited');
  (rateLimitError as any).status = 403;
  mockOctokit.rest.issues.create.mockRejectedValue(rateLimitError);

  await run();

  expect(mockSetFailed).toHaveBeenCalledWith(expect.stringContaining('Rate limited'));
});
```

## Testing Async Operations

```typescript
it('should process items in parallel', async () => {
  const items = [1, 2, 3];

  await run();

  // Verify all operations were called
  expect(mockOctokit.rest.issues.addLabels).toHaveBeenCalledTimes(items.length);
});

it('should handle concurrent API calls', async () => {
  // Set up multiple API calls
  mockOctokit.rest.issues.listForRepo.mockResolvedValue({ data: [{ number: 1 }] });
  mockOctokit.rest.pulls.list.mockResolvedValue({ data: [{ number: 2 }] });

  await run();

  // Both should be called
  expect(mockOctokit.rest.issues.listForRepo).toHaveBeenCalled();
  expect(mockOctokit.rest.pulls.list).toHaveBeenCalled();
});
```

## Spying on Functions

```typescript
import { spyOn } from 'bun:test';

it('should log progress', async () => {
  const consoleSpy = spyOn(console, 'log');

  await run();

  expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('Processing'));

  consoleSpy.mockRestore();
});
```

## Testing with Different Event Types

```typescript
describe('on pull_request event', () => {
  beforeEach(() => {
    setContext({ eventName: 'pull_request' });
    setPayload({ pull_request: { number: 123 } });
  });

  it('should process PR', async () => {
    await run();
    expect(mockOctokit.rest.pulls.get).toHaveBeenCalled();
  });
});

describe('on issues event', () => {
  beforeEach(() => {
    setContext({ eventName: 'issues' });
    setPayload({ issue: { number: 456 }, pull_request: undefined });
  });

  it('should process issue', async () => {
    await run();
    expect(mockOctokit.rest.issues.get).toHaveBeenCalled();
  });
});
```

## Test File Organization

```
src/
├── index.ts              # Main action entry point
├── index.test.ts         # Tests for main entry
├── utils.ts              # Utility functions
├── utils.test.ts         # Tests for utilities
└── __mocks__/            # Optional: shared mock factories
    ├── core.ts
    └── github.ts
```
