## CRITICAL — Blocks Deployment

### [CRITICAL] XML in frontmatter

**What**: Angle brackets (`< >`) used in any frontmatter field value, including `description`, `name`, `argument-hint`, or custom fields.
**Why it's bad**: Frontmatter is injected directly into the system prompt. XML/HTML tags can break prompt structure or trigger security restrictions that prevent the skill from loading.
**Fix**: Remove all XML and HTML tags from frontmatter. Move tagged content into the skill body if needed.

**Example**:

```bad
---
name: format-output
description: Formats output as <html> or <json> based on user request
---
```

```good
---
name: format-output
description: Formats output as HTML or JSON based on user request
---
```

---

### [CRITICAL] Non-kebab-case name

**What**: Skill `name` field contains spaces, capital letters, underscores, or other non-kebab characters.
**Why it's bad**: Skill names are used as identifiers in the registry and CLI. Non-kebab names cause lookup failures, install errors, or silent mismatches.
**Fix**: Use lowercase letters and hyphens only. No spaces, no underscores, no camelCase.

**Example**:

```bad
---
name: processData
---
```

```good
---
name: process-data
---
```

---

### [CRITICAL] Wrong file name

**What**: The skill file is named anything other than exactly `SKILL.md` — e.g., `SKILL.MD`, `Skill.md`, `skill.md`, `INSTRUCTIONS.md`, `README.md`.
**Why it's bad**: Auto-discovery scans for `SKILL.md` (case-sensitive). Any other name is invisible to the skill loader; the skill will never register.
**Fix**: Rename the file to exactly `SKILL.md`.

**Example**:

```bad
skills/my-skill/INSTRUCTIONS.md
skills/my-skill/skill.md
skills/my-skill/README.md
```

```good
skills/my-skill/SKILL.md
```

---

### [CRITICAL] Reserved words in name

**What**: Skill `name` contains the strings `claude` or `anthropic`.
**Why it's bad**: These are reserved identifiers. Skills using them will fail validation and cannot be installed.
**Fix**: Choose a descriptive name that doesn't reference the platform.

**Example**:

```bad
---
name: claude-helper
---
```

```good
---
name: context-helper
---
```

---

### [CRITICAL] Description exceeds 1024 characters

**What**: The `description` frontmatter field is longer than 1024 characters.
**Why it's bad**: The value is silently truncated at 1024 characters. Truncation typically cuts off the trigger phrases at the end, which are the most important part for activation. The skill appears to load but triggers unreliably or never.
**Fix**: Trim the description to its essential what/when/trigger content. Move detailed guidance into the skill body.

**Example**:

```bad
---
description: This skill handles data processing tasks including CSV parsing,
  JSON transformation, XML normalization, Excel import, database export,
  schema validation, type coercion, null handling, deduplication... [continues
  for 800 more characters] ...Use when the user asks to process data.
---
```

```good
---
description: Processes and transforms structured data files (CSV, JSON, XML).
  Use when the user asks to parse, convert, clean, or validate data files.
---
```

---

### [CRITICAL] Missing frontmatter

**What**: The `SKILL.md` file has no `---` delimiters at the top, or is missing required fields (`name`, `description`).
**Why it's bad**: Without frontmatter, Claude falls back to using the first paragraph of the file as the description. This loses the `name` identifier, the structured description, and any metadata — breaking discovery and triggering entirely.
**Fix**: Add a complete frontmatter block with at minimum `name` and `description`.

**Example**:

```bad
# My Skill

This skill helps process files. Run it when needed.
```

```good
---
name: process-files
description: Processes and organizes files by type. Use when the user asks
  to sort, rename, or categorize files in a directory.
---

# Process Files
```

---

## HIGH — Degrades Effectiveness

### [HIGH] Vague description

**What**: The `description` field describes the skill in abstract or generic terms without specifying what triggers it or when to use it.
**Why it's bad**: Claude uses the description to decide whether to activate the skill. Vague descriptions yield trigger rates below 30% — the skill exists but rarely fires.
**Fix**: Apply the formula: [what the skill does] + [when to use it] + [specific trigger phrases].

**Example**:

```bad
---
description: Helps with documents and development tasks.
---
```

```good
---
description: Generates and refines technical documentation (READMEs, API docs,
  changelogs). Use when the user asks to write docs, document a function,
  create a README, or update a changelog.
---
```

---

### [HIGH] Overlapping descriptions

**What**: Two or more skills have descriptions that activate on the same queries, with no differentiation between them.
**Why it's bad**: Claude picks one arbitrarily when descriptions overlap. The wrong skill fires ~50% of the time, and users can't predict behavior.
**Fix**: Add negative cases to each skill's description that explicitly exclude the other skill's domain.

**Example**:

```bad
# skill-a description
Analyzes code for issues. Use when the user asks to review code.

# skill-b description
Reviews code and suggests improvements. Use when the user asks to review code.
```

```good
# skill-a description
Analyzes code for bugs and security issues. Use when the user asks to find
bugs, audit security, or check for errors. Do NOT use for style or formatting
reviews — use code-style for those.

# skill-b description
Reviews code style, formatting, and readability. Use when the user asks to
improve code quality, check naming, or enforce style. Do NOT use for bug
finding — use code-audit for that.
```

---

### [HIGH] Buried constraints

**What**: Non-negotiable rules, safety guardrails, or critical constraints appear after line 100 of the skill body.
**Why it's bad**: Claude processes context with recency and position bias. Instructions deep in a long file get deprioritized, especially in long conversations where the skill content competes with accumulated context. Critical rules are ignored.
**Fix**: Move all non-negotiable constraints to the first 100 lines, immediately after the frontmatter.

**Example**:

```bad
# My Skill

[50 lines of context and background]
[30 lines of general guidance]
[20 lines of examples]

## Important Rules
- Never write to files outside the project root
- Always confirm before deleting
```

```good
# My Skill

## Rules
- Never write to files outside the project root
- Always confirm before deleting

## Context
[background and guidance follows]
```

---

### [HIGH] Deeply nested references

**What**: `SKILL.md` links to `reference.md`, which links to `details.md`, which links to further files — creating a chain of references more than one level deep.
**Why it's bad**: Claude may read the first reference but often stops at the second level. Content in deeply nested files is partially or entirely missed, causing silent gaps in behavior.
**Fix**: All referenced files should link directly from `SKILL.md`. A flat reference structure (SKILL.md → files) is reliable; chains (SKILL.md → ref → details) are not.

**Example**:

```bad
# SKILL.md
See [patterns](./shared/patterns.md) for output formats.

# shared/patterns.md
See [examples](./examples/full-examples.md) for complete examples.
```

```good
# SKILL.md
See [patterns](./shared/patterns.md) for output formats.
See [examples](./shared/examples.md) for complete examples.
```

---

### [HIGH] ALL CAPS directives without rationale

**What**: Instructions written as `NEVER do X` or `ALWAYS do Y` without explaining why.
**Why it's bad**: Language models respond better to explained constraints than unexplained mandates. Without rationale, ALL CAPS rules are more likely to be interpreted as emphasis than as hard constraints, especially when they conflict with user requests.
**Fix**: Replace mandate-style directives with explained constraints. "Avoid X because [reason]" is more reliably followed than "NEVER X".

**Example**:

```bad
NEVER run git push without user confirmation.
ALWAYS use bun instead of npm.
```

```good
Avoid running `git push` without user confirmation — pushing is irreversible
and the user may need to review what's being sent.

Use `bun` instead of `npm` because this project uses Bun workspaces; npm
will break workspace resolution.
```

---

### [HIGH] SKILL.md over 500 lines

**What**: The skill body exceeds 500 lines of content.
**Why it's bad**: Skill effectiveness degrades significantly past 500 lines. Later content is deprioritized, instructions compete with each other, and Claude's ability to follow all of them simultaneously drops sharply.
**Fix**: Move detailed content to files in a `shared/` or `references/` directory and link to them from SKILL.md. Use progressive disclosure — put the most important rules and patterns inline, and link to reference material for edge cases.

**Example**:

```bad
# SKILL.md (600 lines)
[inline patterns, examples, edge cases, full API reference, error codes...]
```

```good
# SKILL.md (120 lines, core instructions)
For output format patterns, see [patterns](./shared/patterns.md).
For error handling, see [errors](./shared/errors.md).
```

---

### [HIGH] First-person description

**What**: The `description` field is written in first person ("I help you...", "I process...").
**Why it's bad**: Claude uses the description to match user intent against skill capabilities. First-person descriptions are interpreted as Claude speaking, not as a skill specification — this causes discovery failures because the matching logic treats them as self-references, not as skill definitions.
**Fix**: Write in third person, describing what the skill does and when to use it.

**Example**:

```bad
---
description: I help you process files and organize directories.
---
```

```good
---
description: Processes files and organizes directories by type or date.
  Use when the user asks to sort, clean up, or reorganize project files.
---
```

---

### [HIGH] No trigger phrases

**What**: The description explains what the skill does but doesn't specify when to activate it — no "Use when..." or equivalent trigger guidance.
**Why it's bad**: Without trigger phrases, Claude has to infer activation from the skill's general description. This produces inconsistent triggering — the skill fires on some synonymous requests and not others, with no way to predict which.
**Fix**: Add explicit trigger phrases using "Use when the user asks to..." followed by specific verbs and phrases the skill should respond to.

**Example**:

```bad
---
description: Generates database migration files for schema changes.
---
```

```good
---
description: Generates database migration files for schema changes. Use when
  the user asks to create a migration, add a column, rename a table, or
  update a schema.
---
```

---

## MEDIUM — Reduces Quality

### [MEDIUM] Time-sensitive information

**What**: Instructions that reference specific dates, version numbers, or time windows — "if before August 2025...", "as of v3.2, use the new API".
**Why it's bad**: Skills are written once and used indefinitely. Hard-coded dates and version pins become incorrect silently, causing the skill to give stale guidance with no indication it's out of date.
**Fix**: Use relative references or version-check patterns instead of absolute dates and version numbers.

**Example**:

```bad
If you're on a version before August 2025, use the legacy endpoint.
As of v3.2, the `transform` method replaces `convert`.
```

```good
Check the project's package.json for the installed version. If using the
legacy API (v2.x), use the `convert` method. For v3.x and later, use
`transform`.
```

---

### [MEDIUM] Inconsistent terminology

**What**: The skill uses multiple terms interchangeably for the same concept — e.g., "endpoint", "URL", "path", and "route" all referring to the same thing.
**Why it's bad**: Claude treats each term as potentially distinct, leading to subtle interpretation drift. Instructions that say "check the endpoint" may not apply when the user says "check the URL" if the skill has used both inconsistently.
**Fix**: Pick one term for each concept and use it throughout the skill. Define it on first use if there's any ambiguity.

**Example**:

```bad
Check the endpoint before calling the URL. The route must match the path
defined in the API. Validate the URL format before hitting the endpoint.
```

```good
Check the endpoint before calling it. The endpoint must match the pattern
defined in the API. Validate the endpoint URL format before making requests.
```

---

### [MEDIUM] Windows-style paths

**What**: File path examples use backslashes (`\`) as separators.
**Why it's bad**: Skills run in Claude Code, which operates primarily on macOS and Linux. Backslash paths don't work on Unix systems and cause confusion when Claude generates commands or file references based on examples.
**Fix**: Use forward slashes in all path examples, regardless of the author's local OS.

**Example**:

```bad
Output goes to: dist\output\report.json
Run: scripts\build.bat
```

```good
Output goes to: dist/output/report.json
Run: scripts/build.sh
```

---

### [MEDIUM] No examples

**What**: The skill gives instructions for what to produce but includes no input/output examples showing what the result should look like.
**Why it's bad**: Without examples, Claude infers the output format from the instructions alone. Ambiguous instructions produce inconsistent output format, structure, and level of detail across invocations.
**Fix**: Add 2–3 concrete before/after or input/output examples that demonstrate the expected behavior.

**Example**:

```bad
Generate a commit message following conventional commits format based on
the staged changes.
```

```good
Generate a commit message following conventional commits format.

Example output for a bug fix:
```

fix(auth): handle expired token refresh race condition

Adds mutex lock around token refresh to prevent duplicate refresh calls
when multiple requests fire simultaneously on expiry.

```

Example output for a new feature:
```

feat(export): add CSV export for report data

```

```

---

### [MEDIUM] No error handling in scripts

**What**: The skill includes scripts or instructs Claude to run commands without handling failure cases — no exit code checks, no error messages, no fallback behavior.
**Why it's bad**: Silent failures leave Claude in an ambiguous state. Without explicit error handling, Claude may proceed as if a step succeeded when it failed, producing incorrect results or corrupting state.
**Fix**: Include explicit error handling — check exit codes, emit clear error messages, and specify what Claude should do when a step fails.

**Example**:

```bad
Run `bun install` then `bun run build`.
```

```good
Run `bun install`. If it fails, stop and report the error — do not proceed.
Run `bun run build`. If the build fails, show the error output and ask the
user whether to fix the errors or abort.
```

---

### [MEDIUM] Loading scripts into context

**What**: Instructions tell Claude to read a script file to understand what it does — "Read scripts/helper.py to understand the algorithm before proceeding."
**Why it's bad**: Loading a script into context consumes tokens and rarely adds value. Claude reads and summarizes the script but doesn't execute it — the information is available but unused. For large scripts, this crowds out more relevant context.
**Fix**: Tell Claude to run the script, not read it. If understanding the output requires knowing how it works, provide a brief inline summary instead of loading the full file.

**Example**:

```bad
Read `scripts/analyze.py` to understand what it checks, then apply
the same logic to the current file.
```

```good
Run `python scripts/analyze.py <target-file>` and use its output to
identify issues in the current file.
```

---

### [MEDIUM] Offering too many tool options without a default

**What**: The skill lists multiple equivalent tools for a task — "You can use Bash, Python, Node, or Deno for this" — without specifying which to prefer.
**Why it's bad**: When given no default, Claude picks arbitrarily based on context clues. This produces inconsistent behavior across invocations and projects, making the skill harder to predict and debug.
**Fix**: Specify the preferred tool explicitly. Mention alternatives only as fallbacks with a clear condition for when to use them.

**Example**:

```bad
You can use Bash, Python, Node.js, or Deno to run this transformation.
```

```good
Use Bash for this transformation. If the project has a `package.json`,
use `bun` (or `node`) instead to match the project's runtime.
```

---

### [MEDIUM] No negative cases in description

**What**: The skill's description has no "Do NOT use for..." clause, even though similar skills exist that handle related but distinct use cases.
**Why it's bad**: Without explicit exclusions, Claude can't distinguish between similar skills based on the description alone. Ambiguous queries trigger the wrong skill.
**Fix**: Add explicit negative cases that name what this skill does not handle and, where possible, name the skill that should handle those cases instead.

**Example**:

```bad
---
description: Reviews pull requests and provides feedback on code quality.
---
```

```good
---
description: Reviews pull requests for correctness, logic errors, and
  security issues. Use when the user asks to review a PR or audit a diff.
  Do NOT use for style or formatting feedback — use code-style for that.
  Do NOT use for writing PR descriptions — use pr-description for that.
---
```

---

### [MEDIUM] context:fork on reference-only skills

**What**: A skill uses `context: fork` but contains no explicit task instructions — it's purely a reference document or pattern guide.
**Why it's bad**: `context: fork` creates a subagent. A subagent needs a task to execute and results to return. A reference-only skill has no task, so the subagent spawns, reads the reference, has nothing to do, and returns nothing. The fork overhead is wasted and the skill produces no output.
**Fix**: Only use `context: fork` for skills that include explicit task instructions with a clear deliverable. Reference-only skills should use `context: include` or no context directive.

**Example**:

```bad
---
name: style-guide
context: fork
---
# Style Guide Reference

Use sentence case for headings. Prefer active voice...
```

```good
---
name: style-guide
context: include
---
# Style Guide Reference

Use sentence case for headings. Prefer active voice...
```

---

## LOW — Minor Improvements

### [LOW] Missing metadata fields

**What**: The frontmatter has only `name` and `description`, with no `version`, `author`, or `tags`.
**Why it's bad**: The skill is functional, but lacks the metadata needed for marketplace discoverability, update detection, and attribution. Without a `version`, `claude plugin update` can't detect when the skill has changed.
**Fix**: Add a metadata block with at minimum `version` (semver), `author`, and relevant `tags`.

**Example**:

```bad
---
name: process-data
description: Processes structured data files.
---
```

```good
---
name: process-data
description: Processes structured data files. Use when the user asks to
  parse, convert, or validate CSV, JSON, or XML files.
version: 1.0.0
author: your-username
tags: [data, csv, json, transform]
---
```

---

### [LOW] No argument-hint

**What**: A slash command skill has no `argument-hint` field in its frontmatter.
**Why it's bad**: When a user types the slash command in Claude Code, the autocomplete shows no hint about what argument to provide. Users have to guess or look up the skill documentation.
**Fix**: Add an `argument-hint` field with a short description of the expected argument.

**Example**:

```bad
---
name: summarize
description: Summarizes a file or URL.
---
```

```good
---
name: summarize
description: Summarizes a file or URL. Use when the user asks to summarize
  or get an overview of content.
argument-hint: <file-path or URL>
---
```

---

### [LOW] Verbose instructions

**What**: Instructions are written as dense prose paragraphs where structured formatting (numbered steps, tables, code blocks) would be clearer.
**Why it's bad**: Prose is harder for Claude to parse into discrete steps. Long paragraphs increase the chance of a step being skipped or reordered. Formatting signals structure explicitly.
**Fix**: Use numbered steps for sequences, tables for options or mappings, and code blocks for commands or templates.

**Example**:

```bad
First you should check if there's a tsconfig.json in the project root and
if there is you should use it, otherwise you should create one. Then run
the type checker and if it passes run the build and if that passes commit.
```

```good
1. Check for `tsconfig.json` in the project root. Create one if missing.
2. Run `bun run typecheck`. Stop and report errors if it fails.
3. Run `bun run build`. Stop and report errors if it fails.
4. Commit the changes.
```

---

### [LOW] Versioned names

**What**: The skill name includes a version suffix — `research-helper-v2`, `commit-v3`, `old-formatter`.
**Why it's bad**: Versioned names create parallel skill registrations. Users end up with multiple versions installed. The correct version to use is unclear. Updates don't replace the old version — they stack alongside it.
**Fix**: Use a single name and evolve the skill in place. Use the `version` metadata field to track changes. Remove old versions rather than naming around them.

**Example**:

```bad
---
name: commit-v2
---
```

```good
---
name: commit
version: 2.0.0
---
```

---

### [LOW] Assuming packages are installed

**What**: The skill instructs Claude to run a tool (e.g., `eslint`, `prettier`, `jq`) without checking whether it's available in the project.
**Why it's bad**: The tool may not be installed, may not be in PATH, or may need a project-local version. Running a missing tool produces an error that Claude has to recover from, and the recovery is usually wrong (installing globally when it should be local, or using the wrong version).
**Fix**: Include an availability check or installation step before using external tools. Prefer project-local invocations (e.g., `bun run lint` over `eslint`).

**Example**:

```bad
Run `eslint src/` to check for linting errors.
```

```good
Check if the project has a lint script: look for `"lint"` in `package.json`
scripts. If found, run `bun run lint`. If not, check if `eslint` is in
`devDependencies` and run `bun eslint src/`. If neither, report that no
linter is configured and ask the user how to proceed.
```

---

### [LOW] Magic numbers in scripts

**What**: Scripts or commands in the skill use unexplained numeric constants — `TIMEOUT = 47`, `MAX_RETRIES = 3`, `sleep 30`.
**Why it's bad**: Magic numbers give no indication of why that specific value was chosen. Claude and future editors can't tell whether the number is a hard limit, a performance tuning value, a protocol requirement, or an arbitrary guess. This makes adjustments risky.
**Fix**: Add a comment explaining the origin or reasoning for any non-obvious numeric constant.

**Example**:

```bad
TIMEOUT = 47
MAX_CHUNK_SIZE = 8192
sleep 30
```

```good
TIMEOUT = 47  # GitHub API rate limit window is ~47s under sustained load
MAX_CHUNK_SIZE = 8192  # Matches default TCP buffer size for streaming
sleep 30  # Wait for the dev server to finish its initial build (~25s typical)
```
