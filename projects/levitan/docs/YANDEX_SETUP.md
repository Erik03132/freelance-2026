# Инструкция: доступы Яндекс Cloud для Realtime (Этап 1, ADR-001)

> Цель: получить `YC_API_KEY`, `YC_FOLDER_ID`, чтобы `deploy/levitan_realtime.py`
> мог держать WS-прокси к `wss://llm.api.cloud.yandex.net/.../realtime`.
> ⚠️ С 2026-06-01 обмен пользовательского OAuth на IAM закрыт — роли назначать
>   **вручную в консоли**, не через токен.

## Шаг 1 — Вход и каталог
1. Зайти в https://console.yandex.cloud под аккаунтом (основной, не федеративный).
2. Создать **каталог (cloud / folder)**, если нет, напр. `levitan-rt`.
3. Скопировать **ID каталога** → это будет `YC_FOLDER_ID`
   (виден в URL: `.../folders/<ID>` или в настройках каталога).

## Шаг 2 — Сервисный аккаунт (SA)
1. `Управление доступом` → `Сервисные аккаунты` → `Создать`.
2. Имя: `levitan-realtime-sa`.
3. **Назначить роли** (кнопка «Назначить роль» на самом SA ИЛИ в каталоге):
   - `ai.speechkit-stt.user`
   - `ai.speechkit-tts.user`
   - `ai.languageModels.user`
   - **`ai.models.user`** ← критично, иначе Realtime выдаст 403.
4. Сохранить.

## Шаг 3 — API-ключ
1. В карточке SA → вкладка **«API-ключи»** → `Создать API-ключ`.
2. ⚠️ Ключ показывается **один раз** — сразу скопировать.
3. Вписать в `levitan/.env`: `YC_API_KEY=<ключ>`.

## Шаг 4 — Проверка
```bash
curl -H "Authorization: Api-Key $YC_API_KEY" \
  "https://llm.api.cloud.yandex.net/llm/v1/realtime/models"
# Ожидаем: список моделей, среди них realtime-модель (yandex-rt / speechkit realtime)
```
Если 401/403 — проверить роли (шаг 2), особенно `ai.models.user`.

## Шаг 5 — .env
```
YC_API_KEY=<из шага 3>
YC_FOLDER_ID=<из шага 1>
YC_REALTIME_MODEL=yandex-rt
YC_REALTIME_VOICE=alena
```
Установить зависимость: `pip install websockets` (добавлено в requirements.txt).

## Что дальше
После получения ключей — `deploy/levitan_realtime.py` (WS-прокси) готов к наполнению
логикой: `session.update` из `levitan_realtime_prompt.py` + мост 8k↔24k + function `save_lead`.
