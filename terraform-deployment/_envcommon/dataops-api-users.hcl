# ---------------------------------------------------------------------------------------------------------------------
# COMMON TERRAGRUNT CONFIGURATION
# This is the common component configuration for mysql. The common variables for each environment to
# deploy mysql are defined here. This configuration will be merged into the environment configuration
# via an include block.
# ---------------------------------------------------------------------------------------------------------------------

# Terragrunt will copy the Terraform configurations specified by the source parameter, along with any files in the
# working directory, into a temporary folder, and execute your Terraform commands in that folder. If any environment
# needs to deploy a different module version, it should redefine this block with a different ref to override the
# deployed version.
terraform {
  # change to this when going live
  source = "git@github.com:cdatai/line-level-data-collection-terraform.git//api-users?ref=main"
  # for development
#  source = "/Users/david/Desktop/code/line-level-data-collection-platform/terraform-modules//api-users"
}


# ---------------------------------------------------------------------------------------------------------------------
# Locals are named constants that are reusable within the configuration.
# ---------------------------------------------------------------------------------------------------------------------
# terragrunt locals are not the same as terraform locals
# https://terragrunt.gruntwork.io/docs/features/locals/
locals {
  # Automatically load environment-level variables
  environment_vars = read_terragrunt_config(find_in_parent_folders("env.hcl"))
  region_vars      = read_terragrunt_config(find_in_parent_folders("region.hcl"))

  # Extract out common variables for reuse
  env             = local.environment_vars.locals.environment
  region          = local.region_vars.locals.aws_region
  # Expose the base source URL so different versions of the module can be deployed in different environments. This will
  # be used to construct the terraform block in the child terragrunt configurations.
  #  base_source_url = "git::git@github.com:cdatai/line-level-data-collection-terraform.git//line-level-data-collection"
}


# ---------------------------------------------------------------------------------------------------------------------
# MODULE PARAMETERS
# These are the variables we have to pass in to use the module. This defines the parameters that are common across all
# environments.
# ---------------------------------------------------------------------------------------------------------------------
inputs = {
  # put sensitive input like master_password in the environment variable TF_VAR_master_password
  env    = "${local.env}"
  region = "${local.region}"
  prefix = "lldc"
  serverless_app_name = "lldc-verification-app"
  module_name = "verification-app"
}
