#!/usr/bin/env bash
set -euo pipefail

# Создаёт нового foundation-агента из шаблона.
# Использование: ./tools/new-agent.sh <agent-id>

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE_DIR="$ROOT/templates/agent-skeleton"
AGENT_ID="${1:-}"

if [ -z "$AGENT_ID" ]; then
  echo "Usage: $(basename "$0") <agent-id>"
  echo "Example: $(basename "$0") security-auditor"
  exit 1
fi

if [[ ! "$AGENT_ID" =~ ^[a-z0-9_-]+$ ]]; then
  echo "Error: agent id must be lowercase alphanumeric with hyphens or underscores"
  exit 1
fi

DEST="$ROOT/foundation/agents/$AGENT_ID"
if [ -e "$DEST" ]; then
  echo "Error: $DEST already exists"
  exit 1
fi

mkdir -p "$DEST"
cp -R "$TEMPLATE_DIR/"* "$DEST/"

python3 - "$DEST" "$AGENT_ID" <<'PY'
import os
import sys

root, agent_id = sys.argv[1:3]
for dirpath, _dirnames, filenames in os.walk(root):
    for fn in filenames:
        path = os.path.join(dirpath, fn)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            new_content = content.replace("{{AGENT_ID}}", agent_id)
            if new_content != content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
        except Exception as e:
            print(f"skip {path}: {e}")
PY

echo "✅ Created agent: $DEST"
echo "Next steps:"
echo "  1. Edit $DEST/agent.yaml"
echo "  2. Edit $DEST/prompt.md"
echo "  3. List connected skills in $DEST/skills.json"
echo "  4. Commit: git add $DEST && git commit -m \"feat(agent): add $AGENT_ID\""
