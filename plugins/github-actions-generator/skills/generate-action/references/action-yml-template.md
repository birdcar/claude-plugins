# action.yml Template

Generate `action.yml` metadata file for a GitHub Action.

## Template

```yaml
name: '{Action Name}'
description: '{One-line description of what the action does}'
author: '{author}'

branding:
  icon: '{icon}'
  color: '{color}'

inputs:
  github-token:
    description: 'GitHub token for API access'
    required: false
    default: ${{ github.token }}
  # Add more inputs based on action requirements

outputs:
  # Add outputs based on action requirements
  # example:
  #   description: 'Description of the output value'

runs:
  using: 'node20'
  main: 'dist/index.js'
```

## Variables

| Variable        | Source                         | Example                                                    |
| --------------- | ------------------------------ | ---------------------------------------------------------- |
| `{Action Name}` | Title case from user input     | `Add Label`, `Create Issue`                                |
| `{description}` | One-line description from user | `Automatically add labels to issues based on content`      |
| `{author}`      | From git config or user input  | `birdcar`                                                  |
| `{icon}`        | Feather icon name              | `tag`, `git-pull-request`, `file-text`                     |
| `{color}`       | Branding color                 | `blue`, `green`, `orange`, `purple`, `yellow`, `gray-dark` |

## Common Input Patterns

**GitHub Token** (most actions need this):

```yaml
inputs:
  github-token:
    description: 'GitHub token for API access'
    required: false
    default: ${{ github.token }}
```

**Required String Input**:

```yaml
inputs:
  label-name:
    description: 'Name of the label to add'
    required: true
```

**Optional Input with Default**:

```yaml
inputs:
  dry-run:
    description: 'Run without making changes'
    required: false
    default: 'false'
```

## Common Output Patterns

**Single Value**:

```yaml
outputs:
  issue-number:
    description: 'Number of the created issue'
```

**JSON Data**:

```yaml
outputs:
  result:
    description: 'JSON object containing operation results'
```

## Branding Icons

Common icons for GitHub Actions:

- `tag` - labeling, tagging
- `git-pull-request` - PR operations
- `git-commit` - commit operations
- `file-text` - file operations
- `check-circle` - validation, checks
- `alert-triangle` - warnings, notifications
- `message-square` - comments, messaging
- `refresh-cw` - sync, update operations

## Notes

- Always include `github-token` input even if not immediately needed
- Use `node20` runtime (current GitHub Actions standard)
- Outputs are set in code via `core.setOutput('name', value)`
- Keep descriptions concise but clear
