# 🌙 Ночной аудит кода — 2026-05-29

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:11:57  
> **Метод:** Cross-Model Peer Review  
> **Режим:** 🔧 AUTO-FIX  
> **Python файлов:** 196 (проверяем: 5)  
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
ai-eggs/agent/_vk_auth.py:3:1: E401 [*] Multiple imports on one line
ai-eggs/agent/_vk_auth.py:25:14: S603 `subprocess` call: check for execution of untrusted input
ai-eggs/agent/_vk_auth.py:37:10: S603 `subprocess` call: check for execution of untrusted input
ai-eggs/agent/_vk_auth.py:48:11: F541 [*] f-string without any placeholders
ai-eggs/agent/_vk_auth.py:53:7: F541 [*] f-string without any placeholders
ai-eggs/agent/_vk_auth.py:54:7: F541 [*] f-string without any placeholders
ai-eggs/agent/_vk_auth.py:55:7: F541 [*] f-string without any placeholders
ai-eggs/agent/_vk_photo_workaround.py:6:1: E401 [*] Multiple imports on one line
ai-eggs/agent/_vk_photo_workaround.py:31:9: S603 `subprocess` call: check for execution of untrusted input
ai-eggs/agent/_vk_photo_workaround.py:61:13: S603 `subprocess` call: check for execution of untrusted input
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
ai-eggs/agent/angelochka_core.py:98:89: E501 Line too long (113 > 88)
ai-eggs/agent/angelochka_core.py:103:1: E402 Module level import not at top of file
ai-eggs/agent/angelochka_core.py:140:89: E501 Line too long (92 > 88)
ai-eggs/agent/angelochka_core.py:148:89: E501 Line too long (130 > 88)
ai-eggs/agent/angelochka_core.py:178:89: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:218:13: F841 Local variable `y` is assigned to but never used
ai-eggs/agent/angelochka_core.py:265:9: B007 Loop control variable `cat_key` not used within loop body
ai-eggs/agent/angelochka_core.py:344:89: E501 Line too long (116 > 88)
ai-eggs/agent/angelochka_core.py:354:89: E501 Line too long (137 > 88)
ai-eggs/agent/angelochka_core.py:368:89: E501 Line too long (102 > 88)
ai-eggs/agent/angelochka_core.py:479:89: E501 Line too long (100 > 88)
ai-eggs/agent/angelochka_core.py:491:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:492:89: E501 Line too long (133 > 88)
```
