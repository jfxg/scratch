variable "docker_host" {
  description = "Docker daemon to target. Use ssh://user@host for a remote server, or unix:///var/run/docker.sock for local."
  type        = string
  default     = "unix:///var/run/docker.sock"
}

variable "traefik_config_dir" {
  description = "Absolute path on the Docker host where Terraform should copy traefik.yml and dynamic.yml before starting Traefik."
  type        = string
  default     = "/opt/scratch/server/traefik"
}

variable "letsencrypt_email" {
  description = "Email address for Let's Encrypt certificate expiry notifications"
  type        = string
}

variable "cloudflare_api_token" {
  description = "Cloudflare API token with Zone → DNS → Edit permission for the domain zone"
  type        = string
  sensitive   = true
}

variable "traefik_dashboard_domain" {
  description = "Optional: domain for the Traefik dashboard (leave empty to disable). E.g. traefik.home.gaquin.dev"
  type        = string
  default     = ""
}

variable "portainer_domain" {
  description = "Domain for the Portainer UI. E.g. portainer.home.gaquin.dev"
  type        = string
}
