# Octokit Patterns

Patterns for GitHub API interactions using Octokit SDK.

## Getting Authenticated Client

```typescript
import * as core from '@actions/core';
import * as github from '@actions/github';

// Using GITHUB_TOKEN from action input
const token = core.getInput('github-token', { required: true });
const octokit = github.getOctokit(token);

// Access context
const { owner, repo } = github.context.repo;
const { eventName, payload, sha, ref } = github.context;
```

## Issues

### Create Issue

```typescript
const { data: issue } = await octokit.rest.issues.create({
  owner,
  repo,
  title: 'Issue title',
  body: 'Issue body with **markdown** support',
  labels: ['bug', 'high-priority'],
  assignees: ['username'],
  milestone: 1,
});

core.info(`Created issue #${issue.number}`);
core.setOutput('issue-number', issue.number);
core.setOutput('issue-url', issue.html_url);
```

### Add Comment

```typescript
const { data: comment } = await octokit.rest.issues.createComment({
  owner,
  repo,
  issue_number: issueNumber,
  body: 'Comment body with **markdown**',
});
```

### Add Labels

```typescript
await octokit.rest.issues.addLabels({
  owner,
  repo,
  issue_number: issueNumber,
  labels: ['needs-review', 'documentation'],
});
```

### List Issues

```typescript
// Simple list
const { data: issues } = await octokit.rest.issues.listForRepo({
  owner,
  repo,
  state: 'open',
  labels: 'bug',
  per_page: 100,
});

// With pagination (get all)
const allIssues = await octokit.paginate(octokit.rest.issues.listForRepo, {
  owner,
  repo,
  state: 'all',
  per_page: 100,
});
```

## Pull Requests

### Get PR from Context

```typescript
// For pull_request events
const pr = github.context.payload.pull_request;
if (!pr) {
  core.setFailed('This action only runs on pull_request events');
  return;
}

const prNumber = pr.number;
const prTitle = pr.title;
const prBody = pr.body;
const baseBranch = pr.base.ref;
const headBranch = pr.head.ref;
```

### Get PR Details

```typescript
const { data: pullRequest } = await octokit.rest.pulls.get({
  owner,
  repo,
  pull_number: prNumber,
});

core.info(`PR: ${pullRequest.title}`);
core.info(`State: ${pullRequest.state}`);
core.info(`Mergeable: ${pullRequest.mergeable}`);
```

### List PR Files

```typescript
const { data: files } = await octokit.rest.pulls.listFiles({
  owner,
  repo,
  pull_number: prNumber,
});

for (const file of files) {
  core.info(`${file.status}: ${file.filename}`);
  // file.status: 'added' | 'removed' | 'modified' | 'renamed' | 'copied' | 'changed' | 'unchanged'
}
```

### Create Review Comment

```typescript
await octokit.rest.pulls.createReviewComment({
  owner,
  repo,
  pull_number: prNumber,
  body: 'Comment on specific line',
  commit_id: github.context.sha,
  path: 'src/index.ts',
  line: 10,
});
```

### Request Reviewers

```typescript
await octokit.rest.pulls.requestReviewers({
  owner,
  repo,
  pull_number: prNumber,
  reviewers: ['username1', 'username2'],
  team_reviewers: ['team-slug'],
});
```

## Repository Operations

### Get File Contents

```typescript
const { data: file } = await octokit.rest.repos.getContent({
  owner,
  repo,
  path: 'path/to/file.ts',
  ref: 'main', // branch, tag, or commit SHA
});

// file.content is base64 encoded
if ('content' in file) {
  const content = Buffer.from(file.content, 'base64').toString('utf-8');
}
```

### Create or Update File

```typescript
// Get existing file SHA (required for updates)
let existingSha: string | undefined;
try {
  const { data: existing } = await octokit.rest.repos.getContent({
    owner,
    repo,
    path: 'path/to/file.ts',
  });
  if ('sha' in existing) {
    existingSha = existing.sha;
  }
} catch {
  // File doesn't exist, will create new
}

await octokit.rest.repos.createOrUpdateFileContents({
  owner,
  repo,
  path: 'path/to/file.ts',
  message: 'Commit message',
  content: Buffer.from(newContent).toString('base64'),
  sha: existingSha, // Required for updates, omit for new files
  branch: 'main',
});
```

### List Repository Topics

```typescript
const { data: topics } = await octokit.rest.repos.getAllTopics({
  owner,
  repo,
});
```

## Commits and Refs

### Get Commit

```typescript
const { data: commit } = await octokit.rest.repos.getCommit({
  owner,
  repo,
  ref: github.context.sha,
});

core.info(`Author: ${commit.commit.author?.name}`);
core.info(`Message: ${commit.commit.message}`);
```

### Compare Commits

```typescript
const { data: comparison } = await octokit.rest.repos.compareCommits({
  owner,
  repo,
  base: 'main',
  head: github.context.sha,
});

core.info(`${comparison.ahead_by} commits ahead`);
core.info(`${comparison.behind_by} commits behind`);
```

## GraphQL Queries

For complex queries, use GraphQL instead of REST:

```typescript
interface QueryResult {
  repository: {
    pullRequest: {
      title: string;
      reviews: {
        nodes: Array<{
          state: string;
          author: { login: string };
        }>;
      };
    };
  };
}

const { repository } = await octokit.graphql<QueryResult>(
  `
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $number) {
        title
        reviews(last: 10) {
          nodes {
            state
            author {
              login
            }
          }
        }
      }
    }
  }
`,
  {
    owner,
    repo,
    number: prNumber,
  }
);
```

## Pagination

```typescript
// Using paginate helper (recommended for large datasets)
const allIssues = await octokit.paginate(
  octokit.rest.issues.listForRepo,
  {
    owner,
    repo,
    per_page: 100,
  },
  (response) => response.data // Optional mapper
);

// Manual pagination
let page = 1;
const allItems: Issue[] = [];
while (true) {
  const { data: items } = await octokit.rest.issues.listForRepo({
    owner,
    repo,
    per_page: 100,
    page,
  });
  if (items.length === 0) break;
  allItems.push(...items);
  page++;
}
```

## Rate Limiting

```typescript
// Check rate limit
const { data: rateLimit } = await octokit.rest.rateLimit.get();
core.info(`Remaining: ${rateLimit.rate.remaining}/${rateLimit.rate.limit}`);
core.info(`Resets at: ${new Date(rateLimit.rate.reset * 1000)}`);

// Handle rate limiting in requests
try {
  await octokit.rest.issues.create({ ... });
} catch (error) {
  if (error instanceof RequestError && error.status === 403) {
    if (error.response?.headers['x-ratelimit-remaining'] === '0') {
      const resetTime = error.response?.headers['x-ratelimit-reset'];
      core.setFailed(`Rate limited. Resets at ${new Date(Number(resetTime) * 1000)}`);
    }
  }
}
```
