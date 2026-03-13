# nest Server Configuration

## Hardware & OS

- **Machine**: Beelink mini PC (Ryzen 9 6900HX, 16 cores, 30GB RAM)
- **OS**: CachyOS (Arch-based), kernel 6.19.3-2-cachyos
- **User**: birdcar (UID 1000, GID 1000), shell: fish
- **Passwordless sudo**: configured
- **Timezone**: America/Chicago

## Storage

- **NVMe** (477GB): OS, configs at `/srv/docker/`, Coolify data at `/data/coolify/`
- **External HDD** (18TB ext4): UUID `dfc6637e`, label "mediastore", mounted at `/mnt/mediastore` (fstab, nofail)
- **Media paths**: `/mnt/mediastore/media/{movies,tv,music,books,audiobooks}`
- **Download paths**: `/mnt/mediastore/downloads/{complete,torrents,usenet}`
- **SABnzbd incomplete**: `/srv/downloads-temp/incomplete` (NVMe for speed)

## Network

- **Tailscale IP**: 100.108.157.126 (machine name: nest)
- **Domain**: birdcar.dev (Cloudflare-managed)
- **Wildcard**: `*.home.birdcar.dev` → 100.108.157.126 (DNS-only, not proxied)
- **UFW**: Active with DROP default. Docker subnets 10.0.0.0/24 and 10.0.1.0/24 allowed for SSH
- **VPN**: Mullvad WireGuard, server: Chicago IL

## Coolify

- **URL**: https://coolify.home.birdcar.dev (or http://100.108.157.126:8000)
- **Version**: 4.0.0-beta.463 (update pending)
- **Proxy**: Traefik v3.6, Cloudflare DNS-01 ACME challenge
- **Server UUID**: cc8skgwss8ckokoos4go8wsw
- **DNS validation**: Disabled (Tailscale IP != public IP)
- **DB access**: `sudo docker exec coolify-db psql -U coolify`

## Projects & Environments

| Project      | UUID                     | Env UUID                 |
| ------------ | ------------------------ | ------------------------ |
| Media Server | h8occ4cs4kosg408gwg008k4 | aw00cgw8s84sw0kgows80sk0 |
| Automation   | no44ss08k4og0444gk8gcgo8 | w0g0kgs8cg04gggoswog8sss |
| Meta         | bwgos8c84w44s0o8so4wk04o | wg8o0osk0ws4k8w0g8g0gk8w |
| Carli        | gg0o4kkokgc8kg4k04coc80o | vk0gg48owk4444swss0g8ssc |
| Crystal      | d8cso40ogck4ko0k0cck0sgw | x8wok40sck0sow88kg08c0g4 |
| Nick         | j40kg0sckok0wc4sgk44ssss | xs04ososcc04wkk0c44ckssk |

## Services

### Media Server Project

| Service        | UUID                     | Container                               | Port        | URL                         |
| -------------- | ------------------------ | --------------------------------------- | ----------- | --------------------------- |
| Jellyfin       | fwoo8cos8ok4kgkcgko8c4c8 | jellyfin-fwoo8cos8ok4kgkcgko8c4c8       | 8096        | jellyfin.home.birdcar.dev   |
| Prowlarr       | hosc888ok4swowsoskwck80g | prowlarr-hosc888ok4swowsoskwck80g       | 9696        | prowlarr.home.birdcar.dev   |
| Sonarr         | w0wwc800gsoskwsw0so0csoo | sonarr-w0wwc800gsoskwsw0so0csoo         | 8989        | sonarr.home.birdcar.dev     |
| Radarr         | ccg80kgscgk0ks8wcgk4cswk | radarr-ccg80kgscgk0ks8wcgk4cswk         | 7878        | radarr.home.birdcar.dev     |
| Bazarr         | tkk8c0gk8cokg0804o4c4k4o | bazarr-tkk8c0gk8cokg0804o4c4k4o         | 6767        | bazarr.home.birdcar.dev     |
| Jellyseerr     | okokgwwo8kgkoggsokowsg0c | jellyseerr-okokgwwo8kgkoggsokowsg0c     | 5055        | jellyseerr.home.birdcar.dev |
| Lidarr         | x4s8w4080w800k8wc80wk844 | lidarr-x4s8w4080w800k8wc80wk844         | 8686        | lidarr.home.birdcar.dev     |
| Download Stack | akcckc48k808gs80c8g0cc4o | gluetun-akcckc48k808gs80c8g0cc4o        | 8080 (qbit) | qbit.home.birdcar.dev       |
| SABnzbd        | is8gowkk4kw4gscko8co8sw4 | sabnzbd-is8gowkk4kw4gscko8co8sw4        | 8085        | sabnzbd.home.birdcar.dev    |
| Recyclarr      | hwswg8c80wsoos4444c0so8c | recyclarr-hwswg8c80wsoos4444c0so8c      | —           | —                           |
| LazyLibrarian  | ro0ww4g8o0ss08wogg0oc0k8 | lazylibrarian-ro0ww4g8o0ss08wogg0oc0k8  | 5299        | librarian.home.birdcar.dev  |
| Kavita         | yoosgwc0o4kkgsgwcgc0w4wc | kavita-yoosgwc0o4kkgsgwcgc0w4wc         | 5000        | books.home.birdcar.dev      |
| Audiobookshelf | qgkggo8kskw84w4s4csccw0s | audiobookshelf-qgkggo8kskw84w4s4csccw0s | 80          | audiobooks.home.birdcar.dev |

### Automation Project

| Service        | UUID                     | URL                        |
| -------------- | ------------------------ | -------------------------- |
| Home Assistant | z4owssssg8o48c0848okwsc0 | assistant.home.birdcar.dev |
| n8n            | (check API)              | n8n.home.birdcar.dev       |

### Meta Project

| Service | UUID                     | URL                                        |
| ------- | ------------------------ | ------------------------------------------ |
| Glance  | l0cws0skkokg08k44g4ocswc | home.birdcar.dev / glance.home.birdcar.dev |

### Nick Project

| Service  | UUID                     | URL                       |
| -------- | ------------------------ | ------------------------- |
| Castopod | ksokwkssgc80wog008c48wok | castopod.home.birdcar.dev |

## Volume Mount Patterns

Most services use one of these patterns:

```yaml
# Full mediastore access (Sonarr, Radarr, Lidarr, LazyLibrarian)
volumes:
  - '/srv/docker/{service}:/config'
  - '/mnt/mediastore:/mnt/mediastore'

# Read-only media access (Jellyfin)
volumes:
  - '/srv/docker/jellyfin:/config'
  - '/mnt/mediastore/media:/media:ro'

# Download access only (SABnzbd, download-stack)
volumes:
  - '/srv/docker/{service}:/config'
  - '/mnt/mediastore/downloads:/downloads'

# Specific library access (Kavita, Audiobookshelf)
volumes:
  - '/mnt/mediastore/media/books:/books'        # Kavita
  - '/mnt/mediastore/media/audiobooks:/audiobooks:ro'  # Audiobookshelf
```

## Inter-Service Communication

Services on the `coolify` network reference each other by container name:

- qBittorrent: `gluetun-akcckc48k808gs80c8g0cc4o:8080`
- SABnzbd: `sabnzbd-is8gowkk4kw4gscko8co8sw4:8085`
- Sonarr: `sonarr-w0wwc800gsoskwsw0so0csoo:8989`
- Radarr: `radarr-ccg80kgscgk0ks8wcgk4cswk:7878`
- Prowlarr: `prowlarr-hosc888ok4swowsoskwck80g:9696`
- Lidarr: `lidarr-x4s8w4080w800k8wc80wk844:8686`
- Jellyfin: `jellyfin-fwoo8cos8ok4kgkcgko8c4c8:8096`
- Bazarr: `bazarr-tkk8c0gk8cokg0804o4c4k4o:6767`

## Usenet

- **Primary**: Newshosting (UNS Holdings backbone), 100 connections, port 563, SSL
- **Backup**: ViperNews block account (own backbone), priority 1, 40 connections

## Beets (Music tagging)

- Installed via uv, config at `~/.config/beets/config.yaml`
- Watcher: `beets-watcher.service` (systemd user service), watches `/mnt/mediastore/media/music/`
- 60s debounce, 90%+ auto-accept threshold
