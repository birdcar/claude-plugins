# Local Configuration Pattern

Skills that need sensitive or machine-specific information (API keys, local file paths, PII, hostnames, credentials) must keep that data out of the repository and out of LLM context. This document defines the standard pattern for local configuration.

## Principle

Configuration lives on-disk in `$XDG_CONFIG_HOME/{skill-name}/` (typically `~/.config/{skill-name}/`). Skills never read config files directly — they run wrapper scripts that extract specific, descriptive environment variables. The LLM sees only the variable names and values, never the raw config files.

This keeps sensitive data out of:

- **Git repositories** — config files are local, not committed
- **LLM context** — only extracted values enter the conversation, not full files
- **Memory systems** — no reason to persist secrets when scripts can source them on demand

## PII and Identity Protection

Beyond credentials and paths, skills must also protect personally identifiable information (PII). When skill output, memory, or committed files might contain real names, email addresses, or other identifiers:

- **Anonymize references to people**: use role-based handles (`@colleague`, `@manager`, `@oncall`) instead of real names or usernames in any content that gets committed, stored in memory, or logged
- **Strip emails and mentions**: sourcing scripts should output descriptive keys, not raw contact info — e.g., `NOTIFY_CHANNEL=ops-alerts` not `NOTIFY_EMAIL=jane@company.com`
- **Config files can contain PII** (they're local and `chmod 600`), but the **scripts that read them should not echo PII** into LLM context unless the skill specifically needs it for the current operation
- **Memory entries should never contain PII** — if you need to remember "the person who manages deploys", store the role, not the name

## Directory Structure

```
~/.config/{skill-name}/
├── credentials.env     # API keys, tokens (chmod 600)
├── paths.env           # Local file paths, mount points
└── config.env          # Non-sensitive preferences (optional)
```

- Use `{skill-name}` matching the plugin or skill name (kebab-case)
- Directory should be `chmod 700` (owner only)
- `credentials.env` must be `chmod 600` (owner read/write only) — this prevents the Read tool and other processes from accessing secrets directly
- `paths.env` and `config.env` should also be `chmod 600` for consistency
- Files use `KEY=value` format, one per line, `#` for comments
- No shell syntax beyond simple assignment — no exports, no command substitution

### Example `credentials.env`

```env
# Coolify instance
COOLIFY_API_TOKEN=bearer-token-here
COOLIFY_BASE_URL=https://coolify.local:8000

# Cloudflare
CF_API_TOKEN=cf-token-here
CF_ZONE_ID=zone-id-here
```

### Example `paths.env`

```env
# Media library paths (machine-specific)
MEDIA_ROOT=/mnt/storage/media
BOOKS_DIR=/mnt/storage/media/books
BACKUP_DIR=/mnt/backup/daily
```

## Sourcing Pattern

Skills access config through wrapper scripts that output only the specific keys needed. The LLM runs the script via Bash and uses its output — it never reads the config files directly.

### Minimal sourcing script (`scripts/load-config.sh`)

```bash
#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/{skill-name}"
CRED_FILE="$CONFIG_DIR/credentials.env"

# Validate config exists
if [[ ! -f "$CRED_FILE" ]]; then
    echo "ERROR: Missing config file: $CRED_FILE" >&2
    echo "Create it with the required keys. See the skill's setup docs." >&2
    exit 1
fi

# Validate permissions — credentials must not be world/group-readable
PERMS=$(stat -c '%a' "$CRED_FILE" 2>/dev/null || stat -f '%Lp' "$CRED_FILE")
if [[ "$PERMS" != "600" ]]; then
    echo "ERROR: $CRED_FILE has permissions $PERMS, expected 600" >&2
    echo "Fix with: chmod 600 $CRED_FILE" >&2
    exit 1
fi

# Source and export only the keys this script needs
set -a
source "$CRED_FILE"
set +a

# Output only the specific values the LLM needs
# (prevents the full file from entering context)
echo "COOLIFY_TOKEN=$COOLIFY_API_TOKEN"
echo "COOLIFY_URL=$COOLIFY_BASE_URL"
```

The permissions check is important: `chmod 600` means only the file owner can read the file. This prevents the LLM's Read tool from accessing the file directly — it must go through the script, which controls exactly which values are exposed.

### Per-operation scripts

For skills with multiple operations needing different credentials, use focused scripts:

```bash
# scripts/get-coolify-token.sh — outputs only the Coolify API token
#!/usr/bin/env bash
set -euo pipefail
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/{skill-name}"
grep '^COOLIFY_API_TOKEN=' "$CONFIG_DIR/credentials.env" | cut -d= -f2- | tr -d '"'
```

This is the tightest pattern — the script outputs a single value, so the LLM can use it inline:

```markdown
## Step 2: Load Credentials

Run `COOLIFY_TOKEN=$(bash ${CLAUDE_SKILL_DIR}/scripts/get-coolify-token.sh)` before making API calls.
```

## Integration in SKILL.md

### Critical Rules section (first 100 lines)

```markdown
## Critical Rules

- NEVER hardcode API keys, tokens, paths, or credentials in commands or output
- NEVER read config files directly with the Read tool — always use sourcing scripts via Bash
- NEVER commit, log, or store in memory real names, emails, or other PII — use anonymized role-based handles (e.g. `@colleague`, `@manager`) in any persisted output
- ALWAYS load sensitive values from local config via scripts in `scripts/`
- If config is missing, instruct the user to create it — do not ask them to paste secrets into the conversation
```

### Setup / Prerequisites section

````markdown
## Prerequisites

This skill requires local configuration at `~/.config/{skill-name}/`:

| File            | Required | Keys                     |
| --------------- | -------- | ------------------------ |
| credentials.env | Yes      | `API_TOKEN`, `API_URL`   |
| paths.env       | No       | `DATA_DIR`, `BACKUP_DIR` |

If missing, instruct the user to create the directory and files (the skill should NOT create these automatically — the user must provide real values):

```bash
mkdir -p ~/.config/{skill-name}
chmod 700 ~/.config/{skill-name}
cat > ~/.config/{skill-name}/credentials.env << 'EOF'
API_TOKEN=your-token-here
API_URL=https://your-instance.example.com
EOF
chmod 600 ~/.config/{skill-name}/credentials.env
```
````

The `chmod 700` on the directory and `chmod 600` on files ensures that only the owner can access them. This is enforced by the sourcing scripts at runtime — if permissions are wrong, the script exits with an error rather than exposing secrets.

### Workflow steps

```markdown
## Step 1: Load Configuration

Run `bash ${CLAUDE_SKILL_DIR}/scripts/load-config.sh` and capture its output.

- If exit code is non-zero, show the error and instruct the user to set up config
- Parse the output key-value pairs for use in subsequent steps
```

## When to Use This Pattern

| Signal                                                       | Action                                                           |
| ------------------------------------------------------------ | ---------------------------------------------------------------- |
| Skill needs API keys or tokens                               | Use `credentials.env`                                            |
| Skill references machine-specific paths                      | Use `paths.env`                                                  |
| Skill needs user identity (email, username)                  | Use `config.env`, source via script that outputs role-based keys |
| Skill references colleagues or contacts by name              | Store real names in `config.env`, output anonymized handles only |
| Skill asks the user for a value that varies per machine      | Store in local config, source via script                         |
| Skill stores a value in memory that could change per machine | Move to local config instead                                     |

## When NOT to Use This Pattern

- Non-sensitive, project-specific values → use `references/` in the skill directory
- Values that are the same for all users → hardcode in SKILL.md or references
- Temporary session state → keep in conversation context
- Values derivable from the codebase → use Grep/Glob to find them at runtime
