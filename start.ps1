$key = "$env:UserProfile/.ssh/azure-vm-rsa"

cd .\tf

$output = terraform state list

if (-not ($output -match "azurerm_linux_virtual_machine")) {
    echo "Initializing terraform project..."
    $key = "$env:UserProfile/.ssh/azure-vm-rsa"
    ssh-keygen -m PEM -t rsa -b 2048 -f $key -N '""'

    terraform init

    terraform plan -out tp.tfplan

    terraform apply tp.tfplan


} else {
    echo "Terraform project already initialized. Starting up VM..."
}

$rg = terraform output -raw resource_group_name
$vm_name = terraform output -raw vm_name

az vm start --name $vm_name --resource-group $rg

$ip = az vm list-ip-addresses --resource-group $rg --name $vm_name `
    --query "[0].virtualMachine.network.publicIpAddresses[0].ipAddress" --output tsv


cd ..

dos2unix .\scripts\vm-start.sh

# Get-Content .\scripts\vm-start.sh | ssh -i $key azureuser@$ip 'bash -s'

scp -i $key `
    .\scripts\vm-start.sh "azureuser@${ip}:~/vm-start.sh"

ssh -i $key azureuser@$ip

az vm deallocate --name $vm_name --resource-group $rg
