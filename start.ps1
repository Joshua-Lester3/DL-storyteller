$key = "$env:UserProfile/.ssh/azure-vm-rsa"
ssh-keygen -m PEM -t rsa -b 2048 -f $key -N '""'

cd .\tf

terraform init

terraform plan -out tp.tfplan

terraform apply tp.tfplan

$ip = terraform output -raw public_ip_address

cd ..

dos2unix .\scripts\vm-start.sh

# Get-Content .\scripts\vm-start.sh | ssh -i $key azureuser@$ip 'bash -s'

scp -i $key .\scripts\vm-start.sh "azureuser@${ip}:~/vm-start.sh"

ssh -i $key azureuser@$ip

cd .\tf

terraform destroy -auto-approve

cd ..
