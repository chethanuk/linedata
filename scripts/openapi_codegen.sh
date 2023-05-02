#!/usr/bin/env bash
set -x
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_DIR=$(realpath "$SCRIPT_DIR"/..)
OUTPUT_ROOT_DIR=$(realpath "$PROJECT_DIR"/out/openapi)

# https://stackoverflow.com/a/33427572
rm -rf "$OUTPUT_ROOT_DIR" || :

mkdir -p "$OUTPUT_ROOT_DIR"

# Set default value for use_opengen_npm variable
default_use_opengen_npm=false
# Set variables using command-line arguments or default value
use_opengen_npm=${1:-$default_use_opengen_npm}

if [ "$use_opengen_npm" = true ]; then
  echo "Using openapi-generator from NPM installation"
  openapi-generator-cli generate \
    --input-spec "$PROJECT_DIR"/doc/openapi.yaml \
    --generator-name python \
    --output "$OUTPUT_ROOT_DIR"/python/gn5-client

  openapi-generator-cli generate \
    --input-spec "$PROJECT_DIR"/doc/dataops_api.yaml \
    --generator-name python \
    --output "$OUTPUT_ROOT_DIR"/python/dataops_api  
else
  echo "Not default Java generator"
  _JAVA_OPTIONS="--add-opens=java.base/java.lang=ALL-UNNAMED --add-opens=java.base/java.util=ALL-UNNAMED" \
    openapi-generator generate \
    --input-spec "$PROJECT_DIR"/doc/openapi.yaml \
    --generator-name python \
    --output "$OUTPUT_ROOT_DIR"/python/gn5-client

  _JAVA_OPTIONS="--add-opens=java.base/java.lang=ALL-UNNAMED --add-opens=java.base/java.util=ALL-UNNAMED" \
    openapi-generator generate \
    --input-spec "$PROJECT_DIR"/doc/dataops_api.yaml \
    --generator-name python \
    --output "$OUTPUT_ROOT_DIR"/python/dataops_api
fi
