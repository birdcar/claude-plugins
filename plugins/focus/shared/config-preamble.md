## Configuration

Before running any `gh` commands, resolve the target repository and timezone:

```bash
CONFIG_JSON=$(${CLAUDE_PLUGIN_ROOT}/scripts/resolve-config.sh)
```

If this fails, tell the user: "Focus is not configured. Run `/focus:init` to set up, or create `~/.config/focus/config.json` with `{\"repo\": \"owner/repo\", \"timezone\": \"America/Chicago\"}`."

Extract values:

```bash
REPO=$(echo "$CONFIG_JSON" | jq -r '.repo')
TZ_NAME=$(echo "$CONFIG_JSON" | jq -r '.timezone')
```

Always use `-R $REPO` in `gh` commands — omitting it silently targets whatever repo `gh` infers from the current directory, which may not be the configured Focus repo. Similarly, use `TZ="$TZ_NAME"` for all timezone-sensitive operations (dates, cron calculations) instead of hardcoding a timezone.
