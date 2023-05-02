#!/usr/bin/env bash
set -x
set -e
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
PROJECT_DIR=$(realpath "$SCRIPT_DIR"/../)
#TERRAGRUNT_ENVIRONMENT=prod
#PROD_OR_NON_PROD=prod
#REGION=eu-west-2
#TERRAGRUNT_ENVIRONMENT=qa
#PROD_OR_NON_PROD=non-prod
#REGION=ap-southeast-1

terragrunt apply --terragrunt-working-dir "$PROJECT_DIR/terraform-deployment/$PROD_OR_NON_PROD/$REGION/$TERRAGRUNT_ENVIRONMENT/gn5-api-users"
terragrunt output -json credentials --terragrunt-working-dir "$PROJECT_DIR/terraform-deployment/$PROD_OR_NON_PROD/$REGION/$TERRAGRUNT_ENVIRONMENT/gn5-api-users"

terragrunt apply --terragrunt-working-dir "$PROJECT_DIR/terraform-deployment/$PROD_OR_NON_PROD/$REGION/$TERRAGRUNT_ENVIRONMENT/dataops-api-users"
terragrunt output -json credentials --terragrunt-working-dir "$PROJECT_DIR/terraform-deployment/$PROD_OR_NON_PROD/$REGION/$TERRAGRUNT_ENVIRONMENT/dataops-api-users"
