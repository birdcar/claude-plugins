#!/usr/bin/env bash
set -euo pipefail

# Roost bootstrap — standardized provisioning for SaaS projects.
# Creates Cloudflare resources, configures services, runs migrations.
#
# Usage:
#   bootstrap.sh [--all|--cf-only|--auth-only|--billing-only|--email-only|--migrate|--seed|--dry-run]
#
# Requires: wrangler, workos CLI, stripe CLI
# Credentials loaded from ~/.config/roost/credentials.env

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(pwd)}"
DRY_RUN=false
SCOPE="all"

# Parse flags
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)   DRY_RUN=true; shift ;;
        --all)       SCOPE="all"; shift ;;
        --cf-only)   SCOPE="cf"; shift ;;
        --auth-only) SCOPE="auth"; shift ;;
        --billing-only) SCOPE="billing"; shift ;;
        --email-only)   SCOPE="email"; shift ;;
        --migrate)   SCOPE="migrate"; shift ;;
        --seed)      SCOPE="seed"; shift ;;
        *)
            echo "ERROR: Unknown flag: $1" >&2
            echo "Usage: bootstrap.sh [--all|--cf-only|--auth-only|--billing-only|--email-only|--migrate|--seed|--dry-run]" >&2
            exit 1
            ;;
    esac
done

# Load credentials
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/roost"
CRED_FILE="$CONFIG_DIR/credentials.env"

if [[ ! -f "$CRED_FILE" ]]; then
    echo "ERROR: Missing $CRED_FILE — run load-config.sh for setup instructions" >&2
    exit 1
fi

PERMS=$(stat -c '%a' "$CRED_FILE" 2>/dev/null || stat -f '%Lp' "$CRED_FILE")
if [[ "$PERMS" != "600" ]]; then
    echo "ERROR: $CRED_FILE has permissions $PERMS, expected 600" >&2
    exit 1
fi

set -a
source "$CRED_FILE"
set +a

# Helpers
run_or_dry() {
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "[DRY RUN] $*"
    else
        echo "[RUN] $*"
        "$@"
    fi
}

check_command() {
    if ! command -v "$1" &>/dev/null; then
        echo "ERROR: $1 is not installed. Install it before running bootstrap." >&2
        exit 1
    fi
}

# Read project name from wrangler.toml or package.json
get_project_name() {
    if [[ -f "$PROJECT_ROOT/packages/api/wrangler.toml" ]]; then
        grep '^name' "$PROJECT_ROOT/packages/api/wrangler.toml" | head -1 | sed 's/name = "\(.*\)"/\1/' | tr -d '"' | tr -d ' '
    elif [[ -f "$PROJECT_ROOT/package.json" ]]; then
        grep '"name"' "$PROJECT_ROOT/package.json" | head -1 | sed 's/.*"name": "\(.*\)".*/\1/'
    else
        basename "$PROJECT_ROOT"
    fi
}

PROJECT_NAME=$(get_project_name)
echo "=== Roost Bootstrap: $PROJECT_NAME ==="
echo "Scope: $SCOPE | Dry run: $DRY_RUN"
echo ""

# --- Cloudflare Resources ---
provision_cf() {
    check_command wrangler
    echo "--- Cloudflare Resources ---"

    # D1 Database
    echo "Creating D1 database: ${PROJECT_NAME}-db"
    run_or_dry wrangler d1 create "${PROJECT_NAME}-db" 2>/dev/null || echo "  (may already exist)"

    # KV Namespace
    echo "Creating KV namespace: ${PROJECT_NAME}-kv"
    run_or_dry wrangler kv namespace create "${PROJECT_NAME}-kv" 2>/dev/null || echo "  (may already exist)"

    # R2 Bucket
    echo "Creating R2 bucket: ${PROJECT_NAME}-uploads"
    run_or_dry wrangler r2 bucket create "${PROJECT_NAME}-uploads" 2>/dev/null || echo "  (may already exist)"

    # Queue
    echo "Creating Queue: ${PROJECT_NAME}-jobs"
    run_or_dry wrangler queues create "${PROJECT_NAME}-jobs" 2>/dev/null || echo "  (may already exist)"

    echo ""
    echo "NOTE: Update wrangler.toml with the IDs output above."
    echo ""
}

# --- D1 Migrations ---
run_migrations() {
    check_command wrangler
    echo "--- D1 Migrations ---"
    if [[ -d "$PROJECT_ROOT/packages/api/src/db/migrations" ]]; then
        run_or_dry wrangler d1 migrations apply "${PROJECT_NAME}-db" --local
        echo "Migrations applied (local). For production: wrangler d1 migrations apply ${PROJECT_NAME}-db --remote"
    else
        echo "No migrations directory found at packages/api/src/db/migrations"
    fi
    echo ""
}

# --- WorkOS Setup ---
provision_auth() {
    check_command workos
    echo "--- WorkOS Setup ---"

    # Seed organizations and users
    if [[ -f "$PROJECT_ROOT/workos-seed.yaml" ]]; then
        echo "Seeding WorkOS from workos-seed.yaml"
        run_or_dry workos seed
    else
        echo "No workos-seed.yaml found. Create one for declarative provisioning."
    fi

    echo ""
    echo "Manual steps:"
    echo "  1. Set redirect URI in WorkOS dashboard"
    echo "  2. Run: wrangler secret put WORKOS_API_KEY"
    echo "  3. Run: wrangler secret put WORKOS_CLIENT_ID"
    echo "  4. Run: wrangler secret put WORKOS_COOKIE_PASSWORD"
    echo "  5. Run: wrangler secret put WORKOS_WEBHOOK_SECRET"
    echo ""
}

# --- Stripe Setup ---
provision_billing() {
    check_command stripe
    echo "--- Stripe Setup ---"

    echo "Creating Stripe products and prices should be done via the Stripe dashboard or CLI."
    echo "Use restricted API keys scoped to the operations needed."
    echo ""
    echo "Manual steps:"
    echo "  1. Create products/prices in Stripe dashboard"
    echo "  2. Run: wrangler secret put STRIPE_SECRET_KEY"
    echo "  3. Run: wrangler secret put STRIPE_WEBHOOK_SECRET"
    echo "  4. Configure webhook endpoint in Stripe dashboard: https://your-api.workers.dev/api/webhooks/stripe"
    echo ""
}

# --- Resend Setup ---
provision_email() {
    echo "--- Resend Setup ---"

    echo "Resend requires domain DNS verification (manual step)."
    echo ""
    echo "Manual steps:"
    echo "  1. Add your domain in the Resend dashboard"
    echo "  2. Configure DNS records (SPF, DKIM, DMARC) as shown in the dashboard"
    echo "  3. Run: wrangler secret put RESEND_API_KEY"
    echo ""
}

# --- Install Dependencies ---
install_deps() {
    check_command bun
    echo "--- Installing Dependencies ---"
    cd "$PROJECT_ROOT"
    run_or_dry bun install
    echo ""
}

# Execute based on scope
case "$SCOPE" in
    all)
        install_deps
        provision_cf
        run_migrations
        provision_auth
        provision_billing
        provision_email
        ;;
    cf)      provision_cf ;;
    migrate) run_migrations ;;
    auth)    provision_auth ;;
    billing) provision_billing ;;
    email)   provision_email ;;
    seed)
        check_command workos
        if [[ -f "$PROJECT_ROOT/workos-seed.yaml" ]]; then
            run_or_dry workos seed
        else
            echo "No workos-seed.yaml found."
        fi
        ;;
esac

echo "=== Bootstrap complete ==="
