output "portainer_url" {
  description = "Public URL for the Portainer dashboard"
  value       = "https://${var.portainer_domain}"
}
