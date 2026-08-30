#!/bin/bash
# Script: verify-omni-route.sh
# Purpose: Verify OmniRoute provider configuration
# Usage: hermes scripts/verify-omni-route.sh

echo "=== OmniRoute Provider Verification ==="
echo "Provider: $(hermes config get model.provider)"
echo "Default model: $(hermes config get model.default)"
echo "Base URL: $(hermes config get model.base_url)"
echo "Key env: $(hermes config get model.key_env)"
echo ""
echo "Checking providers section in config.yaml:"
grep -A 15 "^providers:" ~/.hermes/config.yaml | grep -A 15 omniroute || echo "Provider section not found in expected format"