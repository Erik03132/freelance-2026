levitan-retell
==============

Вариант 3: **Retell Conductor** — hosted голосовой агент Retell AI (распознаёт>>
синтезирует на своей стороне, диал через SIP URI `sip:{call_id}@sip.retellai.com`).

## Статус: НА ПАУЗЕ
Retell не внедряем — у пользователя проблемы с получением API-ключа
(`RETELL_API_KEY` + `agent_id`). Прототип-код сохранён здесь для последующего
сравнения, когда ключ будет доступен.

Верифицированные факты (31.08.2026): Conductor жив, русский поддерживается,
$0.07–0.31/мин, 20 бесплатных competition calls. Endpoint: `POST /v2/register-phone-call`
на `https://api.retellai.com`.

## Структура

    agent/retell/call_mango.py     — CLI: регистрация звонка в Retell + Mango callback
                                     (--help / --dry-run поддерживаются)
    agent/retell/agent_prompt.md   — Conductor description + полный system prompt
                                     (воронка MIN_QTY 50, Ross-308 от 75₽, Крым,
                                     save_lead->Bitrix, faq_lookup 248 триггеров)
    agent/retell/retell-agent.yaml — конфиг Retell-агента

## Запуск (когда будет ключ)

    source .venv/bin/activate
    python agent/retell/call_mango.py --help

Env: `RETELL_API_KEY`, `RETELL_AGENT_ID`, `MANGO_VPBX_API_KEY`, `MANGO_VPBX_API_SALT`.
