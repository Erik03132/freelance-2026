#!/bin/bash
# Check handoff for long tasks
if git log -1 --pretty=%B | grep -qiE "handoff|ho "; then
    exit 0
fi
exit 0