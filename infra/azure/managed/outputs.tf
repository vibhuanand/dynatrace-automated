locals {
  hosts = {
    oneagent01 = {
      ip     = azurerm_public_ip.oneagent.ip_address
      user   = var.admin_username
      groups = ["oneagent"]
    }
    activegate01 = {
      ip     = azurerm_public_ip.activegate.ip_address
      user   = var.admin_username
      groups = ["activegate"]
    }
  }

  all_groups = sort(distinct(flatten([for _, h in local.hosts : h.groups])))

  inventory_blocks = [
    for g in local.all_groups : join("\n", concat(
      ["[${g}]"],
      [
        for name, h in local.hosts :
        "${name} ansible_host=${h.ip} ansible_user=${h.user}"
        if contains(h.groups, g)
      ],
      [""]
    ))
  ]

  ansible_inventory = join("\n", local.inventory_blocks)
}

output "hosts" { value = local.hosts }
output "ansible_inventory" { value = local.ansible_inventory }
