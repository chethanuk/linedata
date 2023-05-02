# Set account-wide variables. These are automatically pulled in to configure the remote state bucket in the root
# terragrunt.hcl configuration.
locals {
  account_name   = "david"
  aws_account_id = "308382289355"
  aws_profile    = "production"
}
