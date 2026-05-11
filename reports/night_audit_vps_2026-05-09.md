# 🌙 Ночной аудит (VPS Fallback) — 2026-05-09

> **Время:** 02:05:01
> **Сервер:** VPS Timeweb (72.56.38.19)
> **Python файлов:** 135

## ⚡ Фаза 1: ruff
```
antigravity/ai-eggs/agent/a2a_protocol.py:166:9: S110 `try`-`except`-`pass` detected, consider logging the exception
antigravity/ai-eggs/agent/a2a_protocol.py:176:89: E501 Line too long (91 > 88)
antigravity/ai-eggs/agent/agg_temp.py:3:1: E401 [*] Multiple imports on one line
antigravity/ai-eggs/agent/agg_temp.py:6:89: E501 Line too long (113 > 88)
antigravity/ai-eggs/agent/agg_temp.py:23:5: E722 Do not use bare `except`
antigravity/ai-eggs/agent/agg_temp.py:23:5: S112 `try`-`except`-`continue` detected, consider logging the exception
antigravity/ai-eggs/agent/agg_temp.py:45:5: E722 Do not use bare `except`
antigravity/ai-eggs/agent/agg_temp.py:45:5: S112 `try`-`except`-`continue` detected, consider logging the exception
antigravity/ai-eggs/agent/agg_temp.py:68:7: F541 [*] f-string without any placeholders
antigravity/ai-eggs/agent/analyze_scan.py:3:1: E401 [*] Multiple imports on one line
antigravity/ai-eggs/agent/analyze_scan.py:4:22: F401 [*] `datetime.datetime` imported but unused
antigravity/ai-eggs/agent/analyze_scan.py:30:11: F541 [*] f-string without any placeholders
antigravity/ai-eggs/agent/analyze_scan.py:39:89: E501 Line too long (95 > 88)
antigravity/ai-eggs/agent/analyze_scan.py:54:11: F541 [*] f-string without any placeholders
antigravity/ai-eggs/agent/analyze_scan.py:80:13: E722 Do not use bare `except`
antigravity/ai-eggs/agent/analyze_scan.py:93:89: E501 Line too long (90 > 88)
antigravity/ai-eggs/agent/analyze_scan.py:94:89: E501 Line too long (92 > 88)
antigravity/ai-eggs/agent/analyze_scan.py:106:13: E722 Do not use bare `except`
antigravity/ai-eggs/agent/analyze_scan.py:113:89: E501 Line too long (92 > 88)
antigravity/ai-eggs/agent/analyze_scan.py:121:89: E501 Line too long (94 > 88)
antigravity/ai-eggs/agent/analyze_scan.py:124:89: E501 Line too long (130 > 88)
antigravity/ai-eggs/agent/analyze_scan.py:129:89: E501 Line too long (98 > 88)
antigravity/ai-eggs/agent/analyze_scan.py:131:89: E501 Line too long (132 > 88)
antigravity/ai-eggs/agent/angelochka_core.py:7:40: F401 [*] `hybrid_search.hybrid_search` imported but unused
antigravity/ai-eggs/agent/angelochka_core.py:7:55: F401 [*] `hybrid_search.init_bm25_index` imported but unused
antigravity/ai-eggs/agent/angelochka_core.py:8:25: F401 [*] `tool_digest.digest_context` imported but unused
antigravity/ai-eggs/agent/angelochka_core.py:43:89: E501 Line too long (99 > 88)
antigravity/ai-eggs/agent/angelochka_core.py:60:89: E501 Line too long (101 > 88)
antigravity/ai-eggs/agent/angelochka_core.py:84:1: E402 Module level import not at top of file
antigravity/ai-eggs/agent/angelochka_core.py:139:89: E501 Line too long (116 > 88)
```
**Ошибок ruff:** 1345 → 1239 (автофикс: 106)
**Секретов:** 0

## 🧠 Фаза 2: Claude
❌ Ошибка Claude API: 'choices'

## 📋 Итоги

| Метрика | Значение |
|---------|----------|
| ⚡ ruff | 1345 |
| 🔐 Секреты | 0 |
| 🔴 Критичных | 0 |
| 🟡 Важных | 0 |
| 🟢 Минорных | 0 |

> 🤖 VPS Fallback — сработал потому что Мак не выполнил аудит в 02:00
