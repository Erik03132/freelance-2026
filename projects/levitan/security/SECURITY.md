# 🔐 Security Audit — levitan

- **Дата:** 2026-08-02T20:10:42.457307+00:00
- **Цель:** `projects/levitan`
- **Файлов просканировано:** 102

## Сводка по severity

| Severity | Кол-во |
|----------|--------|
| 🔴 CRITICAL | 0 |
| 🟠 HIGH | 0 |
| 🟡 MEDIUM | 13 |
| 🔵 LOW | 0 |

## Находки

1. 🟡 **MEDIUM** `shell_true`
   - **Где:** projects/levitan/deploy/levitan_dialog.py:89
   - **Что:** shell=True (риск инъекции)

2. 🟡 **MEDIUM** `path_traversal`
   - **Где:** projects/levitan/deploy/levitan_faq_agent.py:1142
   - **Что:** Возможный path traversal / недоверенный путь

3. 🟡 **MEDIUM** `path_traversal`
   - **Где:** projects/levitan/deploy/levitan_turnbased.py:743
   - **Что:** Возможный path traversal / недоверенный путь

4. 🟡 **MEDIUM** `path_traversal`
   - **Где:** projects/levitan/deploy/levitan_webhook.py:233
   - **Что:** Возможный path traversal / недоверенный путь

5. 🟡 **MEDIUM** `path_traversal`
   - **Где:** projects/levitan/scripts/dialer_bot.py:779
   - **Что:** Возможный path traversal / недоверенный путь

6. 🟡 **MEDIUM** `path_traversal`
   - **Где:** projects/levitan/scripts/dialer_bot.py:933
   - **Что:** Возможный path traversal / недоверенный путь

7. 🟡 **MEDIUM** `path_traversal`
   - **Где:** projects/levitan/scripts/dialer_bot.py:1136
   - **Что:** Возможный path traversal / недоверенный путь

8. 🟡 **MEDIUM** `path_traversal`
   - **Где:** projects/levitan/scripts/dialer_bot.py:1275
   - **Что:** Возможный path traversal / недоверенный путь

9. 🟡 **MEDIUM** `path_traversal`
   - **Где:** projects/levitan/scripts/dialer_bot.py:1415
   - **Что:** Возможный path traversal / недоверенный путь

10. 🟡 **MEDIUM** `path_traversal`
   - **Где:** projects/levitan/scripts/smart_dialer_zadarma_old.py:182
   - **Что:** Возможный path traversal / недоверенный путь

11. 🟡 **MEDIUM** `secret_in_log`
   - **Где:** projects/levitan/test_all.py:28
   - **Что:** Секрет пишется в лог

12. 🟡 **MEDIUM** `secret_in_log`
   - **Где:** projects/levitan/test_all.py:29
   - **Что:** Секрет пишется в лог

13. 🟡 **MEDIUM** `secret_in_log`
   - **Где:** projects/levitan/test_all.py:30
   - **Что:** Секрет пишется в лог
