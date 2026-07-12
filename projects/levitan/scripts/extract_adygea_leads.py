#!/usr/bin/env python3
"""
Extract interesting Adygea leads from Mango call recordings.

Pipeline:
  1. Load Adygea phones (3 districts) from campaign CSVs
  2. Query Mango stats for campaign window (paginated)
  3. Filter calls with duration > 15s matching Adygea numbers
  4. Fetch transcripts via recording_transcripts
  5. Score interest (culture / volume / willingness to sell)
  6. Output Markdown table + CSV
"""

import csv
import hashlib
import json
import os
import re
import signal
import sys
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
sys.path.insert(0, os.path.dirname(__file__))
from mango_s2t import _post, norm_phone  # noqa: E402

API_KEY = os.getenv("MANGO_VPBX_API_KEY", "")
API_SALT = os.getenv("MANGO_VPBX_API_SALT", "")
_MODEL = None

DISTRICT_FILES = {
    "Гиагинский": "data/campaigns/csv/adygea_grain_Гиагинский_район.csv",
    "Кошехабльский": "data/campaigns/csv/adygea_grain_Кошехабльский_2025.csv",
    "Красногвардейский": "data/campaigns/csv/adygea_grain_Красногвардейский_2025.csv",
}
START = "05.07.2026 00:00:00"
END = "10.07.2026 23:59:59"
MIN_DURATION = 15
CULTURES = ["пшеница", "ячмень", "подсолнечник", "кукуруза", "соя", "рапс", "овёс", "овес",
            "горох", "нут", "чечевица", "рис", "гречиха", "просо", "подсол", "зернов", "маслич", "технич"]
INTEREST_KW = ["прода", "продам", "цена", "тонн", "объём", "объем", "интерес", "перезвони",
               "позвони", "менеджер", "скин", "пришл", "готов", "куп", "нужн", "сотруднич", "продаж"]


def timeout(signum, frame):
    raise TimeoutError("network timeout")


def load_adygea_phones():
    phones = {}
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for dist, rel in DISTRICT_FILES.items():
        fn = os.path.join(base, rel)
        with open(fn, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                raw = (r.get("Телефоны") or "").strip()
                name = (r.get("Имя") or r.get("Название") or "").strip()
                cult = (r.get("Описание") or "").strip()
                d = norm_phone(raw)
                if d:
                    phones[d[-10:]] = {"district": dist, "name": name, "culture": cult, "raw": raw}
    return phones


def fetch_all_calls():
    """Paginate Mango stats, return flat list of call legs with recordings."""
    calls = []
    offset = 0
    while True:
        req = _post("stats/calls/request", {
            "start_date": START, "end_date": END,
            "limit": 100, "offset": offset,
        })
        if not req or not req.get("key"):
            break
        key = req["key"]
        result = None
        deadline = time.time() + 40
        while time.time() < deadline:
            res = _post("stats/calls/result/", {"key": key})
            if res and res.get("status") == "complete":
                result = res
                break
            if res and res.get("status") in ("error", "cancel", "not-found"):
                break
            time.sleep(2)
        if not result:
            break
        data = result.get("data", [])
        if isinstance(data, dict):
            data = [data]
        page_calls = 0
        for day in data:
            clist = day.get("list", [])
            if isinstance(clist, dict):
                clist = [clist]
            for c in clist:
                page_calls += 1
                for leg in c.get("context_calls", []):
                    rec = leg.get("recording_id")
                    if rec:
                        calls.append({
                            "number": norm_phone(c.get("called_number", "")),
                            "duration": int(c.get("duration", 0) or 0),
                            "talk": int(c.get("talk_duration", 0) or 0),
                            "rec_id": rec[0] if isinstance(rec, list) else rec,
                            "entry_id": c.get("entry_id", ""),
                            "date": c.get("call_created", ""),
                        })
        if page_calls < 100:
            break
        offset += 100
        if offset > 5000:
            break
    return calls


def download_audio(rec_id, retries=3):
    """Download recording mp3 via Mango queries/recording/post."""
    global _MODEL
    payload = {"recording_id": rec_id, "action": "download"}
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    sign = hashlib.sha256((API_KEY + j + API_SALT).encode()).hexdigest()
    for attempt in range(retries):
        try:
            r = requests.post(
                "https://app.mango-office.ru/vpbx/queries/recording/post",
                data={"vpbx_api_key": API_KEY, "json": j, "sign": sign},
                timeout=60,
            )
            if r.status_code == 200 and len(r.content) > 1000:
                return r.content
        except Exception:
            pass
        time.sleep(5 * (attempt + 1))
    return None


def transcribe_audio(mp3_bytes):
    """Transcribe mp3 bytes with faster_whisper (model loaded once)."""
    global _MODEL
    if _MODEL is None:
        from faster_whisper import WhisperModel
        _MODEL = WhisperModel("base", device="cpu", compute_type="int8")
    tmp = "/tmp/adygea_rec_%d.mp3" % int(time.time() * 1000)
    with open(tmp, "wb") as f:
        f.write(mp3_bytes)
    try:
        segs, _ = _MODEL.transcribe(tmp, language="ru", beam_size=5, vad_filter=True)
        return " ".join(s.text for s in segs).strip()
    finally:
        try:
            os.remove(tmp)
        except Exception:
            pass


def get_transcript(rec_id, retries=3):
    audio = download_audio(rec_id, retries=retries)
    if not audio:
        return None
    return transcribe_audio(audio)


def analyze(transcript, base_culture):
    if not transcript:
        return None
    low = transcript.lower()
    found_cultures = [c for c in CULTURES if c in low]
    has_volume = bool(re.search(r"\d+\s*(тонн|т\.|тон|центнер|цт)", low))
    vol_match = re.search(r"(\d[\d\s]*)\s*(тонн|т\.|тон|центнер|цт)", low)
    volume = vol_match.group(0).strip() if vol_match else ""
    interest_hits = [k for k in INTEREST_KW if k in low]
    score = len(interest_hits) + len(found_cultures) * 2 + (3 if has_volume else 0)
    if not interest_hits and not found_cultures:
        return None
    return {
        "cultures": found_cultures or ([base_culture] if base_culture else []),
        "volume": volume,
        "interest": interest_hits,
        "score": score,
        "transcript": transcript,
    }


def main():
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(2400)
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "adygea_leads")
    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, "leads_raw.json")
    md_path = os.path.join(out_dir, "leads_transcripts.md")

    print("Loading Adygea phones...", file=sys.stderr)
    adygea = load_adygea_phones()
    print(f"  {len(adygea)} phones", file=sys.stderr)
    print("Fetching Mango calls...", file=sys.stderr)
    calls = fetch_all_calls()
    print(f"  {len(calls)} recorded call legs", file=sys.stderr)

    results = []
    seen = set()
    for c in calls:
        num = c["number"]
        if not num:
            continue
        key10 = num[-10:]
        if key10 not in adygea:
            continue
        if c["duration"] < MIN_DURATION and c["talk"] < MIN_DURATION:
            continue
        if c["rec_id"] in seen:
            continue
        seen.add(c["rec_id"])
        meta = adygea[key10]
        print(f"  transcribe {meta['name'][:30]} ({c['duration']}s)...", file=sys.stderr)
        tr = get_transcript(c["rec_id"])
        if not tr:
            continue
        entry = {
            "phone": num, "district": meta["district"], "name": meta["name"],
            "duration": c["duration"], "base_culture": meta["culture"], "transcript": tr,
        }
        a = analyze(tr, meta["culture"])
        if a:
            entry.update(a)
            results.append(entry)
        else:
            entry["score"] = 0
            entry["interest"] = []
            entry["cultures"] = [meta["culture"]] if meta["culture"] else []
            entry["volume"] = ""
            results.append(entry)
        # incremental save
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        time.sleep(1)

    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    hot = [r for r in results if r.get("score", 0) > 0]
    print(f"\n## 🔥 Интересные клиенты Адыгеи ({len(hot)} из {len(results)} обработано)\n")
    print("| # | Имя | Район | Телефон | Культура | Объём | Длит. | Заинтересованность |")
    print("|---|------|-------|---------|----------|-------|-------|---------------------|")
    for i, r in enumerate(hot, 1):
        name = re.sub(r"^(Глава|Дир|Предс)\.?\s*:\s*", "", r["name"])
        print(f"| {i} | {name} | {r['district']} | {r['phone']} | {', '.join(r.get('cultures', []))} "
              f"| {r.get('volume') or '—'} | {r['duration']}с | {', '.join(r.get('interest', [])[:4])} |")
    with open(md_path, "w", encoding="utf-8") as f:
        for i, r in enumerate(results, 1):
            f.write(f"### {i}. {r['name']} ({r['district']}) — score {r.get('score',0)}\n")
            f.write(f"Телефон: {r['phone']}\nКультура: {', '.join(r.get('cultures', []))}\n")
            f.write(f"Объём: {r.get('volume') or '—'}\nДлительность: {r['duration']}с\n\n")
            f.write(f"```\n{r['transcript']}\n```\n\n---\n\n")
    print(f"\nSaved → {json_path}\nSaved transcripts → {md_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
