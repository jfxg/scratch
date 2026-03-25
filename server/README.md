# server

Terraform-managed foundation for a Docker host: Traefik reverse proxy with automatic HTTPS via Let's Encrypt (Cloudflare DNS-01) and Portainer for container management.

Once deployed, any Docker container on the server can be routed through Traefik by adding labels — no firewall rules or manual certificate management required.

## What gets deployed

| Component | What it does |
|-----------|-------------|
| **Traefik v3** | Reverse proxy. Handles TLS termination, HTTP→HTTPS redirect, and routes traffic to containers via Docker labels or `dynamic.yml`. |
| **Portainer CE** | Web UI for managing Docker on the server. Available at `portainer.<server_domain>`. |
| `traefik` network | Bridge network all proxied containers must join. |
| `traefik-certs` volume | Persists Let's Encrypt certificates across restarts. |
| `portainer-data` volume | Persists Portainer state. |

Service subdomains are derived from `server_domain` automatically:

```
portainer-<server_domain>   →  Portainer UI
traefik-<server_domain>     →  Traefik dashboard
```

## Directory layout

```
server/
├── Makefile                    # init / plan / deploy / destroy targets
├── environments/
│   ├── example.tfvars.example  # template — copy and fill in per server
│   └── <env>.tfvars            # your actual config (gitignored)
├── terraform/                  # Terraform resources
│   ├── main.tf                 # provider, locals, config sync
│   ├── variables.tf            # input variable definitions
│   ├── traefik.tf              # Traefik container
│   ├── portainer.tf            # Portainer container
│   ├── network.tf              # traefik bridge network
│   └── volumes.tf              # named volumes
└── traefik/
    ├── traefik.yml             # static Traefik config (entrypoints, TLS, providers)
    └── dynamic.yml             # live-reloaded routes for non-Docker services
```

## Prerequisites

- **Terraform ≥ 1.6** on the machine you run deploys from
- **SSH access** to the target server as `docker_user` (key-based auth recommended)
- **Docker** running on the target server
- **Cloudflare** managing DNS for `server_domain`, with an API token that has `Zone → DNS → Edit` permission

## Creating an environment

Each server gets its own environment file. The `ENV` name is also used as the Terraform workspace name, so state is isolated per server.

```bash
cp environments/example.tfvars.example environments/home.tfvars
```

Edit `environments/home.tfvars`:

```hcl
server_domain        = "home.example.com"   # SSH target + base for subdomains
docker_user          = "john"               # SSH user on the server
traefik_config_dir   = "/opt/traefik"       # where Terraform uploads Traefik configs
letsencrypt_email    = "you@example.com"
cloudflare_api_token = "your-token"
```

Environment files match `*.tfvars` and are gitignored. The `*.tfvars.example` template is committed.

## Deploying

All commands are run from the `server/` directory. `ENV` defaults to `home`.

```bash
# First time on a new machine — download the Terraform provider
make init ENV=home

# Preview what Terraform will create/change
make plan ENV=home

# Apply changes
make deploy ENV=home

# Tear everything down
make destroy ENV=home
```

`make deploy` will:
1. Select (or create) the `home` Terraform workspace
2. SSH to `docker_user@server_domain` and create `traefik_config_dir`
3. Upload `traefik/traefik.yml` and `traefik/dynamic.yml` to the server
4. Create the `traefik` network, named volumes, and start both containers

After a successful deploy, Portainer is available at `https://portainer-<server_domain>`.

### Multiple servers

Each server gets its own tfvars file and Terraform workspace:

```bash
cp environments/example.tfvars.example environments/lab.tfvars
# fill in lab.tfvars
make deploy ENV=lab
```

Workspaces keep state fully isolated — deploying to `lab` never touches `home`.

## Routing containers through Traefik

Any container on the server can be proxied by joining the `traefik` network and adding labels:

```yaml
# docker-compose.yml
services:
  myapp:
    image: myapp
    networks:
      - traefik
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.myapp.rule=Host(`app.example.com`)"
      - "traefik.http.routers.myapp.entrypoints=https"
      - "traefik.http.routers.myapp.tls.certresolver=letsencrypt"
      - "traefik.http.services.myapp.loadbalancer.server.port=8080"

networks:
  traefik:
    external: true
```

Traefik picks up new containers automatically — no restart required. As long as the domain DNS is managed by the same Cloudflare credentials, Traefik will automatically generate appropriate certs for the app domain.

## Adding routes for non-Docker services

`traefik/dynamic.yml` is bind-mounted into the Traefik container and **hot-reloaded** — edit it on the server and routes take effect within seconds, no restart needed.

Use it for services that aren't in Docker: host-level apps, other machines on the local network, etc.

```yaml
# /opt/traefik/dynamic.yml  (on the server)
http:
  routers:
    adguard:
      rule: "Host(`adguard.home.example.com`)"
      entrypoints:
        - https
      service: adguard-service
      tls:
        certresolver: letsencrypt

  services:
    adguard-service:
      loadBalancer:
        servers:
          - url: "http://host.docker.internal:3080"
```

Backend URL patterns:

| Service location | URL format |
|-----------------|------------|
| Host-level app | `http://host.docker.internal:<port>` |
| Another machine on the network | `http://<local-ip>:<port>` |
| Docker container (by name) | `http://<container-name>:<port>` |

> `dynamic.yml` in this repo is a commented skeleton. Add environment-specific routes directly on each server after deploying — they won't be overwritten unless you re-run `make deploy`.

## Traefik configuration

`traefik/traefik.yml` is the static config (entrypoints, TLS resolver, providers). It is uploaded to the server by Terraform and requires a container restart to take effect after changes.

Key settings:

- HTTP (port 80) permanently redirects to HTTPS (port 443)
- TLS certificates via Let's Encrypt DNS-01 using Cloudflare
- Docker provider watches the `traefik` network; containers must opt in with `traefik.enable=true`
- File provider watches `/dynamic/` for live route updates (`dynamic.yml`)
- Dashboard enabled at `traefik-<server_domain>` (HTTPS, requires auth if you want to restrict access)
