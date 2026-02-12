---
description: Draft a customer response in Nick's voice using Slack mrkdwn. Use when replying to customers, teammates, or developer success threads.
---

# Customer Reply

Draft a response to a customer or teammate in Nick's voice.

## Voice Reference

@../../shared/voice.md

## Workflow

1. Read the customer's message carefully. Identify each distinct question or point they're making, in order.
2. For each point, determine:
   - Is this correct and needs no response? Skip it or confirm briefly ("Yep, you're correct").
   - Is this partially correct? Confirm what's right, correct only what's wrong.
   - Is this a question? Answer it directly.
   - Is this ambiguous? Ask a clarifying question. Frame it as "Assuming X the answer is Y" when possible.
3. Draft the response in Slack mrkdwn format.
4. Before finalizing, check:
   - Are there any em-dashes? Remove them.
   - Are there any "business-y" phrases? Remove them.
   - Are there unnecessary closers ("let me know if you have questions")? Remove them.
   - Is anything restated that the customer already said clearly? Remove it.
   - Are all links real and verified? Remove any you can't confirm.
5. Present the draft to Nick for review.
6. After approval, offer to copy to clipboard.

## Important

- Do NOT fabricate documentation URLs. If you're not certain a URL exists, either omit it or say "I'll need to find the exact link for this."
- Default to Slack mrkdwn unless Nick asks for GitHub Flavored Markdown.
- Keep responses as short as they can be while still being complete. If the answer is one sentence, the response is one sentence.
