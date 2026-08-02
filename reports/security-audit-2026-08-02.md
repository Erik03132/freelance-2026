# 🔐 Security Audit — 2026-08-02

**Инструменты:** ai-defender (статический scan) · gitleaks 8.30.1 · bandit 1.9.4 · pip-audit 2.10.1
**Данные:** `reports/gitleaks-2026-08-02.json` (71 находка, 165 коммитов)

## CRITICAL — живые секреты в git (нужна ротация)

Репозиторий `freelance-2026` закоммичен в GitHub (`origin https://github.com/Erik03132/freelance-2026.git`).
Следующие живые секреты находятся в рабочем дереве И истории → **считаются скомпрометированными**.

| Файл | Что утекло | Статус |
|------|-----------|--------|
| `opencode.json` | Funpay API-ключ (`Funpay_MYbt...`) | 🔴 в дереве + история |
| `tools/omni-auto-router/omniroute-recover.sh` | JWT_SECRET, API_KEY_SECRET, INITIAL_PASSWORD (пароль OmniRoute) | 🔴 в дереве + история |
| `.backups/antigravity-brain/session_backup_apr15_night.md` | 4 API-ключа в бэкап-доке | 🔴 история |
| `checkpoints/chp_*.md`, `reports/night_audit_ai-eggs_*.md` | ключи в отчётах (вероятно, уже ротированы) | 🟠 история |
| `mango_api.py` (удалён из дерева) | Mango ключ+salt | 🟠 история |
| `.cursor/rules/global/rembrandt-designer.mdc` (удалён) | GCP-ключи | 🟠 история |

**Действие (человек-гейт):**
1. **Funpay-ключ** — ротировать в аккаунте Funpay, заменить в `opencode.json`, ключ вынести из git.
2. **OmniRoute JWT/API/пароль** — сгенерировать новые (JWT: `openssl rand -hex 32`), обновить `omniroute-recover.sh` + запущенный сервис на VPS.
3. Проверить, публичный ли репозиторий GitHub (если public — экспозиция публична).
4. `opencode.json` и `*.sh` с секретами — вынести значения в `.env` (gitignored), в репо оставить placeholder.

## HIGH/MEDIUM — код проектов (bandit + static)

| Проект | Находки |
|--------|---------|
| **levitan** | HIGH×4: chmod 0o777 (`deploy/levitan_fifo_bridge.py:188`), MD5-хеши для ключей (`tts_engine.py:25`, `upload_greeting.py:52`, `smart_dialer_zadarma_old.py:183`). MEDIUM: SQLi-конструкции ×4 (`crm/app.py:185,189,324,393`), bind 0.0.0.0 (`crm/app.py:559`), tmp-insecure ×2, печать 15 символов ключей в `test_all.py:28-30` |
| **ai-scout** | чисто (после FP-фикса) |
| **freelance-agent** | чисто |
| **angel-backend** | пустой каталог, аудит пропущен |

## Ложные срабатывания, исправленные в ходе аудита
- `deploy_webhook.sh` — `${MANGO_VPBX_API_KEY}` это **интерполяция env**, не утечка.
- `resend.ts` `console.error('RESEND_API_KEY не задан')` — логируется имя переменной, не значение → уточнён сканер.

## Артефакты
- `projects/levitan/security/SECURITY.md` + `audit-report.json`
- `projects/ai-scout/security/SECURITY.md` + `audit-report.json`
- `freelance-agent/security/SECURITY.md` + `audit-report.json`
- `reports/gitleaks-2026-08-02.json`
