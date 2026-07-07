#!/usr/bin/env python3
"""
Mango — получение расшифровок разговоров через API.

Алгоритм:
  1. Расширенная статистика (calls/request → calls/result) → recording_id
  2. recording_transcripts → текст расшифровки
  3. Если 2 недоступен (rate limit) → fallback на Whisper

Требует: MANGO_VPBX_API_KEY, MANGO_VPBX_API_SALT в .env
"""

import hashlib
import json
import logging
import os
import re
import time
from datetime import datetime, timedelta
from typing import Optional

import requests

log = logging.getLogger("mango_s2t")

API_KEY = os.getenv("MANGO_VPBX_API_KEY", "")
API_SALT = os.getenv("MANGO_VPBX_API_SALT", "")
API_BASE = "https://app.mango-office.ru/vpbx/"


def norm_phone(num: str) -> str:
    d = re.sub(r"\D", "", num or "")
    if len(d) == 11 and d.startswith("8"):
        d = "7" + d[1:]
    elif len(d) == 10:
        d = "7" + d
    return d


def _sign(payload: dict) -> tuple[str, str, str]:
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    s = hashlib.sha256((API_KEY + j + API_SALT).encode()).hexdigest()
    return API_KEY, j, s


def _post(endpoint: str, payload: dict, timeout: int = 30) -> Optional[dict]:
    key, j, sign = _sign(payload)
    try:
        r = requests.post(
            f"{API_BASE}{endpoint}",
            data={"vpbx_api_key": key, "json": j, "sign": sign},
            timeout=timeout,
        )
        if r.status_code == 429:
            log.warning("Rate limited on %s", endpoint)
            return None
        data = r.json()
        result = data.get("result", -1)
        if result != 1000 and result != -1:
            log.debug("API %s → result=%s", endpoint, result)
        return data
    except Exception as e:
        log.error("API %s: %s", endpoint, e)
        return None


def _poll_stats(key: str, max_wait: int = 30) -> Optional[dict]:
    deadline = time.time() + max_wait
    while time.time() < deadline:
        data = _post("stats/calls/result/", {"key": key})
        if not data:
            time.sleep(2)
            continue
        status = data.get("status", "")
        if status == "complete":
            return data
        if status in ("error", "cancel", "not-found"):
            return None
        time.sleep(2)
    return None


def find_recording_via_stats(
    phone: str, after_ts: float, timeout: int = 60
) -> Optional[dict]:
    """
    Найти recording_id через расширенную статистику ВАТС.
    Возвращает dict: {recording_id, entry_id, duration, talk_duration, called_number}
    """
    target = norm_phone(phone)
    if not target:
        return None

    start_dt = datetime.fromtimestamp(after_ts - 120).strftime("%d.%m.%Y %H:%M:%S")
    end_dt = (datetime.fromtimestamp(after_ts) + timedelta(hours=2)).strftime("%d.%m.%Y %H:%M:%S")

    resp = _post("stats/calls/request", {
        "start_date": start_dt,
        "end_date": end_dt,
        "limit": 50,
        "offset": 0,
        "search_string": target,
    })
    if not resp:
        log.info("Stats request failed for %s", phone)
        return None

    stats_key = resp.get("key")
    if not stats_key:
        return None

    result = _poll_stats(stats_key, max_wait=timeout)
    if not result:
        return None

    data = result.get("data", [])
    if isinstance(data, dict):
        data = [data]

    for day in data:
        call_list = day.get("list", [])
        if isinstance(call_list, dict):
            call_list = [call_list]
        for call in call_list:
            if norm_phone(call.get("called_number", "")) != target:
                continue
            if call.get("talk_duration", 0) == 0:
                continue
            context_calls = call.get("context_calls", [])
            for leg in context_calls:
                rec_ids = leg.get("recording_id", [])
                if rec_ids:
                    return {
                        "recording_id": rec_ids[0],
                        "entry_id": call.get("entry_id", ""),
                        "duration": call.get("duration", 0),
                        "talk_duration": call.get("talk_duration", 0),
                        "called_number": call.get("called_number", ""),
                    }

    return None


def get_transcript(recording_id: str, retries: int = 3) -> Optional[str]:
    """
    Получить расшифровку разговора через recording_transcripts.
    Возвращает текст расшифровки (все фразы склеенные).
    """
    for attempt in range(retries):
        resp = _post("queries/recording_transcripts", {
            "recording_id": recording_id,
        }, timeout=60)
        if resp is None and attempt < retries - 1:
            time.sleep(10 * (attempt + 1))
            continue

        if not resp:
            return None

        data = resp.get("data")
        if not data:
            return None

        phrases = data.get("phrases", [])
        if not phrases:
            return None

        parts = []
        for phrase in phrases:
            if isinstance(phrase, list) and len(phrase) >= 2:
                speaker = phrase[0]
                text = phrase[1]
                speaker_label = {"client": "Клиент", "operator": "Оператор"}.get(speaker, speaker)
                parts.append(f"{speaker_label}: {text}")

        return "\n".join(parts) if parts else None

    return None


def fetch_summary(phone: str, after_ts: float, timeout: int = 60) -> Optional[str]:
    """
    Полный цикл: найти recording_id → получить расшифровку.
    Возвращает текст расшифровки или None.
    """
    found = find_recording_via_stats(phone, after_ts, timeout=timeout)
    if not found:
        return None

    rec_id = found["recording_id"]
    log.info("Found recording_id for %s: %s", phone, rec_id[:40])

    transcript = get_transcript(rec_id)
    return transcript
