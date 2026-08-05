#!/bin/bash
# Check ADR for architectural changes
if git diff --cached --name-only | grep -qE "docs/adr/ADR-"; then
    exit 0
fi
if git log -1 --pretty=%B | grep -qiE "arch|architecture|refactor|design|migrate"; then
    echo "ERROR: Architectural change requires ADR"
    exit 1
fi
exit 0