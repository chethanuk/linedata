#!/usr/bin/env bash
set -x
set -e
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
PROJECT_DIR=$(realpath "$SCRIPT_DIR"/../)
#SERVERLESS_ENVIRONMENT=production
#SERVERLESS_ENVIRONMENT=qa

cd "$PROJECT_DIR"/line-level-data-collection && serverless deploy --config serverless_verification_module.yml --verbose --stage $SERVERLESS_ENVIRONMENT && cd -
# print stack output
cd "$PROJECT_DIR"/line-level-data-collection && serverless info --config serverless_verification_module.yml --verbose --stage $SERVERLESS_ENVIRONMENT && cd -
