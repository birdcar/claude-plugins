# Improve Skill

Iteratively improve an existing skill based on feedback, corrections, or identified issues.

## Trigger

Invoked via `/improve-skill {skill-name}` with optional feedback or context.

## Process

1. **Locate the Skill**
   - Search `plugins/*/skills/` for the specified skill name
   - Read the current INSTRUCTIONS.md
   - Understand the skill's purpose and current implementation

2. **Gather Context**
   If feedback is provided, analyze it. Otherwise, prompt for:
   - What's not working as expected?
   - What behavior should change?
   - Any specific scenarios that fail?

3. **Analyze Current Instructions**
   Evaluate the existing skill for:
   - Clarity of trigger documentation
   - Completeness of process steps
   - Coverage of edge cases
   - Robustness of rules
   - Quality of examples

4. **Propose Improvements**
   Based on feedback and analysis, suggest specific changes:
   - Additional process steps
   - New rules to handle edge cases
   - Better examples
   - Clarified language
   - Error handling additions

5. **Present Changes**
   Show a diff-style view of proposed changes:

   ```
   ## Proposed Changes to {skill-name}

   ### Addition: New Rule
   + - Handle edge case X by doing Y

   ### Modification: Process Step 3
   - 3. Old step description
   + 3. Improved step description with more detail

   ### Addition: Example
   + ## Example: Edge Case Handling
   + User: `/skill-name --edge-case`
   + Result: Handles it gracefully
   ```

6. **Apply or Iterate**
   - If user approves, apply the changes to INSTRUCTIONS.md
   - If user has more feedback, incorporate and re-propose
   - Track what was changed for potential rollback

## Improvement Categories

### Clarity Improvements

- Ambiguous language made specific
- Complex steps broken down
- Jargon explained or removed

### Robustness Improvements

- Edge cases handled
- Error scenarios addressed
- Fallback behaviors defined

### Completeness Improvements

- Missing steps added
- Examples included
- Rules expanded

### Consistency Improvements

- Alignment with other skills in the repo
- Standardized formatting
- Consistent terminology

## Example

User: `/improve-skill commit`

Analysis reveals:

- Missing guidance on merge commits
- No example for breaking changes
- Unclear on when to use which commit type

Proposed additions:

```markdown
### Merge Commits

When committing a merge, use the format:
`merge: integrate {branch} into {target}`

### Breaking Changes

For breaking changes, use:
`feat!: description` or `fix!: description`
Include a BREAKING CHANGE footer explaining the impact.

### Commit Type Selection

- `feat`: New functionality visible to users
- `fix`: Bug fix for existing functionality
- `docs`: Documentation only
- `chore`: Maintenance (deps, configs)
- `refactor`: Code change that doesn't alter behavior
- `ci`: CI/CD changes
```

## Important Rules

- Always show proposed changes before applying
- Preserve the skill's original intent - don't change what it does, just how well it does it
- Make incremental improvements - don't rewrite entire skills
- Reference specific feedback when explaining changes
- Keep backup of original in case rollback is needed
- After applying changes, run `bun run typecheck` and `bun run build` to verify
