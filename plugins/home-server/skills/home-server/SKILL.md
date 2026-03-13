---
name: home-server
description: >-
  Manages the nest home server: Coolify deployments, Traefik routing,
  Tailscale networking, Cloudflare DNS, and all deployed applications
  (Jellyfin, *arr stack, LazyLibrarian, Kavita, Audiobookshelf, Castopod,
  Home Assistant, Glance, SABnzbd, n8n, etc). Use when the user asks to
  deploy, configure, troubleshoot, or optimize any service on their home
  server, manage DNS/networking, check service status, or tune application
  settings. Also triggers on mentions of Coolify, Traefik, Tailscale,
  Cloudflare, or any deployed service by name.
  Do NOT use for creating or modifying Claude Code skills, plugins, or
  commands. Do NOT use for general Docker administration unrelated to
  this server's Coolify instance.
---

## Critical Rules

- ALWAYS read credentials from `~/.config/nest/credentials.env` — NEVER hardcode API keys in commands or output
- ALWAYS prefer the Coolify API (`$COOLIFY_API_URL`) over direct Docker commands for service management
- When deploying new services, ALWAYS try Coolify one-click templates first before custom docker-compose
- One-click services MUST have "Connect to Predefined Network" enabled for Traefik routing — remind the user or set it via API
- docker_compose_raw MUST be base64-encoded when PATCHing via the Coolify API
- FQDN is stored separately on the `service_applications` table — updating docker-compose alone does NOT update routing
- NEVER expose services publicly without explicit user confirmation — all services are Tailscale-only by default
- Before making infrastructure changes, state what you're about to do and get confirmation
- When troubleshooting cert issues, check: (1) container network includes coolify-proxy, (2) Traefik labels have correct port, (3) ACME cert exists in `/data/coolify/proxy/acme.json`
- Glance config at `/data/coolify/services/l0cws0skkokg08k44g4ocswc/config/glance.yml` live-reloads — no restart needed

## Credentials

All credentials are stored at `~/.config/nest/credentials.env` (chmod 600). To load them:

```bash
# Read a single value
grep '^COOLIFY_API_TOKEN=' ~/.config/nest/credentials.env | cut -d= -f2- | tr -d '"'

# Source all values (for multi-command operations)
set -gx (grep -v '^#' ~/.config/nest/credentials.env | grep '=' | string split -m1 '=')
```

If the credentials file is missing, use the `credential-manager` agent to recreate it from memory.

## Server Architecture

Read `~/.config/nest/server-config.md` for the complete server topology, service UUIDs, container names, volume mounts, and network layout.

Read `~/.config/nest/coolify-patterns.md` for Coolify API patterns, common operations, and known gotchas.

Read `~/.config/nest/networking.md` for Tailscale, Cloudflare, and Traefik configuration details.

## Workflow

### Step 1: Understand Intent

Parse the user's natural language request and classify it:

- **Deploy**: New service deployment → use `coolify-specialist` agent
- **Configure**: Modify existing service settings → use `coolify-specialist` or `app-tuner` agent
- **Network**: DNS, certs, routing, public access → use `networking-specialist` agent
- **Troubleshoot**: Something broken → read logs, check config, determine which specialist to dispatch
- **Optimize**: Tune performance or quality → use `app-tuner` agent
- **Status**: Check what's running → query Coolify API directly (no agent needed)
- **Dashboard**: Modify Glance → edit the config file directly (live-reloads)

### Step 2: Load Credentials

Before any API call, load the relevant credentials:

```bash
COOLIFY_TOKEN=$(grep '^COOLIFY_API_TOKEN=' ~/.config/nest/credentials.env | cut -d= -f2- | tr -d '"')
```

### Step 3: Dispatch to Specialist

For complex tasks, dispatch to the appropriate agent using the Agent tool:

| Task Domain                              | Agent                               | Model  |
| ---------------------------------------- | ----------------------------------- | ------ |
| Coolify API, deployments, docker-compose | `home-server:coolify-specialist`    | sonnet |
| Tailscale, Cloudflare, Traefik, certs    | `home-server:networking-specialist` | sonnet |
| App-specific tuning, docs research       | `home-server:app-tuner`             | sonnet |
| Post-session skill updates               | `home-server:retrospect`            | sonnet |

For simple tasks (status checks, Glance edits, single API calls), handle directly without spawning an agent.

### Step 4: Validate

After making changes:

1. Verify the service is running: check Coolify API status
2. Verify HTTPS works: `curl -vk https://{service}.home.birdcar.dev 2>&1 | grep 'subject:'`
3. Verify the cert is Let's Encrypt (not TRAEFIK DEFAULT CERT)
4. For app-specific changes, verify the app is responding correctly

### Step 5: Update Knowledge (if applicable)

If this session revealed new information about the server (new services, changed configs, gotchas discovered), update:

1. `~/.claude/projects/-home-birdcar/memory/MEMORY.md` — for cross-session memory
2. `~/.claude/projects/-home-birdcar/memory/media-server-setup.md` — for detailed server notes
3. `~/.config/nest/server-config.md` — for skill-internal reference

## Common Operations Quick Reference

### Check all services status

```bash
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" "$COOLIFY_API_URL/projects" | python3 -m json.tool
```

### Deploy a one-click service

1. Create via Coolify UI or API
2. Enable "Connect to Predefined Network" (`connect_to_docker_network: true`)
3. Set FQDN in Coolify UI
4. Verify Traefik picks it up and issues cert

### Restart a service

```bash
curl -s -X POST -H "Authorization: Bearer $COOLIFY_TOKEN" "$COOLIFY_API_URL/services/{uuid}/restart"
```

### Check Traefik cert status

```bash
sudo python3 -c "
import json
with open('/data/coolify/proxy/acme.json') as f:
    data = json.load(f)
for r, info in data.items():
    for c in info.get('Certificates', []):
        print(c['domain']['main'])
"
```
