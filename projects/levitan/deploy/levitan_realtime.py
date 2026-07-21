#!/usr/bin/env python3
"""Levitan Realtime — WS-прокси к Яндекс Realtime API (ADR-001).

Архитектура (из ADR-001):
    Клиент (телефон) → Mango callback → baresip (8kHz PCM s16, FIFO)
        → ЭТОТ прокси (ресэмплинг 8k↔24k)
        → wss://llm.api.cloud.yandex.net/.../realtime
        → аудио-дельты (24kHz) → baresip → клиенту

Прокси ОБЯЗАТЕЛЕН: у Яндекса нет ephemeral-токенов для клиента,
а SIP/браузер не ставит `Authorization: Api-Key`. Прокси держит ключ.

TODO (Этапы 2-5 ADR-001):
  - [ ] asyncio мост client_ws ↔ yc_ws (PCM 8k↔24k через audioop)
  - [ ] session.update: промпт из levitan_realtime_prompt.SYSTEM_PROMPT,
        voice=YC_REALTIME_VOICE, server_vad, tools=[save_lead]
  - [ ] FAQ-кэш: при совпадении триггера → отдать предзагруженное аудио
        (ADR-002: filler/pre-buffer, latency < 500мс)
  - [ ] function calling response.output_item.done → POST /api/contacts (save_lead)
  - [ ] barge-in: speech_started прерывает ответ
  - [ ] тёплый пул WS к Яндексу (ADR-002)
"""

import asyncio
import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import websockets

# === CONFIG (из .env) ===
YC_API_KEY = os.getenv("YC_API_KEY", "__FILL_ME__")
YC_FOLDER_ID = os.getenv("YC_FOLDER_ID", "__FILL_ME__")
YC_REALTIME_MODEL = os.getenv("YC_REALTIME_MODEL", "yandex-rt")
YC_REALTIME_VOICE = os.getenv("YC_REALTIME_VOICE", "alena")
YC_RT_URL = "wss://llm.api.cloud.yandex.net/llm/v1/realtime"

# Промпт + FAQ-кэш + save_lead tool
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from levitan_realtime_prompt import SYSTEM_PROMPT, FAQ_CACHE, TOOLS, build_dynamic_suffix

LOG_DIR = Path(os.getenv("LEVITAN_LOG_DIR", "/var/log/levitan"))
try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
except PermissionError:
    LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
    LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(LOG_DIR / "realtime.log")],
)
log = logging.getLogger("levitan-realtime")


# === ЗАГЛУШКИ (наполняются на Этапах 2-5) ===

async def connect_yandex(ws_path: str = YC_RT_URL) -> "websockets.WebSocketClientProtocol":
    """Открыть WS к Яндекс Realtime с Api-Key в заголовке.

    TODO: держать тёплый пул (ADR-002) вместо открытия с нуля на каждый звонок.
    """
    headers = {"Authorization": f"Api-Key {YC_API_KEY}"}
    log.info(f"Connecting to Yandex Realtime: {ws_path}")
    return await websockets.connect(ws_path, additional_headers=headers)


async def send_session_update(yc_ws):
    """Отправить session.update: промпт + голос + VAD + tools.

    Динамика (caller_id/город/даты) — ЧЕРЕЗ build_dynamic_suffix в КОНЕЦ
    (ADR-002: byte-стабильный промпт → prefix cache hit ≥80%).
    """
    dynamic = build_dynamic_suffix()  # TODO: реальные данные звонка
    payload = {
        "type": "session.update",
        "session": {
            "folderId": YC_FOLDER_ID,
            "instructions": SYSTEM_PROMPT + dynamic,
            "voice": YC_REALTIME_VOICE,
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "input_audio_transcription": {"model": "kora-rtc"},
            "turn_detection": {"type": "server_vad", "silence_duration_ms": 300},
            "tools": TOOLS,
            "tool_choice": "auto",
        },
    }
    await yc_ws.send(json.dumps(payload))
    log.info("session.update sent (byte-stable prompt + dynamic suffix)")


async def handle_tool_call(yc_ws, item: dict):
    """response.output_item.done с tool=save_lead → сохранить лид.

    TODO: POST /api/contacts (CRM ai-eggs / Битрикс24) или локальная CRM Левитана.
    Пока — заглушка с логом.
    """
    args = item.get("arguments", {})
    log.info(f"save_lead → {args}")
    # TODO: httpx.post(CRM_URL, json=args)
    await yc_ws.send(json.dumps({
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "system",
            "content": [{"type": "text", "text": "Лид сохранён. Подтвердите клиенту."}],
        },
    }))


async def faq_cache_lookup(transcript: str) -> str | None:
    """Поиск по FAQ-кэшу (ADR-002, минимальная задержка).

    TODO: нормализация + fuzzy/semantic match против FAQ_CACHE ключей.
    При命中 → вернуть готовую реплику (без LLM). Пока — заглушка (всегда None).
    """
    return None


async def bridge_call(client_ws, call_meta: dict):
    """Основной цикл моста для одного звонка.

    client_ws — WebSocket от baresip/телефонии (PCM 8kHz s16).
    yc_ws — WebSocket к Яндексу (PCM 24kHz s16).
    TODO: resample 8k↔24k (audioop.ratecv), маршрутизация событий:
      client→yc: input_audio_buffer.append
      yc→client: response.output_audio.delta
      yc: speech_started (barge-in), response.output_item.done (tool)
    """
    yc_ws = await connect_yandex()
    await send_session_update(yc_ws)
    log.info(f"Bridge started for call {call_meta.get('call_id')}")
    # TODO: asyncio.gather(client_to_yc, yc_to_client, faq_shortcut)
    await yc_ws.close()


async def voice_stream_endpoint(websocket):
    """FastAPI WS endpoint /voice/stream-rt (ADR-001 Этап 2).

    Принимает PCM-аудио от baresip, мостит в Яндекс Realtime.
    """
    call_meta = {"call_id": websocket.headers.get("x-call-id", "unknown")}
    await bridge_call(websocket, call_meta)


# === Запуск (заглушка, для локальной проверки коннекта) ===
async def _smoke_test():
    """Проверка доступов: коннект + session.update без аудио-моста."""
    if YC_API_KEY == "__FILL_ME__":
        log.error("YC_API_KEY не заполнен — см. docs/YANDEX_SETUP.md")
        return
    try:
        ws = await connect_yandex()
        await send_session_update(ws)
        log.info("✅ Smoke test OK: коннект и session.update прошли")
        await ws.close()
    except Exception as e:
        log.error(f"Smoke test FAILED: {e}")


if __name__ == "__main__":
    asyncio.run(_smoke_test())
