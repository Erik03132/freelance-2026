# macos-harness — computer-use бэкенд для Mac

**Что:** тонкий слой из 6 примитивов (`see`/`key`/`type`/`click`/`ax`/`script`)
поверх Core Graphics + Accessibility + screencapture + AppleScript + Browser
Harness. Даёт LLM-агенту «руки» на Mac'е без написания интеграций под каждое
приложение.
Репозиторий: https://github.com/browser-use/macos-harness (v0.1.2, alpha, 6 коммитов).

**Где юзать:** автоматизация GUI-задач без API (банк-клиенты, старое desktop-ПО,
веб без доступа), бэкенд computer-use для голосовых агентов бюро (Levitan/AVM/Angela).

**Диск:** установка ~150–250 МБ (в основном pyobjc). Chromium не тянет
(`browser-harness` цепляется к уже стоящему Chrome через CDP).
Установка: `uv tool install --python 3.12 macos-harness` + `macos-harness doctor`.

**Риски (экспертиза, авг-2026):**
- Фоновый КЛАВИАТУРНЫЙ ввод (`type`/`key`) в macOS шатается — многие фоновые
  аппы не получают key-события. Клики (`click`) по фону работают надёжно.
  Обход: `mac.script('tell app … to keystroke')` или `mac.ax.perform(AXPress)`.
- Телеметрия ВКЛ по умолчанию → сразу `macos-harness telemetry disable`.
- Модель безопасности = 100% доверие агенту (произвольный AppleScript).
  Нет подтверждения/allowlist необратимых действий → только под присмотром.
- Нулевое реальное device-тестирование (тесты мокают фреймворки).

**Статус:** НЕ ставить вслепую. Кандидат в решения, проверить живьём перед продом.

---

## Фичи / примитивы (из README, авг-2026)

**Шесть примитивов — весь Mac:**
- `mac.see(app)` — скриншот фонового окна **без** вывода приложения на передний план (Core Graphics window capture).
- `mac.key("cmd+k", app=...)` — клавиатурное событие напрямую в PID приложения (CGEvent to PID).
- `mac.type("текст", app=...)` — посимвольный ввод в приложение.
- `mac.click(x, y, app=...)` — клик по координатам в окне приложения.
- `mac.ax.at(x, y, app=...)` — сырая Apple Accessibility (достать/нажать UI-элемент: `mac.ax.perform(AXPress)`).
- `mac.script('tell application "X" to …')` — AppleScript / Apple Events, когда зрения не хватает.

В том же Python-процессе «из коробки» доступны: `browser` (Browser Harness → реальный залогиненный Chrome через CDP), `Path`, `subprocess`. Философия: **нет** пер-апп инструментов (ни Spotify-, ни Slack-, ни Final Cut-тулов); модель сама дописывает недостающую логику обычным Python прямо в процессе.

**Как работает (архитектура):**
```
              один персистентный Python-процесс
        mac.*                  browser.*          Path / subprocess
   CGWindow скриншоты   →   Browser Harness →   файлы + shell
   CGEvent в PID         →   (CDP)          →
   AX + Apple Events     →   реальный Chrome
```
- Захват фоновых окон без вывода на передний план.
- Клавиатура/клики по PID — не «globally», а в конкретное приложение.
- Рисует анимированный **click-through курсор**, не двигая реальный системный указатель.
- Accessibility + Apple Events, когда скриншот/зрение не справляются.
- Browser Harness = управление настоящим браузером с сессиями.
- Рядом — обычный Python и локальная ФС.

**Пример (из README):**
```python
frame = mac.see("Spotify")
mac.key("cmd+k", app="Spotify")
mac.type("Alessia Cara", app="Spotify")
mac.click(640, 420, app="Spotify")
item = mac.ax.at(640, 420, app="Spotify")
mac.script('tell application "Spotify" to play')
print(browser.page_info())
print(list(Path.home().iterdir()))
```

**Раздача агенту (paste в Codex / Claude Code):**
```
Install or upgrade macOS Harness from https://github.com/browser-use/macos-harness
with uv using Python 3.12. Register the skill printed by `macos-harness skill`,
then run `macos-harness doctor`. Explain any missing macOS permissions and ask
before requesting them. Finally, verify the harness by capturing one
already-running app without bringing it to the foreground.
```

**Права и приватность:**
- `macos-harness doctor` — показывает реально нужные macOS-разрешения (Accessibility, Screen Recording).
- Никогда не активирует/не поднимает целевое приложение и не двигает физический курсор.
- Телеметрия ВКЛ по умолчанию: пишет только категорию CLI-команды, успех, длительность, версию пакета, OS/arch, детектнутый agent-клиент. **НЕ** пишет промпты, имена приложений, скриншоты, UI-текст, скрипты, пути, заголовки окон. Выключить: `macos-harness telemetry disable`.
- Экспериментальное, только macOS, MIT.

**Подтверждение (пост vibecoding_tg/3706, 19.08.2026):** macOS Harness «запустил сам себя» —
живой пример самоприменения агентом (bootstrapping). Усиливает кандидатуру как
рабочего computer-use рантайма.

**Метки (topics):** accessibility, agent, automation, cdp, computer-use, macos, python.
