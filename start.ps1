$key = "$env:UserProfile/.ssh/azure-vm-rsa"
ssh-keygen -m PEM -t rsa -b 2048 -f $key -N '""'

terraform init

terraform plan -out tp.tfplan

terraform apply tp.tfplan

$ip = terraform output -raw public_ip_address

ssh -i $key azureuser@$ip

terraform destroy -auto-approve
