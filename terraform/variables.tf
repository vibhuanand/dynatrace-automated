// filename: terraform/variables.tf
variable "name_prefix" {
  type        = string
  description = "Prefix for naming Azure resources"
  default     = "innovizion-dt"
}

variable "location" {
  type        = string
  description = "Azure region"
  default     = "canadacentral"
}

variable "ssh_public_key" {
  type        = string
  description = "SSH public key content for VM access"
}

variable "admin_username" {
  type        = string
  description = "Admin username for the Linux VM"
  default     = "azureuser"
}

variable "vm_size" {
  type        = string
  description = "VM size"
  default     = "Standard_B2ms"
}

variable "allowed_ssh_cidr" {
  type        = string
  description = "CIDR allowed to SSH (lock to your public IP/32)"
  default     = "0.0.0.0/0"
}
