#!/usr/bin/env bash
# Run all agent + shared-package tests hermetically (no network).
# Usage: bash run_tests.sh [pytest-args]
set -euo pipefail
cd "$(dirname "$0")"
exec python3 -m pytest . -q --no-header "$@"
