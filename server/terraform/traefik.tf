locals {
  # Server-side path to server/traefik/. Must resolve on the Docker host (the
  # server), not on the machine running Terraform. Set via var.traefik_config_dir.
  traefik_config_dir = var.traefik_config_dir
}

resource "docker_image" "traefik" {
  name         = "traefik:v3.1"
  keep_locally = true
}

resource "docker_container" "traefik" {
  name    = "traefik"
  image   = docker_image.traefik.image_id
  restart = "always"

  depends_on = [terraform_data.traefik_config_sync]

  # CLI args that complement traefik.yml.
  # The email is passed here so traefik.yml can stay a static file in the repo.
  command = [
    "--certificatesresolvers.letsencrypt.acme.email=${var.letsencrypt_email}",
  ]

  env = [
    "CF_DNS_API_TOKEN=${var.cloudflare_api_token}",
  ]

  # Static Traefik configuration
  volumes {
    host_path      = "${local.traefik_config_dir}/traefik.yml"
    container_path = "/etc/traefik/traefik.yml"
    read_only      = true
  }

  # Dynamic routing configuration (custom routes for non-Docker services)
  volumes {
    host_path      = "${local.traefik_config_dir}/dynamic.yml"
    container_path = "/dynamic/dynamic.yml"
    read_only      = true
  }

  # Let's Encrypt certificate storage — persisted in a named volume
  volumes {
    volume_name    = docker_volume.traefik_certs.name
    container_path = "/letsencrypt"
  }

  # Docker socket — required for label-based container discovery
  volumes {
    host_path      = "/var/run/docker.sock"
    container_path = "/var/run/docker.sock"
    read_only      = true
  }

  ports {
    internal = 80
    external = 80
  }

  ports {
    internal = 443
    external = 443
  }

  networks_advanced {
    name = docker_network.traefik.name
  }

  # On Linux, host.docker.internal is not automatically resolvable inside
  # containers (unlike Docker Desktop on Mac/Windows). This adds the mapping
  # so dynamic.yml can use host.docker.internal to reach host-level services.
  host {
    host = "host.docker.internal"
    ip   = "host-gateway"
  }

  labels {
    label = "traefik.enable"
    value = "true"
  }

  labels {
    label = "traefik.http.routers.traefik-dashboard.rule"
    value = "Host(`${local.traefik_domain}`)"
  }

  labels {
    label = "traefik.http.routers.traefik-dashboard.entrypoints"
    value = "https"
  }

  labels {
    label = "traefik.http.routers.traefik-dashboard.tls.certresolver"
    value = "letsencrypt"
  }

  labels {
    label = "traefik.http.routers.traefik-dashboard.service"
    value = "api@internal"
  }
}
