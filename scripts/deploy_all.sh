#!/usr/bin/env bash
set -x
set -e
#### prod config ####
#export PROD_OR_NON_PROD=prod
#export REGION=eu-west-2
#export SERVERLESS_ENVIRONMENT=production
#export TERRAGRUNT_ENVIRONMENT=prod

#### QA config ####
export PROD_OR_NON_PROD=non-prod
export REGION=ap-southeast-1
export SERVERLESS_ENVIRONMENT=qa
export TERRAGRUNT_ENVIRONMENT=qa
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
PROJECT_DIR=$(realpath "$SCRIPT_DIR"/../)

bash "${PROJECT_DIR}/scripts/deploy_terraform.sh"
bash "${PROJECT_DIR}/scripts/migrate_database.sh"
bash "${PROJECT_DIR}/scripts/deploy_serverless.sh"
bash "${PROJECT_DIR}/scripts/deploy_serverless_verification_app.sh"
bash "${PROJECT_DIR}/scripts/create_users.sh"
