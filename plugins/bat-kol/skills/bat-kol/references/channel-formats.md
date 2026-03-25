# Channel Format Constraints

Default formatting rules for each built-in channel. These serve as fallback references when a user's channel config file is missing or incomplete.

## Slack

- **Markup**: mrkdwn (Slack's markdown variant)
  - Bold: `*text*`
  - Italic: `_text_`
  - Strikethrough: `~text~`
  - Code inline: `` `code` ``
  - Code block: ` ```code``` `
  - Blockquote: `> text`
  - Lists: `- item` or `1. item`
  - Links: `<url|display text>`
  - User mentions: `@name`
  - Channel mentions: `#channel`
- **Length**: No hard character limit, but messages over ~2000 chars lose readability. Prefer concise messages. Use threads for extended discussion.
- **Conventions**:
  - Lead with context or TL;DR for longer messages
  - Use emoji sparingly and purposefully (not decoratively)
  - Thread replies for follow-up, not new channel messages
  - Use bullet points over paragraphs for scanability
  - Link unfurling: Slack auto-previews URLs — avoid redundant descriptions of linked content
- **Default register**: `internal`

## Email

- **Markup**: Plain text primary, HTML optional
  - Plain text: use line breaks and indentation for structure
  - HTML: standard tags (`<p>`, `<strong>`, `<em>`, `<ul>`, `<li>`, `<a href>`, `<br>`)
  - Avoid complex HTML (tables, CSS) — email client rendering is inconsistent
- **Structure**:
  - Subject line: concise, action-oriented, no ALL CAPS
  - Greeting: match register formality ("Hi Name," vs "Dear Mr. Name,")
  - Body: front-load the key point or ask in the first paragraph
  - Closing: match register ("Best," vs "Regards," vs "Thanks,")
  - Signature: omit unless user specifies one
- **Length**: No hard limit, but respect the reader's time. Aim for 3-5 short paragraphs maximum for routine messages.
- **Conventions**:
  - One topic per email — if multiple topics, suggest separate emails
  - CC/BCC suggestions: include if context makes recipients obvious
  - Reply context: quote relevant portions when replying, not the entire thread
- **Default register**: `professional`

## Bluesky

- **Markup**: Plain text only (no markdown rendering)
  - Links are auto-detected
  - Mentions: `@handle.bsky.social`
  - Hashtags: `#tag`
- **Length**: 300 characters per post (hard limit, enforced by AT Protocol)
  - Thread splitting: for content exceeding 300 chars, split into a thread
  - Each thread post should be self-contained enough to make sense if seen alone
  - Number thread posts: (1/N), (2/N), etc. in the post text
- **Conventions**:
  - Casual-to-professional tone (platform norm)
  - Alt text for images (describe if suggesting image inclusion)
  - Hashtags: 1-3 maximum, placed at end of post
  - No engagement bait ("RT if you agree")
  - Thread openers should hook the reader — don't start with "Thread:"
- **Default register**: `social`

## GitHub

- **Markup**: GitHub Flavored Markdown (GFM)
  - Standard markdown plus: task lists (`- [ ]`), tables, strikethrough, autolinks
  - Syntax-highlighted code blocks: ` ```language `
  - Mentions: `@username`
  - Issue/PR refs: `#123`, `org/repo#123`
  - Commit refs: full SHA or abbreviated
- **Content types** (each has distinct conventions):
  - **PR description**: Summary of changes, motivation, testing notes. Use a structured format with sections.
  - **Issue**: Clear problem statement, reproduction steps, expected vs actual behavior. Use labels context.
  - **Commit message**: Conventional commits format (`type(scope): description`). Subject line under 72 chars. Body wraps at 72 chars.
  - **Code review comment**: Specific, actionable, reference line numbers. Distinguish blocking vs non-blocking feedback.
  - **Discussion/comment**: Context-aware, reference related issues/PRs.
- **Length**: No hard limit, but respect the reader. PR descriptions should be thorough; comments should be concise.
- **Conventions**:
  - Reference related issues with `Fixes #123` or `Relates to #456`
  - Use task lists for multi-part work
  - Code suggestions in review: use ` ```suggestion ` blocks
- **Default register**: `professional`

## Generic (Fallback)

- **Markup**: Plain text, standard markdown if the user wants formatting
- **Length**: No constraints — adapt to context
- **Conventions**: Follow the register's voice rules without channel-specific formatting
- **Default register**: `professional`
- Used for any custom channel that doesn't have a dedicated drafter agent
