terraform {
  required_version = ">= 1.6"

  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

locals {
  docker_host       = "ssh://${var.docker_user}@${var.server_domain}"
  docker_ssh_target = "${var.docker_user}@${var.server_domain}"
  portainer_domain  = "portainer.${var.server_domain}"
  traefik_domain    = "traefik.${var.server_domain}"
}

provider "docker" {
  host = local.docker_host
}

resource "terraform_data" "traefik_config_sync" {
  triggers_replace = [
    local.docker_host,
    var.traefik_config_dir,
    filesha256("${path.module}/../traefik/traefik.yml"),
    filesha256("${path.module}/../traefik/dynamic.yml"),
  ]

  provisioner "local-exec" {
    command     = <<-EOT
      set -euo pipefail

      config_dir='${var.traefik_config_dir}'
      src_dir='${path.module}/../traefik'

      ssh_target='${local.docker_ssh_target}'
      ssh "$ssh_target" "mkdir -p '$config_dir'"
      scp "$src_dir/traefik.yml" "$src_dir/dynamic.yml" "$ssh_target:$config_dir/"
    EOT
    interpreter = ["/bin/bash", "-c"]
  }
}
