#!/usr/bin/env bash
set -euo pipefail

# Load roost credentials from local config.
# Outputs key=value pairs for use by the skill.
# Never outputs raw config files — only specific keys needed.

CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/roost"
CRED_FILE="$CONFIG_DIR/credentials.env"

if [[ ! -d "$CONFIG_DIR" ]]; then
    echo "ERROR: Config directory not found: $CONFIG_DIR" >&2
    echo "Create it with:" >&2
    echo "  mkdir -p $CONFIG_DIR && chmod 700 $CONFIG_DIR" >&2
    exit 1
fi

if [[ ! -f "$CRED_FILE" ]]; then
    echo "ERROR: Missing credentials file: $CRED_FILE" >&2
    echo "Create it with the required keys:" >&2
    echo "" >&2
    echo "  cat > $CRED_FILE << 'EOF'" >&2
    echo "  CF_API_TOKEN=your-cloudflare-api-token" >&2
    echo "  CF_ACCOUNT_ID=your-cloudflare-account-id" >&2
    echo "  WORKOS_API_KEY=your-workos-api-key" >&2
    echo "  WORKOS_CLIENT_ID=your-workos-client-id" >&2
    echo "  STRIPE_SECRET_KEY=your-stripe-secret-key" >&2
    echo "  RESEND_API_KEY=your-resend-api-key" >&2
    echo "  EOF" >&2
    echo "  chmod 600 $CRED_FILE" >&2
    exit 1
fi

# Validate permissions — credentials must not be world/group-readable
PERMS=$(stat -c '%a' "$CRED_FILE" 2>/dev/null || stat -f '%Lp' "$CRED_FILE")
if [[ "$PERMS" != "600" ]]; then
    echo "ERROR: $CRED_FILE has permissions $PERMS, expected 600" >&2
    echo "Fix with: chmod 600 $CRED_FILE" >&2
    exit 1
fi

# Source credentials
set -a
source "$CRED_FILE"
set +a

# Output only the specific keys the skill needs
# Each key is validated before output
missing=()
for key in CF_API_TOKEN CF_ACCOUNT_ID WORKOS_API_KEY WORKOS_CLIENT_ID STRIPE_SECRET_KEY RESEND_API_KEY; do
    val="${!key:-}"
    if [[ -z "$val" ]]; then
        missing+=("$key")
    else
        echo "$key=$val"
    fi
done

if [[ ${#missing[@]} -gt 0 ]]; then
    echo "WARNING: Missing keys in $CRED_FILE: ${missing[*]}" >&2
fi
