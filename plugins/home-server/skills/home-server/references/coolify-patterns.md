# Coolify API Patterns & Gotchas

## API Basics

```bash
# Load credentials
COOLIFY_TOKEN=$(grep '^COOLIFY_API_TOKEN=' ~/.config/nest/credentials.env | cut -d= -f2- | tr -d '"')
COOLIFY_API="http://100.108.157.126:8000/api/v1"

# Common headers
-H "Authorization: Bearer $COOLIFY_TOKEN" -H "Accept: application/json"
```

## Common Operations

### List projects

```bash
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" "$COOLIFY_API/projects"
```

### Get project environment (list services)

```bash
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" "$COOLIFY_API/projects/{project_uuid}/{env_uuid}"
```

### Get service details

```bash
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" "$COOLIFY_API/services/{service_uuid}"
```

### Restart service

```bash
curl -s -X POST -H "Authorization: Bearer $COOLIFY_TOKEN" "$COOLIFY_API/services/{service_uuid}/restart"
```

### Update docker-compose (MUST be base64-encoded)

```bash
python3 -c "
import json, base64
compose = '''...your compose yaml...'''
encoded = base64.b64encode(compose.encode()).decode()
print(json.dumps({'docker_compose_raw': encoded}))
" > /tmp/patch.json

curl -s -X PATCH \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @/tmp/patch.json \
  "$COOLIFY_API/services/{service_uuid}"
```

### Update connect_to_docker_network

```bash
curl -s -X PATCH \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"connect_to_docker_network": true}' \
  "$COOLIFY_API/services/{service_uuid}"
```

## Known Gotchas

### 1. One-click services need "Connect to Predefined Network"

By default, `connect_to_docker_network` is `false` for one-click service templates. Without it, Traefik cannot route to the container even though Traefik auto-connects to the service's network. ALWAYS enable this for services that need HTTPS via Traefik.

### 2. FQDN stored separately from docker-compose

The FQDN (which drives Traefik label generation including loadbalancer port) is stored on the `service_applications` table, not in docker_compose_raw. To update it:

```bash
sudo docker exec coolify-db psql -U coolify -c \
  "UPDATE service_applications SET fqdn = 'https://example.home.birdcar.dev:PORT' WHERE uuid = 'APP_UUID';"
```

### 3. Port in FQDN matters

The port suffix in the FQDN (e.g., `:8080`) tells Coolify which internal container port to configure in Traefik's loadbalancer labels. If the app listens on a different port than the template expects, both the FQDN port AND the docker-compose `SERVICE_URL_*` env var must be updated.

### 4. Container names include UUID suffix

Coolify appends `-{service_uuid}` to container names. Use the full name for inter-service hostnames.

### 5. Coolify DNS validation disabled

Tailscale IP (100.108.157.126) doesn't match public IP, so DNS validation is disabled in Coolify settings. This is expected.

### 6. Gluetun + Traefik conflict

Can't use Coolify FQDN for services behind Gluetun (generates conflicting labels). Use custom Traefik labels in the compose with explicit `service` directives for multi-port routing.

### 7. Gluetun health check

Use `wget -q -O /dev/null` not `wget -q --spider` — Mullvad rejects HEAD requests (exit code 8).

### 8. SABnzbd access

Default `inet_exposure = 0` blocks non-localhost. Must set to `4` and add domains to `host_whitelist` in config.

### 9. Coolify upgrade

Upgrade via: `curl -fsSL https://cdn.coollabs.io/coolify/install.sh | sudo bash`
Do NOT pass `--upgrade` flag (it gets misinterpreted as a version tag).

## Service Template Patterns

### Custom service with Traefik labels (for services not in one-click catalog)

```yaml
services:
  myservice:
    image: 'org/image:latest'
    container_name: myservice
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/Chicago
    volumes:
      - '/srv/docker/myservice:/config'
      - '/mnt/mediastore:/mnt/mediastore'
    labels:
      - traefik.enable=true
      - traefik.http.routers.myservice.rule=Host(`myservice.home.birdcar.dev`)
      - traefik.http.routers.myservice.entrypoints=https
      - traefik.http.routers.myservice.tls=true
      - traefik.http.routers.myservice.tls.certresolver=letsencrypt
      - traefik.http.services.myservice.loadbalancer.server.port=INTERNAL_PORT
      # HTTP redirect
      - traefik.http.routers.myservice-http.rule=Host(`myservice.home.birdcar.dev`)
      - traefik.http.routers.myservice-http.entrypoints=http
      - traefik.http.middlewares.myservice-redirect.redirectscheme.scheme=https
      - traefik.http.routers.myservice-http.middlewares=myservice-redirect
    restart: unless-stopped
networks:
  default:
    external: true
    name: coolify
```
