# GitHub Profile README Component Catalog

## Stats Cards (github-readme-stats)

Base URL: `https://github-readme-stats.vercel.app/api`

### General Stats Card

```
https://github-readme-stats.vercel.app/api?username={USERNAME}&show_icons=true&theme={THEME}
```

Common parameters:

- `theme`: dark, radical, merko, gruvbox, tokyonight, onedark, cobalt, synthwave, highcontrast, dracula, transparent
- `show_icons`: true/false
- `hide`: comma-separated stats to hide (stars, commits, prs, issues, contribs)
- `count_private`: true/false
- `hide_border`: true/false
- `bg_color`: hex without #, or gradient like `0,color1,color2`
- `title_color`, `text_color`, `icon_color`: hex without #
- `custom_title`: override card title

### Top Languages Card

```
https://github-readme-stats.vercel.app/api/top-langs/?username={USERNAME}&layout={LAYOUT}&theme={THEME}
```

Layouts: `compact`, `donut`, `donut-vertical`, `pie`, `hide_progress`

- `hide`: comma-separated languages to exclude
- `langs_count`: number of languages to show (default 5)

### Repo Pin Card

```
https://github-readme-stats.vercel.app/api/pin/?username={USERNAME}&repo={REPO}&theme={THEME}
```

### WakaTime Stats Card

```
https://github-readme-stats.vercel.app/api/wakatime?username={WAKATIME_USERNAME}&theme={THEME}
```

Requires WakaTime account linked to GitHub.

## Streak Stats (github-readme-streak-stats)

```
https://streak-stats.demolab.com/?user={USERNAME}&theme={THEME}
```

Parameters:

- `theme`: dark, highcontrast, radical, etc.
- `hide_border`: true/false
- `date_format`: e.g. `M j[, Y]`
- `background`: hex color
- `ring`, `fire`, `currStreakNum`, `sideNums`, `currStreakLabel`, `sideLabels`, `dates`: hex colors

## Trophies (github-profile-trophy)

```
https://github-profile-trophy.vercel.app/?username={USERNAME}&theme={THEME}
```

Parameters:

- `theme`: onedark, gruvbox, dracula, monokai, flat, alduin
- `column`: number of columns (-1 for no wrap)
- `row`: number of rows
- `margin-w`, `margin-h`: margins in px
- `no-frame`: true/false
- `no-bg`: true/false
- `rank`: comma-separated ranks to show (SECRET, SSS, SS, S, AAA, AA, A, B, C)

## Capsule Render (Headers/Footers)

```
https://capsule-render.vercel.app/api?type={TYPE}&color={COLOR}&height={HEIGHT}&text={TEXT}&section={SECTION}
```

Types: `wave`, `egg`, `shark`, `slice`, `rect`, `soft`, `cylinder`, `waving`, `venom`, `transparent`, `rounded`, `block`

Parameters:

- `color`: hex without #, or `gradient` or `auto` or `timeGradient` or `timeAuto`
- `height`: pixels (default 200 for header, 100 for footer)
- `text`: URL-encoded text
- `section`: `header` (default) or `footer`
- `textBg`: true/false (background behind text)
- `animation`: `fadeIn`, `scaleIn`, `blinking`, `twinkling`
- `fontColor`: hex without #
- `fontSize`: pixels
- `fontAlign`: 0-100 (default 50, centered)
- `fontAlignY`: 0-100 (default varies by type)
- `desc`: subtitle text
- `descSize`, `descColor`, `descAlign`, `descAlignY`: subtitle styling
- `reversal`: true/false (flip animation)
- `stroke`: border hex color
- `strokeWidth`: border width

For footer: add `&section=footer`

## Typing SVG Animation

```
https://readme-typing-svg.demolab.com?font={FONT}&size={SIZE}&pause={PAUSE}&color={COLOR}&center=true&vCenter=true&width={WIDTH}&lines={LINES}
```

Parameters:

- `font`: font name (e.g., Fira+Code, JetBrains+Mono)
- `size`: font size
- `pause`: pause between lines in ms (default 1000)
- `color`: hex with # URL-encoded as %23
- `center`, `vCenter`: true/false
- `width`, `height`: dimensions
- `lines`: semicolon-separated lines to cycle through
- `repeat`: true/false (default true)
- `duration`: typing speed in ms per character

## Shields.io Badges

### Static Badge

```
https://img.shields.io/badge/{LABEL}-{MESSAGE}-{COLOR}?style={STYLE}&logo={LOGO}&logoColor={LOGO_COLOR}
```

### Tech Stack Badge Pattern

```
https://img.shields.io/badge/{TECH_NAME}-{HEX_COLOR}?style=for-the-badge&logo={LOGO_SLUG}&logoColor=white
```

Common tech badges:

- TypeScript: `TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white`
- Python: `Python-3776AB?style=for-the-badge&logo=python&logoColor=white`
- React: `React-61DAFB?style=for-the-badge&logo=react&logoColor=black`
- Node.js: `Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white`
- Go: `Go-00ADD8?style=for-the-badge&logo=go&logoColor=white`
- Rust: `Rust-000000?style=for-the-badge&logo=rust&logoColor=white`
- Docker: `Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white`
- AWS: `AWS-232F3E?style=for-the-badge&logo=amazonwebservices&logoColor=white`
- PostgreSQL: `PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white`
- Redis: `Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white`

Styles: `flat`, `flat-square`, `plastic`, `for-the-badge`, `social`

Logo slugs: find at https://simpleicons.org/

### Social Badges

```
![GitHub followers](https://img.shields.io/github/followers/{USERNAME}?style=social)
![GitHub stars](https://img.shields.io/github/stars/{USERNAME}?style=social)
![Twitter Follow](https://img.shields.io/twitter/follow/{TWITTER_HANDLE}?style=social)
```

## Profile View Counter (komarev)

```
https://komarev.com/ghpvc/?username={USERNAME}&color={COLOR}&style={STYLE}
```

Parameters:

- `color`: named color (blue, green, red) or hex
- `style`: flat, flat-square, plastic, for-the-badge
- `label`: custom label text (default "Profile views")
- `abbreviated`: true/false

## Contribution Snake (Platane/snk)

Generated via GitHub Actions (see actions-templates.md). Output is an SVG:

```markdown
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/{USERNAME}/{USERNAME}/output/github-snake-dark.svg">
  <img src="https://raw.githubusercontent.com/{USERNAME}/{USERNAME}/output/github-snake.svg">
</picture>
```

## Dark/Light Mode Support

Use the `<picture>` element to serve different images based on color scheme:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="{DARK_URL}" />
  <source media="(prefers-color-scheme: light)" srcset="{LIGHT_URL}" />
  <img alt="{ALT_TEXT}" src="{FALLBACK_URL}" />
</picture>
```

Apply to stats cards by using `&theme=dark` for the dark variant and default/light theme for the light variant.

## lowlighter/metrics

Advanced alternative to github-readme-stats with 47+ plugins. Self-hosted via GitHub Actions.

Action: `lowlighter/metrics@latest`

Common plugins:

- `base`: activity, community, repositories, metadata
- `languages`: detailed language breakdown
- `isocalendar`: 3D contribution calendar
- `achievements`: detailed achievement badges
- `notable`: contributions to notable repos
- `stars`: starred repos list
- `topics`: topic icons
- `reactions`: reaction stats

Output: SVG or PNG committed to repo.

Configuration is via the workflow YAML — see actions-templates.md for examples.

## Spotify Now Playing (novatorem pattern)

Requires a Vercel deployment of the novatorem app or similar service.

Alternative: use `kittinan/spotify-github-profile` GitHub Action.

```markdown
[![Spotify](https://novatorem-{USERNAME}.vercel.app/api/spotify)](https://open.spotify.com/user/{SPOTIFY_USER_ID})
```

Setup requires:

1. Spotify Developer app (CLIENT_ID, CLIENT_SECRET)
2. Vercel deployment or GitHub Action
3. Refresh token generation via OAuth flow

## GitHub Activity Feed

Use `jamesgeorge007/github-activity-readme` Action to embed recent activity.

```markdown
<!-- GITHUB-ACTIVITY:START -->
<!-- GITHUB-ACTIVITY:END -->
```

Updated via GitHub Actions cron job.
