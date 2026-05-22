# 🌙 Ночной аудит кода — 2026-05-23

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:02:10  
> **Метод:** Cross-Model Peer Review  
> **Режим:** 🔧 AUTO-FIX  
> **Python файлов:** 188 (проверяем: 5)  
> **Источник:** ТОП-5 критических файлов (нет git diff)

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
ai-eggs/agent/angelochka_core.py:97:1: E402 Module level import not at top of file
ai-eggs/agent/angelochka_core.py:153:89: E501 Line too long (116 > 88)
ai-eggs/agent/angelochka_core.py:163:89: E501 Line too long (137 > 88)
ai-eggs/agent/angelochka_core.py:177:89: E501 Line too long (102 > 88)
ai-eggs/agent/angelochka_core.py:288:89: E501 Line too long (100 > 88)
ai-eggs/agent/angelochka_core.py:300:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:301:89: E501 Line too long (133 > 88)
ai-eggs/agent/angelochka_core.py:318:89: E501 Line too long (110 > 88)
ai-eggs/agent/angelochka_core.py:319:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:332:90: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:348:89: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:349:89: E501 Line too long (137 > 88)
ai-eggs/agent/angelochka_core.py:391:89: E501 Line too long (91 > 88)
ai-eggs/agent/angelochka_core.py:409:88: E501 Line too long (95 > 88)
ai-eggs/agent/angelochka_core.py:418:88: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:433:1: E402 Module level import not at top of file
ai-eggs/agent/angelochka_core.py:556:88: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:575:89: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:661:89: E501 Line too long (133 > 88)
ai-eggs/agent/angelochka_core.py:665:89: E501 Line too long (98 > 88)
ai-eggs/agent/angelochka_core.py:683:89: E501 Line too long (94 > 88)
ai-eggs/agent/angelochka_core.py:685:89: E501 Line too long (91 > 88)
ai-eggs/agent/angelochka_core.py:688:89: E501 Line too long (100 > 88)
```
