#!/usr/bin/env python3
"""
Levitan Turn-Based Dialog Engine
=================================
Архитектура: каждый ход диалога = отдельный callback-звонок.

Цикл:
1. Подменяем WAV → callback → baresip проигрывает WAV клиенту
2. Клиент отвечает → baresip записывает dec.wav
3. Disconnect (5 сек тишины или клиент вешает трубку)
4. Берём запись → STT → LLM → TTS → новый WAV
5. Новый callback → goto 1

Зависимости (VPS): faster-whisper, edge-tts, ffmpeg, requests
Запуск: python3 levitan_turnbased.py
PM2: pm2 start levitan_turnbased.py --name levitan-dialog --interpreter python3
"""

import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
import threading
import uuid
import wave
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

# === CONFIG ===
API_KEY = os.getenv("MANGO_VPBX_API_KEY", "")
API_SALT = os.getenv("MANGO_VPBX_API_SALT", "")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("LEVITAN_TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("LEVITAN_TELEGRAM_CHAT_ID", "")

MANGO_API_BASE = "https://app.mango-office.ru/vpbx/"
MANGO_FROM_EXTENSION = os.getenv("MANGO_FROM_EXTENSION", "22")

# Пути
BARESIP_AUFILE_PATH = Path(os.getenv("BARESIP_AUFILE_PATH", "/tmp/levitan_play.wav"))
BARESIP_RECORD_DIR = Path(os.getenv("BARESIP_RECORD_DIR", "/root"))
GREETING_WAV = Path(os.getenv("LEVITAN_GREETING_WAV", "/tmp/levitan_greeting_lead.wav"))
TTS_OUTPUT_DIR = Path("/tmp/levitan_tts")
TTS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LOG_DIR = Path(os.getenv("LEVITAN_LOG_DIR", "/var/log/levitan"))
LOG_DIR.mkdir(parents=True, exist_ok=True)
EVENTS_PATH = LOG_DIR / "events.jsonl"
DIALOGS_DIR = LOG_DIR / "dialogs"
DIALOGS_DIR.mkdir(parents=True, exist_ok=True)

# Параметры диалога
MAX_TURNS = int(os.getenv("LEVITAN_MAX_TURNS", "8"))
CALLBACK_DELAY = float(os.getenv("LEVITAN_CALLBACK_DELAY", "3.0"))  # сек между турами
RECORDING_WAIT_TIMEOUT = int(os.getenv("LEVITAN_RECORDING_WAIT", "30"))  # макс ожидание записи
MIN_RECORDING_SIZE = 2000  # минимальный размер записи (байт) для обработки

# === LOGGING ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "turnbased.log"),
    ],
)
log = logging.getLogger("levitan-tb")

# === LLM PROMPT ===
SYSTEM_PROMPT = """Ты — Иван, менеджер по закупкам компании «Глобал Филдс Экспорт».
Ты звонишь сельхозпроизводителям и агрохолдингам, чтобы предложить выкуп их урожая.

Компания закупает:
- Зерновые: пшеница, ячмень, кукуруза
- Масличные: подсолнечник, рапс, соя
- Бобовые: горох, нут, чечевица

Базисы: CPT, FOB, DAP.
Контакты: +7(918)639-30-30, info@globalfields.ru

Цель: выяснить заинтересованность, собрать данные (культура, объем, регион, базис, сроки).

Правила:
- Говори как живой человек, кратко (1-2 предложения)
- Задавай один вопрос за раз
- Не дави, не навязывай
- Если клиент не заинтересован — вежливо прощайся
- Если заинтересован — собери максимальную информацию
- Отвечай ТОЛЬКО репликой для голоса. Без markdown, списков, эмодзи.
"""


# ============================================================
# MANGO API
# ============================================================

def _mango_sign(payload: dict) -> str:
    """Подпись для Mango API."""
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256((API_KEY + j + API_SALT).encode()).hexdigest()


def mango_callback(phone: str, command_id: str = "") -> dict:
    """Инициировать callback через Mango API."""
    if not command_id:
        command_id = f"levitan_{uuid.uuid4().hex[:8]}"

    payload = {
        "command_id": command_id,
        "from": {"extension": MANGO_FROM_EXTENSION},
        "to_number": _norm_phone(phone),
    }

    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    sign = hashlib.sha256((API_KEY + j + API_SALT).encode()).hexdigest()

    try:
        r = requests.post(
            f"{MANGO_API_BASE}commands/callback",
            data={"vpbx_api_key": API_KEY, "json": j, "sign": sign},
            timeout=20,
        )
        result = r.json()
        log.info(f"Callback → {phone}: {result}")
        return result
    except Exception as e:
        log.error(f"Callback failed: {e}")
        return {"error": str(e)}


def mango_download_recording(recording_id: str, output_path: str) -> bool:
    """Скачать запись разговора из Mango API."""
    payload = {"recording_id": recording_id}
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    sign = hashlib.sha256((API_KEY + j + API_SALT).encode()).hexdigest()

    try:
        r = requests.post(
            f"{MANGO_API_BASE}queries/recording/post",
            data={"vpbx_api_key": API_KEY, "json": j, "sign": sign},
            timeout=60,
            stream=True,
        )
        if r.status_code == 200 and len(r.content) > 1000:
            with open(output_path, "wb") as f:
                f.write(r.content)
            log.info(f"Recording downloaded: {output_path} ({len(r.content)} bytes)")
            return True
        else:
            log.warning(f"Recording download failed: status={r.status_code}, size={len(r.content)}")
            return False
    except Exception as e:
        log.error(f"Recording download error: {e}")
        return False


def _norm_phone(num: str) -> str:
    d = re.sub(r"\D", "", num or "")
    if len(d) == 11 and d.startswith("8"):
        d = "7" + d[1:]
    return d


# ============================================================
# BARESIP AUDIO MANAGEMENT
# ============================================================

def set_baresip_audio(wav_path: Path):
    """
    Подменить WAV файл для baresip aufile.
    baresip проиграет этот файл при следующем звонке.
    """
    try:
        # Копируем WAV в путь aufile
        shutil.copy2(str(wav_path), str(BARESIP_AUFILE_PATH))
        log.info(f"Baresip audio set: {wav_path.name} → {BARESIP_AUFILE_PATH}")
        return True
    except Exception as e:
        log.error(f"Failed to set baresip audio: {e}")
        return False


def get_latest_recording(after_timestamp: float = 0) -> Optional[Path]:
    """
    Найти последнюю запись baresip (dec.wav).
    Ищем файлы dump-*-dec.wav новее after_timestamp.
    """
    recordings = []
    for pattern in ["dump-*-dec.wav", "*.wav"]:
        for f in BARESIP_RECORD_DIR.glob(pattern):
            if f.stat().st_mtime > after_timestamp and f.stat().st_size > MIN_RECORDING_SIZE:
                recordings.append(f)

    if not recordings:
        return None

    # Самый свежий
    recordings.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return recordings[0]


def wait_for_recording(after_timestamp: float, timeout: int = RECORDING_WAIT_TIMEOUT) -> Optional[Path]:
    """Ждать появления новой записи."""
    start = time.time()
    while time.time() - start < timeout:
        rec = get_latest_recording(after_timestamp)
        if rec:
            # Подождать пока файл допишется
            time.sleep(1.0)
            return rec
        time.sleep(0.5)
    return None


# ============================================================
# STT (faster-whisper)
# ============================================================

_whisper_model = None


def get_whisper():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
        log.info("Whisper model loaded")
    return _whisper_model


def transcribe(wav_path: str) -> str:
    """Транскрибировать WAV файл."""
    try:
        model = get_whisper()
        segments, info = model.transcribe(
            wav_path,
            language="ru",
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )
        text = " ".join(s.text for s in segments).strip()
        log.info(f"STT [{Path(wav_path).name}]: «{text[:100]}»")
        return text
    except Exception as e:
        log.error(f"STT error: {e}")
        return ""


# ============================================================
# LLM (OpenRouter)
# ============================================================

def llm_response(transcript: list[dict]) -> str:
    """Сгенерировать ответ через OpenRouter."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    # Берём последние 10 реплик для контекста
    messages.extend(transcript[-10:])

    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "HTTP-Referer": "https://levitan.app",
            },
            json={
                "model": "deepseek/deepseek-chat-v3-0324",
                "messages": messages,
                "max_tokens": 150,
                "temperature": 0.7,
            },
            timeout=25,
        )
        resp = r.json()["choices"][0]["message"]["content"].strip()
        log.info(f"LLM: «{resp[:100]}»")
        return resp
    except Exception as e:
        log.error(f"LLM error: {e}")
        return "Извините, не расслышал. Повторите, пожалуйста."


# ============================================================
# TTS (edge-tts → WAV 8kHz mono)
# ============================================================

def synthesize_wav(text: str) -> Optional[Path]:
    """Синтезировать текст в WAV 8000Hz mono."""
    ts = int(time.time() * 1000)
    mp3_path = TTS_OUTPUT_DIR / f"tts_{ts}.mp3"
    wav_path = TTS_OUTPUT_DIR / f"tts_{ts}.wav"

    try:
        # edge-tts → MP3
        result = subprocess.run(
            [sys.executable, "-m", "edge_tts",
             "--voice", "ru-RU-DmitryNeural",
             "--text", text,
             "--write-media", str(mp3_path)],
            capture_output=True,
            timeout=30,
        )
        if result.returncode != 0 or not mp3_path.exists():
            log.error(f"edge-tts failed: {result.stderr.decode()[:200]}")
            return None

        # MP3 → WAV 8kHz mono (для телефонии)
        result = subprocess.run(
            ["ffmpeg", "-i", str(mp3_path),
             "-ar", "8000", "-ac", "1", "-sample_fmt", "s16",
             str(wav_path), "-y"],
            capture_output=True,
            timeout=15,
        )
        mp3_path.unlink(missing_ok=True)

        if result.returncode != 0 or not wav_path.exists():
            log.error(f"ffmpeg failed: {result.stderr.decode()[:200]}")
            return None

        # Добавляем 1 сек тишины в начало (lead silence)
        wav_with_lead = TTS_OUTPUT_DIR / f"tts_{ts}_lead.wav"
        _add_lead_silence(wav_path, wav_with_lead, seconds=1.0)

        if wav_with_lead.exists():
            wav_path.unlink(missing_ok=True)
            return wav_with_lead

        return wav_path

    except Exception as e:
        log.error(f"TTS error: {e}")
        return None


def _add_lead_silence(input_wav: Path, output_wav: Path, seconds: float = 1.0):
    """Добавить тишину в начало WAV."""
    try:
        with wave.open(str(input_wav), "rb") as w:
            params = w.getparams()
            frames = w.readframes(w.getnframes())

        silence_frames = int(params.framerate * seconds) * params.sampwidth * params.nchannels
        silence = b"\x00" * silence_frames

        with wave.open(str(output_wav), "wb") as w:
            w.setparams(params)
            w.writeframes(silence + frames)
    except Exception as e:
        log.error(f"Lead silence error: {e}")
        # Fallback: просто копируем
        shutil.copy2(str(input_wav), str(output_wav))


# ============================================================
# TELEGRAM NOTIFICATIONS
# ============================================================

def notify_telegram(text: str):
    """Отправить уведомление в Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
    except Exception as e:
        log.error(f"Telegram: {e}")


# ============================================================
# DIALOG SESSION (Turn-Based)
# ============================================================

class TurnBasedDialog:
    """
    Сессия turn-based диалога.
    Каждый ход = отдельный callback-звонок.
    """

    def __init__(self, phone: str, campaign: str = "levitan"):
        self.phone = _norm_phone(phone)
        self.campaign = campaign
        self.session_id = f"dialog_{uuid.uuid4().hex[:8]}"
        self.transcript: list[dict] = []
        self.turn = 0
        self.active = True
        self.started_at = datetime.now()
        self.last_call_time: float = 0

    def run(self):
        """Запустить диалог (блокирующий)."""
        log.info(f"{'='*60}")
        log.info(f"DIALOG START: {self.phone} | session={self.session_id}")
        log.info(f"{'='*60}")

        notify_telegram(
            f"🎙 <b>Диалог начат</b>\n"
            f"Телефон: {self.phone}\n"
            f"Сессия: {self.session_id}"
        )

        try:
            # === ТУР 0: Приветствие ===
            self._turn_greeting()

            # === ТУРНИРЫ 1..N ===
            while self.active and self.turn < MAX_TURNS:
                self._turn_response()

        except Exception as e:
            log.error(f"Dialog error: {e}", exc_info=True)
        finally:
            self._finish()

    def _turn_greeting(self):
        """Тур 0: Приветствие."""
        log.info(f"[Turn 0] Greeting → {self.phone}")

        # Ставим приветствие как aufile
        if not GREETING_WAV.exists():
            log.error(f"Greeting WAV not found: {GREETING_WAV}")
            self.active = False
            return

        set_baresip_audio(GREETING_WAV)
        time.sleep(0.5)

        # Callback
        self.last_call_time = time.time()
        result = mango_callback(self.phone, f"levitan_greet_{self.session_id}")

        if result.get("result") != 1000:
            log.warning(f"Callback failed: {result}")
            # Может быть другой формат ответа, продолжаем
            if "error" in result:
                self.active = False
                return

        self.transcript.append({
            "role": "assistant",
            "content": "Здравствуйте! Меня зовут Иван, я представляю компанию «Глобал Филдс Экспорт». "
                       "Мы закупаем зерновые, масличные и бобовые культуры у сельхозпроизводителей по всей России. "
                       "Подскажите, пожалуйста, выращиваете ли вы что-то из этого на продажу?"
        })

        # Ждём запись ответа клиента
        recording = wait_for_recording(self.last_call_time, timeout=RECORDING_WAIT_TIMEOUT)

        if not recording:
            log.info("[Turn 0] No recording received — client didn't answer or hung up")
            self.active = False
            return

        # Транскрибируем
        client_text = transcribe(str(recording))
        if not client_text or len(client_text.strip()) < 3:
            log.info("[Turn 0] No speech detected in recording")
            self.active = False
            return

        self.transcript.append({"role": "user", "content": client_text})
        log.info(f"[Turn 0] Client: «{client_text[:100]}»")

        # Проверяем отказ
        if self._is_rejection(client_text):
            self._respond_and_close(
                "Понял, спасибо за время. Если в будущем появится интерес — мы на связи. До свидания!"
            )
            return

        self.turn = 1

    def _turn_response(self):
        """Тур N: Ответ агента → ожидание ответа клиента."""
        log.info(f"[Turn {self.turn}] Generating response...")

        # LLM генерирует ответ
        response = llm_response(self.transcript)
        if not response:
            self.active = False
            return

        self.transcript.append({"role": "assistant", "content": response})
        log.info(f"[Turn {self.turn}] Agent: «{response[:100]}»")

        # TTS → WAV
        wav_path = synthesize_wav(response)
        if not wav_path:
            log.error(f"[Turn {self.turn}] TTS failed, ending dialog")
            self.active = False
            return

        # Подменяем aufile
        set_baresip_audio(wav_path)

        # Пауза между звонками
        time.sleep(CALLBACK_DELAY)

        # Новый callback
        self.last_call_time = time.time()
        cmd_id = f"levitan_t{self.turn}_{self.session_id}"
        result = mango_callback(self.phone, cmd_id)

        if "error" in result:
            log.warning(f"[Turn {self.turn}] Callback failed, ending")
            self.active = False
            return

        # Ждём запись ответа
        recording = wait_for_recording(self.last_call_time, timeout=RECORDING_WAIT_TIMEOUT)

        if not recording:
            log.info(f"[Turn {self.turn}] No recording — client didn't answer")
            self.active = False
            return

        # Транскрибируем
        client_text = transcribe(str(recording))
        if not client_text or len(client_text.strip()) < 3:
            log.info(f"[Turn {self.turn}] No speech detected")
            # Даём ещё одну попытку
            if self.turn > 2:
                self.active = False
            return

        self.transcript.append({"role": "user", "content": client_text})
        log.info(f"[Turn {self.turn}] Client: «{client_text[:100]}»")

        # Проверяем отказ / прощание
        if self._is_rejection(client_text):
            self._respond_and_close(
                "Понял, спасибо за время. Если в будущем появится интерес — мы на связи. До свидания!"
            )
            return

        # Проверяем завершение (клиент дал всю инфу)
        if self._is_complete(client_text):
            self._respond_and_close(
                "Отлично, я всё зафиксировал. Наш менеджер свяжется с вами для обсуждения условий. "
                "Спасибо за время, до свидания!"
            )
            return

        self.turn += 1

    def _respond_and_close(self, text: str):
        """Финальная реплика и закрытие."""
        self.transcript.append({"role": "assistant", "content": text})

        wav_path = synthesize_wav(text)
        if wav_path:
            set_baresip_audio(wav_path)
            time.sleep(CALLBACK_DELAY)
            mango_callback(self.phone, f"levitan_close_{self.session_id}")
            # Не ждём ответа на прощание
            time.sleep(10)

        self.active = False

    def _is_rejection(self, text: str) -> bool:
        """Проверить отказ клиента."""
        rejection_phrases = [
            "не интересно", "не интересует", "не надо", "отказ",
            "до свидания", "не продаем", "не продаём", "не выращиваем",
            "не звоните", "отстаньте", "нет спасибо", "нет, спасибо",
            "не нужно", "занят", "перезвоните",
        ]
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in rejection_phrases)

    def _is_complete(self, text: str) -> bool:
        """Проверить достаточность собранных данных (6+ турнов)."""
        if self.turn < 4:
            return False
        # Если уже 6 турнов — закрываем
        if self.turn >= 6:
            return True
        return False

    def _finish(self):
        """Сохранить результаты диалога."""
        duration = (datetime.now() - self.started_at).total_seconds()

        dialog_data = {
            "session_id": self.session_id,
            "phone": self.phone,
            "campaign": self.campaign,
            "turns": self.turn,
            "duration_sec": round(duration),
            "started_at": self.started_at.isoformat(),
            "ended_at": datetime.now().isoformat(),
            "transcript": self.transcript,
        }

        # Сохраняем JSON
        path = DIALOGS_DIR / f"{self.session_id}.json"
        with open(path, "w") as f:
            json.dump(dialog_data, f, ensure_ascii=False, indent=2)

        log.info(f"{'='*60}")
        log.info(f"DIALOG END: {self.phone} | turns={self.turn} | {duration:.0f}s")
        log.info(f"Saved: {path}")
        log.info(f"{'='*60}")

        # Telegram отчёт
        transcript_text = "\n".join([
            f"{'🤖' if e['role'] == 'assistant' else '👤'} {e['content'][:80]}"
            for e in self.transcript
        ])

        notify_telegram(
            f"🏁 <b>Диалог завершён</b>\n"
            f"Телефон: {self.phone}\n"
            f"Ходов: {self.turn}\n"
            f"Длительность: {duration:.0f} сек\n\n"
            f"<b>Транскрипт:</b>\n{transcript_text[:1500]}"
        )

        # Восстанавливаем приветствие для следующего звонка
        if GREETING_WAV.exists():
            set_baresip_audio(GREETING_WAV)


# ============================================================
# EVENT WATCHER (слушает events.jsonl от webhook)
# ============================================================

def watch_for_calls():
    """
    Мониторит events.jsonl и запускает диалог при появлении
    нового callback_connected.
    """
    seen = set()
    active_phones = set()  # Не звоним одному номеру одновременно

    log.info("="*60)
    log.info("LEVITAN TURN-BASED ENGINE STARTED")
    log.info(f"  Greeting: {GREETING_WAV}")
    log.info(f"  Aufile path: {BARESIP_AUFILE_PATH}")
    log.info(f"  Record dir: {BARESIP_RECORD_DIR}")
    log.info(f"  Max turns: {MAX_TURNS}")
    log.info("="*60)

    # Устанавливаем приветствие по умолчанию
    if GREETING_WAV.exists():
        set_baresip_audio(GREETING_WAV)

    while True:
        try:
            if EVENTS_PATH.exists():
                with open(EVENTS_PATH) as f:
                    for line in f:
                        line = line.strip()
                        if not line or line in seen:
                            continue
                        seen.add(line)

                        try:
                            event = json.loads(line)
                        except json.JSONDecodeError:
                            continue

                        # Ищем новые подключения
                        if event.get("type") == "callback_connected":
                            phone = event.get("phone", "")
                            call_id = event.get("call_id", "")

                            if not phone or len(phone) < 11:
                                continue

                            if phone in active_phones:
                                log.info(f"Skip {phone} — already in dialog")
                                continue

                            # Проверяем, что это НЕ наш собственный callback
                            # (иначе будет рекурсия)
                            cmd_id = event.get("command_id", "")
                            if "levitan_t" in cmd_id or "levitan_close" in cmd_id:
                                # Это наш ответный звонок — не запускаем новый диалог
                                continue

                            log.info(f"New call detected: {phone}")
                            active_phones.add(phone)

                            def run_dialog(ph):
                                try:
                                    dialog = TurnBasedDialog(ph)
                                    dialog.run()
                                finally:
                                    active_phones.discard(ph)

                            t = threading.Thread(target=run_dialog, args=(phone,), daemon=True)
                            t.start()

            time.sleep(1)
        except Exception as e:
            log.error(f"Watch error: {e}")
            time.sleep(5)


# ============================================================
# MANUAL TRIGGER (для тестирования)
# ============================================================

def manual_call(phone: str):
    """Запустить диалог вручную (для тестирования)."""
    dialog = TurnBasedDialog(phone)
    dialog.run()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Ручной запуск: python3 levitan_turnbased.py 79687896924
        phone = sys.argv[1]
        log.info(f"Manual call to: {phone}")
        manual_call(phone)
    else:
        # Режим наблюдения за событиями
        watch_for_calls()
