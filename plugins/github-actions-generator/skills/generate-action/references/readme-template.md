# README Template

Template for generating README.md files for GitHub Actions.

## Template

````markdown
# {Action Name}

{Description from action.yml}

## Usage

```yaml
- uses: {owner}/{repo}/{action-path}@v{version}
  with:
    # Required inputs
    {input-name}: {example-value}
    # Optional inputs
    {optional-input}: {example-value} # default: {default}
```

## Inputs

| Name           | Description   | Required | Default       |
| -------------- | ------------- | -------- | ------------- |
| `{input-name}` | {description} | {yes/no} | {default/N/A} |

## Outputs

| Name            | Description   |
| --------------- | ------------- |
| `{output-name}` | {description} |

## Example Workflow

```yaml
name: Example using {Action Name}

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  example:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: {owner}/{repo}/{action-path}@v{version}
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          {other-inputs}
```

## Development

```bash
# Install dependencies
bun install

# Run tests
bun test

# Build
bun run build

# Lint
bun run lint
```

## License

{License from root repo or MIT}
````

## Template Variables

| Variable        | Source                         | Example                           |
| --------------- | ------------------------------ | --------------------------------- |
| `{Action Name}` | action.yml `name` field        | `Add Label`, `Create Issue`       |
| `{Description}` | action.yml `description` field | `Automatically add labels to PRs` |
| `{owner}`       | Git remote or user input       | `birdcar`, `workos`               |
| `{repo}`        | Git remote or user input       | `actions`, `se-tools`             |
| `{action-path}` | Relative path in monorepo      | `packages/add-label`              |
| `{version}`     | Latest git tag or user input   | `1.0.0`                           |
| `{input-name}`  | From action.yml inputs         | `label-name`, `github-token`      |
| `{output-name}` | From action.yml outputs        | `issue-number`, `result`          |

## Version Detection

To determine the version for README examples:

1. **Check git tags**:

   ```bash
   git describe --tags --abbrev=0
   ```

2. **For monorepos with prefixed tags**:

   ```bash
   git tag --list '{action-name}-v*' --sort=-version:refname | head -1
   ```

3. **If no tags exist**:
   - Ask user for intended first version
   - Suggest `v1.0.0` as starting point

4. **Never use**:
   - `@latest` (doesn't exist in GitHub Actions)
   - `@main` or `@master` (unstable)

## Generating Inputs Table

Read from action.yml and format:

```yaml
# action.yml
inputs:
  github-token:
    description: 'GitHub token for API access'
    required: false
    default: ${{ github.token }}
  label-name:
    description: 'Name of the label to add'
    required: true
```

Becomes:

| Name           | Description                 | Required | Default               |
| -------------- | --------------------------- | -------- | --------------------- |
| `github-token` | GitHub token for API access | No       | `${{ github.token }}` |
| `label-name`   | Name of the label to add    | Yes      | N/A                   |

## Generating Outputs Table

Read from action.yml:

```yaml
# action.yml
outputs:
  added:
    description: 'Whether the label was added'
  label-url:
    description: 'URL of the label in the repository'
```

Becomes:

| Name        | Description                        |
| ----------- | ---------------------------------- |
| `added`     | Whether the label was added        |
| `label-url` | URL of the label in the repository |

## License Detection

Check for license in order:

1. Root repository LICENSE file
2. Root package.json `license` field
3. Default to MIT if not found
