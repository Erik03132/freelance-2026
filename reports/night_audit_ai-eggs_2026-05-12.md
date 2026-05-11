# 🌙 Ночной аудит кода — 2026-05-12

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:00:04  
> **Метод:** Cross-Model Peer Review  
> **Режим:** 🔧 AUTO-FIX  
> **Python файлов:** 137 (проверяем: 3)  
> **Источник:** git diff HEAD~1 (3 файлов)

---

## ⚡ Фаза 1: Машинный анализ

### 🔍 ruff — lint
```
ai-eggs/agent/a2a_protocol.py:166:9: S110 `try`-`except`-`pass` detected, consider logging the exception
ai-eggs/agent/a2a_protocol.py:176:89: E501 Line too long (91 > 88)
ai-eggs/agent/agg_temp.py:3:1: E401 [*] Multiple imports on one line
ai-eggs/agent/agg_temp.py:6:89: E501 Line too long (113 > 88)
ai-eggs/agent/agg_temp.py:23:5: E722 Do not use bare `except`
ai-eggs/agent/agg_temp.py:23:5: S112 `try`-`except`-`continue` detected, consider logging the exception
ai-eggs/agent/agg_temp.py:45:5: E722 Do not use bare `except`
ai-eggs/agent/agg_temp.py:45:5: S112 `try`-`except`-`continue` detected, consider logging the exception
ai-eggs/agent/agg_temp.py:68:7: F541 [*] f-string without any placeholders
ai-eggs/agent/analyze_scan.py:3:1: E401 [*] Multiple imports on one line
ai-eggs/agent/analyze_scan.py:4:22: F401 [*] `datetime.datetime` imported but unused
ai-eggs/agent/analyze_scan.py:30:11: F541 [*] f-string without any placeholders
ai-eggs/agent/analyze_scan.py:39:89: E501 Line too long (95 > 88)
ai-eggs/agent/analyze_scan.py:54:11: F541 [*] f-string without any placeholders
ai-eggs/agent/analyze_scan.py:80:13: E722 Do not use bare `except`
ai-eggs/agent/analyze_scan.py:93:89: E501 Line too long (90 > 88)
ai-eggs/agent/analyze_scan.py:94:89: E501 Line too long (92 > 88)
ai-eggs/agent/analyze_scan.py:106:13: E722 Do not use bare `except`
ai-eggs/agent/analyze_scan.py:113:89: E501 Line too long (92 > 88)
ai-eggs/agent/analyze_scan.py:121:89: E501 Line too long (94 > 88)
ai-eggs/agent/analyze_scan.py:124:89: E501 Line too long (130 > 88)
ai-eggs/agent/analyze_scan.py:129:89: E501 Line too long (98 > 88)
ai-eggs/agent/analyze_scan.py:131:89: E501 Line too long (132 > 88)
ai-eggs/agent/angelochka_core.py:7:40: F401 [*] `hybrid_search.hybrid_search` imported but unused
ai-eggs/agent/angelochka_core.py:7:55: F401 [*] `hybrid_search.init_bm25_index` imported but unused
ai-eggs/agent/angelochka_core.py:8:25: F401 [*] `tool_digest.digest_context` imported but unused
ai-eggs/agent/angelochka_core.py:43:89: E501 Line too long (99 > 88)
ai-eggs/agent/angelochka_core.py:60:89: E501 Line too long (101 > 88)
ai-eggs/agent/angelochka_core.py:84:1: E402 Module level import not at top of file
ai-eggs/agent/angelochka_core.py:139:89: E501 Line too long (116 > 88)
ai-eggs/agent/angelochka_core.py:149:89: E501 Line too long (137 > 88)
ai-eggs/agent/angelochka_core.py:162:89: E501 Line too long (102 > 88)
ai-eggs/agent/angelochka_core.py:189:89: E501 Line too long (100 > 88)
ai-eggs/agent/angelochka_core.py:197:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:198:89: E501 Line too long (133 > 88)
ai-eggs/agent/angelochka_core.py:205:89: E501 Line too long (97 > 88)
ai-eggs/agent/angelochka_core.py:217:89: E501 Line too long (110 > 88)
ai-eggs/agent/angelochka_core.py:218:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:227:90: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:243:89: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:244:89: E501 Line too long (137 > 88)
ai-eggs/agent/angelochka_core.py:261:15: F541 [*] f-string without any placeholders
ai-eggs/agent/angelochka_core.py:282:89: E501 Line too long (91 > 88)
ai-eggs/agent/angelochka_core.py:300:88: E501 Line too long (95 > 88)
ai-eggs/agent/angelochka_core.py:309:88: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:324:1: E402 Module level import not at top of file
ai-eggs/agent/angelochka_core.py:446:88: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:465:89: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:544:18: B007 Loop control variable `score` not used within loop body
ai-eggs/agent/angelochka_core.py:551:89: E501 Line too long (114 > 88)
```
