#!/usr/bin/env bash
set -x
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_DIR=$(realpath "$SCRIPT_DIR"/../)
ENVIRONMENT=staging
PROD_OR_NON_PROD=non-prod

# shellcheck disable=SC2164
cd "$PROJECT_DIR"/line-level-data-collection && serverless remove --stage $ENVIRONMENT && cd -

terragrunt destroy --terragrunt-working-dir "$PROJECT_DIR/terraform-deployment/$PROD_OR_NON_PROD/ap-southeast-1/$ENVIRONMENT/line-level-data-collection"
