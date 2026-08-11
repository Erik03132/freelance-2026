# Handoff 2026-08-11 11:44 — Levitan: аудио-путь приветствия (тишина 5с → фрагмент → обрывки)

## Критически важный вывод для следующей сессии

**Текущий `levitan_agent.py` = `bak_winner` (md5 d9a3e82a1b4d87487cb8cedafa4c71fb).**
В нём перед приветствием стоит `await asyncio.sleep(3.5)` + `print("media bridge settled")`.

**Вчерашний РАБОЧИЙ звонок 18:19 был на `bak_endpointing`** (не bak_winner!):
- ready 18:19:13 → settled 18:19:14 = **1 секунда** (в bak_endpointing sleep(1.0))
- приветствие звучало чисто, без тишины

Сегодня 09:36 и 11:25 — на bak_winner (sleep 3.5):
- ready → settled = 3-4 секунды
- абонент слышал 5с тишины → фрагмент приветствия → обрывки

**Это НЕ проблема LLM (LLM уже починен, см. ниже). Это sleep(3.5) + старт медиа-моста.**

## Полный diff bak_endpointing vs bak_winner (уже получен, VPS)

`bak_endpointing` (РАБОЧИЙ вчера 18:19):
- `await asyncio.sleep(1.0)` перед greeting (bak_winner: 3.5)
- first-chunk timeout 10с (winner: 18с)
- `reasoning_effort=none` — только для deepseek-моделей (winner: для ВСЕХ моделей — из-за этого kimi-k2.7-code давал 400)
- max_completion_tokens=2500 (winner: 1500)
- закрывает все стримы кроме победителя в цикле после гонки (winner: закрывает внутри)
- LLM_MAX_HISTORY truncate 6 (winner: нет)

## Решение (следующий шаг)

**Восстановить `bak_endpointing` как рабочий агент** ИЛИ минимум убрать sleep(3.5)→sleep(1.0) в текущем.
Но bak_endpointing брал reasoning_effort только для deepseek — а сейчас используем qwen3.7-plus/minimax-m2.7 (Go-тариф). Надо проверить: принимают ли они reasoning_effort=none (qwen3.7-plus — да, minimax-m2.7 — да, подтверждено звонком 11:25).

**Рекомендуемый план:**
1. Взять bak_endpointing за основу (рабочий звук!)
2. Перенести в него reasoning_effort=none для ВСЕХ моделей (иначе qwen/minimax поедут с reasoning — медленнее)
3. Оставить LLM_MODEL=opencode-go/qwen3.7-plus, LLM_FALLBACK_MODEL=opencode-go/minimax-m2.7
4. Перезапустить службу, сделать контрольный звонок через mango_callback
5. Цель: приветствие без тишины, паузы 2-3с

## Статус LLM (УЖЕ ПОЧИНЕНО, не трогать)

- **Корневая причина найдена:** ключ sk-WU8LhvjA8... подключён под провайдером `opencode-zen` (endpoint /zen/v1), но тариф ключа — **OpenCode Go** (endpoint /zen/go/v1). Go-тариф на Zen-endpoint отдаёт 403.
- **Фикс сделан:** `UPDATE provider_connections SET provider='opencode-go', name='OpenCode Go' WHERE id='opencode-zen-001'` + `pm2 restart omniroute`.
- Go-модели бесплатные. Текущие: LLM_MODEL=opencode-go/qwen3.7-plus, LLM_FALLBACK_MODEL=opencode-go/minimax-m2.7 (бэкап unit: /root/levitan-agent.service.bak_20260811_go).
- Бенч TTFT через OmniRoute (streaming, reasoning_effort=none):
  - qwen3.7-plus: TTFT 1.5-2.0с (стрим) — ГОНОЧНЫЙ ПОБЕДИТЕЛЬ
  - minimax-m2.7: TTFT 1.28с голый (принимает reasoning_effort=none)
  - kimi-k2.7-code: TTFT 2.5с голый, но **400 на reasoning_effort=none** — исключён
  - GLM-5.2, deepseek-v4-pro: 14-24с — медленные
- Звонок 11:25 (SCL_9A5TSgYarpLy): LLM-гонка выиграна minimax-m2.7 за 12с, диалог шёл, **без RuntimeError**.

## Инфраструктура / SSH

- **Прямой SSH работает:** `ssh root@217.149.23.113` (ключ ~/.freelance-2026/.ssh_agent_key не нужен — идёт с дефолтным).
- Туннель 22001 (запасной): `kill 875; nohup python3 ~/freelance-2026/projects/levitan/scripts/ssh_tunnel.py 22001 &`
- Стек: livekit.agents 1.6.6, venv /opt/pipecat-venv, агент /opt/pipecat-agent/levitan_agent.py, SIP-транк user4, кодек PCMA/8000 (у всех звонков одинаковый).
- systemd unit: /etc/systemd/system/levitan-agent.service, служба levitan-agent.
- Mango тест-звонок: `levitan_rtp_agent.mango_callback('79859234644', 'test_levitan_go_...')`, сигнатура sha256(API_KEY + j + API_SALT), ключи в /opt/pipecat-agent/.env, result 1000 = принят.

## RTP-статистика звонков (livekit-sip "call statistics", /root/.pm2/logs/livekit-sip-error.log)

| Звонок | audio_out_frames | mixer.input_samples | room.input_packets | mux_gaps |
|--------|------------------|--------------------|--------------------|----------|
| YEST 18:19 (рабочий) | 3010/481600 | 1290240 | 1344 | 0 |
| TODAY 09:36 | 2722/435520 | 744960 | 776 | 4 |
| TODAY 11:25 | 2054/328640 | 808320 | 842 | 1 (mixer.restarts=35) |

## Файлы для следующего агента

- /opt/pipecat-agent/levitan_agent.py (bak_winner, md5 d9a3e82a1b4d87487cb8cedafa4c71fb)
- /opt/pipecat-agent/levitan_agent.py.bak_endpointing — **рабочий звук вчера**
- /opt/pipecat-agent/levitan_agent.py.bak_winner, .bak_pauses, .bak_aexit2
- /root/levitan-agent.service.bak_20260811_go — юнит до правок (qwen+minimax)
- bench_ttft.py /opt/pipecat-agent/bench_ttft.py
- Локально: scripts/ssh_tunnel.py
