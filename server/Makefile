# Usage:
#   make init    ENV=home   # Initialize Terraform (run once per machine)
#   make plan    ENV=home   # Preview changes
#   make deploy  ENV=home   # Apply changes
#   make destroy ENV=home   # Tear down all resources
#
# ENV corresponds to environments/<ENV>.tfvars.
# Copy environments/example.tfvars.example to environments/<ENV>.tfvars and fill it in.

ENV    ?= home
TFVARS  = ../environments/$(ENV).tfvars
TF      = cd terraform && terraform

.PHONY: init plan deploy destroy

init:
	$(TF) init

plan: _workspace
	$(TF) plan -var-file=$(TFVARS)

deploy: _workspace
	$(TF) apply -var-file=$(TFVARS)

destroy: _workspace
	$(TF) destroy -var-file=$(TFVARS)

# Select (or create) the workspace for the target environment.
.PHONY: _workspace
_workspace: init
	cd terraform && (terraform workspace select $(ENV) 2>/dev/null || terraform workspace new $(ENV))
