"""WebSocket-сервер для обработки событий Mango Office."""

import logging

from fastapi import FastAPI, Request

logger = logging.getLogger(__name__)

app = FastAPI(title="Levitan Webhook Server")

# Хранилище активных звонков
active_calls: dict[str, dict] = {}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "active_calls": len(active_calls)}


@app.post("/mango/webhook")
async def mango_webhook(request: Request):
    """
    Webhook endpoint для событий Mango Office.

    Обрабатывает:
    - call_state: начало/завершение звонка
    - dtmf: нажатие клавиш
    - recording_added: добавление записи
    """
    try:
        data = await request.json()
        event_type = data.get("event")
        call_id = data.get("call_id")

        logger.info(f"Mango event: {event_type}, call_id: {call_id}")

        # Обработка событий звонка
        if event_type == "call_state":
            await _handle_call_state(data)
        elif event_type == "dtmf":
            await _handle_dtmf(data)
        elif event_type == "recording_added":
            await _handle_recording(data)

        return {"result": 0}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"result": 1, "error": str(e)}


async def _handle_call_state(data: dict):
    """Обработка события состояния звонка."""
    call_id = data.get("call_id")
    state = data.get("state")

    if call_id:
        if call_id not in active_calls:
            active_calls[call_id] = {}

        active_calls[call_id]["state"] = state
        active_calls[call_id]["data"] = data

        if state == "answer":
            logger.info(f"Call answered: {call_id}")
            # Уведомляем об активном звонке
            await _notify_call_started(call_id, data)
        elif state == "end":
            logger.info(f"Call ended: {call_id}")
            await _notify_call_ended(call_id, data)
            # Удаляем из активных через время
            if call_id in active_calls:
                del active_calls[call_id]


async def _handle_dtmf(data: dict):
    """Обработка DTMF сигнала."""
    call_id = data.get("call_id")
    digit = data.get("digit")

    logger.info(f"DTMF: call_id={call_id}, digit={digit}")

    if call_id and call_id in active_calls:
        active_calls[call_id]["last_dtmf"] = digit
        await _notify_dtmf(call_id, digit)


async def _handle_recording(data: dict):
    """Обработка добавления записи звонка."""
    call_id = data.get("call_id")
    recording_url = data.get("recording_url")

    logger.info(f"Recording added: call_id={call_id}, url={recording_url}")

    if call_id and call_id in active_calls:
        active_calls[call_id]["recording_url"] = recording_url


async def _notify_call_started(call_id: str, data: dict):
    """Уведомление о начале звонка."""
    # Здесь будет интеграция с call_session
    pass


async def _notify_call_ended(call_id: str, data: dict):
    """Уведомление о завершении звонка."""
    # Здесь будет интеграция с post_call
    pass


async def _notify_dtmf(call_id: str, digit: str):
    """Уведомление о DTMF сигнале."""
    # Здесь будет интеграция с call_session
    pass


def get_active_call(call_id: str) -> dict | None:
    """Получить информацию об активном звонке."""
    return active_calls.get(call_id)


def update_call_data(call_id: str, key: str, value):
    """Обновить данные звонка."""
    if call_id in active_calls:
        active_calls[call_id][key] = value
