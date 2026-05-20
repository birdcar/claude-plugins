# Anti-Patterns

> Not ported. Restructured from skill-forge's prior flat anti-pattern list into the standard reference shape used by `shared/references/*-pattern.md`.

## Problem

Anti-patterns are the failure modes that make skills load but not work, or work but not trigger, or trigger but mislead. A flat checklist tells you _what_ to avoid; this document teaches _why_ each cluster of mistakes exists so a generator (or human author) can recognize new variants of the same failure.

This file is the canonical reference grepped by `agents/skill-validator.md` and consumed by `agents/skill-optimizer.md`. The validator scans for severity tags (`[CRITICAL]`, `[HIGH]`, `[MEDIUM]`, `[LOW]`) and reports matches. **Severity tags must be preserved verbatim** — they are load-bearing for the validator's grep.

## Golden Rules

These five rules collapse every cluster below into one mental model:

1. **Descriptions are trigger surfaces, not summaries.** Anything in the description has to help Claude decide _whether_ to fire. Anything that doesn't earn its place against that bar belongs in the body.
2. **Structure exists to enable progressive disclosure.** The skill body is hot context; references are warm; scripts are cold. Putting cold content in hot context degrades every other instruction.
3. **Agents and tools follow least-privilege.** Every additional tool, every loaded file, every forked subagent costs reliability. Justify each one against a concrete need.
4. **Specs and learnings are the memory of the skill.** When they drift or stay empty, the next improve run reasons from stale or absent context and silently regresses behavior.
5. **Secrets and PII never live in the repo.** Local config (`$XDG_CONFIG_HOME/{skill-name}/`) is the only correct home — `${CLAUDE_PLUGIN_ROOT}` is not private.

## Trade-offs

| Tension                                      | Benefit of one side                           | Cost of overcorrecting                                    |
| -------------------------------------------- | --------------------------------------------- | --------------------------------------------------------- |
| Description precision vs recall              | Tight triggers fire on the right queries      | Over-narrow descriptions miss synonymous requests         |
| Strict tool grants vs flexibility            | Least-privilege agents are auditable and safe | Over-restriction forces awkward workarounds in edge cases |
| Inline guidance vs progressive disclosure    | Inline content is always in context           | Inline bloat pushes past the 500-line effectiveness cliff |
| Mandate-style rules vs explained constraints | Short rules are easy to scan                  | Unexplained mandates get treated as emphasis, not law     |
| Spec-as-design vs spec-as-implementation     | Design intent stays relevant across refactors | Implementation-detail specs go stale on first edit        |
| Local config vs convenience                  | Secrets stay out of git history               | Setup requires an extra one-time step per machine         |

## Implementation Patterns

### Cluster 1: Description Anti-Patterns

**Problem.** The description is the only thing Claude sees when deciding whether to activate a skill. It is a trigger surface. Vague, first-person, overlapping, or trigger-less descriptions all produce the same failure: the skill loads, but it fires on the wrong queries — or never fires at all. Trigger rates below 30% almost always trace back to this cluster.

- **[CRITICAL] XML in frontmatter** — Angle brackets (`< >`) in any frontmatter value (`description`, `name`, `argument-hint`, custom fields). Frontmatter is injected directly into the system prompt; tags can break prompt structure or trigger security restrictions that prevent the skill from loading. Fix: strip all XML/HTML tags from frontmatter; if you need them in content, move into the body.
- **[CRITICAL] Description exceeds 1024 characters** — The value is silently truncated at 1024 chars. Truncation cuts the trigger phrases at the end, which are the most important part. Fix: trim to essential what/when/trigger; move detail into the body.
- **[HIGH] Vague description** — Abstract or generic terms without specifying what triggers it or when to use it. Yields trigger rates below 30%. Fix: apply the formula `[what] + [when] + [specific trigger phrases]`.
- **[HIGH] Overlapping descriptions** — Two or more skills activate on the same queries with no differentiation. Wrong skill fires ~50% of the time. Fix: add negative cases that explicitly exclude the other skill's domain.
- **[HIGH] First-person description** — `"I help you..."`, `"I process..."`. Treated as Claude self-referring, not as a skill spec, breaking discovery. Fix: write third-person.
- **[HIGH] No trigger phrases** — Description explains _what_ without _when_. Activation is inferred and inconsistent. Fix: add explicit `"Use when the user asks to..."` with concrete verbs.
- **[HIGH] ALL CAPS directives without rationale** — `NEVER X` / `ALWAYS Y` without a reason. Without rationale, ALL CAPS reads as emphasis, not as a hard constraint, especially when it conflicts with the user. Fix: `"Avoid X because [reason]"`.
- **[MEDIUM] No negative cases in description** — No `"Do NOT use for..."` clause despite similar skills existing. Ambiguous queries trigger the wrong skill. Fix: name what this skill does _not_ handle and which skill does.

**Right way (Implementation Pattern).** A well-formed description packs four moves into one paragraph: a third-person _what_, a `Use when…` trigger sentence with the verbs users actually say, a `Do NOT use for… — use {other-skill} instead` clause if a sibling exists, and zero XML, zero first-person, zero ALL CAPS. Stay under 1024 characters; everything else goes in the body.

```good
---
name: review-pr
description: Reviews pull requests for correctness, logic errors, and security
  issues. Use when the user asks to review a PR, audit a diff, or check a
  change before merge. Do NOT use for style or formatting feedback — use
  code-style for that. Do NOT use for writing PR descriptions — use
  pr-description for that.
---
```

### Cluster 2: Identity and Naming Anti-Patterns

**Problem.** Names, file paths, and metadata fields are the skill's identity in the registry. Get any of them wrong and the skill is either invisible (auto-discovery skips it), unaddressable (CLI can't find it), or undetectable as changed (`claude plugin update` sees no version delta). These are mechanical failures with mechanical fixes — but unlike the description cluster, they often hard-block deployment.

- **[CRITICAL] Non-kebab-case name** — Spaces, capitals, underscores, camelCase in the `name` field. Causes lookup failures, install errors, silent mismatches. Fix: lowercase + hyphens only.
- **[CRITICAL] Wrong file name** — Anything other than exactly `SKILL.md` (case-sensitive). Auto-discovery never registers the skill. Fix: rename to `SKILL.md`.
- **[CRITICAL] Reserved words in name** — `claude` or `anthropic` in the name. Fails validation. Fix: choose a descriptive name that doesn't reference the platform.
- **[CRITICAL] Missing frontmatter** — No `---` delimiters, or missing `name`/`description`. Claude falls back to the first paragraph as the description; identifier and metadata are lost. Fix: add a complete frontmatter block.
- **[LOW] Missing metadata fields** — Only `name` and `description`, no `version`, `author`, `tags`. Skill works but is undiscoverable in the marketplace and `claude plugin update` cannot detect changes. Fix: add `version` (semver), `author`, `tags`.
- **[LOW] No argument-hint** — Slash-command skill lacks `argument-hint`. Autocomplete shows no hint about what to type. Fix: add a short `argument-hint`.
- **[LOW] Versioned names** — `commit-v2`, `research-helper-v2`. Creates parallel registrations that stack instead of replace. Fix: keep a single name, use `version` metadata.

**Right way (Implementation Pattern).** Treat the filename, the directory name, and the `name` field as a single atomic identifier. They should all agree on the same kebab-case string, with no version suffix and no platform reserved word. Add `version`, `author`, and `tags` as standard metadata so the marketplace and update detection both work.

```good
# skills/process-data/SKILL.md
---
name: process-data
description: Processes structured data files. Use when the user asks to
  parse, convert, or validate CSV, JSON, or XML files.
version: 1.0.0
author: your-username
tags: [data, csv, json, transform]
argument-hint: <file-path>
---
```

### Cluster 3: Structural and Progressive-Disclosure Anti-Patterns

**Problem.** The skill body is hot context — every line competes for Claude's attention with every other line and with the rest of the conversation. Past ~500 lines, effectiveness degrades sharply; buried rules get deprioritized; deeply nested references aren't read at all. Structural anti-patterns all share one failure mode: instructions that exist on disk but don't actually steer behavior.

- **[HIGH] Buried constraints** — Non-negotiable rules appear after line 100. Recency and position bias deprioritize them, especially in long sessions. Fix: move all hard constraints into the first 100 lines, immediately after frontmatter.
- **[HIGH] Deeply nested references** — `SKILL.md → ref.md → details.md → …`. Claude often stops at the second level. Fix: flat reference structure — all referenced files link directly from `SKILL.md`.
- **[HIGH] SKILL.md over 500 lines** — Effectiveness drops; later instructions compete with earlier ones. Fix: progressive disclosure — core rules inline, edge cases and patterns linked from `shared/` or `references/`.
- **[MEDIUM] Inconsistent terminology** — `endpoint`/`URL`/`path`/`route` used interchangeably. Each term is treated as potentially distinct, causing subtle interpretation drift. Fix: pick one term per concept and use it throughout.
- **[MEDIUM] No examples** — Instructions but no input/output examples. Output format and structure vary across invocations. Fix: 2–3 concrete before/after or input/output examples.
- **[LOW] Verbose instructions** — Dense prose paragraphs where numbered steps, tables, or code blocks would be clearer. Steps get skipped or reordered. Fix: numbered lists for sequences, tables for options, code blocks for commands.

**Right way (Implementation Pattern).** Front-load the body with hard constraints, then context, then patterns; link to reference docs for anything that's reference material rather than load-bearing instruction. Aim for ≤300 lines of skill body, with `shared/` or `references/` carrying detail. Use numbered steps and tables to make structure explicit.

```good
# SKILL.md (120 lines)
## Rules
- Never write to files outside the project root.
- Always confirm before deleting.

## Workflow
1. Check `tsconfig.json`. Create one if missing.
2. Run `bun run typecheck`. Stop and report errors if it fails.
3. Run `bun run build`. Stop and report errors if it fails.

## References
- Patterns: [shared/patterns.md](./shared/patterns.md)
- Errors: [shared/errors.md](./shared/errors.md)
```

### Cluster 4: Agent, Tool, and Script Anti-Patterns

**Problem.** Every tool grant, every forked subagent, every script Claude is told to _read_ rather than _run_ has a cost: tokens, indeterminism, or surface area. This cluster is about least-privilege and about reserving LLM reasoning for actual decisions — not for mechanical execution that scripts can do deterministically.

- **[MEDIUM] context:fork on reference-only skills** — Skill uses `context: fork` but has no explicit task or deliverable. Subagent spawns, reads, has nothing to do, returns nothing. Fix: only use `context: fork` for skills with a clear task; reference-only skills use `context: include`.
- **[MEDIUM] Offering too many tool options without a default** — `"You can use Bash, Python, Node, or Deno"`. Claude picks arbitrarily, producing inconsistent behavior. Fix: name the preferred tool; list alternatives only as fallbacks with conditions.
- **[MEDIUM] Inline deterministic logic instead of scripts** — Fixed shell sequences, transformations, or validation steps written inline. Wastes LLM tokens on deterministic work; varies across runs as Claude paraphrases. Fix: move fixed logic to `scripts/`; have the skill invoke and react to output.
- **[MEDIUM] No error handling in scripts** — Commands or scripts without exit-code checks, error messages, or fallback behavior. Silent failures leave Claude in an ambiguous state. Fix: explicit error handling and explicit fallback instructions.
- **[MEDIUM] Loading scripts into context** — `"Read scripts/helper.py to understand the algorithm..."`. Burns tokens reading something Claude won't execute from context. Fix: tell Claude to _run_ the script; if it needs context, write a brief inline summary.
- **[MEDIUM] Windows-style paths** — Backslashes in path examples. Skills run primarily on macOS/Linux; backslashes break or confuse generated commands. Fix: forward slashes everywhere.
- **[MEDIUM] Time-sensitive information** — Hard-coded dates or version pins (`"as of v3.2..."`, `"if before August 2025..."`). Goes stale silently. Fix: relative references and runtime version checks.
- **[LOW] Assuming packages are installed** — `eslint src/` without checking the tool is available. Missing tool produces an error Claude recovers from incorrectly (global install instead of local, wrong version). Fix: check availability first; prefer project-local invocations.
- **[LOW] Magic numbers in scripts** — `TIMEOUT = 47`, `sleep 30` with no rationale. Future editors can't tell hard limit from arbitrary guess. Fix: comment the origin or reasoning for any non-obvious constant.

**Right way (Implementation Pattern).** Reserve the LLM for decisions; push deterministic work into scripts. For each tool reference, ask three questions: _Is this tool installed?_ _Is there a default I should name?_ _What happens if it fails?_ Each answer becomes one line in the skill — either a check, a default, or a fallback. For subagents, ask: _Does this task have a deliverable?_ If not, don't fork.

```good
# In SKILL.md
Run `bash ${CLAUDE_PLUGIN_ROOT}/scripts/lint-changed.sh`.
- If it exits non-zero, show the output and ask the user which errors to fix.
- The script handles the git diff + grep + lint loop deterministically.

# In scripts/lint-changed.sh
#!/usr/bin/env bash
set -euo pipefail
# TIMEOUT=47 — GitHub API rate limit window is ~47s under sustained load
...
```

### Cluster 5: Spec, Learnings, and Workflow Anti-Patterns

**Problem.** A skill's spec and learnings file are the persistent memory the next improve run reasons from. When the spec drifts, when learnings stay empty, or when a retrospective edits functional code instead of knowledge, future runs operate on stale or wrong context — and silently regress behavior. This cluster is about the integrity of the feedback loop.

- **[HIGH] Spec drift** — Actual skill structure has diverged from `docs/spec.md` without the spec being updated. Future improve runs propose changes against stale intent. Fix: update `docs/spec.md` on every modification (the improve pipeline does this automatically; manual edits bypass it).
- **[HIGH] Empty learnings file** — `docs/learnings.md` exists but only contains the header. Either retrospectives aren't running, or they aren't capturing anything — both signal a broken feedback loop. Fix: ensure retrospectives run after every forge/improve; if there's genuinely nothing to capture, write a note saying so rather than leaving it silently empty.
- **[HIGH] Retrospective modifies target code** — A retrospective agent edits `SKILL.md`, agents, commands, or hooks instead of only writing knowledge files (`docs/`, `references/`, `shared/`). Bypasses approval gates and can regress behavior silently. Fix: restrict retrospectives to `docs/learnings.md` and _proposed_ reference updates; functional changes go through `/improve-skill`.
- **[MEDIUM] Spec describes implementation instead of design intent** — `docs/contract.md` reads like an implementation guide (function names, line-by-line instructions) instead of a design doc (problem, goals, decisions, rationale). Goes stale on first refactor. Fix: keep contract focused on problem/goals/scope/decisions; component manifest and architecture go in `spec.md`; implementation lives in the artifacts themselves.

**Right way (Implementation Pattern).** Maintain a clear contract between the four artifacts: `docs/contract.md` captures _why_ (problem, goals, rationale); `docs/spec.md` captures _what_ (component manifest, architecture); the generated files capture _how_; `docs/learnings.md` captures _what we found out_. Retrospectives write only to the last one and propose edits to the middle two — never to the artifacts themselves.

```good
docs/contract.md    # design intent: problem, goals, decisions, rationale
docs/spec.md        # component manifest: what files exist and why
docs/learnings.md   # retrospective findings, append-only
SKILL.md, agents/, commands/, hooks/  # the actual implementation
```

### Cluster 6: Security and Privacy Anti-Patterns

**Problem.** Anything committed to git is committed forever. Secrets, PII, and machine-specific identifiers in skill files don't get cleaned up by `.gitignore` after the fact — they live in history. The fix is uniform: keep sensitive material in `$XDG_CONFIG_HOME/{skill-name}/` and source it through scripts that emit only what the skill needs.

- **[CRITICAL] Sensitive data stored in repository** — API keys, tokens, credentials, machine-specific paths, or PII tracked by git, including under `${CLAUDE_PLUGIN_ROOT}` or `references/`. Even in private repos this is permanent. Fix: store in `$XDG_CONFIG_HOME/{skill-name}/` (typically `~/.config/{skill-name}/`); source via scripts that emit only the values needed. See `${CLAUDE_PLUGIN_ROOT}/shared/local-config-pattern.md`.
- **[HIGH] PII in committed or persisted content** — Real names, emails, usernames in skill files, references, memory entries, or anything that hits git. Hard to scrub from history; may violate privacy expectations. Fix: anonymize to role-based handles (`@deploy-lead`, `@oncall`); store real identifiers in local config and source through scripts; memory entries describe roles, never individuals.

**Right way (Implementation Pattern).** Treat `${CLAUDE_PLUGIN_ROOT}` as public even if the repo is private. Use the local-config pattern uniformly: a `~/.config/{skill-name}/config.env` file with `chmod 600`, sourced through a script in the skill that outputs only the variable the skill needs at that moment.

```good
# ~/.config/my-skill/credentials.env (chmod 600, not in any repo)
COOLIFY_TOKEN=abc123
DEPLOY_LEAD_SLACK=jane.smith

# scripts/get-token.sh — sources from XDG_CONFIG_HOME, outputs only what's needed
#!/usr/bin/env bash
set -euo pipefail
source "${XDG_CONFIG_HOME:-$HOME/.config}/my-skill/credentials.env"
echo "$COOLIFY_TOKEN"
```

## Gotchas

Cross-cutting issues that don't sit neatly inside one cluster:

1. **Severity tags are load-bearing.** `agents/skill-validator.md` greps this file for `[CRITICAL]`, `[HIGH]`, `[MEDIUM]`, `[LOW]`. Changing the bracket format or dropping the tag from a line silently removes the rule from validation.
2. **Anti-patterns interact.** A vague description (Cluster 1) plus an empty learnings file (Cluster 5) compound: low trigger rate goes uncaptured, so the next improve run has no evidence to act on.
3. **"Fix the symptom" vs "fix the cause" diverge most in Cluster 3.** Trimming a 600-line `SKILL.md` to 499 lines clears the line-count check but doesn't fix the underlying problem — content that should be in references is still inline.
4. **`context: fork` is the most-misused agent directive.** It looks cheap (one frontmatter line) but spawns a full subagent. Combined with a reference-only skill (Cluster 4), it produces silent no-ops.
5. **Local config is one-time setup, not per-skill setup.** A shared `~/.config/{skill-name}/` layout means multiple skills in the same family can share credentials without re-prompting.

## Related Patterns

- [skill-anatomy.md](skill-anatomy.md) — the structural contract this file's Cluster 3 enforces
- [description-engineering.md](description-engineering.md) — deep dive on Cluster 1
- [quality-checklist.md](quality-checklist.md) — the validator's positive-form counterpart to this file
- [agentic-subsystems.md](agentic-subsystems.md) — Cluster 4 in pattern form (being written in parallel)
- [shared/references/multi-agent-pattern.md](references/multi-agent-pattern.md) — coordinator/fork/swarm trade-offs referenced by Cluster 4
- [shared/references/memory-persistence-pattern.md](references/memory-persistence-pattern.md) — the memory model Cluster 5 protects
- [shared/references/context-engineering-pattern.md](references/context-engineering-pattern.md) — progressive disclosure theory behind Cluster 3
- [shared/local-config-pattern.md](local-config-pattern.md) — the secret-handling pattern Cluster 6 mandates

<!-- TODO: No new anti-patterns were invented during restructure. If gaps are discovered in future passes, note them here with a proposed severity and cluster before adding to the body. -->
