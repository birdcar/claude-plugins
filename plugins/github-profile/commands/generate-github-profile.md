---
name: generate-github-profile
description: Generate a stunning GitHub Profile README with dynamic content and GitHub Actions
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, TodoWrite, WebFetch, WebSearch
argument-hint: [GitHub username]
---

This command is a thin entry point into the `github-profile:generate-github-profile` skill workflow.

## Entry Point

If `$ARGUMENTS` is provided, treat the first argument as the GitHub username.

If `$ARGUMENTS` is empty, the skill workflow will ask the user for their username via AskUserQuestion.

## Delegation

Follow the `github-profile:generate-github-profile` skill workflow exactly. That skill is the full orchestrator — this command only handles entry and hands off to it.

Do not duplicate the workflow logic here.
