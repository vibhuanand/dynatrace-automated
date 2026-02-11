# dynatrace-automated

Infrastructure + Dynatrace configuration as code.

You define a deployment in a YAML plan (with optional imports). A renderer compiles it into:
- **Terraform** (Azure infra for Managed) → outputs host inventory
- **Ansible** (rolls out OneAgent/ActiveGate using Dynatrace Deployment API)
- **Monaco** (applies tenant config: SLOs, alerting, zones, tags, synthetics, dashboards)

Pipeline flow: **Plan → Render → (Terraform outputs) → Inventory → Ansible → Monaco**.

<WIP>