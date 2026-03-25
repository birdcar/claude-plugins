# bat-kol — Contract

## Problem Statement

Writing for different platforms and audiences requires constant mental context-switching. A Slack update to your team uses different tone, formatting, and structure than a customer email or a Bluesky post. Developers spend time reformatting and re-voicing the same content for each destination, and the results are inconsistent — especially under time pressure. There's no way to encode personal voice rules, channel formatting constraints, and writing style preferences into a system that applies them automatically.

## Goals

1. Draft messages in the user's authentic voice for any supported channel, requiring only a topic or session context as input
2. Maintain independent voice registers (professional, internal, personal, social) that combine with channel format rules to produce contextually appropriate output
3. Support cascading configuration so voice profiles can be overridden per-project (like .gitignore resolution)
4. Train voice profiles from interviews, writing samples, and API/MCP scraping of existing communication history
5. Allow a global writing style framework (e.g. Stanley Fish, Strunk & White) as a base layer that registers can override

## Success Criteria

- [ ] Auto-triggers on natural language drafting requests ("draft an email", "respond in slack", "write a reply")
- [ ] `/train-voice` walks through guided interview, accepts samples, and scrapes channel APIs when available
- [ ] `/write-for <channel> [topic]` produces a draft — session summary if no topic, prompted draft if topic given
- [ ] `/add-channel <name>` creates a new channel definition with format rules and default register
- [ ] Cascading config resolution: project `.bat-kol/` overrides global `$XDG_CONFIG_HOME/bat-kol/`
- [ ] Each draft presented via AskUserQuestion with options: copy to clipboard, edit further, regenerate
- [ ] Channel drafter agents produce correctly formatted output (mrkdwn for Slack, HTML for email, char-limited for Bluesky, etc.)
- [ ] Voice profile files are human-readable and editable markdown

## Scope Boundaries

### In Scope

- Voice register system (professional, internal, personal, social) with training
- Channel format system (Slack, Email, Bluesky, GitHub, Generic) with custom channel support
- Cascading config resolution (env var → cwd → parent → XDG global)
- Global writing style framework with per-register override
- Training via interview + samples + API/MCP scraping (gh CLI, Bluesky AT Protocol, Slack MCP)
- Session summarization for a target channel
- Prompted drafting for a target channel

### Out of Scope

- Real-time channel monitoring or inbox management — that's ghostwriter's domain
- Voice cloning from other people's writing — only the user's own voice
- Customer support ticket handling — customer-reply handles that separately

### Future Considerations

- ~~MCP-based direct sending~~ — implemented in v0.8.0 via channel delivery config
- Voice evolution tracking (how voice profiles change over training sessions)
- Multi-user support (team voice profiles)
- Channel-specific templates (PR template, email signature)

## Design Decisions

| Decision                        | Choice                                       | Rationale                                                                                                                                         |
| ------------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Register ↔ Channel relationship | Independent dimensions                       | Channel handles formatting, register handles voice. Combined at draft time. User specifies both (channel has a default register for convenience). |
| Config location                 | `${XDG_CONFIG_HOME:-$HOME/.config}/bat-kol/` | Follows XDG convention, respects `$XDG_CONFIG_HOME` env var. Separate from `.claude/` to avoid coupling.                                          |
| Cascading override              | `.bat-kol/` directory convention             | Like `.gitignore` — walk up from cwd until found, fall back to global. Project context can override voice for specific repos.                     |
| Training approach               | Interview + samples + API scraping           | Interview captures intent, samples capture patterns, API scraping captures actual historical voice. Most thorough.                                |
| customer-reply coexistence      | Keep both, separate scope                    | Other users depend on customer-reply. User will deprecate locally after bat-kol is ready.                                                         |
| Custom channels                 | `/train-voice` + `/add-channel`              | `/train-voice` can add channels as part of training flow. `/add-channel` is a dedicated shortcut for just channel setup.                          |
| Draft delivery                  | AskUserQuestion with options + opt-in send   | Copy to clipboard, edit, regenerate, or send directly (if channel has delivery configured). Delivery always requires confirmation.                |
| Writing style layer             | Global + register override                   | One global framework by default. Any register can specify its own framework to override.                                                          |
