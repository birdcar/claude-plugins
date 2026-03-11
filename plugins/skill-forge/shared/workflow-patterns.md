# Workflow Patterns Reference

## 1. Sequential Orchestration

**When to use**: Linear workflows where each step depends on the previous one. Most common pattern.

**Examples**: Build → test → deploy, extract → transform → load, intake → process → deliver

**SKILL.md structure**:

```markdown
## Workflow

1. Step 1: {action}
   - Validation: {check before proceeding}
2. Step 2: {action}
   - Depends on: Step 1 output
   - Validation: {check}
3. Step 3: {action}
   - Rollback: if this fails, {undo steps}
```

**Key characteristics**:

- Explicit step ordering with numbered steps
- Validation gates between steps
- Rollback instructions for failure cases
- Each step's output feeds the next step's input

**Primitives typically used**: TodoWrite (track progress), AskUserQuestion (approval gates), Edit/Write (file operations)

---

## 2. Multi-MCP Coordination

**When to use**: Skills that orchestrate multiple MCP servers or external services in sequence.

**Examples**: Fetch from Notion → process → write to GitHub, query BigQuery → analyze → post to Slack

**SKILL.md structure**:

```markdown
## Phase 1: Data Collection

- Use {MCP-Server-1} to {gather data}
- Store intermediate results in {format}

## Phase 2: Processing

- Transform data from Phase 1
- Apply {business logic}

## Phase 3: Output

- Use {MCP-Server-2} to {deliver results}
- Verify delivery succeeded
```

**Key characteristics**:

- Clear phase separation between services
- Intermediate data format specified explicitly
- Central error handling — if one service fails, don't partially complete
- MCP tool names fully qualified: `ServerName:tool_name`

**Primitives typically used**: MCP tools (fully qualified), Bash (for data transformation), AskUserQuestion (confirm before external actions)

---

## 3. Iterative Refinement

**When to use**: Creative or quality-sensitive tasks where the first output needs improvement. Draft → validate → refine loops.

**Examples**: Code generation with tests, document drafting with review, configuration tuning

**SKILL.md structure**:

```markdown
## Process

1. Generate initial draft
2. Validate against quality criteria:
   - [ ] Criterion 1
   - [ ] Criterion 2
   - [ ] Criterion 3
3. If any criteria fail:
   - Identify specific failures
   - Revise draft targeting failed criteria
   - Return to step 2
4. Termination: all criteria pass OR 3 iterations reached
5. Present final output for user approval
```

**Key characteristics**:

- Explicit quality criteria (checkable, not subjective)
- Maximum iteration count to prevent infinite loops
- Each iteration targets specific failures, not wholesale rewrites
- User approval as final gate

**Primitives typically used**: TodoWrite (track criteria), AskUserQuestion (approval after each round or final), Agent (subagent for validation)

---

## 4. Context-Aware Tool Selection

**When to use**: Skills that need to choose different tools/approaches based on the input context. Decision-tree workflows.

**Examples**: File processor that handles .pdf/.xlsx/.csv differently, deployment that varies by environment, formatter that detects language

**SKILL.md structure**:

```markdown
## Tool Selection

Analyze the input and select the appropriate approach:

| Input type    | Tool/Approach                         | Notes               |
| ------------- | ------------------------------------- | ------------------- |
| `.pdf` files  | `Bash(python scripts/pdf_extract.py)` | Requires pdfplumber |
| `.xlsx` files | `Bash(python scripts/xlsx_parse.py)`  | Uses openpyxl       |
| `.csv` files  | Direct Read + parse                   | No external deps    |
| Unknown       | AskUserQuestion to clarify            | Don't guess         |

## Process

1. Detect input type from file extension/content
2. Select tool per table above
3. If detection is ambiguous, ask user
4. Execute with selected tool
5. Normalize output to common format
```

**Key characteristics**:

- Decision table mapping inputs to tools
- Explicit fallback for unknown inputs (ask, don't guess)
- Transparency — tell the user which approach was selected and why
- Common output format regardless of input path

**Primitives typically used**: Glob/Grep (detect input type), AskUserQuestion (ambiguous cases), Bash (tool execution), multiple tool-specific paths

---

## 5. Domain-Specific Intelligence

**When to use**: Skills embedding specialized knowledge — compliance rules, style guides, API conventions, business logic. The skill IS the knowledge.

**Examples**: Security auditor, brand voice enforcer, API design reviewer, compliance checker

**SKILL.md structure**:

```markdown
## Domain Rules

### Rule 1: {name}

- Check: {what to look for}
- Pass criteria: {what correct looks like}
- Fail action: {what to do if violated}
- Severity: CRITICAL | HIGH | MEDIUM | LOW

### Rule 2: {name}

...

## Process

1. Collect relevant code/content
2. Apply each rule in order
3. Generate findings report with severity
4. For CRITICAL findings: block and require fix
5. For HIGH findings: warn and recommend
6. Present report with actionable fixes
```

**Key characteristics**:

- Rules are the core value — the SKILL.md embeds domain expertise
- Severity-based triage (not everything is equally important)
- Actionable findings (don't just flag problems, suggest fixes)
- Audit trail — record what was checked and what passed/failed

**Primitives typically used**: Read/Grep (collect evidence), TodoWrite (track findings), AskUserQuestion (present report), Agent (parallelize rule checking)

---

## Choosing a Pattern

| Signal in brain dump             | Likely pattern                              |
| -------------------------------- | ------------------------------------------- |
| "First do X, then Y, then Z"     | Sequential                                  |
| "Get data from A, send to B"     | Multi-MCP                                   |
| "Generate and refine until good" | Iterative refinement                        |
| "Handle different types of..."   | Context-aware                               |
| "Check/enforce/audit rules"      | Domain-specific                             |
| Mix of signals                   | Combine patterns — most real skills use 2-3 |

## Combining Patterns

Most production skills combine patterns:

- Sequential + Iterative: linear steps where one step uses a refinement loop
- Domain-specific + Sequential: apply rules in a specific order with dependencies
- Context-aware + Sequential: select approach first, then follow linear steps

When combining, the outer pattern determines the SKILL.md's top-level structure, and inner patterns appear within individual steps.
