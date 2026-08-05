#!/bin/bash
# Check tests for new Python code
if git diff --cached --name-only | grep -qE "test_.*\.py$"; then
    exit 0
fi
if git diff --cached --name-only | grep -qE "\.py$" && ! git diff --cached --name-only | grep -qE "test_.*\.py$"; then
    echo "WARN: New Python code without test file"
    exit 0
fi
exit 0