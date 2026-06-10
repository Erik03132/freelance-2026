# 🌙 Ночной аудит кода — 2026-06-11

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 02:00:03  
> **Метод:** Cross-Model Peer Review  
> **Режим:** 🔧 AUTO-FIX  
> **Python файлов:** 203 (проверяем: 2)  
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
ai-eggs/agent/_bx_explore.py:3:8: F401 [*] `csv` imported but unused
ai-eggs/agent/_bx_explore.py:4:8: F401 [*] `json` imported but unused
ai-eggs/agent/_bx_explore.py:6:8: F401 [*] `sys` imported but unused
ai-eggs/agent/_bx_explore.py:40:89: E501 Line too long (91 > 88)
ai-eggs/agent/_bx_explore.py:47:89: E501 Line too long (137 > 88)
ai-eggs/agent/_bx_explore.py:59:89: E501 Line too long (94 > 88)
ai-eggs/agent/_bx_turkey.py:6:1: E401 [*] Multiple imports on one line
ai-eggs/agent/_bx_turkey.py:6:13: F401 [*] `json` imported but unused
ai-eggs/agent/_bx_turkey.py:6:23: F401 [*] `re` imported but unused
ai-eggs/agent/_bx_turkey.py:6:27: F401 [*] `sys` imported but unused
ai-eggs/agent/_bx_turkey.py:33:16: E701 Multiple statements on one line (colon)
ai-eggs/agent/_bx_turkey.py:48:17: E701 Multiple statements on one line (colon)
ai-eggs/agent/_bx_turkey.py:52:15: E701 Multiple statements on one line (colon)
ai-eggs/agent/_bx_turkey.py:80:17: E701 Multiple statements on one line (colon)
ai-eggs/agent/_bx_turkey.py:84:15: E701 Multiple statements on one line (colon)
ai-eggs/agent/_bx_turkey.py:118:89: E501 Line too long (94 > 88)
ai-eggs/agent/_bx_turkey.py:166:7: S108 Probable insecure usage of temporary file or directory: "/tmp/turkey_deals.csv"
ai-eggs/agent/_bx_turkey.py:178:89: E501 Line too long (91 > 88)
ai-eggs/agent/_fix_csv_read.py:3:8: F401 [*] `re` imported but unused
ai-eggs/agent/_fix_csv_read.py:14:5: B007 Loop control variable `i` not used within loop body
ai-eggs/agent/_fix_csv_read.py:21:89: E501 Line too long (103 > 88)
ai-eggs/agent/_fix_csv_read.py:25:89: E501 Line too long (95 > 88)
ai-eggs/agent/_fix_csv_read.py:28:88: E501 Line too long (95 > 88)
ai-eggs/agent/_fix_csv_read.py:30:89: E501 Line too long (89 > 88)
ai-eggs/agent/_fix_fuzzy.py:19:89: E501 Line too long (95 > 88)
ai-eggs/agent/_fix_fuzzy.py:23:89: E501 Line too long (103 > 88)
ai-eggs/agent/_fix_fuzzy.py:24:89: E501 Line too long (94 > 88)
ai-eggs/agent/_fix_fuzzy.py:25:89: E501 Line too long (98 > 88)
ai-eggs/agent/_fix_fuzzy.py:29:89: E501 Line too long (95 > 88)
ai-eggs/agent/_fix_fuzzy.py:33:89: E501 Line too long (97 > 88)
ai-eggs/agent/_fix_fuzzy.py:35:89: E501 Line too long (99 > 88)
ai-eggs/agent/_fix_fuzzy.py:41:89: E501 Line too long (95 > 88)
ai-eggs/agent/_fix_fuzzy.py:45:89: E501 Line too long (97 > 88)
ai-eggs/agent/_fix_fuzzy.py:47:89: E501 Line too long (96 > 88)
ai-eggs/agent/_fix_fuzzy.py:51:89: E501 Line too long (103 > 88)
ai-eggs/agent/_fix_fuzzy.py:54:89: E501 Line too long (94 > 88)
ai-eggs/agent/_fix_fuzzy.py:55:89: E501 Line too long (98 > 88)
ai-eggs/agent/_fix_fuzzy.py:59:89: E501 Line too long (98 > 88)
ai-eggs/agent/_vk_auth.py:29:14: S603 `subprocess` call: check for execution of untrusted input
ai-eggs/agent/_vk_auth.py:41:10: S603 `subprocess` call: check for execution of untrusted input
```
