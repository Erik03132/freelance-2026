#!/bin/bash
# Check CLAUDE.md updated for bugfixes
if git diff --cached --name-only | grep -q "CLAUDE.md"; then
    exit 0
fi
if git log -1 --pretty=%B | grep -qiE "fix|bug|error|crash"; then
    echo "ERROR: Bugfix commit requires CLAUDE.md update"
    exit 1
fi
exit 0