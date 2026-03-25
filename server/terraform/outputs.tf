output "portainer_url" {
  description = "Public URL for the Portainer dashboard"
  value       = "https://${local.portainer_domain}"
}

output "traefik_url" {
  description = "Public URL for the Traefik dashboard"
  value       = "https://${local.traefik_domain}"
}