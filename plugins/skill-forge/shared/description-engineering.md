# Description Engineering

## The Formula

```
[What it does] + [When to use it] + [Key trigger terms/conditions]
```

Every description MUST contain all three components. Missing any one degrades trigger accuracy.

## Third-Person Rule

Always write in third person. First person causes discovery failures.

**Good:**

```
Processes Excel files and generates reports. Use when analyzing .xlsx files or tabular data.
```

**Bad:**

```
I can help you process Excel files and create reports.
```

## Trigger Phrase Engineering

Include the exact phrases users would say:

- **Action verbs:** "create", "build", "generate", "fix", "optimize", "review"
- **Domain terms:** file types (.pdf, .xlsx), frameworks, tools, ecosystem-specific nouns
- **Quoted phrases** embedded in structure: `Use when the user asks to "deploy to production"`

Structure:

```
Use when the user asks to "{phrase1}", "{phrase2}", "{phrase3}", or {broader condition}.
```

## Negative Cases

Prevent activation conflicts with adjacent skills:

```
Do NOT use for general code review (use code-reviewer instead),
documentation writing, or when the user wants to modify existing
code that isn't a skill.
```

Include negative cases when:

- Other skills in the same plugin or project cover adjacent domains
- The skill name is generic enough to over-trigger
- Keywords overlap with common programming tasks

## Character Budget

- **Hard limit:** 1024 characters (silently truncated beyond this)
- **Effective target:** as short as possible while satisfying all three formula components
- **Context pressure:** all installed skill descriptions share ~16,000 chars at startup — more installed skills means more competition for attention
- Every character must earn its place

## Quality Tiers

| Tier      | Characteristics                                                | Trigger rate |
| --------- | -------------------------------------------------------------- | ------------ |
| Poor      | Vague ("Helps with documents"), no triggers, first-person      | <30%         |
| Adequate  | Specific what + when, but no negative cases                    | 50–70%       |
| Good      | Formula complete, trigger phrases, negative cases              | 70–85%       |
| Excellent | Precise triggers, tested negative cases, concise, domain terms | 90%+         |

## Optimization Loop

After writing, generate 20 trigger-eval queries:

**10 should-trigger:**

- 3 exact trigger phrase matches
- 3 paraphrased variants (same intent, different words)
- 2 edge cases (minimal context, ambiguous phrasing)
- 2 embedded in longer messages

**10 should-NOT-trigger:**

- 3 adjacent domain queries
- 3 general programming queries
- 2 keyword-overlap-wrong-context
- 2 queries for other known skills in the same plugin

Test in a fresh session. Target: 90%+ should-trigger, <10% should-not-trigger. Refine and retest until targets are met.

## Debugging

**Skill isn't triggering:**

1. Ask Claude: "When would you use the {name} skill?" — it will quote the description back
2. Check for activation conflicts: another skill's description may be catching the queries
3. Add more domain-specific trigger phrases
4. Verify description is under 1024 chars

**Skill over-triggers:**

1. Add explicit negative cases: "Do NOT use for..."
2. Narrow trigger phrases — replace generic verbs with specific ones
3. Consider `disable-model-invocation: true` if timing or side-effects matter

## Examples

Same hypothetical skill ("pdf-processor") across quality tiers:

**Poor:**

```
Helps with PDF files.
```

**Adequate:**

```
Processes PDF files — extracts text, fills forms, and merges documents.
```

**Good:**

```
Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs.
Use when working with .pdf files, document extraction, or form filling.
```

**Excellent:**

```
Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs.
Use when the user asks to "extract text from PDF", "fill a PDF form", "merge PDFs",
or works with .pdf files needing content extraction or manipulation.
Do NOT use for image processing, OCR on non-PDF formats, or general file conversion.
```
