# Networking Reference

## Current Architecture

```
Internet → Cloudflare DNS → Tailscale (100.108.157.126) → Traefik → Docker containers
```

- All services are Tailscale-only (not publicly accessible)
- Cloudflare provides DNS-only records (no proxy/CDN)
- Traefik handles TLS termination with Let's Encrypt certs via Cloudflare DNS-01 challenge
- Each `*.home.birdcar.dev` subdomain resolves to the Tailscale IP

## Cloudflare

- **Account email**: nickcannariato@gmail.com
- **Zone**: birdcar.dev
- **API Token scope**: Zone:DNS:Edit for birdcar.dev
- **DNS records**: Wildcard `*.home.birdcar.dev` → 100.108.157.126 (DNS-only, not proxied)
- **Record type**: A record, DNS-only (grey cloud)

### Adding a new subdomain

New subdomains under `*.home.birdcar.dev` are automatically covered by the wildcard record. No Cloudflare changes needed — just configure the service in Coolify with the FQDN.

### Adding a new domain

To add a completely new domain:

1. Add the domain to Cloudflare
2. Create API token with Zone:DNS:Edit for the new zone
3. Add CF credentials to Traefik's environment in `/data/coolify/proxy/docker-compose.yml`
4. Create DNS records pointing to Tailscale IP
5. Traefik will auto-issue certs via DNS-01

## Tailscale

- **Machine name**: nest
- **IP**: 100.108.157.126
- **Auth**: Authenticated via `tailscale up`

### Making a service publicly accessible (Tailscale Funnel)

Tailscale Funnel exposes a service to the public internet through Tailscale's infrastructure:

```bash
# Serve a local port on the tailnet
sudo tailscale serve --bg https+insecure://localhost:PORT

# Make it publicly accessible via funnel
sudo tailscale funnel --bg https+insecure://localhost:PORT
```

The public URL will be `https://nest.tailXXXXX.ts.net/`

**Important considerations**:

- Funnel only works on ports 443, 8443, and 10000
- The public URL uses your Tailscale machine name, not custom domains
- For custom domain public access, use Cloudflare Tunnel instead
- Funnel traffic counts against Tailscale bandwidth limits

### Tailscale Serve (tailnet-only)

For services you want accessible on the tailnet without Traefik:

```bash
sudo tailscale serve --bg --set-path /myservice https+insecure://localhost:PORT
```

## Traefik

- **Version**: 3.6.9
- **Container**: coolify-proxy
- **Config**: `/data/coolify/proxy/docker-compose.yml`
- **ACME storage**: `/data/coolify/proxy/acme.json`
- **Network**: coolify (Docker network)

### Certificate resolver

```
--certificatesresolvers.letsencrypt.acme.email=nickcannariato@gmail.com
--certificatesresolvers.letsencrypt.acme.storage=/traefik/acme.json
--certificatesresolvers.letsencrypt.acme.dnschallenge=true
--certificatesresolvers.letsencrypt.acme.dnschallenge.provider=cloudflare
--certificatesresolvers.letsencrypt.acme.dnschallenge.delaybeforecheck=10
--certificatesresolvers.letsencrypt.acme.dnschallenge.resolvers=1.1.1.1:53,1.0.0.1:53
```

### Troubleshooting certs

1. Check if cert exists: `sudo python3 -c "import json; [print(c['domain']['main']) for c in json.load(open('/data/coolify/proxy/acme.json'))['letsencrypt']['Certificates']]"`
2. Check Traefik logs: `sudo docker logs coolify-proxy 2>&1 | grep -i 'acme\|certificate\|error'`
3. Check container network: `sudo docker network inspect {network} --format '{{range .Containers}}{{.Name}} {{end}}'`
4. Test cert: `curl -vk https://service.home.birdcar.dev 2>&1 | grep 'subject:'`
5. If stuck on TRAEFIK DEFAULT CERT, restart Traefik: `sudo docker restart coolify-proxy`

## Cloudflare Tunnel (for public access with custom domains)

If a service needs to be publicly accessible on a custom domain (not just tailnet):

1. Create a Cloudflare Tunnel: `cloudflared tunnel create nest`
2. Configure the tunnel to route to the local service
3. Add a CNAME record in Cloudflare DNS pointing to the tunnel
4. The tunnel handles TLS — no need for Traefik on the public side

**Note**: This is currently NOT configured. All services are tailnet-only. Implement only when the user explicitly requests public access.

## UFW Firewall

- Default: DROP (incoming)
- Docker subnets allowed: 10.0.0.0/24, 10.0.1.0/24 (for SSH from containers)
- Tailscale traffic bypasses UFW (handled by tailscale0 interface)
