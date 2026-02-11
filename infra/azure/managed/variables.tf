variable "location" { type = string, default = "canadacentral" }
variable "prefix"   { type = string, default = "dt" }

variable "admin_username" { type = string, default = "azureuser" }
variable "ssh_public_key" { type = string }

variable "vm_size" { type = string, default = "Standard_B2s" }
