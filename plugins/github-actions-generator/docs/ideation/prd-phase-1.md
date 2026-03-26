# PRD: GitHub Actions Generator Skill - Phase 1

**Contract**: ./contract.md
**Phase**: 1 of 3
**Focus**: Core scaffolding and action structure generation

## Phase Overview

Phase 1 establishes the foundational capability of the skill: scaffolding a new GitHub Action package within an existing Bun workspace monorepo. This phase delivers immediate value by automating the tedious setup process that developers currently do manually.

After this phase, developers can invoke the skill, describe their action, and receive a fully-structured action package with proper Bun Catalog integration, TypeScript configuration, Biome setup, and a skeleton action.yml. The action won't have implementation logic yet, but the structure will be correct and ready for development.

This phase is sequenced first because all subsequent phases (implementation, testing, documentation) depend on having a properly scaffolded action structure.

## User Stories

1. As a developer maintaining an actions monorepo, I want to scaffold a new action by describing what it does so that I don't have to manually create package.json, tsconfig, and boilerplate files
2. As a developer, I want new actions to automatically use Bun Catalog for dependencies so that dependency versions stay consistent across my monorepo
3. As a developer, I want the skill to ask whether a new dependency should be global or local so that I can make informed decisions about dependency scope
4. As a developer, I want generated actions to include Biome configuration so that formatting and linting are consistent from the start

## Functional Requirements

### Action Discovery & Context

- **FR-1.1**: Skill detects it's in a Bun workspace monorepo by checking for root package.json with workspaces field
- **FR-1.2**: Skill identifies the actions directory pattern (e.g., `packages/`, `actions/`) from existing structure
- **FR-1.3**: Skill reads root package.json to understand available Bun Catalog dependencies
- **FR-1.4**: Skill checks for .bun-create template and uses it if available

### Scaffolding Generation

- **FR-1.5**: Skill prompts for action name (kebab-case) and brief description
- **FR-1.6**: Skill generates package.json with Bun Catalog dependencies (`"@actions/core": "catalog:"`)
- **FR-1.7**: Skill generates tsconfig.json extending root config or with sensible defaults
- **FR-1.8**: Skill generates action.yml skeleton with name, description, inputs/outputs placeholders
- **FR-1.9**: Skill generates src/index.ts with basic action entrypoint structure
- **FR-1.10**: Skill generates biome.json or extends root Biome config

### Dependency Management

- **FR-1.11**: When user requests a new dependency, skill asks if it should be global (root package.json + catalog) or local (action package.json only)
- **FR-1.12**: If global, skill adds to root package.json and updates Bun Catalog, then uses `catalog:` in action
- **FR-1.13**: If local, skill adds dependency directly to action's package.json with pinned version

### Workspace Integration

- **FR-1.14**: Skill runs `bun install` after scaffolding to link the new package
- **FR-1.15**: Skill verifies TypeScript compilation succeeds
- **FR-1.16**: Skill verifies Biome check passes

## Non-Functional Requirements

- **NFR-1.1**: Scaffolding completes in under 30 seconds for typical action
- **NFR-1.2**: Generated code follows existing patterns in the repository when detectable
- **NFR-1.3**: All generated files use consistent formatting (Biome-compliant)
- **NFR-1.4**: Skill provides clear error messages if workspace structure is incompatible

## Dependencies

### Prerequisites

- Existing Bun workspace monorepo with package.json workspaces field
- Bun installed and available in PATH
- Root package.json with @actions/_ and @octokit/_ packages (or skill guides setup)

### Outputs for Next Phase

- Scaffolded action package at `{actions-dir}/{action-name}/`
- Valid package.json with Bun Catalog dependencies
- Compilable TypeScript entrypoint (src/index.ts)
- action.yml with structure ready for inputs/outputs definition
- Biome configuration in place

## Acceptance Criteria

- [ ] Skill detects Bun workspace and identifies actions directory
- [ ] New action package created with correct directory structure
- [ ] package.json uses `catalog:` for shared dependencies
- [ ] tsconfig.json properly configured for action compilation
- [ ] action.yml contains valid YAML with name and description
- [ ] src/index.ts compiles without TypeScript errors
- [ ] `bun install` succeeds and links the new package
- [ ] `biome check` passes on generated files
- [ ] Dependency scope question asked when adding new dependencies

## Open Questions

- Should the skill support customizing the actions directory path, or assume convention?
- Should generated tsconfig extend a root tsconfig or be standalone?
