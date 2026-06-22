#!/usr/bin/env bash
set -euo pipefail

# Создаёт новый foundation-скилл из шаблона.
# Использование: ./tools/new-skill.sh <domain> <skill-name>
# Домены: text, code, productivity, business

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE_DIR="$ROOT/templates/skill-skeleton"
DOMAIN="${1:-}"
NAME="${2:-}"

if [ -z "$DOMAIN" ] || [ -z "$NAME" ]; then
  echo "Usage: $(basename "$0") <domain> <skill-name>"
  echo "Domains: text, code, productivity, business"
  echo "Example: $(basename "$0") code generate-tests"
  exit 1
fi

if [[ ! "$DOMAIN" =~ ^(text|code|productivity|business)$ ]]; then
  echo "Error: domain must be one of: text, code, productivity, business"
  exit 1
fi

if [[ ! "$NAME" =~ ^[a-z0-9_-]+$ ]]; then
  echo "Error: skill name must be lowercase alphanumeric with hyphens or underscores"
  exit 1
fi

DEST="$ROOT/foundation/skills/$DOMAIN/$NAME"
if [ -e "$DEST" ]; then
  echo "Error: $DEST already exists"
  exit 1
fi

mkdir -p "$DEST"
cp -R "$TEMPLATE_DIR/"* "$DEST/"

python3 - "$DEST" "$NAME" <<'PY'
import os
import sys

root, name = sys.argv[1:3]
for dirpath, _dirnames, filenames in os.walk(root):
    for fn in filenames:
        path = os.path.join(dirpath, fn)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            new_content = content.replace("{{SKILL_NAME}}", name)
            if new_content != content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
        except Exception as e:
            print(f"skip {path}: {e}")
PY

echo "✅ Created skill: $DEST"
echo "Next steps:"
echo "  1. Edit $DEST/skill.yaml"
echo "  2. Edit $DEST/prompt.md"
echo "  3. Add 3–5 examples in $DEST/examples.md"
echo "  4. Commit: git add $DEST && git commit -m \"feat(skill): add $NAME\""
