# github-profile

Generates a complete GitHub Profile README from your actual GitHub data — including the README itself, GitHub Actions workflows for dynamic content, and any SVG assets needed for dark/light mode support.

## What problem it solves

Setting up a GitHub profile README that looks good and stays current is a surprisingly manual process. You need to pick a layout, find the right shields.io badge URLs, wire up GitHub Actions for dynamic content (contribution snake, blog feeds, WakaTime stats, Spotify now-playing), handle dark/light mode with `<picture>` elements, and keep it all under a reasonable length. Most people either spend a weekend on it or give up and leave a two-line bio.

This plugin walks through that entire process in one session. It researches your actual GitHub data first — repos, languages, pinned projects — so nothing is fabricated, then generates everything based on your preferences.

## Installation

```bash
/plugin marketplace add birdcar/claude-plugins
/plugin install github-profile@birdcar
```

Requires the `gh` CLI for repository creation and data gathering.

## Usage

```
/generate-github-profile <username>
```

The command runs through five phases:

1. **Context gathering** — asks about your professional focus, tech stack, which sections you want (About Me, Stats, Tech Stack, Projects, Blog, Spotify, WakaTime, Snake), and your preferred style
2. **Research** — a subagent fetches your real profile data, top repos, pinned repos via GraphQL, and language distribution
3. **Generation** — a second subagent produces the README (capped at 300 lines), any Actions workflows, and optional SVG assets
4. **Add-ons** — offers additional sections if you want to layer more on
5. **Repo setup** — creates or clones your `username/username` repo, deploys the files, and walks you through any secrets the Actions need

## Style templates

You pick one of four styles during context gathering:

- **Professional** — waving header, muted grays and blues, `flat-square` badges, minimal animation
- **Creative** — cylinder/slice headers, bold gradients, `for-the-badge` badges, typing SVG
- **Minimal** — no header or a soft one, monochrome palette, `flat` badges, no animation
- **Playful** — venom/cylinder headers, bright and rainbow colors, `plastic` badges, multiple animations

## What gets generated

The README uses 150+ technology badges from shields.io and `<picture>` elements for dark/light mode where applicable. Dynamic content is powered by GitHub Actions workflows — the plugin includes templates for blog RSS feeds, contribution snake animation, WakaTime coding stats, Spotify now-playing, and GitHub activity feeds. All secrets are templated (no hardcoded API keys).

## Agents

| Agent                | Model  | Role                                                    |
| -------------------- | ------ | ------------------------------------------------------- |
| `profile-researcher` | sonnet | Gathers real GitHub data via API and GraphQL            |
| `profile-generator`  | sonnet | Produces README, workflows, and SVG assets from research |

## Honest trade-offs

The research phase adds time but exists for a reason — profile READMEs built on fabricated data look worse than no README at all. The 300-line cap on the generated README keeps things scannable, but if you select all eight sections with a large tech stack, some content will be condensed to fit.
