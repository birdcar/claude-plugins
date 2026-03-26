# PRD: GitHub Actions Generator Skill - Phase 2

**Contract**: ./contract.md
**Phase**: 2 of 3
**Focus**: Action implementation and unit testing

## Phase Overview

Phase 2 enables the skill to help developers implement the actual action logic and write comprehensive unit tests. Building on the scaffolded structure from Phase 1, this phase adds the "brain" to the action—the TypeScript code that performs the action's purpose.

After this phase, developers can describe what their action should do, and the skill will help write the implementation using Octokit SDKs, @actions/core, and other appropriate libraries. The skill will also generate thorough unit tests using bun:test, covering happy paths, edge cases, and error conditions.

This phase is sequenced second because implementation requires the scaffolded structure, and testing requires implementation.

## User Stories

1. As a developer, I want to describe my action's behavior and have the skill help implement it so that I can focus on the "what" rather than the "how"
2. As a developer, I want the skill to use Octokit SDKs correctly for GitHub API interactions so that I don't have to learn the SDK's patterns from scratch
3. As a developer, I want comprehensive unit tests generated so that I have confidence the action works correctly
4. As a developer, I want the skill to handle @actions/core patterns (getInput, setOutput, setFailed) correctly so that my action integrates properly with GitHub Actions runtime

## Functional Requirements

### Implementation Assistance

- **FR-2.1**: Skill asks user to describe action's purpose and expected behavior
- **FR-2.2**: Skill generates TypeScript implementation using appropriate Octokit packages
- **FR-2.3**: Skill uses @actions/core for input/output handling (getInput, setOutput, setFailed)
- **FR-2.4**: Skill uses @actions/github for context access (github.context, getOctokit)
- **FR-2.5**: Skill prefers Bun runtime utilities over npm packages (Bun.file, bun:test, etc.)
- **FR-2.6**: Skill updates action.yml inputs/outputs based on implementation

### Code Quality

- **FR-2.7**: Generated code includes JSDoc comments for exported functions and types
- **FR-2.8**: Comments added only for complex, edge-case, or non-obvious code
- **FR-2.9**: Code follows TypeScript strict mode conventions
- **FR-2.10**: Error handling uses setFailed() for user-facing errors with clear messages

### Unit Testing

- **FR-2.11**: Skill generates test file at src/index.test.ts (or tests/ directory)
- **FR-2.12**: Tests use bun:test (describe, it, expect, mock)
- **FR-2.13**: Tests cover happy path scenarios with expected inputs
- **FR-2.14**: Tests cover edge cases (empty inputs, missing optional params)
- **FR-2.15**: Tests cover error conditions (API failures, invalid inputs)
- **FR-2.16**: Tests mock @actions/core and Octokit clients appropriately

### Iteration Support

- **FR-2.17**: Skill can iterate on existing implementation based on feedback
- **FR-2.18**: Skill can add new functionality to existing action
- **FR-2.19**: Skill updates tests when implementation changes

## Non-Functional Requirements

- **NFR-2.1**: Generated code compiles without TypeScript errors
- **NFR-2.2**: All generated tests pass on first run (given correct implementation)
- **NFR-2.3**: Code is readable without excessive abstraction
- **NFR-2.4**: Implementation follows patterns from existing actions in the repo when available

## Dependencies

### Prerequisites

- Phase 1 complete: scaffolded action structure exists
- action.yml with at least name and description
- Bun Catalog dependencies available (@octokit/_, @actions/_)

### Outputs for Next Phase

- Implemented action in src/index.ts
- Populated action.yml with all inputs/outputs and their descriptions
- Passing unit tests in src/index.test.ts
- TypeScript compiles to dist/index.js (or configured output)

## Acceptance Criteria

- [ ] Skill gathers action requirements through conversation
- [ ] Implementation uses @actions/core correctly (getInput, setOutput, setFailed)
- [ ] Implementation uses Octokit SDKs for GitHub API calls
- [ ] Bun runtime utilities used where appropriate (not external npm packages)
- [ ] JSDoc comments present on public API
- [ ] No unnecessary comments in straightforward code
- [ ] action.yml inputs/outputs match implementation
- [ ] Unit tests exist and cover happy path
- [ ] Unit tests cover at least 2 edge cases
- [ ] Unit tests cover at least 1 error case
- [ ] All tests pass with `bun test`
- [ ] TypeScript compiles without errors
- [ ] Biome check passes

## Open Questions

- None currently identified
