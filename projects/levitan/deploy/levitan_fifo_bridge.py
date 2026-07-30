#!/usr/bin/env python3
"""Levitan FIFO Bridge — real-time аудио-мост для baresip.

baresip читает аудио из FIFO. Этот скрипт непрерывно пишет в FIFO:
тишина → TTS ответ → тишина. Параллельно читает dec.wav (голос клиента)
через sndfile, делает STT → FAQ-кэш → TTS.

Запуск: python3 deploy/levitan_fifo_bridge.py
"""

import json
import logging
import os
import re
import threading
import time
import wave
from difflib import SequenceMatcher
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

FIFO_PATH = Path("/tmp/levitan_fifo")
BARESIP_RECORD_DIR = Path.home() / ".baresip" / "recordings"
GREETING_WAV = Path("/tmp/levitan_greeting_lead.wav")
FAQ_CACHE_PATH = Path(__file__).resolve().parent.parent / "docs" / "ANGELLA_BROILERS_FAQ_CACHE.json"
LOG_DIR = Path("/var/log/levitan")
LOG_DIR.mkdir(parents=True, exist_ok=True)

API_KEY = os.getenv("MANGO_VPBX_API_KEY", "")
API_SALT = os.getenv("MANGO_VPBX_API_SALT", "")
MANGO_FROM_EXTENSION = os.getenv("MANGO_FROM_EXTENSION", "22")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(LOG_DIR / "fifo_bridge.log")],
)
log = logging.getLogger("fifo-bridge")

_faq_cache: dict = {}
_whisper_model = None

SAMPLE_RATE = 8000
SAMPLE_WIDTH = 2
CHANNELS = 1

REJECTION_PHRASES = [
    "не интересно",
    "не интересует",
    "не надо",
    "отказ",
    "до свидания",
    "не продаем",
    "не продаём",
    "не выращиваем",
    "не нужно",
    "не хочу",
    "не буду",
]


def get_whisper():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel

        _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
        log.info("Whisper model loaded")
    return _whisper_model


def transcribe(wav_path: str) -> str:
    try:
        model = get_whisper()
        segments, _ = model.transcribe(wav_path, language="ru", beam_size=5, vad_filter=True)
        text = " ".join(s.text for s in segments).strip()
        if text:
            log.info(f"STT: «{text[:100]}»")
        return text
    except Exception as e:
        log.error(f"STT error: {e}")
        return ""


def load_faq_cache():
    global _faq_cache
    try:
        data = json.loads(FAQ_CACHE_PATH.read_text(encoding="utf-8"))
        _faq_cache = {k: v for k, v in data.items() if not k.startswith("_")}
        log.info(f"FAQ cache: {len(_faq_cache)} triggers")
    except Exception as e:
        log.error(f"FAQ load: {e}")


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[ёй]", lambda m: {"ё": "е", "й": "и"}.get(m.group(), m.group()), text)
    text = re.sub(r"[^а-я0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def faq_lookup(text: str) -> str | None:
    if not _faq_cache:
        return None
    norm = normalize(text)
    if len(norm) < 3:
        return None
    best_score = 0.0
    best_reply = None
    for trigger, reply in _faq_cache.items():
        score = SequenceMatcher(None, norm, normalize(trigger)).ratio()
        if score > best_score:
            best_score = score
            best_reply = reply
    if best_score >= 0.72:
        log.info(f"FAQ match ({best_score:.2f}): {text[:40]} → {best_reply[:60]}")
        return best_reply
    return None


def synthesize_wav(text: str) -> Path | None:
    try:
        import edge_tts

        tmp_mp3 = Path(f"/tmp/tts_{hash(text)}.mp3")
        tmp_wav = Path(f"/tmp/tts_{hash(text)}.wav")
        if tmp_wav.exists():
            return tmp_wav
        import asyncio

        asyncio.run(edge_tts.Communicate(text, "ru-RU-DariyaNeural").save(str(tmp_mp3)))
        import subprocess

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(tmp_mp3),
                "-acodec",
                "pcm_s16le",
                "-ar",
                str(SAMPLE_RATE),
                "-ac",
                "1",
                str(tmp_wav),
            ],
            capture_output=True,
            timeout=30,
        )
        if tmp_wav.exists():
            return tmp_wav
    except Exception as e:
        log.error(f"TTS error: {e}")
    try:
        from levitan_faq_agent import synthesize_wav as old_tts

        return old_tts(text)
    except Exception:
        return None


class SilenceGenerator:
    def __init__(self):
        self.frame_size = int(SAMPLE_RATE * SAMPLE_WIDTH * CHANNELS * 0.02)
        self.silence = b"\x00" * self.frame_size

    def generate(self, seconds: float):
        frames = int(SAMPLE_RATE * seconds)
        return b"\x00" * (frames * SAMPLE_WIDTH * CHANNELS)


class FifoWriter:
    def __init__(self):
        self.fifo = FIFO_PATH
        self.fd = None
        self.running = False
        self._greeting_sent = False

    def open(self):
        if self.fifo.exists():
            self.fifo.unlink()
        os.mkfifo(str(self.fifo))
        os.chmod(str(self.fifo), 0o777)
        log.info(f"FIFO created: {self.fifo}")
        self.fd = os.open(str(self.fifo), os.O_WRONLY)
        log.info("FIFO opened for writing")
        self.running = True
        t = threading.Thread(target=self._silence_loop, daemon=True)
        t.start()

    def _silence_loop(self):
        silence = SilenceGenerator()
        while self.running:
            try:
                os.write(self.fd, silence.silence)
                time.sleep(0.02)
            except BrokenPipeError:
                log.info("FIFO broken pipe (call ended)")
                time.sleep(1)
                break
            except Exception as e:
                log.error(f"FIFO write: {e}")
                time.sleep(0.1)

    def write_wav(self, wav_path: Path, lead_seconds: float = 0.0):
        if not wav_path.exists():
            log.error(f"WAV not found: {wav_path}")
            return
        try:
            with wave.open(str(wav_path), "rb") as w:
                params = w.getparams()
                frames = w.readframes(w.getnframes())
            data = frames
            if lead_seconds > 0:
                lead = (
                    b"\x00"
                    * int(params.framerate * lead_seconds)
                    * params.sampwidth
                    * params.nchannels
                )
                data = lead + frames
            chunk_size = 320
            for i in range(0, len(data), chunk_size):
                if not self.running:
                    break
                os.write(self.fd, data[i : i + chunk_size])
                time.sleep(0.02)
        except Exception as e:
            log.error(f"Write WAV error: {e}")

    def write_pcm(self, data: bytes):
        try:
            os.write(self.fd, data)
        except Exception:
            pass

    def close(self):
        self.running = False
        if self.fd:
            try:
                os.close(self.fd)
            except Exception:
                pass
        if self.fifo.exists():
            self.fifo.unlink()


class DecWatcher:
    def __init__(self, fifo: FifoWriter):
        self.fifo = fifo
        self.last_size = 0
        self.last_path = None

    def _latest_dec(self) -> Path | None:
        if not BARESIP_RECORD_DIR.exists():
            return None
        decs = sorted(
            BARESIP_RECORD_DIR.glob("dump-*-dec.wav"), key=lambda p: p.stat().st_mtime, reverse=True
        )
        return decs[0] if decs else None

    def wait_for_new_audio(self, timeout: float = 30.0) -> Path | None:
        start = time.time()
        while time.time() - start < timeout:
            rec = self._latest_dec()
            if rec:
                size = rec.stat().st_size
                if self.last_path and rec.name != self.last_path.name:
                    self.last_path = rec
                    self.last_size = 0
                    return rec
                if size > self.last_size + 16000:
                    self.last_size = size
                    return rec
                if self.last_path is None:
                    self.last_path = rec
                    self.last_size = size
            time.sleep(0.2)
        return None

    def get_new_chunks(self, prev_size: int = 0) -> tuple[Path, int]:
        rec = self._latest_dec()
        if not rec:
            return None, prev_size
        size = rec.stat().st_size
        return rec, size

    def get_client_response(self, timeout: float = 15.0) -> str:
        dec_path = self.wait_for_new_audio(timeout=timeout)
        if not dec_path:
            return ""
        time.sleep(1.0)
        return transcribe(str(dec_path))


def mango_callback(phone: str, command_id: str = "") -> dict:
    import hashlib
    import requests

    if not command_id:
        command_id = f"levitan_{phone[-4:]}{int(time.time())}"
    payload = {
        "command_id": command_id,
        "from": {"extension": MANGO_FROM_EXTENSION},
        "to_number": phone,
    }
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    sign = hashlib.sha256((API_KEY + j + API_SALT).encode()).hexdigest()
    try:
        r = requests.post(
            "https://app.mango-office.ru/vpbx/commands/callback",
            data={"vpbx_api_key": API_KEY, "json": j, "sign": sign},
            timeout=20,
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def main():
    log.info("=" * 60)
    log.info("LEVITAN FIFO BRIDGE STARTED (real-time)")
    log.info("=" * 60)
    load_faq_cache()

    fifo = FifoWriter()
    fifo.open()

    dec = DecWatcher(fifo)

    last_call_phone = ""

    try:
        while True:
            dec_path = dec.wait_for_new_audio(timeout=60.0)
            if not dec_path:
                continue
            size = dec_path.stat().st_size
            if size < 16000:
                time.sleep(2)
                continue
            log.info(f"New audio detected: {dec_path.name} ({size} bytes)")
            text = transcribe(str(dec_path))
            if not text or len(text.strip()) < 3:
                continue
            rejected = any(p in text.lower() for p in REJECTION_PHRASES)
            if rejected:
                log.info("Rejection detected")
                continue
            interested = not rejected
            if interested:
                log.info("INTEREST detected!")
                answer = faq_lookup(text)
                if answer:
                    tts = synthesize_wav(answer)
                    if tts:
                        fifo.write_wav(tts, lead_seconds=0.5)
                        log.info(f"Answer played: {answer[:60]}")
                else:
                    tts = synthesize_wav("Спасибо за интерес! Наш менеджер перезвонит вам.")
                    if tts:
                        fifo.write_wav(tts, lead_seconds=0.5)
            time.sleep(5)
    except KeyboardInterrupt:
        log.info("Shutting down...")
    finally:
        fifo.close()


if __name__ == "__main__":
    main()
