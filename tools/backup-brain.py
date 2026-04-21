#!/usr/bin/env python3
"""
🛡️ ANTIGRAVITY BRAIN BACKUP — Agent-Side Copier
=================================================
Этот скрипт НЕ вызывается напрямую из терминала (TCC блокирует ~/.gemini).
Вместо этого, его логика встроена в workflow Antigravity-агента.

Чтобы запустить бэкап, скажите агенту: "Сделай бэкап мозга"

Агент:
1. Прочитает файлы из ~/.gemini/antigravity/ (у него есть доступ)
2. Скопирует их в tools/.backup-staging/antigravity-brain/
3. Запустит tools/antigravity-backup.sh для архивации

Этот файл — документация процесса.
"""

BACKUP_MANIFEST = {
    "critical": [
        "skills/kulibin-engineer/SKILL.md",
        "skills/marketer-strategist/SKILL.md",
        "skills/shakespeare-editor/SKILL.md",
        "skills/sherl-research/SKILL.md",
        "knowledge/agent-standards/metadata.json",
        "knowledge/gbp-protocol/metadata.json",
        "knowledge/gbp-protocol/timestamps.json",
        "knowledge/pricing-rules/metadata.json",
        "knowledge/pricing-rules/timestamps.json",
        "knowledge/pricing-rules/artifacts/pricing_constitution.md",
        "knowledge/knowledge.lock",
        "GLOBAL_CORE_STANDARDS.md",
        "GLOBAL_STATUS_MANIFEST.md",
        "mcp_config.json",
        "installation_id",
    ],
    "important": [
        "implicit/",  # ~30 .pb files with learned contexts
        "shared/logic/",
        "annotations/",
        "prompting/browser/",
    ],
    "optional": [
        "brain/",  # conversation logs (can be large)
    ]
}

RESTORE_INSTRUCTIONS = """
# 🔄 Инструкция по восстановлению

## После переустановки Antigravity:

1. Найдите последний бэкап:
   ls -lahtr ~/antigravity-backups/

2. Запустите восстановление:
   ./tools/antigravity-backup.sh --restore ~/antigravity-backups/<архив>.tar.gz

3. Перезапустите Antigravity

4. Проверьте:
   - Скиллы загружены? (видны в списке skills)
   - Knowledge Items на месте? (видны в подсказках)
   - MCP серверы подключены? (проверить в настройках)

## Если нужно восстановить только скиллы:
   tar -xzf <архив>.tar.gz antigravity-brain/skills/
   cp -R antigravity-brain/skills/* ~/.gemini/antigravity/skills/
"""

if __name__ == "__main__":
    print(__doc__)
    print(RESTORE_INSTRUCTIONS)
