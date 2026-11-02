#!/usr/bin/env bash

set -euo pipefail

#########################################
# Author: Christian Javier Zuñiga Mera
# email: christianjmera@gmail.com
#########################################

PROJECT_DIR="${PROJECT_DIR:-${GITHUB_WORKSPACE:-$PWD}}"
TEST_REQUIREMENTS_FILE="${TEST_REQUIREMENTS_FILE:-requirements-dev.txt}"
TEST_PATH="${TEST_PATH:-tests}"

echo "=================================="
echo " Python automated tests"
echo "=================================="

cd "$PROJECT_DIR"

echo "Project directory: $PROJECT_DIR"
echo "Requirements file: $TEST_REQUIREMENTS_FILE"
echo "Test path: $TEST_PATH"

if [[ ! -f "$TEST_REQUIREMENTS_FILE" ]]; then
    echo "ERROR: Requirements file not found"
    exit 1
fi

python -m pip install -r "$TEST_REQUIREMENTS_FILE"

python -m pytest -v "$TEST_PATH"

echo "Tests completed successfully"
