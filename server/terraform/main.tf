terraform {
  required_version = ">= 1.6"

  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {
  # Target Docker daemon is set via docker_host in terraform.tfvars.
  # Use ssh://user@host to target a remote server from your laptop.
  # Use unix:///var/run/docker.sock to target the local machine.
  host = var.docker_host
}

locals {
  docker_host_is_ssh = startswith(var.docker_host, "ssh://")
  docker_ssh_target  = local.docker_host_is_ssh ? trimprefix(var.docker_host, "ssh://") : ""
}

resource "terraform_data" "traefik_config_sync" {
  triggers_replace = [
    var.docker_host,
    var.traefik_config_dir,
    filesha256("${path.module}/../traefik/traefik.yml"),
    filesha256("${path.module}/../traefik/dynamic.yml"),
  ]

  provisioner "local-exec" {
    command     = <<-EOT
      set -euo pipefail

      config_dir='${var.traefik_config_dir}'
      src_dir='${path.module}/../traefik'

      if [[ '${var.docker_host}' == ssh://* ]]; then
        ssh_target='${local.docker_ssh_target}'
        ssh "$ssh_target" "mkdir -p '$config_dir'"
        scp "$src_dir/traefik.yml" "$src_dir/dynamic.yml" "$ssh_target:$config_dir/"
      else
        mkdir -p "$config_dir"
        cp "$src_dir/traefik.yml" "$src_dir/dynamic.yml" "$config_dir/"
      fi
    EOT
    interpreter = ["/bin/bash", "-c"]
  }
}
