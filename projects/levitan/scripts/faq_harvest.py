#!/usr/bin/env python3
"""
FAQ harvest — ночной сборник кандидатов в FAQ из записей звонков менеджеров.

Источник: /var/log/levitan/events.jsonl (recording_added) + Mango recording_transcripts.
Алгоритм:
  1. Разобрать events.jsonl за последние N часов → набор recording_id (UNIQUE).
  2. Для каждого recording_id → get_transcript (Mango API / bootstrap/re-use mango_s2t).
  3. Если транскрипт пуст -> пропустить.
  4. LLM (OmniRoute) извлекает пары (вопрос клиента -> ответ менеджера), короткие, пригодные для FAQ.
  5. Сборник в /root/faq_harvest/report_YYYYMMDD.md + кандидатов в .jsonl.
  6. Через системы подтверждения (реально — ручной просмотр отчёта) -> пополнение FAQ.

Запуск ночью (cron): 30 0 * * *  python3 /opt/faq-harvest/faq_harvest.py >> /var/log/levitan/faq_harvest.log 2>&1
"""

import json
import logging
import os
import re
import time
from collections import OrderedDict
from datetime import UTC, datetime, timedelta
from pathlib import Path

import requests

_ENV_CANDIDATES = [
    "/opt/levitan/projects/levitan/.env",
    "/opt/pipecat-agent/.env",
    os.path.expanduser("~/.env"),
]
for _p in _ENV_CANDIDATES:
    try:
        for _line in Path(_p).read_text(encoding="utf-8").splitlines():
            _line = _line.strip()
            if _line and "=" in _line and not _line.startswith("#"):
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k, _v)
    except FileNotFoundError:
        pass

log = logging.getLogger("faq_harvest")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

EVENTS = "/var/log/levitan/events.jsonl"
OUT_DIR = Path("/root/faq_harvest")
OUT_DIR.mkdir(parents=True, exist_ok=True)

MANGO_KEY = os.getenv("MANGO_VPBX_API_KEY", "")
MANGO_SALT = os.getenv("MANGO_VPBX_API_SALT", "")
API_BASE = "https://app.mango-office.ru/vpbx/"
OMNI = os.getenv("OMNIROUTE_BASE", "http://127.0.0.1:20128/v1")
LLM_MODEL = os.getenv("FAQ_HARVEST_MODEL", "deepseek/deepseek-chat")
LLM_PROXY = os.getenv("LLM_PROXY", "") or None

HOURS = int(os.getenv("FAQ_HARVEST_HOURS", "30"))


def _sign(payload: dict):
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    s = __import__("hashlib").sha256((MANGO_KEY + j + MANGO_SALT).encode()).hexdigest()
    return MANGO_KEY, j, s


def _post(endpoint: str, payload: dict, timeout: int = 30) -> dict | None:
    key, j, sign = _sign(payload)
    try:
        r = requests.post(
            f"{API_BASE}{endpoint}",
            data={"vpbx_api_key": key, "json": j, "sign": sign},
            timeout=timeout,
        )
        if r.status_code == 429:
            return None
        return r.json()
    except Exception as e:
        log.error("API %s: %s", endpoint, e)
        return None


def collect_recording_ids(hours: int) -> list[str]:
    """recording_id из events.jsonl за последние N часов, по порядку, UNIQUE."""
    now = datetime.now(UTC)
    cutoff = now - timedelta(hours=hours)
    seen: OrderedDict[str, None] = OrderedDict()
    try:
        for line in Path(EVENTS).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            ts_raw = ev.get("timestamp", "")
            if ts_raw:
                try:
                    ts = datetime.fromisoformat(ts_raw)
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=UTC)
                except Exception:
                    ts = None
                if ts is not None and ts < cutoff:
                    continue
            if ev.get("type") == "recording_added":
                rid = str(ev.get("recording_id", "")).strip()
                if rid:
                    seen[rid] = None
    except FileNotFoundError:
        log.warning("events.jsonl не найден: %s", EVENTS)
    return list(seen.keys())


def get_transcript(recording_id: str) -> str | None:
    """Mango recording_transcripts -> тело расшифровки (list[dict] текст)."""
    data = _post(
        "queries/recording_transcripts/",
        {"recording_id": recording_id},
        timeout=60,
    )
    if not data:
        return None
    res = data.get("result") or data.get("data") or data
    text_parts = []
    if isinstance(res, list):
        for item in res:
            if isinstance(item, dict):
                t = item.get("transcript") or item.get("text") or ""
                if t:
                    text_parts.append(str(t))
            elif isinstance(item, str):
                text_parts.append(item)
    elif isinstance(res, dict):
        t = res.get("transcript") or res.get("text")
        if t:
            text_parts.append(str(t))
    txt = "\n".join(text_parts).strip()
    if txt:
        return txt
    log.info("  %s: Mango transcripts недоступен (5008), fallback → whisper", recording_id)
    return transcribe_via_whisper(recording_id)


def _download_audio(recording_id: str) -> bytes | None:
    """Mango queries/recording/post action=download -> mp3 bytes."""
    payload = {"recording_id": recording_id, "action": "download"}
    key, j, sign = _sign(payload)
    try:
        r = requests.post(
            f"{API_BASE}queries/recording/post",
            data={"vpbx_api_key": key, "json": j, "sign": sign},
            timeout=120,
        )
        if r.status_code == 200 and len(r.content) > 1024:
            return r.content
    except Exception as e:
        log.error("download %s: %s", recording_id, e)
    return None


_WHISPER_MODEL = None


def transcribe_via_whisper(recording_id: str) -> str | None:
    """Fallback: скачать mp3 и расшифровать faster-whisper локально."""
    global _WHISPER_MODEL
    audio = _download_audio(recording_id)
    if not audio:
        return None
    try:
        if _WHISPER_MODEL is None:
            from faster_whisper import WhisperModel

            _WHISPER_MODEL = WhisperModel("base", device="cpu", compute_type="int8")
        tmp = f"/tmp/faq_harvest_{int(time.time() * 1000)}.mp3"
        with open(tmp, "wb") as f:
            f.write(audio)
        try:
            segs, _ = _WHISPER_MODEL.transcribe(tmp, language="ru", beam_size=5, vad_filter=True)
            return " ".join(s.text for s in segs).strip()
        finally:
            try:
                os.remove(tmp)
            except Exception:
                pass
    except Exception as e:
        log.error("whisper %s: %s", recording_id, e)
        return None


def extract_qa(text: str) -> list[dict]:
    """LLM из транскрипта диалога: пары (вопрос, ответ менеджера) → кандидаты FAQ.
    Возвращает [{"trigger": str, "answer": str}, ...]."""
    if LLM_PROXY:
        return _extract_qa_proxied(text)
    return _extract_qa_omni(text)


def _extract_qa_omni(text: str) -> list[dict]:
    prompt_ = _qa_prompt(text)
    try:
        r = requests.post(
            f"{OMNI}/chat/completions",
            json={
                "model": LLM_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Ты анализируешь стенограмму звонка менеджера птицефабрики и клиента. "
                            "Извлекаешь вопросы клиента и ТОЧНЫЕ ответы менеджера, пригодные для FAQ."
                        ),
                    },
                    {"role": "user", "content": prompt_},
                ],
                "temperature": 0.2,
                "max_tokens": 900,
            },
            timeout=60,
        )
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        return _parse_qa_json(content)
    except Exception as e:
        log.error("LLM extract: %s", e)
        return []


def _extract_qa_proxied(text: str) -> list[dict]:
    prompt_ = _qa_prompt(text)
    try:
        r = requests.post(
            f"{OMNI}/chat/completions",
            json={
                "model": LLM_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Ты анализируешь стенограмму звонка менеджера птицефабрики и клиента. "
                            "Извлекаешь вопросы клиента и ТОЧНЫЕ ответы менеджера, пригодные для FAQ."
                        ),
                    },
                    {"role": "user", "content": prompt_},
                ],
                "temperature": 0.2,
                "max_tokens": 900,
            },
            timeout=60,
            proxies={"http": LLM_PROXY, "https": LLM_PROXY},
        )
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        return _parse_qa_json(content)
    except Exception as e:
        log.error("LLM extract: %s", e)
        return []


def _qa_prompt(text: str) -> str:
    return f"""Ниже стенограмма диалога. Извлеки максимум 6 пар вопрос-ответ менеджера,
которые могут стать FAQ-записями. Требования:
- trigger: короткий типичный вопрос клиента (как его обычно формулируют).
- answer: ответ менеджера, факты БЕЗ галлюцинаций, 1-3 предложения.
- НЕ включай: личные данные, номера телефонов, историю конкретного заказа.
Верни ТОЛЬКО JSON-массив, например:
[{{"trigger": "доставляете ли в москву", "answer": "Да, доставляем по всей России, подробности уточнит менеджер."}}]

СТЕНОГРАММА:
{text[:6000]}
"""


def _parse_qa_json(content: str) -> list[dict]:
    m = re.search(r"\[.*\]", content, re.S)
    if not m:
        return []
    try:
        parsed = json.loads(m.group(0))
    except Exception as e:
        log.error("parse QA json: %s", e)
        return []
    out = []
    for it in parsed:
        if isinstance(it, dict) and it.get("trigger") and it.get("answer"):
            out.append({"trigger": str(it["trigger"]).strip(), "answer": str(it["answer"]).strip()})
    return out


def render_report(records: list[dict]) -> str:
    lines = [
        f"# FAQ harvest — {datetime.now().isoformat()}",
        f"Записей разобрано: {len(records)}\n",
    ]
    for rec in records:
        lines.append("---")
        lines.append(f"### {rec['recording_id']}")
        lines.append(f"- источник: {rec.get('source')}")
        lines.append("")
        for qa in rec.get("qa", []):
            lines.append(f"**Q:** {qa['trigger']}")
            lines.append(f"**A:** {qa['answer']}")
            lines.append("")
    return "\n".join(lines)


def main():
    ids = collect_recording_ids(HOURS)
    log.info("recording_ids за %s ч: %s", HOURS, len(ids))
    records = []
    for rid in ids:
        txt = get_transcript(rid)
        if not txt:
            log.info("  skip %s (нет транскрипта)", rid)
            continue
        log.info("  %s: %s символов", rid, len(txt))
        qa = extract_qa(txt)
        if not qa:
            continue
        records.append({"recording_id": rid, "source": "mango_transcript", "qa": qa})
        time.sleep(0.5)
    report = render_report(records)
    today = datetime.now().strftime("%Y%m%d")
    out = OUT_DIR / f"report_{today}.md"
    out.write_text(report, encoding="utf-8")
    log.info("Отчёт: %s (пар: %s)", out, sum(len(r["qa"]) for r in records))


if __name__ == "__main__":
    main()
