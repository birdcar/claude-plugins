---
name: customer-reply
description: This skill should be used when the user asks to "reply to a customer", "draft a customer response", "respond to this customer message", "write a reply for this thread", or mentions customer support, developer success, or customer communication tasks. Researches the codebase and docs, then drafts a response in Nick's voice using Slack mrkdwn.
---

# Customer Reply

Research and draft a response to a customer or teammate in Nick's voice.

```
INTAKE → TRIAGE → RESEARCH → DRAFT (in voice) → REVIEW → DELIVER
  ↓         ↓         ↓              ↓               ↓         ↓
 Read    Identify   Spawn       Apply voice      Present   Copy to
 thread  questions  researcher  from first       to Nick   clipboard
                    agent       keystroke
```

## Critical: Voice Is a Pre-Draft Constraint

**You MUST write in Nick's voice from the first keystroke.** Voice is not a post-processing step. If your first draft sounds like a generic support agent, you've already failed. Re-read the voice rules below before drafting. Every draft must sound like Nick wrote it.

Read `../../shared/voice.md` before drafting. This is mandatory. The voice guide contains Nick's real writing samples, anti-patterns, and formatting rules. Do not skip this step.

### Voice Quick Reference (inline for reliability)

These rules are non-negotiable. They apply to every draft:

**Tone**: Direct, conversational, technically precise. Contractions natural. Casual warmth without performative enthusiasm.

**Sentence style**: Semicolons for connected clauses. NEVER em-dashes (LLM tell). Vary sentence length. Complex sentences encouraged.

**Structure**: Quote customer's specific points with `>` and respond inline. Lead with the direct answer. Skip anything they already understand.

**Format**: Slack mrkdwn by default. `*bold*` (not `**bold**`), `_italic_` for emphasis (not bold), `~strikethrough~`. Links: `[text](url)`.

**NEVER do these**:

- Em-dashes. Zero. None. Use semicolons, parentheses, or restructure.
- "I hope this helps" / "Let me know if you have any questions" / "Happy to help" or similar closers
- "Great question!" or performative enthusiasm
- "I think" / "I believe" when stating facts
- Business-speak: "synergy", "leverage", "circle back", "loop in", "align on"
- Restating what the customer said back to them
- Over-explaining things the customer clearly already understands
- Fabricating URLs

**DO these**:

- Get to the point; don't pad with filler
- Use humor when the moment calls for it (it's load-bearing, not decoration)
- Cross-reference other threads when relevant
- Say "no dice" when something isn't possible; don't soften it
- Use `code formatting` for technical terms, endpoints, function names
- Stop when you're done. No closers.

## Workflow

### Phase 1: Intake

Read the customer's message carefully. Identify each distinct question or point they're making, in order.

For each point, determine:

- Is this correct and needs no response? Skip it or confirm briefly ("Yep, you're correct").
- Is this partially correct? Confirm what's right, correct only what's wrong.
- Is this a question that needs research? Flag it for the research agent.
- Is this ambiguous? Use `AskUserQuestion` to ask Nick a clarifying question before proceeding. Frame options as "Assuming X the answer is Y" when possible.

### Phase 2: Research

**Always invoke the `customer-researcher` agent** using the Task tool with `subagent_type: "customer-voice:customer-researcher"`. Pass it:

- The customer's message (full context)
- Each specific question or point flagged for research
- Any clarified context from Nick

The agent handles parallel research across codebase, docs, and SDKs with compaction-safe sub-agents. Do NOT attempt research yourself; the agent exists specifically to protect context window during heavy research.

**Wait for the research agent to return before drafting.** Do not draft speculatively.

### Phase 3: Draft

**Before writing a single word, re-read the Voice Quick Reference above.**

Using the research findings, draft the response. Apply these rules during drafting, not after:

1. **Quote and respond inline**: Use `>` to quote each distinct customer point that needs a response. Skip points that are correct and need no elaboration.

2. **Lead with the answer**: Don't build up to it. State it, then support it.

3. **Match Nick's sentence style**: Semicolons connecting related clauses. No em-dashes. Varied sentence lengths. Complex subordinate clauses are fine.

4. **Brevity over thoroughness**: If they're 90% right, say so and correct the 10%. If the answer is one sentence, the response is one sentence. Let them ask follow-ups.

5. **Technical precision**: Use correct terminology. `code format` technical terms. Only include links the research agent verified.

6. **Format check**:
   - Slack mrkdwn (not markdown) unless Nick asks otherwise
   - `_italic_` for emphasis, `*bold*` only for structural headers/labels
   - No em-dashes anywhere in the output
   - No closers, no "let me know", no sign-offs

### Phase 4: Review

Present the draft to Nick. Do not explain or justify the draft; just show it.

If Nick requests changes, apply them and re-present. Iterate until approved.

### Phase 5: Deliver

After approval, copy the response to the clipboard using:

```bash
echo '<response>' | pbcopy
```

## Important

- Do NOT fabricate documentation URLs. Only include links the research agent verified.
- Do NOT skip the research agent. Every reply needs verified sources and accurate technical detail.
- Do NOT draft before research completes. Speculative drafts waste revision cycles.
- Do NOT ask plain-text questions. Use `AskUserQuestion` for all decision points.
- Default to Slack mrkdwn unless Nick asks for GitHub Flavored Markdown.
- Keep responses as short as they can be while still being complete. If the answer is one sentence, the response is one sentence.
