# Задача: Поднять OmniRoute на VPS как рабочий хаб провайдеров (копия локальной версии)

## Статус на момент передачи
- OmniRoute на VPS (TimeWeb, РФ) = systemd-сервис `omniroute.service`, active.
- Слушает: `127.0.0.1:20128` (API/v1), `127.0.0.1:20131` (EmbedWs), `127.0.0.1:20132` (Dashboard WS).
- **Сейчас НЕ работает**: `/v1/chat/completions` возвращает пусто; веб-UI `/dashboard` = 000/404 на всех портах (20128/20129/20130/20132).
- Лог обрывается на `Starting server...` — висит на инициализации, не доходит до `Dashboard listening`.
- Провайдеры хранятся в `/root/.omniroute/storage.sqlite` (4 credential, один битый `theoldllm`).
  Файл `provider-credentials.json` OmniRoute **игнорирует** (читает из sqlite, не из JSON).
- Локальная версия на Маке (`/Users/igorvasin/.omniroute/`) знает только `openrouter` (рабочий ключ) и
  через веб-UI `/dashboard/combos` настроена комбо `auto/free-coding`.
- us-прокси (`172.120.21.141:64468`) нужен **внутри VPS** для OmniRoute→зарубежные провайдеры
  (OpenRouter/Nous). В `.env` OmniRoute прописан `HTTPS_PROXY=...64468`. `ENABLE_SOCKS5_PROXY=false`,
  `ENABLE_TLS_FINGERPRINT=true` (маскировка под Chrome).

## Цель
Серверный OmniRoute = копия локального (те же провайдеры/комбо), чтобы агенты на VPS ходили в
`omniroute / auto/free-coding` как primary-провайдер (по архитектуре Игоря).

## Шаги
1. **Найти правильный порт веб-UI.** Лог пишет `Dashboard WebSocket server listening on 127.0.0.1:20132`
   (это WS, не HTTP). HTTP-дашборд, видимо, на другом порту или не поднимается из-за зависания init.
   Проверить лог на строку `Dashboard listening on ...` (HTTP-порт).
2. **Понять, почему висит на старте.** Проверить:
   - доступен ли us-прокси **ИЗ VPS** прямо сейчас (из РФ до VPS — прямой ssh; us-прокси может быть мёртв);
   - не блокирует ли РКН зарубежные провайдеры напрямую (OmniRoute с `ENABLE_SOCKS5_PROXY=false`
     стучится напрямую, минуя SOCKS — может упираться в блокировку РФ).
3. **Перенести настройки локального OmniRoute на VPS.** Скопировать `storage.sqlite` (или через веб-UI
   импортировать провайдеры/комбо) с Мака на VPS. **НЕ копировать raw sqlite вслепую** — проверить схему
   и совместимость версий (локальная vs v3.8.49 на VPS).
4. **Прописать OpenRouter-ключ в VPS-OmniRoute.** Ключ есть в `/opt/levitan/projects/levitan/.env`
   (`OPENROUTER_API_KEY`, len 73). Через веб-UI или напрямую в sqlite.
5. **Проверить** `/v1/chat/completions` с `auto/free-coding` возвращает ответ (не пусто).
6. **Включить в Hermes `config.yaml`** как primary: `provider: omniroute, default: auto/free-coding`;
   fallback — прямые провайдеры (opencode-zen/hy3-free и т.д., через us-прокси внутри VPS).

## Риски
- OmniRoute может зависать на init из-за недоступности зарубежных провайдеров из РФ без прокси.
  Нужно проверить, жив ли us-прокси ИЗ VPS (а не из Мака).
- Переустановка OmniRoute = потеря настроек БД; предпочтительнее перенос sqlite/ключей.
- Веб-UI может требовать проброса порта на Мак (ssh -L 20129:127.0.0.1:20129 ...) для доступа к
  `/dashboard/combos` с локальной машины.

## Что УЖЕ сделано (не терять)
- `config.yaml` VPS: `model.provider: omniroute, default: hy3-free` + `fallback_providers` на
  opencode-zen (hy3-free / claude-sonnet-4-5 / claude-opus-4-8). Каскад рабочий (проверено живым тестом
  `hermes -p batrak` → вернул персону Батрака).
- SOUL-файлы batrak/chief доставлены на VPS, контент проверен.
- OPENROUTER_API_KEY прописан в `/root/.omniroute/provider-credentials.json` (но OmniRoute его игнорирует).
