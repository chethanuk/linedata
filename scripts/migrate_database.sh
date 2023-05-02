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

DB_HOST="$(terragrunt output -raw rds_host_name --terragrunt-working-dir "$PROJECT_DIR/terraform-deployment/$PROD_OR_NON_PROD/$REGION/$TERRAGRUNT_ENVIRONMENT/shared-infrastructure")"
DB_PORT="$(terragrunt output -raw rds_port --terragrunt-working-dir "$PROJECT_DIR/terraform-deployment/$PROD_OR_NON_PROD/$REGION/$TERRAGRUNT_ENVIRONMENT/shared-infrastructure")"
DB_USERNAME="$(terragrunt output -raw rds_user_name --terragrunt-working-dir "$PROJECT_DIR/terraform-deployment/$PROD_OR_NON_PROD/$REGION/$TERRAGRUNT_ENVIRONMENT/shared-infrastructure")"
DB_PASSWORD="$(terragrunt output -raw rds_user_password --terragrunt-working-dir "$PROJECT_DIR/terraform-deployment/$PROD_OR_NON_PROD/$REGION/$TERRAGRUNT_ENVIRONMENT/shared-infrastructure")"
DB_NAME="$(terragrunt output -raw rds_db_name --terragrunt-working-dir "$PROJECT_DIR/terraform-deployment/$PROD_OR_NON_PROD/$REGION/$TERRAGRUNT_ENVIRONMENT/shared-infrastructure")"

FLYWAY_DB_URL="jdbc:postgresql://${DB_HOST}:${DB_PORT}/${DB_NAME}" \
  FLYWAY_USER="${DB_USERNAME}" \
  FLYWAY_PASSWORD="${DB_PASSWORD}" \
  flyway -locations="filesystem:${PROJECT_DIR}/line-level-data-collection/db_migration/sql" \
  -configFiles="${PROJECT_DIR}/line-level-data-collection/db_migration/conf/flyway.conf" \
  migrate
