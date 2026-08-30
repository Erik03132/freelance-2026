#!/usr/bin/env bash
# First smoke-test call to the Nous Research Inference API.
# Usage: NOUS_API_KEY=sk-... bash first_request.sh
set -euo pipefail

: "${NOUS_API_KEY:?Set NOUS_API_KEY (from portal.nousresearch.com -> Settings -> API Keys)}"

curl -sS https://inference-api.nousresearch.com/v1/chat/completions \
  -H "Authorization: Bearer ${NOUS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nousresearch/hermes-4-70b",
    "messages": [{"role":"user","content":"Привет, ты работаешь?"}],
    "max_tokens": 100
  }' | python3 -m json.tool
