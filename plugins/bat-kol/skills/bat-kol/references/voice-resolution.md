# Voice Resolution Algorithm

## Config Directory Structure

```
bat-kol/
├── style.md              # Global writing style framework
├── registers/
│   ├── professional.md   # Formal business communication
│   ├── internal.md       # Team/workplace casual
│   ├── personal.md       # Friends, family, personal blog
│   └── social.md         # Social media voice
├── channels/
│   ├── slack.md          # Slack formatting + conventions
│   ├── email.md          # Email formatting + conventions
│   ├── bluesky.md        # Bluesky formatting + constraints
│   ├── github.md         # GitHub formatting + conventions
│   └── {custom}.md       # User-defined channels
└── samples/
    ├── professional/     # Writing samples for training
    ├── internal/
    ├── personal/
    └── social/
```

## Cascading Resolution Order

The `resolve-config.sh` script resolves config using this priority (highest first):

1. **`$BAT_KOL_CONFIG` env var** — Explicit override pointing to a config directory. Useful for testing or switching between config sets.
2. **`.bat-kol/` in cwd or parent** — Walk from cwd upward until a `.bat-kol/` directory is found. Enables per-project voice overrides (e.g., open-source projects use a different register than internal repos).
3. **`${XDG_CONFIG_HOME:-$HOME/.config}/bat-kol/`** — Global fallback. This is where most users keep their primary voice config.

When a project override is active (priority 1 or 2), individual files inherit from global config if not overridden locally. For example, a project `.bat-kol/` that only contains `registers/professional.md` will still use the global `style.md` and global channel configs.

## Voice Assembly Stack

The assembled voice profile is built bottom-to-top. Each layer can override rules from the layer below:

| Layer               | Source                 | Controls                                                          |
| ------------------- | ---------------------- | ----------------------------------------------------------------- |
| 1. Global style     | `style.md`             | Writing philosophy, sentence rhythm, word choice principles       |
| 2. Register rules   | `registers/{name}.md`  | Tone, formality level, vocabulary constraints, sentence structure |
| 3. Channel format   | `channels/{name}.md`   | Markup syntax, character limits, structural conventions           |
| 4. Project override | `.bat-kol/` in project | Any of the above, scoped to a specific project                    |

## Channel-Register Independence

Channel and register are independent dimensions:

- **Channel** = formatting rules (mrkdwn, HTML, char limits, thread conventions)
- **Register** = voice rules (tone, formality, vocabulary, sentence patterns)

Each channel defines a **default register** (e.g., slack defaults to `internal`, email defaults to `professional`). The user can override the register for any channel at draft time.

The final voice is: `global_style + register.rules + channel.format_rules`

## Script Output Format

`resolve-config.sh` outputs JSON:

```json
{
  "config_root": "/path/to/.bat-kol",
  "global_config": "/home/user/.config/bat-kol",
  "project_override": true,
  "style": "/path/to/style.md",
  "register": "/path/to/registers/professional.md",
  "register_name": "professional",
  "channel": "/path/to/channels/email.md",
  "channel_name": "email",
  "samples_dir": "/path/to/samples/professional",
  "available_registers": ["internal", "personal", "professional", "social"],
  "available_channels": ["bluesky", "email", "github", "slack"]
}
```

Empty string values indicate the file was not found. The config-resolver agent handles missing files gracefully by using sensible defaults.

## Missing Config Handling

| Missing file               | Behavior                                                                              |
| -------------------------- | ------------------------------------------------------------------------------------- |
| No config directory at all | Script exits non-zero with setup instructions                                         |
| No `style.md`              | Skip global style layer — registers stand alone                                       |
| No register file           | Use channel's default register; if that's also missing, use neutral professional tone |
| No channel file            | Use generic channel (plain text, no special formatting)                               |
| No samples directory       | Training proceeds without sample analysis                                             |
