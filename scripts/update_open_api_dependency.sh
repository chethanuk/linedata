#!/usr/bin/env bash
set -x
set -e

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
PROJECT_DIR=$(realpath "$SCRIPT_DIR"/../)

# clean up
rm -rf "$PROJECT_DIR"/line-level-data-collection/external

# regenerate
if [[ $(uname) == "Linux" ]]; then
  bash "${PROJECT_DIR}/scripts/openapi_codegen.sh" true
elif [[ $(uname) == "Darwin" ]]; then
  bash "${PROJECT_DIR}/scripts/openapi_codegen.sh"
else
  echo "This operating system is not supported"
fi

# sync to target dir
mkdir "${PROJECT_DIR}"/line-level-data-collection/external
cp -r "${PROJECT_DIR}"/out/openapi/python/gn5-client "${PROJECT_DIR}"/line-level-data-collection/external/gn5-client

