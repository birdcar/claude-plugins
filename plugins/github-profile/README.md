# github-profile

Generates a complete GitHub Profile README from your actual GitHub data — including the README itself, GitHub Actions workflows for dynamic content, and any SVG assets needed for dark/light mode support.

## What problem it solves

Setting up a GitHub profile README that looks good and stays current is a surprisingly manual process. You need to pick a layout, find the right shields.io badge URLs, wire up GitHub Actions for dynamic content (contribution snake, blog feeds, WakaTime stats, Spotify now-playing), handle dark/light mode with `<picture>` elements, and keep it all under a reasonable length. Most people either spend a weekend on it or give up and leave a two-line bio.

This plugin walks through that entire process in one session. It researches your actual GitHub data first — repos, languages, pinned projects — so nothing is fabricated, then generates everything based on your preferences.

## Installation

```bash
claude plugin install github-profile@birdcar-plugins
```

Requires the `gh` CLI for repository creation and data gathering.

## Usage

```
/generate-github-profile <username>
```

The command runs through five phases: context gathering (professional focus, which sections you want, style preference), research (a subagent fetches your real profile data via the GitHub API and GraphQL), generation (a second subagent produces the README, any Actions workflows, and optional SVG assets), an add-on menu for anything you want to layer on after the initial pass, and repo setup (creates or clones your `username/username` repo, deploys the files, and walks you through any secrets the Actions need).

You can also trigger it naturally — say "generate a GitHub profile README for myusername" and the skill picks it up.

## Sections you can include

About Me, GitHub Stats Cards, Tech Stack badges, Featured Projects, Blog Posts Feed (RSS), Spotify Now Playing, WakaTime Coding Stats, and Contribution Snake Animation. You pick during the context gathering phase. Dynamic sections (blog, Spotify, WakaTime, snake) get corresponding GitHub Actions workflows that keep content current.

## Style options

Four styles are available: Professional (waving header, muted grays and blues, `flat-square` badges, minimal animation), Creative (cylinder/slice headers, bold gradients, `for-the-badge` badges, typing SVG), Minimal (no header or a soft one, monochrome, `flat` badges, no animation), and Playful (venom/cylinder headers, bright and rainbow colors, `plastic` badges, multiple animations).

## What gets generated

The README uses shields.io badges and `<picture>` elements for dark/light mode where applicable. Dynamic content is powered by GitHub Actions — templates are included for blog RSS feeds, contribution snake, WakaTime stats, Spotify now-playing, and GitHub activity feeds. All secrets are templated as `${{ secrets.SECRET_NAME }}` — no hardcoded API keys.

Two subagents handle the work: `profile-researcher` (sonnet) gathers real GitHub data via API and GraphQL, then `profile-generator` (sonnet) produces the README, workflows, and assets from those findings.

## Honest trade-offs

The research phase adds time but exists for a reason — profile READMEs built on fabricated data look worse than no README at all. The generated README is capped at 300 lines to keep it scannable; if you select all eight sections with a large tech stack, some content will be condensed to fit.
