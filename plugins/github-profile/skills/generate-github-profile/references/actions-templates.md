# GitHub Actions Workflow Templates

## Common Patterns

### Bot Commit Identity

All workflows that commit back to the repo should use this identity:

```yaml
env:
  GIT_AUTHOR_NAME: github-actions[bot]
  GIT_AUTHOR_EMAIL: 41898282+github-actions[bot]@users.noreply.github.com
  GIT_COMMITTER_NAME: github-actions[bot]
  GIT_COMMITTER_EMAIL: 41898282+github-actions[bot]@users.noreply.github.com
```

### Avoid Empty Commits

Always check for changes before committing:

```yaml
- name: Commit changes
  run: |
    git add -A
    git diff --staged --quiet || git commit -m "chore: update {section}"
    git push
```

### Required Permissions

For workflows that commit to the repo:

```yaml
permissions:
  contents: write
```

---

## Blog Post Feed Updater

Updates a section of the README with latest blog posts from an RSS feed.

```yaml
name: Blog Posts
on:
  schedule:
    - cron: '0 6 * * *' # Daily at 06:00 UTC
  workflow_dispatch:

permissions:
  contents: write

jobs:
  update-readme:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: gautamkrishnar/blog-post-workflow@v1
        with:
          feed_list: '{RSS_FEED_URL}'
          max_post_count: 5
          readme_path: ./README.md
          comment_tag_name: BLOG-POST-LIST
          commit_message: 'chore: update blog posts'
          committer_username: github-actions[bot]
          committer_email: 41898282+github-actions[bot]@users.noreply.github.com
```

README markers:

```markdown
### Latest Blog Posts

<!-- BLOG-POST-LIST:START -->
<!-- BLOG-POST-LIST:END -->
```

---

## Contribution Snake Generator

Generates an SVG animation of contributions being eaten by a snake.

```yaml
name: Contribution Snake
on:
  schedule:
    - cron: '0 12 * * *' # Daily at 12:00 UTC
  workflow_dispatch:

permissions:
  contents: write

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: Platane/snk@v3
        with:
          github_user_name: ${{ github.repository_owner }}
          outputs: |
            dist/github-snake.svg
            dist/github-snake-dark.svg?palette=github-dark

      - uses: crazy-max/ghaction-github-pages@v4
        with:
          target_branch: output
          build_dir: dist
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

README usage:

```markdown
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/{USERNAME}/{USERNAME}/output/github-snake-dark.svg">
  <img alt="Contribution snake animation" src="https://raw.githubusercontent.com/{USERNAME}/{USERNAME}/output/github-snake.svg">
</picture>
```

---

## WakaTime Stats Updater

Updates README with coding activity from WakaTime.

```yaml
name: WakaTime Stats
on:
  schedule:
    - cron: '0 0 * * *' # Daily at midnight UTC
  workflow_dispatch:

permissions:
  contents: write

jobs:
  update-readme:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: anmol098/waka-readme-stats@master
        with:
          WAKATIME_API_KEY: ${{ secrets.WAKATIME_API_KEY }}
          GH_TOKEN: ${{ secrets.GH_TOKEN }}
          SHOW_LINES_OF_CODE: 'True'
          SHOW_PROFILE: 'True'
          SHOW_SHORT_INFO: 'True'
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

README markers:

```markdown
### Coding Activity

<!--START_SECTION:waka-->
<!--END_SECTION:waka-->
```

Required secrets:

- `WAKATIME_API_KEY`: from https://wakatime.com/settings/api-key
- `GH_TOKEN`: GitHub PAT with `repo` scope (for private repo stats)

---

## GitHub Activity Feed Updater

Embeds recent GitHub activity into the README.

```yaml
name: GitHub Activity
on:
  schedule:
    - cron: '0 8 * * *' # Daily at 08:00 UTC
  workflow_dispatch:

permissions:
  contents: write

jobs:
  update-readme:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: jamesgeorge007/github-activity-readme@master
        with:
          MAX_LINES: 5
          COMMIT_MSG: 'chore: update GitHub activity'
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

README markers:

```markdown
### Recent Activity

<!--START_SECTION:activity-->
<!--END_SECTION:activity-->
```

---

## Spotify Now Playing

Uses `kittinan/spotify-github-profile` for Spotify integration via GitHub Actions.

```yaml
name: Spotify Now Playing
on:
  schedule:
    - cron: '*/30 * * * *' # Every 30 minutes
  workflow_dispatch:

permissions:
  contents: write

jobs:
  update-readme:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: kittinan/spotify-github-profile@master
        with:
          SPOTIFY_CLIENT_ID: ${{ secrets.SPOTIFY_CLIENT_ID }}
          SPOTIFY_CLIENT_SECRET: ${{ secrets.SPOTIFY_CLIENT_SECRET }}
          SPOTIFY_REFRESH_TOKEN: ${{ secrets.SPOTIFY_REFRESH_TOKEN }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Required secrets:

- `SPOTIFY_CLIENT_ID`: from Spotify Developer Dashboard
- `SPOTIFY_CLIENT_SECRET`: from Spotify Developer Dashboard
- `SPOTIFY_REFRESH_TOKEN`: generated via OAuth flow (see https://github.com/kittinan/spotify-github-profile for setup)

---

## lowlighter/metrics (Advanced)

Comprehensive metrics generation with many plugins.

```yaml
name: Metrics
on:
  schedule:
    - cron: '0 4 * * *' # Daily at 04:00 UTC
  workflow_dispatch:

permissions:
  contents: write

jobs:
  metrics:
    runs-on: ubuntu-latest
    steps:
      - uses: lowlighter/metrics@latest
        with:
          token: ${{ secrets.METRICS_TOKEN }}
          user: { USERNAME }
          template: classic
          base: header, activity, community, repositories, metadata
          plugin_languages: yes
          plugin_languages_analysis_timeout: 15
          plugin_languages_categories: markup, programming
          plugin_languages_colors: github
          plugin_languages_limit: 8
          plugin_isocalendar: yes
          plugin_isocalendar_duration: full-year
          plugin_achievements: yes
          plugin_achievements_threshold: C
          plugin_notable: yes
          config_timezone: America/New_York
```

Required secrets:

- `METRICS_TOKEN`: GitHub PAT with `read:user`, `read:org`, `repo` scopes

Output: SVG file committed to the repo, referenced from README.

---

## Multi-Source Updater (Combined)

For profiles with multiple dynamic sections, a single workflow can handle all updates:

```yaml
name: Update Profile
on:
  schedule:
    - cron: '0 6 * * *' # Daily at 06:00 UTC
  workflow_dispatch:

permissions:
  contents: write

jobs:
  blog-posts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: gautamkrishnar/blog-post-workflow@v1
        with:
          feed_list: '{RSS_FEED_URL}'
          max_post_count: 5

  snake:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Platane/snk@v3
        with:
          github_user_name: ${{ github.repository_owner }}
          outputs: |
            dist/github-snake.svg
            dist/github-snake-dark.svg?palette=github-dark
      - uses: crazy-max/ghaction-github-pages@v4
        with:
          target_branch: output
          build_dir: dist
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Note: separate jobs run in parallel, which is faster than sequential steps. Use separate workflows if jobs have different cron schedules or failure isolation is important.
