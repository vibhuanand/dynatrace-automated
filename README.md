<!-- filename: README.md -->
# Innovizion Dynatrace End-to-End Automation (Azure + Terraform)

This repo automates Dynatrace end-to-end:

1. Terraform provisions Azure infrastructure (VM used as ActiveGate + OneAgent demo host).
2. Ansible installs Dynatrace ActiveGate + OneAgent.
3. Monaco applies Dynatrace configuration as code (MZ, tags, dashboards, alert profiles, SLOs).
4. Dynatrace API scripts validate and export audit evidence.
5. GitHub Actions orchestrates the full pipeline.

## Prerequisites
- Dynatrace tenant (SaaS or Managed)
- API token (config + read access)
- PaaS token (download installers)
- Azure subscription + service principal

## GitHub Secrets required
Azure:
- AZURE_CREDENTIALS
- ARM_SUBSCRIPTION_ID, ARM_TENANT_ID, ARM_CLIENT_ID, ARM_CLIENT_SECRET

Dynatrace:
- DT_TENANT_URL
- DT_API_TOKEN
- DT_PAAS_TOKEN

SSH:
- SSH_PRIVATE_KEY
- SSH_USER (azureuser)

## How it works
- `terraform/` creates RG, VNet, subnet, NSG, Linux VM, Public IP
- `ansible/` installs Dynatrace ActiveGate + OneAgent
- `dynatrace/monaco/` deploys Dynatrace config
- `dynatrace/api/` validates + exports audit JSON to artifacts
