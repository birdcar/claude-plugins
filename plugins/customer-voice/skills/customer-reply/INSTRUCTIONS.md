---
description: Research and draft a customer response in Nick's voice using Slack mrkdwn. Use when replying to customers, teammates, or developer success threads.
---

# Customer Reply

Research and draft a response to a customer or teammate in Nick's voice.

## Voice Reference

@../../shared/voice.md

## Workflow

1. Read the customer's message carefully. Identify each distinct question or point they're making, in order.

2. For each point, determine:
   - Is this correct and needs no response? Skip it or confirm briefly ("Yep, you're correct").
   - Is this partially correct? Confirm what's right, correct only what's wrong.
   - Is this a question that needs research? Flag it for the research agent.
   - Is this ambiguous? Ask Nick a clarifying question before proceeding. Frame it as "Assuming X the answer is Y" when possible.

3. **Always invoke the `customer-researcher` agent** using the Task tool. Pass it the customer's message and any clarified context. The agent will search the codebase, verify docs, and return findings. Do NOT attempt research yourself; the agent handles compaction-safe parallel research.

4. Using the research findings, draft the response in Slack mrkdwn format.

5. Before finalizing, check:
   - Are there any em-dashes? Remove them.
   - Are there any "business-y" phrases? Remove them.
   - Are there unnecessary closers ("let me know if you have questions")? Remove them.
   - Is anything restated that the customer already said clearly? Remove it.
   - Are all links verified by the research agent? Remove any unverified links.

6. Present the draft to Nick for review.

7. After approval, offer to copy to clipboard.

## Important

- Do NOT fabricate documentation URLs. Only include links the research agent verified.
- Do NOT skip the research agent. Every reply needs verified sources and accurate technical detail.
- Default to Slack mrkdwn unless Nick asks for GitHub Flavored Markdown.
- Keep responses as short as they can be while still being complete. If the answer is one sentence, the response is one sentence.
