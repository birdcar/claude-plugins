---
name: generate-github-profile
description: >-
  Generates comprehensive GitHub Profile READMEs with dynamic content, GitHub
  Actions workflows, and SVG assets. Use when the user asks to "generate a
  GitHub profile README", "create a profile README", "update my GitHub profile",
  "make a cool GitHub README", or wants help with their username/username repo.
  Do NOT use for general README documentation, repository READMEs, or GitHub
  Actions unrelated to profile pages.
---

# Generate GitHub Profile README

## Critical Rules

- Use AskUserQuestion for all user decisions — plain text questions break the
  interaction model and prevent structured responses.
- Spawn profile-researcher agent before generating to gather real GitHub data —
  generating without research produces generic, inaccurate profiles.
- Never fabricate GitHub usernames, repo names, or API URLs — hallucinated URLs
  render as broken images and damage credibility.
- Create the username/username repo via `gh` CLI if it does not exist — this is
  the only repo GitHub renders as a profile README.
- Generate all artifacts to a staging area first, present for approval before
  writing to the final location — prevents overwriting existing profile content
  the user wants to keep.
- All GitHub stats card URLs must use the user's exact GitHub username — verify
  spelling from the research phase.

## Workflow

### Step 1: Context Gathering

If no GitHub username was provided as an argument, use AskUserQuestion to ask
for it.

Then conduct an interview using AskUserQuestion for each decision:

1. **Professional focus**: Ask about their work, tech stack, current role, and
   what they want to highlight.

2. **Sections**: Present section options via AskUserQuestion with multiSelect:
   - About Me (Recommended)
   - GitHub Stats Cards
   - Tech Stack / Skills Badges
   - Featured Projects
   - Blog Posts Feed
   - Spotify Now Playing
   - WakaTime Coding Stats
   - Contribution Snake Animation

3. **Style**: Ask about tone preference:
   - Professional (Recommended) — clean layout, muted colors
   - Creative — custom SVGs, animated headers, bold colors
   - Minimal — text-focused, few images
   - Playful — emoji-heavy, fun widgets, games

4. **Dynamic content**: Ask whether they want GitHub Actions for auto-updating
   sections (blog posts, stats, snake animation). Explain that this requires
   the repo to have Actions enabled and may need API tokens.

5. **Integrations**: If they selected Spotify, WakaTime, or blog posts, ask
   for the relevant details (RSS feed URL, etc.). Note that API keys will be
   added as repo secrets later.

### Step 2: Research

Spawn the profile-researcher agent with:

- The GitHub username
- The selected sections and style preferences

```
Agent tool:
  subagent_type: "github-profile:profile-researcher"
  description: "Research GitHub profile data"
  prompt: |
    Research the GitHub user "{username}".
    Gather: public repos, languages, stars, contribution data, pinned repos,
    bio, company, location, blog URL, existing profile README content.
    User wants these sections: {selected_sections}
    Style preference: {style}
```

Wait for research results before proceeding.

### Step 3: Generation

Spawn the profile-generator agent with research findings and user preferences:

```
Agent tool:
  subagent_type: "github-profile:profile-generator"
  description: "Generate profile README artifacts"
  prompt: |
    Generate a GitHub Profile README for "{username}".

    Research findings:
    {research_summary}

    User preferences:
    - Sections: {selected_sections}
    - Style: {style}
    - Dynamic content: {yes/no}
    - Integrations: {integration_details}

    Write all files to: {target_directory}

    Refer to these reference docs for component URLs and Actions templates:
    - ${CLAUDE_SKILL_DIR}/references/github-profile-patterns.md
    - ${CLAUDE_SKILL_DIR}/references/actions-templates.md
```

Summarize what was generated for the user, including a preview of the README
structure.

### Step 4: Add-on Menu

After initial generation, present an add-on menu via AskUserQuestion with
multiSelect. Only show add-ons that were not already included:

- Add Spotify Now Playing integration
- Add WakaTime coding stats
- Add blog post feed (RSS)
- Add contribution snake animation
- Add GitHub Activity feed
- Done — no more add-ons

For each selected add-on:

1. Ask for any required configuration (API keys, URLs) via AskUserQuestion
2. Generate the corresponding README section and Actions workflow
3. Insert the section into the existing README at the appropriate location

Loop until the user selects "Done".

### Step 5: Repo Setup and Delivery

1. Check if the username/username repo exists:

   ```bash
   gh repo view {username}/{username} --json name 2>/dev/null
   ```

2. If it does not exist, create it:

   ```bash
   gh repo create {username}/{username} --public --description "My GitHub Profile"
   ```

3. Clone or navigate to the repo:

   ```bash
   gh repo clone {username}/{username} /tmp/github-profile-{username}
   ```

4. Copy all generated files into the repo directory.

5. Present a setup summary to the user covering:
   - Files created (README.md, any workflows, any SVGs)
   - Secrets that need to be added to the repo (list each with instructions):
     - `WAKATIME_API_KEY` if WakaTime was selected
     - `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` if Spotify was selected
     - `GH_TOKEN` if any Actions need authenticated GitHub API access
   - How to enable Actions on the repo (Settings > Actions > General)
   - Cron schedule summary for any dynamic content workflows
   - Links to external service signup pages where needed

6. Ask the user via AskUserQuestion whether to commit and push now or leave
   the files for manual review.

## Examples

### Example 1: Minimal Professional Profile

User wants: About, Stats, Tech Stack badges. No dynamic content.

Generated README.md structure:

```markdown
![Header](https://capsule-render.vercel.app/api?type=waving&color=0:333333,100:666666&height=200&text=Jane%20Doe&...)

## About Me

Senior backend engineer at Acme Corp. Building distributed systems with Go and Rust.

## GitHub Stats

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github-readme-stats.vercel.app/api?username=janedoe&theme=dark&...">
  <img src="https://github-readme-stats.vercel.app/api?username=janedoe&...">
</picture>

## Tech Stack

![Go](https://img.shields.io/badge/Go-00ADD8?style=for-the-badge&logo=go&logoColor=white)
![Rust](https://img.shields.io/badge/Rust-000000?style=for-the-badge&logo=rust&logoColor=white)

![Footer](https://capsule-render.vercel.app/api?type=waving&color=0:333333,100:666666&height=100&section=footer)
```

No workflows generated. Single file delivery.

### Example 2: Full Dynamic Profile

User wants: About, Stats, Blog, Spotify, Snake, WakaTime. Creative style.

Generated files:

- `README.md` — full profile with comment delimiters for updatable sections
- `.github/workflows/blog-posts.yml` — daily blog post feed update
- `.github/workflows/snake.yml` — daily contribution snake generation
- `.github/workflows/waka-readme.yml` — daily WakaTime stats update

README includes `<!-- BLOG-POST-LIST:START -->` / `<!-- BLOG-POST-LIST:END -->`
comment pairs for each dynamic section. Actions workflows update content
between these markers.

Required secrets: `WAKATIME_API_KEY`, `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`

### Example 3: Playful Creative Profile

User wants: Animated typing header, stats with streak, contribution snake,
profile views counter. Playful style.

Generated README.md uses:

- readme-typing-svg for animated intro text
- github-readme-streak-stats for contribution streaks
- Platane/snk for contribution snake (via Actions)
- komarev profile view counter badge
- capsule-render with animation type "cylinder" and bright gradient colors

## Reference Documents

For detailed component catalogs and ready-to-use templates, see:

- [GitHub Profile Patterns](./references/github-profile-patterns.md) — all
  available README components with URLs, parameters, and configuration
- [Actions Templates](./references/actions-templates.md) — GitHub Actions
  workflow YAML templates for dynamic content
