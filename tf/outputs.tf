output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "public_ip_address" {
  value = azurerm_linux_virtual_machine.lnx-tf-vm.public_ip_address
}

output "tls_private_key" {
  value     = tls_private_key.lnx-tf-ssh.private_key_pem
  sensitive = true
}

output "vm_name" {
  value = azurerm_linux_virtual_machine.lnx-tf-vm.name
}
