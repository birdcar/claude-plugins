---
name: forge-harness
description: >-
  Scaffolds an agentic harness into a target repository — AGENTS.md or CLAUDE.md,
  feature_list.json, progress.md, init.sh, and session-handoff.md. Detects the
  target's stack (Node, Python, Go, Rust, Java, .NET) and emits stack-appropriate
  verification commands. Use when the user asks to "scaffold a harness", "add
  AGENTS.md", "set up CLAUDE.md", "make this repo agent-ready", "create a feature
  tracker for this repo", "add session continuity", or "audit this repo's
  agent harness".
  Do NOT use for creating a Claude Code skill (use forge-skill instead) or for
  improving an existing skill (use improve-skill).
---

## Critical Rules

- ALWAYS use AskUserQuestion for decisions — never plain text questions
- ALWAYS use the bundled scripts (`scripts/create-harness.mjs`, `scripts/validate-harness.mjs`) when working on a local repo — they are deterministic and faster than hand-writing files
- ALWAYS confirm overwrites with the user before passing `--force` to `create-harness.mjs` — the script skips existing files by default for a reason
- ALWAYS read `${CLAUDE_PLUGIN_ROOT}/shared/agentic-subsystems.md` before scaffolding — the 5 subsystems (Instructions / State / Verification / Scope / Lifecycle) are the design framework
- The script bundles are pure Node built-ins — no npm install needed in the target repo
- Keep the harness MINIMAL on first scaffold — memory persistence, tool safety, multi-agent coordination are opt-ins, not defaults
- Generated files live in the TARGET REPO, not the plugin — `${CLAUDE_PLUGIN_ROOT}` is the source; `--target <path>` is the destination

## Step 1 — Confirm Target & Intent

Accept the brain dump from `$ARGUMENTS` or from the conversation context. Determine:

- **Target directory** — absolute path to the repo being harnessed. If unclear, use AskUserQuestion to ask.
- **Intent** — one of:
  - `create` — scaffold a new harness from scratch
  - `audit` — score an existing harness across the 5 subsystems and recommend improvements
  - `report` — produce a shareable HTML assessment

If intent is ambiguous, use AskUserQuestion to ask the user to pick one.

If the target directory already has `AGENTS.md` or `CLAUDE.md`, default to **audit** mode unless the user explicitly asked to create. Surprise overwrites are a `--force` event and require explicit consent.

## Step 2 — Detect Stack & Verify Capabilities

Spawn or invoke deterministic detection via Bash:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/create-harness.mjs --target <ABSOLUTE_PATH> --help
```

(This is a dry-run probe — the `--help` flag prints capabilities without writing.)

Then run actual detection (no flags = preview mode does not exist; the script writes by default, so we use AskUserQuestion before calling it):

For `create` intent, before running the script, show the user what will be generated:

> The harness scaffolder will write the following to `<TARGET>`:
>
> - `AGENTS.md` (or `CLAUDE.md` if --agent-file is set)
> - `feature_list.json` (5 placeholder features)
> - `progress.md`
> - `session-handoff.md`
> - `init.sh` (with detected verification commands)
>
> Existing files will be skipped unless `--force` is set.
>
> 1. Proceed
> 2. Use CLAUDE.md instead of AGENTS.md
> 3. Override package manager (npm, pnpm, yarn, bun)
> 4. Override verification commands manually
> 5. Cancel

## Step 3 — Create Harness (intent=create)

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/create-harness.mjs --target <ABSOLUTE_PATH> [--agent-file CLAUDE.md] [--package-manager npm|pnpm|yarn|bun] [--commands "cmd one,cmd two"]
```

After running, report:

- The detected stack (e.g., `typescript-react`)
- The verification commands that ended up in `init.sh`
- Which files were written vs skipped (existing)
- Next steps for the user: replace placeholder features in `feature_list.json` with real ones; run `./init.sh` from the target repo to verify baseline; commit the harness.

If overwriting is required, surface a discrete second prompt:

> File `<path>` already exists. Force overwrite?
>
> 1. Yes, overwrite this file
> 2. No, skip this file
> 3. Yes, overwrite ALL existing harness files (`--force`)

Never silently pass `--force` without explicit user approval.

## Step 4 — Audit Harness (intent=audit)

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/validate-harness.mjs --target <ABSOLUTE_PATH> --json
```

The script returns a JSON report with:

- `overall` score (0–100)
- `bottleneck` (which of the 5 subsystems scored lowest)
- Per-subsystem score (0–5) with individual check results

Present the result to the user. If overall < 70, recommend the first 2–3 changes that would lift the lowest-scoring subsystem. Do NOT claim the bottleneck is the _cause_ of any agent failure without evidence — say "candidate bottleneck" until confirmed by an actual agent session.

## Step 5 — Render HTML Report (intent=report)

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/validate-harness.mjs --target <ABSOLUTE_PATH> --html <TARGET>/harness-assessment.html
```

Or for the structural benchmark:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/run-benchmark.mjs --target <ABSOLUTE_PATH> --html <TARGET>/harness-benchmark.html
```

After writing the HTML, tell the user the absolute path so they can open it in a browser.

Be clear with the user: **this is a structural benchmark, not a behavioral one.** It confirms the harness is present and coherent. Real effectiveness still requires before/after agent-session testing on representative tasks.

## Step 6 — Recommend Next Steps

For every successful run, end with concrete next-step recommendations the user can copy-paste into their backlog:

- Replace placeholder features in `feature_list.json` with real project features
- Run `./init.sh` to verify the baseline before adding new scope
- Commit the harness with a descriptive message
- If the project will have multi-session work: confirm `session-handoff.md` is filled in at end of session
- If working with memory persistence: see `${CLAUDE_PLUGIN_ROOT}/shared/references/memory-persistence-pattern.md`
- If working with multi-agent coordination: see `${CLAUDE_PLUGIN_ROOT}/shared/references/multi-agent-pattern.md`

## Step 7 — Retrospective (Optional)

If the run revealed a recurring pattern (e.g., a stack the detector didn't classify correctly, a verification command that's wrong for the user's setup), append a note to `${CLAUDE_PLUGIN_ROOT}/shared/learnings.md` with the date and observation. Pattern accumulation drives future generator improvements.

## When to Read References

Load only the reference needed for the user's problem:

- Memory across sessions: [Memory Persistence](../../shared/references/memory-persistence-pattern.md)
- Reusable workflows as skills: [Skill Runtime](../../shared/references/) — see also the sibling `forge-skill`
- Permissions, tools, concurrency: [Tool Registry & Safety](../../shared/references/tool-registry-pattern.md)
- Context budget and progressive disclosure: [Context Engineering](../../shared/references/context-engineering-pattern.md)
- Delegation and parallel agents: [Multi-Agent Coordination](../../shared/references/multi-agent-pattern.md)
- Hooks, startup, long-running work: [Lifecycle & Bootstrap](../../shared/references/lifecycle-bootstrap-pattern.md)
- Non-obvious failure modes: [Gotchas](../../shared/references/gotchas.md)
- 5-subsystem framework: [Agentic Subsystems](../../shared/agentic-subsystems.md)

## Deliverable Checklist

For a usable minimal harness, the target project ends with:

- [ ] `AGENTS.md` or `CLAUDE.md` (Instructions subsystem)
- [ ] `feature_list.json` (State subsystem — feature tracker)
- [ ] `progress.md` (State subsystem — session continuity)
- [ ] `init.sh` (Verification subsystem)
- [ ] `session-handoff.md` for multi-session work (Lifecycle subsystem)
- [ ] Documented verification evidence pattern (recorded in `progress.md` or `feature_list.json`)

If you cannot create files (e.g., sandbox restrictions), provide exact file contents and the `node scripts/create-harness.mjs ...` command instead.
