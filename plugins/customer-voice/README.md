> **Deprecated.** This plugin has been superseded by the `ghostwriter` plugin. It is no longer maintained. Install `ghostwriter` instead.

---

# customer-voice

Drafts pre-sales customer responses in a consistent voice, backed by parallel research across a local codebase and public docs.

## What it does

Given a customer message, the plugin runs research across the WorkOS monorepo, public docs at workos.com/docs, relevant SDK repos, and the WorkOS blog. Research runs in parallel via sub-agents so findings survive context compaction. Once research completes, it drafts a reply using voice rules encoded in `shared/voice.md` — direct, technically precise, Slack mrkdwn formatted, no em-dashes or corporate closers. The approved draft copies to your clipboard via `pbcopy`.

## Commands

`/customer-reply` — paste the customer message after invoking it. The command handles intake, triage, parallel research, draft, review loop, and clipboard copy.

## Agents

`customer-researcher` — spawned by `/customer-reply` to run parallel research sub-agents. Not intended for direct use.

## Setup

On first use, the researcher agent asks for two paths and saves them to `config.local.md` (gitignored):

- `workos_monorepo_path` — absolute path to your local WorkOS monorepo checkout
- `sdk_base_path` — absolute path to the directory containing local SDK checkouts

It won't prompt again after that.

## Voice

Voice rules live in `shared/voice.md`. The short version: direct, conversational, technically precise, Slack mrkdwn by default. No em-dashes, no corporate closers, no restating what the customer already said. Edit that file to refine the voice as new writing samples accumulate.

When research sources conflict, priority is: codebase > API reference > other docs > SDKs > blog. The researcher only returns URLs it verified — fabricated links are a hard failure.

## Install

This plugin is deprecated and not recommended for new installs. Use the `ghostwriter` plugin instead.
