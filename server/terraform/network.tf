# Shared network for Traefik and all services it proxies.
# Any container that needs to be reachable via Traefik must join this network.
resource "docker_network" "traefik" {
  name   = "traefik"
  driver = "bridge"
}
