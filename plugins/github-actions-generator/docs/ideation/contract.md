# GitHub Actions Generator Skill Contract

**Created**: 2026-01-22
**Confidence Score**: 95/100
**Status**: Draft

## Problem Statement

Developers maintaining GitHub Action monorepos (like `birdcar/actions` or `workos/se-tools`) need a streamlined, consistent way to generate new TypeScript-based GitHub Actions. Currently, creating a new action requires manually setting up the package structure, configuring dependencies through Bun Catalog, writing boilerplate code, setting up tests, creating documentation, and ensuring CI workflows are in place.

This manual process is error-prone, time-consuming, and leads to inconsistencies across actions within the same repository. Developers want to focus on the action's core logic, not the scaffolding and boilerplate.

The skill should support the full lifecycle: from initial scaffolding through implementation, testing, CI setup, and release guidance—all while leveraging Bun's native capabilities to minimize external dependencies.

## Goals

1. **Scaffold new GitHub Actions instantly** — Generate a complete action package structure using the repo's .bun-create template, properly integrated with Bun workspaces and Catalog
2. **Implement action logic collaboratively** — Help developers write the core action code based on their description, following TypeScript best practices with Octokit SDKs
3. **Generate comprehensive unit tests** — Create thorough bun:test suites covering happy paths, edge cases, and error conditions
4. **Produce quality documentation** — Generate README files with usage examples showing actual versioned releases (not "latest"), inputs/outputs tables, and clear descriptions
5. **Support release workflow** — Guide developers through CI workflow generation, versioning, and publishing best practices

## Success Criteria

- [ ] New action scaffolded via .bun-create integrates cleanly with existing Bun workspace
- [ ] Dependencies correctly use Bun Catalog (global deps in root, propagated via catalog)
- [ ] Generated TypeScript compiles without errors
- [ ] Biome linting/formatting passes with zero issues
- [ ] Unit tests pass and cover core functionality
- [ ] README includes working "uses" example with actual version tag
- [ ] action.yml properly defines all inputs/outputs with descriptions
- [ ] CI workflow runs tests and builds on PR
- [ ] No unnecessary dependencies—Bun runtime utilities used over npm packages where available

## Scope Boundaries

### In Scope

- JavaScript/TypeScript GitHub Actions (compiled to JS, Node.js runtime)
- Bun workspace + Catalog dependency management
- Full Octokit toolkit (@octokit/rest, @octokit/graphql, @octokit/core) + @actions/\* packages
- Biome for linting and formatting
- bun:test for unit testing
- README generation with versioned usage examples
- CI workflow generation (.github/workflows for testing actions)
- Release/publishing guidance and workflows
- JSDoc comments for public APIs
- Clarifying comments only for complex/edge-case code

### Out of Scope

- Composite (YAML-based) actions — JS/TS only
- Docker container actions — JS/TS only
- Integration tests or e2e tests via act — unit tests only
- Action marketplace publishing automation — guidance only
- Monorepo initial setup — assumes existing Bun workspace structure
- Non-GitHub CI systems — GitHub Actions workflows only

### Future Considerations

- Composite action support if needed later
- Integration test scaffolding with mocked GitHub API
- Automated changelog generation
- Action deprecation workflows

---

_This contract was generated from brain dump input. Review and approve before proceeding to PRD generation._
