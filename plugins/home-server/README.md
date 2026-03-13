# home-server

A Claude Code plugin that manages a personal Coolify-based home server through four specialized agents. Deploy services, configure networking, tune applications, and troubleshoot issues without leaving your terminal.

## What problem it solves

Managing a home server means juggling the Coolify API, Traefik routing, Tailscale networking, Cloudflare DNS, and a dozen deployed services each with their own configuration quirks. That's a lot of context to hold in your head: which API endpoints need base64 encoding, which services overwrite their own config on startup, whether a cert failure is a network issue or a Traefik label typo.

This plugin encodes all of that operational knowledge into four agents that know how the server works. You describe what you want in plain language, and it classifies the task, dispatches to the right specialist, and validates the result.

The server config is mine (specific service UUIDs, mount paths, domain names), but the architecture -- Coolify + Traefik + Tailscale + Cloudflare with agent-based task routing -- is reusable if you're building something similar.

## Installation

```bash
/plugin marketplace add birdcar/claude-plugins
/plugin install home-server@birdcar
```

You'll also need a `~/.config/home-server/credentials.env` file (chmod 600) with your Coolify API token, Cloudflare API token, and Tailscale auth key.

## How it works

When you ask the plugin to do something, it classifies your request and dispatches to one of four agents:

**coolify-specialist** handles deployments and service configuration through the Coolify REST API. It knows to try one-click templates before custom docker-compose, to base64-encode `docker_compose_raw` on PATCH requests, and to connect services to the predefined network for Traefik routing.

**networking-specialist** manages the full network path: Cloudflare DNS, Tailscale VPN, Traefik reverse proxy, and TLS certificates via DNS-01 challenge. Services are Tailscale-only by default -- public exposure requires explicit confirmation.

**app-tuner** researches and applies app-specific optimizations. Jellyfin transcoding settings, *arr stack quality profiles (respecting Recyclarr ownership), media server tuning. It pulls from TRaSH Guides and official docs rather than guessing.

**retrospect** runs after sessions (via `/home-server-retrospect`) to review what was learned and update the plugin's reference files so knowledge accumulates over time.

Simple tasks like status checks or Glance dashboard edits are handled directly without spawning an agent.

## Deployed services

Jellyfin, Sonarr, Radarr, Lidarr, Prowlarr, Bazarr, SABnzbd, LazyLibrarian, Kavita, Audiobookshelf, Castopod, Home Assistant, Glance, n8n.

## Infrastructure details

- Coolify API at an internal Tailscale IP (never exposed publicly)
- Config persistence: `/srv/docker/{service}/` on NVMe
- Media volume: `/mnt/mediastore/` structured for hardlink compatibility
- Environment standards: `PUID=1000`, `PGID=1000`, `TZ=America/Chicago`
- Reference docs live at `~/.config/home-server/` (server-config.md, coolify-patterns.md, networking.md)

## Guardrails worth knowing about

The plugin loads credentials before every API call and refuses to hardcode tokens in commands. It prefers the Coolify API over direct Docker commands. It won't expose services publicly without asking first. After making changes, it verifies the service is running, HTTPS works, and the TLS cert is from Let's Encrypt (not Traefik's default self-signed cert).

A few service-specific gotchas are encoded too: LazyLibrarian overwrites its config on startup so you have to stop it before editing, Glance config live-reloads without a restart, and Recyclarr owns quality profiles in the *arr stack so manual overrides get clobbered.

## Commands

| Command | Purpose |
| --- | --- |
| `/home-server-retrospect` | Review the current session for new knowledge and update reference files |
