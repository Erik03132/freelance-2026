#!/usr/bin/env bash
set -euo pipefail

# Создаёт новый проект из шаблона /templates/project-skeleton/
# Использование: ./tools/new-project.sh <project-name>

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE_DIR="$ROOT/templates/project-skeleton"
PROJECTS_DIR="$ROOT/projects"
NAME="${1:-}"

if [ -z "$NAME" ]; then
  echo "Usage: $(basename "$0") <project-name>"
  echo "Example: $(basename "$0") ai-sales-assistant"
  exit 1
fi

if [[ ! "$NAME" =~ ^[a-z0-9_-]+$ ]]; then
  echo "Error: project name must be lowercase alphanumeric with hyphens or underscores"
  exit 1
fi

DEST="$PROJECTS_DIR/$NAME"
if [ -e "$DEST" ]; then
  echo "Error: $DEST already exists"
  exit 1
fi

mkdir -p "$PROJECTS_DIR"
cp -R "$TEMPLATE_DIR" "$DEST"
DATE=$(date +%Y-%m-%d)

python3 - "$DEST" "$NAME" "$DATE" <<'PY'
import os
import sys

root, name, date = sys.argv[1:4]

for dirpath, _dirnames, filenames in os.walk(root):
    for fn in filenames:
        path = os.path.join(dirpath, fn)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            new_content = content.replace("{{PROJECT_NAME}}", name).replace("{{DATE}}", date)
            if new_content != content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
        except Exception as e:
            print(f"skip {path}: {e}")
PY

echo "✅ Created project: $DEST"
echo ""
echo "Next steps:"
echo "  1. Edit $DEST/config/project.yaml"
echo "  2. Edit $DEST/docs/overview.md"
echo "  3. Add project-specific skills to $DEST/project-skills/"
echo "  4. Add project-specific agents to $DEST/project-agents/"
echo "  5. Commit: git add $DEST && git commit -m \"chore: init project $NAME\""
