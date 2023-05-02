### Install the dependency

```shell
git submodule update --init
sh install_dependencies_mac.sh
sh install_helper_software.sh
```

### Deployment
* You need to use the production aws account credential for deployment
* You need to download the deployment credential from 1Password in the Research Vault with the name `Line Level Data Collection Deployment Credential`
* To deploy to production env, you'll need to comment out QA config and re-enable production config before running the
  following command

```shell
# if you need to regenerate the openapi client for data validation purposes
bash scripts/update_open_api_dependency.sh
# this command will deploy everything
bash scripts/deploy_all.sh
```
If you want to use other profile
```
AWS_PROFILE=YOUR_PROFILE_NAME AWS_DEFAULT_REGION=ap-southeast-1 bash scripts/deploy_all.sh
```

### FQA
**Missing `terraform.tfvars` file**
Create
```
./terraform-deployment/non-prod/ap-southeast-1/qa/shared-infrastructure/terraform.tfvars
```

**Password for database**
Please ask David or Paco. We will upload it to 1Password later.
```
+ terragrunt apply --terragrunt-working-dir /home/paco/cdatai/line-level-data-collection/terraform-deployment/non-prod/ap-southeast-1/qa/shared-infrastructure
var.db_password
  Enter a value:
```

**What is /Users/david/Desktop/code/**
You need to modify `terraform-deployment/_envcommon/*.hcl`
```
terraform {
  # change to this when going live
  #    source = "git@github.com:cdatai/line-level-data-collection-terraform.git//line-level-data-collection"
  # for development
  source = "/Users/david/Desktop/code/line-level-data-collection-platform/terraform-modules//api-users"
}
```
