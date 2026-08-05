#!/bin/bash
# Check CONTEXT.md for new domain terms
if git diff --cached --name-only | grep -q "CONTEXT.md"; then
    exit 0
fi
if git log -1 --pretty=%B | grep -qiE "new|add|implement|feature"; then
    echo "WARN: New feature may need CONTEXT.md update"
    exit 0
fi
exit 0