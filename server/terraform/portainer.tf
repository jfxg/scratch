resource "docker_image" "portainer" {
  name         = "portainer/portainer-ce:latest"
  keep_locally = true
}

resource "docker_container" "portainer" {
  name    = "portainer"
  image   = docker_image.portainer.image_id
  restart = "always"

  volumes {
    host_path      = "/var/run/docker.sock"
    container_path = "/var/run/docker.sock"
    read_only      = true
  }

  volumes {
    volume_name    = docker_volume.portainer_data.name
    container_path = "/data"
  }

  networks_advanced {
    name = docker_network.traefik.name
  }

  labels {
    label = "traefik.enable"
    value = "true"
  }

  labels {
    label = "traefik.http.routers.portainer.rule"
    value = "Host(`${var.portainer_domain}`)"
  }

  labels {
    label = "traefik.http.routers.portainer.entrypoints"
    value = "https"
  }

  labels {
    label = "traefik.http.routers.portainer.tls.certresolver"
    value = "letsencrypt"
  }

  labels {
    label = "traefik.http.services.portainer.loadbalancer.server.port"
    value = "9000"
  }
}
