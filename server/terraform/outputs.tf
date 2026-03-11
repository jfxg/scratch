output "portainer_url" {
  description = "Public URL for the Portainer dashboard"
  value       = "https://${local.portainer_domain}"
}
