variable "server_domain" {
  description = "Base domain for this server. Used as the SSH target and to derive service subdomains (portainer.<domain>, traefik.<domain>)."
  type        = string
}

variable "docker_user" {
  description = "SSH user for connecting to the Docker host (e.g. john)."
  type        = string
}

variable "traefik_config_dir" {
  description = "Absolute path on the Docker host where Terraform should copy traefik.yml and dynamic.yml before starting Traefik."
  type        = string
  default     = "/opt/traefik"
}

variable "letsencrypt_email" {
  description = "Email address for Let's Encrypt certificate expiry notifications."
  type        = string
}

variable "cloudflare_api_token" {
  description = "Cloudflare API token with Zone → DNS → Edit permission for the domain zone."
  type        = string
  sensitive   = true
}
