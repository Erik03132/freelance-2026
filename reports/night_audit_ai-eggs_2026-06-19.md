# 🌙 Ночной аудит кода — 2026-06-19

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:00:05  
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
ai-eggs/agent/angela_outbound.py:25:8: F401 [*] `traceback` imported but unused
ai-eggs/agent/angela_outbound.py:46:89: E501 Line too long (95 > 88)
ai-eggs/agent/angela_outbound.py:51:89: E501 Line too long (99 > 88)
ai-eggs/agent/angela_outbound.py:85:89: E501 Line too long (98 > 88)
ai-eggs/agent/angela_outbound.py:140:5: F841 Local variable `count` is assigned to but never used
ai-eggs/agent/angela_outbound.py:190:89: E501 Line too long (91 > 88)
ai-eggs/agent/angela_outbound.py:194:89: E501 Line too long (122 > 88)
ai-eggs/agent/angela_outbound.py:204:17: S603 `subprocess` call: check for execution of untrusted input
ai-eggs/agent/angela_outbound.py:205:21: S607 Starting a process with a partial executable path
ai-eggs/agent/angela_outbound.py:206:89: E501 Line too long (110 > 88)
ai-eggs/agent/angela_outbound.py:259:89: E501 Line too long (103 > 88)
ai-eggs/agent/angela_outbound.py:268:89: E501 Line too long (94 > 88)
ai-eggs/agent/angela_outbound.py:286:89: E501 Line too long (106 > 88)
ai-eggs/agent/angela_outbound.py:336:89: E501 Line too long (120 > 88)
ai-eggs/agent/angela_outbound.py:342:89: E501 Line too long (92 > 88)
ai-eggs/agent/angela_outbound.py:346:5: F841 Local variable `p` is assigned to but never used
```
