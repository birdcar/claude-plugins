# Implementation Spec: GitHub Actions Generator Skill - Phase 1

**PRD**: ./prd-phase-1.md
**Estimated Effort**: M

## Technical Approach

This phase creates a Claude Code skill that scaffolds GitHub Actions within Bun workspace monorepos. The skill will be implemented as an INSTRUCTIONS.md file in the claude-plugins repository, following the existing skill patterns.

The skill uses conversation-driven context gathering: it reads the workspace structure, asks targeted questions about the new action, and generates files using Write/Edit tools. It leverages Bun's native capabilities and integrates with the existing .bun-create template if present.

Key technical decisions:

- Skill as INSTRUCTIONS.md (not a code-based skill) for simplicity and maintainability
- File generation via Claude's Write tool rather than external templating
- Workspace detection through package.json analysis
- Dependency management through direct package.json editing + Bun Catalog

## File Changes

### New Files

| File Path                                                                                   | Purpose                                   |
| ------------------------------------------------------------------------------------------- | ----------------------------------------- |
| `plugins/github-actions-generator/plugin.json`                                              | Plugin manifest defining the skill        |
| `plugins/github-actions-generator/package.json`                                             | Package metadata for the plugin           |
| `plugins/github-actions-generator/tsconfig.json`                                            | TypeScript config (standard plugin setup) |
| `plugins/github-actions-generator/skills/generate-action/INSTRUCTIONS.md`                   | Core skill instructions                   |
| `plugins/github-actions-generator/skills/generate-action/references/package-template.md`    | Template reference for package.json       |
| `plugins/github-actions-generator/skills/generate-action/references/action-yml-template.md` | Template reference for action.yml         |
| `plugins/github-actions-generator/skills/generate-action/references/tsconfig-template.md`   | Template reference for tsconfig.json      |
| `plugins/github-actions-generator/skills/generate-action/references/entrypoint-template.md` | Template reference for src/index.ts       |

### Modified Files

| File Path            | Changes                     |
| -------------------- | --------------------------- |
| Root `tsconfig.json` | Add reference to new plugin |

### Deleted Files

None.

## Implementation Details

### Plugin Structure

**Pattern to follow**: `plugins/essentials/` or similar existing plugin

**Overview**: Standard Claude Code plugin with a single skill for generating GitHub Actions.

```
plugins/github-actions-generator/
├── plugin.json
├── package.json
├── tsconfig.json
└── skills/
    └── generate-action/
        ├── INSTRUCTIONS.md
        └── references/
            ├── package-template.md
            ├── action-yml-template.md
            ├── tsconfig-template.md
            └── entrypoint-template.md
```

**plugin.json structure**:

```json
{
  "name": "github-actions-generator",
  "description": "Generate TypeScript GitHub Actions with Bun workspaces",
  "skills": ["skills/generate-action"]
}
```

**Implementation steps**:

1. Create plugin directory structure
2. Write plugin.json with skill reference
3. Write package.json with plugin metadata
4. Write tsconfig.json extending root config

### INSTRUCTIONS.md Skill

**Overview**: The core skill file that defines how Claude assists with action generation.

**Key sections**:

1. **Trigger Conditions**: When to invoke this skill
2. **Context Gathering**: How to detect workspace structure
3. **Conversation Flow**: Questions to ask the user
4. **File Generation**: Templates and generation instructions
5. **Validation**: Post-generation checks

**INSTRUCTIONS.md structure**:

```markdown
# Generate GitHub Action

Generate TypeScript GitHub Actions for Bun workspace monorepos.

## When to Use

Use this skill when the user wants to:

- Create a new GitHub Action
- Scaffold an action in their actions monorepo
- Add a new action to an existing Bun workspace

## Prerequisites

Before starting, verify:

1. Current directory is a Bun workspace (package.json with "workspaces")
2. @actions/core and @octokit/\* packages are in root package.json
3. Identify the actions directory pattern

## Workflow

### Step 1: Detect Workspace Structure

[Instructions for reading package.json, finding actions dir, etc.]

### Step 2: Gather Action Details

[Questions to ask: name, description, inputs, outputs]

### Step 3: Handle Dependencies

[Logic for global vs local dependencies]

### Step 4: Generate Files

[File generation order and templates]

### Step 5: Validate

[Commands to run for verification]
```

**Implementation steps**:

1. Write trigger conditions section
2. Write prerequisite checks
3. Write workspace detection instructions
4. Write conversation flow for gathering action details
5. Write dependency handling logic
6. Write file generation section with template references
7. Write validation section

### Reference Templates

**package-template.md**:

```markdown
# Package.json Template

Generate package.json for a new action:

\`\`\`json
{
"name": "@{scope}/{action-name}",
"version": "0.0.0",
"private": true,
"type": "module",
"main": "dist/index.js",
"scripts": {
"build": "bun build src/index.ts --outdir dist --target node",
"test": "bun test",
"lint": "biome check .",
"format": "biome format --write ."
},
"dependencies": {
"@actions/core": "catalog:",
"@actions/github": "catalog:",
"@octokit/rest": "catalog:"
},
"devDependencies": {
"@biomejs/biome": "catalog:",
"@types/bun": "catalog:"
}
}
\`\`\`

## Variables

- `{scope}`: Organization scope from root package.json or user input
- `{action-name}`: Kebab-case action name from user input
```

**action-yml-template.md**:

```markdown
# action.yml Template

\`\`\`yaml
name: '{Action Name}'
description: '{Action description}'
author: '{author}'

inputs:

# Add inputs based on user requirements

# example:

# description: 'Example input'

# required: false

# default: ''

outputs:

# Add outputs based on user requirements

# example:

# description: 'Example output'

runs:
using: 'node20'
main: 'dist/index.js'
\`\`\`
```

**tsconfig-template.md**:

```markdown
# tsconfig.json Template

\`\`\`json
{
"extends": "../../tsconfig.json",
"compilerOptions": {
"outDir": "dist",
"rootDir": "src",
"declaration": true
},
"include": ["src/**/*"],
"exclude": ["node_modules", "dist"]
}
\`\`\`

If no root tsconfig exists, use standalone config:
[Full standalone config]
```

**entrypoint-template.md**:

```markdown
# src/index.ts Template

\`\`\`typescript
import _ as core from '@actions/core';
import _ as github from '@actions/github';

async function run(): Promise<void> {
try {
// Get inputs
// const myInput = core.getInput('my-input');

    // Action logic here

    // Set outputs
    // core.setOutput('my-output', result);

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
```

**Implementation steps**:

1. Create references directory
2. Write each template file with clear variable placeholders
3. Include usage notes in each template

## Validation Commands

```bash
# After scaffolding, run:
cd {action-directory}
bun install
bun run build
biome check .
```

## Testing Requirements

### Manual Testing

- [ ] Create test Bun workspace monorepo with existing action
- [ ] Invoke skill and create new action
- [ ] Verify package.json uses catalog: for dependencies
- [ ] Verify tsconfig.json properly configured
- [ ] Verify action.yml has correct structure
- [ ] Verify src/index.ts compiles
- [ ] Verify bun install succeeds
- [ ] Verify biome check passes

## Error Handling

| Error Scenario                      | Handling Strategy                                   |
| ----------------------------------- | --------------------------------------------------- |
| Not a Bun workspace                 | Inform user, suggest creating workspace first       |
| Missing @actions/\* in root         | Guide user to add dependencies to root package.json |
| Actions directory not found         | Ask user for directory path or suggest creating one |
| Name collision with existing action | Warn user and ask for different name                |

## Open Items

- [ ] Determine if skill should auto-detect scope from root package.json
- [ ] Decide on biome.json handling (extend root vs standalone)
