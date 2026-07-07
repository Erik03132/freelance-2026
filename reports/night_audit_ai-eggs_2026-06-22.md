# 🌙 Ночной аудит кода — 2026-06-22

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:00:03  
> **Метод:** Cross-Model Peer Review  
> **Режим:** 🔧 AUTO-FIX  
> **Python файлов:** 207 (проверяем: 2)  
> **Источник:** git diff HEAD~1 (2 файлов)

---

## ⚡ Фаза 1: Машинный анализ

### 🔍 ruff — lint
```
ai-eggs/agent/_archived/send_infra_report.py:17:89: E501 Line too long (90 > 88)
ai-eggs/agent/_archived/send_project_report.py:16:89: E501 Line too long (110 > 88)
ai-eggs/agent/_archived/send_project_report.py:19:89: E501 Line too long (188 > 88)
ai-eggs/agent/_archived/send_project_report.py:24:89: E501 Line too long (99 > 88)
ai-eggs/agent/_archived/send_project_report.py:29:89: E501 Line too long (143 > 88)
ai-eggs/agent/_archived/send_project_report.py:32:89: E501 Line too long (182 > 88)
ai-eggs/agent/_archived/send_project_report.py:35:89: E501 Line too long (143 > 88)
ai-eggs/agent/_archived/send_project_report.py:38:89: E501 Line too long (193 > 88)
ai-eggs/agent/_archived/send_project_report.py:41:89: E501 Line too long (299 > 88)
ai-eggs/agent/_archived/send_project_report.py:55:89: E501 Line too long (132 > 88)
ai-eggs/agent/_vk_auth.py:29:14: S603 `subprocess` call: check for execution of untrusted input
ai-eggs/agent/_vk_auth.py:41:10: S603 `subprocess` call: check for execution of untrusted input
ai-eggs/agent/_vk_get_token.py:26:17: S105 Possible hardcoded password assigned to: "client_secret"
ai-eggs/agent/_vk_get_token.py:31:5: S603 `subprocess` call: check for execution of untrusted input
ai-eggs/agent/_vk_get_token.py:43:89: E501 Line too long (101 > 88)
ai-eggs/agent/_vk_photo_workaround.py:24:89: E501 Line too long (126 > 88)
ai-eggs/agent/_vk_photo_workaround.py:34:9: S603 `subprocess` call: check for execution of untrusted input
ai-eggs/agent/a2a_protocol.py:166:9: S110 `try`-`except`-`pass` detected, consider logging the exception
ai-eggs/agent/a2a_protocol.py:176:89: E501 Line too long (91 > 88)
ai-eggs/agent/agg_temp.py:8:89: E501 Line too long (113 > 88)
ai-eggs/agent/agg_temp.py:25:5: E722 Do not use bare `except`
ai-eggs/agent/agg_temp.py:25:5: S112 `try`-`except`-`continue` detected, consider logging the exception
ai-eggs/agent/agg_temp.py:47:5: E722 Do not use bare `except`
ai-eggs/agent/agg_temp.py:47:5: S112 `try`-`except`-`continue` detected, consider logging the exception
ai-eggs/agent/analyze_scan.py:40:89: E501 Line too long (95 > 88)
ai-eggs/agent/analyze_scan.py:81:13: E722 Do not use bare `except`
ai-eggs/agent/analyze_scan.py:94:89: E501 Line too long (90 > 88)
ai-eggs/agent/analyze_scan.py:95:89: E501 Line too long (92 > 88)
ai-eggs/agent/analyze_scan.py:107:13: E722 Do not use bare `except`
ai-eggs/agent/analyze_scan.py:114:89: E501 Line too long (92 > 88)
ai-eggs/agent/analyze_scan.py:122:89: E501 Line too long (94 > 88)
ai-eggs/agent/analyze_scan.py:125:89: E501 Line too long (130 > 88)
ai-eggs/agent/analyze_scan.py:130:89: E501 Line too long (98 > 88)
ai-eggs/agent/analyze_scan.py:132:89: E501 Line too long (132 > 88)
ai-eggs/agent/angela_outbound.py:45:89: E501 Line too long (95 > 88)
ai-eggs/agent/angela_outbound.py:50:89: E501 Line too long (99 > 88)
ai-eggs/agent/angela_outbound.py:84:89: E501 Line too long (98 > 88)
ai-eggs/agent/angela_outbound.py:139:5: F841 Local variable `count` is assigned to but never used
ai-eggs/agent/angela_outbound.py:189:89: E501 Line too long (91 > 88)
ai-eggs/agent/angela_outbound.py:193:89: E501 Line too long (122 > 88)
ai-eggs/agent/angela_outbound.py:203:17: S603 `subprocess` call: check for execution of untrusted input
ai-eggs/agent/angela_outbound.py:204:21: S607 Starting a process with a partial executable path
ai-eggs/agent/angela_outbound.py:205:89: E501 Line too long (110 > 88)
ai-eggs/agent/angela_outbound.py:258:89: E501 Line too long (103 > 88)
ai-eggs/agent/angela_outbound.py:267:89: E501 Line too long (94 > 88)
ai-eggs/agent/angela_outbound.py:285:89: E501 Line too long (106 > 88)
ai-eggs/agent/angela_outbound.py:335:89: E501 Line too long (120 > 88)
ai-eggs/agent/angela_outbound.py:341:89: E501 Line too long (92 > 88)
ai-eggs/agent/angela_outbound.py:345:5: F841 Local variable `p` is assigned to but never used
ai-eggs/agent/angela_outbound.py:379:89: E501 Line too long (97 > 88)
```

🔧 **ruff --fix:** 0 ошибок исправлено автоматически (ветка: \'auto-fix/night-audit-2026-06-22\')

**Критических ошибок ruff (E,F,S,B):** 1800

### 🔐 Hardcoded секреты
```
⚠️ _vk_get_token.py: 26:client_secret = "hHbZxrka2uZ6jB1inYsH"

```

### 📝 Изменения за день
```
 ai-eggs                                   |   0
 angel-backend                             |   0
 checkpoints/chp_20260618_230001.md        |  25 ++++
 chp.md                                    |  82 +++--------
 dreams/dream_2026-06-18.md                |  13 ++
 dreams/patterns.md                        |  93 +++++++++++++
 reports/night_audit_ai-eggs_2026-06-18.md | 126 +++++++++++++++++
 reports/night_audit_ai-eggs_2026-06-19.md | 199 +++++++++++++++++++++++++++
 tools/habr_intelligence.py                |   2 +-
 10 files changed, 614 insertions(+), 146 deletions(-)
```

---

## 🔬 Фаза 2: Gemini 2.5 Pro — Глубокий аудит

⚠️ Gemini CLI недоступен — фаза пропущена

---

## 🧠 Фаза 3: Claude — Cross-Model Peer Review

⚠️ Claude API недоступен: ❌ Ошибка Claude API: Expecting value: line 2 column 1 (char 1)

---

## 📋 Итоговая сводка

| Метрика | Значение |
|---------|----------|
| 📅 Дата | 2026-06-22 |
| ⏰ Время | 02:00:03 → 02:00:38 |
| 📁 Python файлов | 207 |
| 📝 Изменено за день | 10 |
| ⚡ ruff ошибок (E,F,S,B) | 1800 |
| 🔐 Hardcoded секретов | 1 |
| 🔬 Gemini аудит | ⏭️ |
| 🧠 Claude cross-review | ⏭️ |
| 🔴 Критичных (Claude) | 0 |
| 🟡 Важных (Claude) | 0 |
| 🟢 Минорных (Claude) | 0 |

### Метод аудита
```
Код писали: Gemini 2.5 Pro + Claude Opus (через Antigravity)
Проверяли:
  Фаза 1: ruff 0.15 (машина, 100% точность)
  Фаза 2: Gemini CLI 2.5 Pro (глубокий анализ, бесплатно)
  Фаза 3: moonshotai/kimi-k2 (cross-model review, OpenRouter)
  
Cross-Model Peer Review: два профессора из разных школ
проверяют код друг друга → максимум найденных багов
```

---

> 🤖 Сгенерировано: `tools/night_audit.sh v2` — Cross-Model Peer Review
