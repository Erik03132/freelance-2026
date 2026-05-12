# 🌙 Ночной аудит кода — 2026-05-13

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:00:05  
> **Метод:** Cross-Model Peer Review  
> **Режим:** 🔧 AUTO-FIX  
> **Python файлов:** 146 (проверяем: 3)  
> **Источник:** git diff HEAD~1 (3 файлов)

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
ai-eggs/agent/_archived/send_report.py:8:13: F821 Undefined name `os`
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
ai-eggs/agent/angelochka_core.py:44:89: E501 Line too long (99 > 88)
ai-eggs/agent/angelochka_core.py:61:89: E501 Line too long (101 > 88)
ai-eggs/agent/angelochka_core.py:85:1: E402 Module level import not at top of file
ai-eggs/agent/angelochka_core.py:141:89: E501 Line too long (116 > 88)
ai-eggs/agent/angelochka_core.py:151:89: E501 Line too long (137 > 88)
ai-eggs/agent/angelochka_core.py:164:89: E501 Line too long (102 > 88)
ai-eggs/agent/angelochka_core.py:191:89: E501 Line too long (100 > 88)
ai-eggs/agent/angelochka_core.py:203:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:204:89: E501 Line too long (133 > 88)
ai-eggs/agent/angelochka_core.py:211:89: E501 Line too long (97 > 88)
ai-eggs/agent/angelochka_core.py:223:89: E501 Line too long (110 > 88)
ai-eggs/agent/angelochka_core.py:224:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:233:90: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:249:89: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:250:89: E501 Line too long (137 > 88)
ai-eggs/agent/angelochka_core.py:288:89: E501 Line too long (91 > 88)
ai-eggs/agent/angelochka_core.py:306:88: E501 Line too long (95 > 88)
ai-eggs/agent/angelochka_core.py:315:88: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:330:1: E402 Module level import not at top of file
ai-eggs/agent/angelochka_core.py:453:88: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:472:89: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:551:18: B007 Loop control variable `score` not used within loop body
```
