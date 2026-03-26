# home-server

A Claude Code plugin for managing a personal home server running Coolify, Traefik, Tailscale, and Cloudflare DNS. It encodes operational knowledge into four specialists so you don't have to context-switch between API docs, gotcha lists, and network topology every time you want to deploy a service or fix a cert.

## The problem

Managing a home server means remembering a lot of things simultaneously: which Coolify API fields need base64 encoding, how Traefik picks up service routing (FQDN is a separate table, not just a label), which services overwrite their own config on startup, and whether a cert failure is a network issue or a label typo. None of that is hard, but it's tedious to re-derive every session.

So I encoded it into agents that already know how this server works.

## Installation

```bash
/plugin marketplace add birdcar/claude-plugins
/plugin install home-server@birdcar
```

You'll also need `~/.config/home-server/credentials.env` (chmod 600) with your `COOLIFY_API_TOKEN`, `COOLIFY_API_URL`, `CF_API_TOKEN`, and `TS_AUTH_KEY`. The plugin reads credentials from that file before every API call and refuses to accept hardcoded tokens.

## How it works

When you describe what you want, the plugin classifies the intent and either handles it directly or dispatches to a specialist agent:

**coolify-specialist** handles service deployments and configuration through the Coolify REST API. It knows to try one-click templates before custom docker-compose, to base64-encode `docker_compose_raw` on PATCH requests, to enable "Connect to Predefined Network" for Traefik routing, and to set the FQDN on the `service_applications` table separately from the compose config.

**networking-specialist** manages the full network path: Cloudflare DNS records, Tailscale VPN, Traefik reverse proxy, and TLS via DNS-01 challenge. Services default to Tailscale-only -- public exposure requires explicit confirmation.

**app-tuner** researches and applies app-specific optimizations, pulling from TRaSH Guides and official docs. Useful for Jellyfin transcoding settings, Sonarr/Radarr quality profiles (respecting Recyclarr ownership), and similar tuning that requires reading external documentation rather than just calling an API.

**retrospect** reviews sessions for new knowledge and updates the plugin's reference files so that configs, gotchas, and service UUIDs accumulate across conversations rather than getting re-discovered each time.

Simple tasks (status checks, Glance dashboard edits) are handled directly without spawning an agent.

## Infrastructure assumptions

This plugin is built around a specific server setup:

- Coolify API at an internal Tailscale IP, never publicly exposed
- Config persistence at `/srv/docker/{service}/` on NVMe
- Media volume at `/mnt/mediastore/` structured for hardlink compatibility
- Environment defaults: `PUID=1000`, `PGID=1000`, `TZ=America/Chicago`
- Reference docs at `~/.config/home-server/` (server-config.md, coolify-patterns.md, networking.md)

The agent architecture -- classify intent, dispatch to specialist, validate result -- is the reusable part if you're building something similar for your own setup.

## Gotchas encoded in the plugin

A few service-specific behaviors that would otherwise need re-learning:

- LazyLibrarian overwrites its config on startup, so stop the container before editing
- Glance config live-reloads without a restart
- Recyclarr owns quality profiles in the \*arr stack -- manual overrides get clobbered on the next sync
- After any infrastructure change, the plugin verifies HTTPS works and the cert is Let's Encrypt, not Traefik's default self-signed cert

## Commands

| Command                   | What it does                                                            |
| ------------------------- | ----------------------------------------------------------------------- |
| `/home-server-retrospect` | Review the current session for new knowledge and update reference files |
