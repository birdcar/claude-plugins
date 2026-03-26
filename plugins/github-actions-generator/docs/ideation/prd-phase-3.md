# PRD: GitHub Actions Generator Skill - Phase 3

**Contract**: ./contract.md
**Phase**: 3 of 3
**Focus**: Documentation, CI workflows, and release guidance

## Phase Overview

Phase 3 completes the action lifecycle by generating high-quality documentation and CI/release infrastructure. After Phase 2 delivers a working, tested action, this phase ensures the action is discoverable, usable, and maintainable.

After this phase, each action has a comprehensive README with real usage examples (using actual version tags, not "latest"), CI workflows that test the action on every PR, and guidance for publishing releases. The developer can confidently share the action with their team or the public.

This phase is sequenced last because documentation describes the implementation (requires Phase 2), and CI/release workflows test and publish the completed action.

## User Stories

1. As a developer, I want a README that shows exactly how to use my action so that consumers don't have to read the source code
2. As a developer, I want usage examples to show real version tags so that consumers use stable releases, not floating references
3. As a developer, I want CI workflows that test my action on every PR so that I catch regressions early
4. As a developer, I want guidance on releasing new versions so that I follow best practices for action versioning

## Functional Requirements

### README Generation

- **FR-3.1**: Skill generates README.md in action directory
- **FR-3.2**: README includes action name and clear description of what it does
- **FR-3.3**: README includes "Usage" section with complete `uses:` example
- **FR-3.4**: Usage example shows actual version tag (e.g., `@v1.0.0`), detected from git tags or prompted
- **FR-3.5**: README includes inputs table with name, description, required flag, and default
- **FR-3.6**: README includes outputs table with name and description
- **FR-3.7**: README includes example workflow snippet showing real-world usage
- **FR-3.8**: README includes "Development" section with build/test commands

### CI Workflow Generation

- **FR-3.9**: Skill generates .github/workflows/test-{action-name}.yml for action-specific CI
- **FR-3.10**: CI workflow runs on pull requests affecting the action's directory
- **FR-3.11**: CI workflow runs `bun install`, `bun run build`, `bun test` for the action
- **FR-3.12**: CI workflow runs `biome check` on the action's files
- **FR-3.13**: CI workflow uses appropriate Node.js version for GitHub Actions runtime

### Release Workflow Guidance

- **FR-3.14**: Skill provides guidance on semantic versioning for actions (v1, v1.0.0, etc.)
- **FR-3.15**: Skill can generate release workflow that builds and tags on release creation
- **FR-3.16**: Release workflow updates major version tag (v1 -> v1.2.0) for floating references
- **FR-3.17**: Skill explains action versioning best practices (major version tags, changelogs)

### Documentation Quality

- **FR-3.18**: README uses consistent markdown formatting
- **FR-3.19**: Code examples are syntax-highlighted with correct language tags
- **FR-3.20**: README includes badges for CI status if applicable

## Non-Functional Requirements

- **NFR-3.1**: README is readable and comprehensive but not verbose
- **NFR-3.2**: CI workflows follow GitHub Actions best practices
- **NFR-3.3**: Generated documentation matches tone/style of existing repo docs if present
- **NFR-3.4**: Version examples use actual tags from repository when available

## Dependencies

### Prerequisites

- Phase 2 complete: implemented action with passing tests
- action.yml fully populated with inputs/outputs
- Git repository with tagging capability (for version detection)

### Outputs for Next Phase

- README.md in action directory
- CI workflow at .github/workflows/test-{action-name}.yml
- Optional: release workflow at .github/workflows/release-{action-name}.yml
- Developer understands versioning and release process

## Acceptance Criteria

- [ ] README.md exists in action directory
- [ ] README includes accurate description matching action.yml
- [ ] README usage example uses real version tag (not "latest" or "@main")
- [ ] README inputs table matches action.yml inputs
- [ ] README outputs table matches action.yml outputs
- [ ] README includes working example workflow
- [ ] CI workflow file created at .github/workflows/
- [ ] CI workflow triggers on PR to action directory
- [ ] CI workflow runs install, build, test, and lint
- [ ] CI workflow passes when run manually
- [ ] Release guidance provided (versioning strategy documented or explained)

## Open Questions

- Should CI workflow be per-action or a monorepo-wide workflow with path filters?
- Should release workflow auto-update major version tags (v1 -> latest v1.x.x)?
