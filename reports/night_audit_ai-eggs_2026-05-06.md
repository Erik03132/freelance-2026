# 🌙 Ночной аудит кода — 2026-05-06

> **Проект:** AI-Eggs (Анжелочка)  
> **Время:** 09:07:10  
> **Метод:** Cross-Model Peer Review  
> **Режим:** 📋 Только отчёт  
> **Python файлов:** 122 (проверяем: 5)  
> **Источник:** ТОП-5 критических файлов (нет git diff)

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
ai-eggs/agent/angelochka_core.py:33:89: E501 Line too long (99 > 88)
ai-eggs/agent/angelochka_core.py:50:89: E501 Line too long (101 > 88)
ai-eggs/agent/angelochka_core.py:74:1: E402 Module level import not at top of file
ai-eggs/agent/angelochka_core.py:130:89: E501 Line too long (116 > 88)
ai-eggs/agent/angelochka_core.py:140:89: E501 Line too long (137 > 88)
ai-eggs/agent/angelochka_core.py:177:89: E501 Line too long (100 > 88)
ai-eggs/agent/angelochka_core.py:185:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:186:89: E501 Line too long (133 > 88)
ai-eggs/agent/angelochka_core.py:193:89: E501 Line too long (97 > 88)
ai-eggs/agent/angelochka_core.py:206:89: E501 Line too long (110 > 88)
ai-eggs/agent/angelochka_core.py:207:89: E501 Line too long (89 > 88)
ai-eggs/agent/angelochka_core.py:215:90: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:231:89: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:232:89: E501 Line too long (137 > 88)
ai-eggs/agent/angelochka_core.py:249:15: F541 [*] f-string without any placeholders
ai-eggs/agent/angelochka_core.py:273:89: E501 Line too long (91 > 88)
ai-eggs/agent/angelochka_core.py:291:88: E501 Line too long (95 > 88)
ai-eggs/agent/angelochka_core.py:300:88: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:315:1: E402 Module level import not at top of file
ai-eggs/agent/angelochka_core.py:437:88: E501 Line too long (93 > 88)
ai-eggs/agent/angelochka_core.py:450:89: E501 Line too long (116 > 88)
ai-eggs/agent/angelochka_core.py:454:89: E501 Line too long (98 > 88)
ai-eggs/agent/angelochka_core.py:479:89: E501 Line too long (115 > 88)
ai-eggs/agent/angelochka_core.py:496:89: E501 Line too long (96 > 88)
ai-eggs/agent/angelochka_core.py:506:89: E501 Line too long (90 > 88)
```

**Критических ошибок ruff (E,F,S,B):** 1160

### 🔐 Hardcoded секреты
✅ Не найдено

### 📝 Изменения за день
```
 .../webpack/webpack.788a16ca6bca809d.hot-update.js |   60 -
 .../webpack/webpack.a334f19729ade55c.hot-update.js |   18 -
 .../webpack/webpack.c539ee2d895100da.hot-update.js |   18 -
 .../webpack/webpack.e7297ad03e1c6492.hot-update.js |   18 -
 dashboard/.next/trace                              |   17 -
 .../.next/types/app/api/assets/[filename]/route.ts |  343 ---
 dashboard/.next/types/app/layout.ts                |   79 -
 dashboard/.next/types/package.json                 |    1 -
 tools/night_audit.sh                               |   27 +-
 80 files changed, 73 insertions(+), 8295 deletions(-)
```

---
⏭️ AI-фазы пропущены (--phase1-only)

---

## 📋 Итоговая сводка

| Метрика | Значение |
|---------|----------|
| 📅 Дата | 2026-05-06 |
| ⏰ Время | 09:07:10 → 09:07:12 |
| 📁 Python файлов | 122 |
| 📝 Изменено за день | 80 |
| ⚡ ruff ошибок (E,F,S,B) | 1160 |
| 🔐 Hardcoded секретов | 0 |
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
  Фаза 3: Claude Sonnet 4 (cross-model review, OpenRouter)
  
Cross-Model Peer Review: два профессора из разных школ
проверяют код друг друга → максимум найденных багов
```

---

> 🤖 Сгенерировано: `tools/night_audit.sh v2` — Cross-Model Peer Review
