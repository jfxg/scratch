resource "docker_volume" "traefik_certs" {
  name = "traefik-certs"
}

resource "docker_volume" "portainer_data" {
  name = "portainer-data"
}
