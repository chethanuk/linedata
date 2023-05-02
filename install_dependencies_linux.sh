
apt-get update && sudo apt-get install -y gnupg software-properties-common
wget -O- https://apt.releases.hashicorp.com/gpg | \
	gpg --dearmor | \
	sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg

gpg --no-default-keyring \
	--keyring /usr/share/keyrings/hashicorp-archive-keyring.gpg \
	--fingerprint
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
	https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \
	sudo tee /etc/apt/sources.list.d/hashicorp.list
apt update && apt-get install terraform
touch ~/.bashrc
terraform -install-autocomplete

apt-get install libpq-dev python-dev
pip install --upgrade pip setuptools

wget https://github.com/gruntwork-io/terragrunt/releases/download/v0.45.0/terragrunt_linux_amd64
mv terragrunt_linux_amd64 terragrunt
chmod u+x terragrunt
mv terragrunt /usr/local/bin/terragrunt

snap install flyway
npm install -g serverless@3.26.0

cd line-level-data-collection
bash serverless_dependency_install.sh

# Install openapi-generator https://openapi-generator.tech/docs/installation/#npm
npm install @openapitools/openapi-generator-cli -g
openapi-generator-cli version-manager set 6.5.0