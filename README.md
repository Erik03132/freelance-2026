# freelance-2026

Портфель фриланс-проектов (Levitan, AI-Scout, AI-Eggs, Angel-backend, HH-AI-Agent, Sinergy и др.).

## Setup после клонирования

```bash
# 1. Окружение: скопировать секреты (gitignored)
cp .env.example .env
# (или восстановить .env из бэкапа — ключи ротированы, см. SECRETS_ROTATION.md)

# 2. Pre-commit хуки (gitleaks no-secrets, ruff, check-claude-md/adr/tests/context/handoff)
pip install pre-commit gitleaks
pre-commit install

# 3. Хук-скрипты уже в репо (githooks/), их копировать не нужно.
#    Проверка: pre-commit run --all-files
```

Хуки: `.pre-commit-config.yaml` → `githooks/*.sh` (версионируются). После клона достаточно `pre-commit install`.

Секреты: см. `SECRETS_ROTATION.md` — список ключей, которые были в git-истории (репо был публичным до 02.08.2026) и требуют ротации.
