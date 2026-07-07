#!/usr/bin/env python3
"""Levitan Real-Time Dialog Engine — FIFO-based conversation loop."""

import hashlib, json, logging, os, re, subprocess, sys, threading, time, wave
from datetime import datetime
from pathlib import Path
import requests

# === CONFIG ===
API_KEY = os.getenv("MANGO_VPBX_API_KEY", "")
API_SALT = os.getenv("MANGO_VPBX_API_SALT", "")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
AUDIO_ID = int(os.getenv("LEVITAN_AUDIO_ID", "1000555922"))
FIFO_PATH = "/tmp/audio_pipe"
RECORDINGS_DIR = Path("/root")

LOG_DIR = Path("/var/log/levitan")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(), logging.FileHandler(LOG_DIR / "dialog.log")],
)
log = logging.getLogger("levitan-dialog")

SYSTEM_PROMPT = """Ты Иван, менеджер компании «Глобал Филдс Экспорт». Ты звонишь сельхозпроизводителям.
Компания закупает зерновые (пшеница, ячмень, кукуруза), масличные (подсолнечник, рапс, соя), бобовые (горох, нут, чечевица).
Базисы: CPT, FOB, DAP. Контакты: +7(918)639-30-30, info@globalfields.ru.

Твоя задача: выяснить заинтересованность и собрать данные (культура, объем, регион, базис, сроки).
Говори кратко, 1-2 предложения. Задавай один вопрос за раз. Не дави. Если не заинтересован — вежливо прощайся."""

# === Audio Helpers ===

def create_silence_wav(seconds: float, path: str):
    """Create silence WAV file."""
    nframes = int(8000 * seconds)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(8000)
        w.writeframes(b"\x00" * (nframes * 2))

def write_to_fifo(data: bytes):
    """Write raw PCM data to FIFO."""
    try:
        with open(FIFO_PATH, "wb") as f:
            f.write(data)
    except Exception as e:
        log.error(f"FIFO write: {e}")

def wav_to_pcm(wav_path: str) -> bytes:
    """Extract raw PCM from WAV file."""
    with wave.open(wav_path, "rb") as w:
        return w.readframes(w.getnframes())

def play_wav_via_fifo(wav_path: str):
    """Play WAV file through FIFO."""
    try:
        data = wav_to_pcm(wav_path)
        write_to_fifo(data)
        duration = len(data) / (8000 * 2)
        log.info(f"🎵 Played {duration:.1f}s via FIFO: {wav_path}")
        return duration
    except Exception as e:
        log.error(f"Play WAV: {e}")
        return 0

def play_silence_via_fifo():
    """Switch FIFO to silence."""
    import subprocess
    # Kill old silence feeder and start new one
    subprocess.run("pkill -f 'silence_feeder'", shell=True)
    def feed_silence():
        silence = b"\x00" * 16000
        while True:
            try:
                write_to_fifo(silence)
                time.sleep(0.1)
            except:
                break
    t = threading.Thread(target=feed_silence, daemon=True)
    t.start()

# === STT ===

_model = None

def get_stt_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        _model = WhisperModel("base", device="cpu", compute_type="int8")
    return _model

def transcribe(filepath: str) -> str:
    try:
        model = get_stt_model()
        segments, _ = model.transcribe(filepath, language="ru", beam_size=5, vad_filter=True)
        text = " ".join(s.text for s in segments).strip()
        log.info(f"STT: {text[:100]}")
        return text
    except Exception as e:
        log.error(f"STT: {e}")
        return ""

# === LLM ===

def generate_response(transcript: list[dict]) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for entry in transcript[-6:]:
        messages.append(entry)
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "HTTP-Referer": "https://levitan.app"},
            json={"model": "deepseek/deepseek-chat-v3-0324", "messages": messages, "max_tokens": 150, "temperature": 0.7},
            timeout=20)
        resp = r.json()["choices"][0]["message"]["content"]
        log.info(f"LLM: {resp[:100]}")
        return resp
    except Exception as e:
        log.error(f"LLM: {e}")
        return "Извините, не расслышал. Повторите, пожалуйста."

# === TTS ===

def synthesize(text: str) -> str:
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Generate greeting WAV locally  
        local_path = f"/tmp/levitan_tts_{int(time.time())}.mp3"
        
        # Direct call to edge-tts
        subprocess.run([sys.executable, "-m", "edge_tts", "--voice", "ru-RU-SvetlanaNeural",
                       "--text", text, "--write-media", local_path],
                      capture_output=True, timeout=30)
        
        # Convert to WAV 8000Hz
        wav_path = local_path.replace(".mp3", ".wav")
        subprocess.run(["ffmpeg", "-i", local_path, "-ar", "8000", "-ac", "1",
                       "-sample_fmt", "s16", wav_path, "-y"],
                      capture_output=True, timeout=10)
        
        # Verify
        if os.path.exists(wav_path) and os.path.getsize(wav_path) > 100:
            return wav_path
        return ""
    except Exception as e:
        log.error(f"TTS: {e}")
        return ""

# === Dialog Session ===

class DialogSession:
    def __init__(self, call_id: str, phone: str):
        self.call_id = call_id
        self.phone = phone
        self.transcript = []
        self.turn = 0
        self.active = True

    def run(self):
        log.info(f"🎙️ Dialog started: {self.phone}")

        try:
            # Load and play greeting
            greeting_path = "/tmp/levitan_greeting_lead.wav"
            if not os.path.exists(greeting_path):
                log.error(f"Greeting WAV not found: {greeting_path}")
                return

            duration = play_wav_via_fifo(greeting_path)
            self.transcript.append({"role": "assistant", "content": "[Приветствие и вопрос о культурах]"})
            log.info(f"Greeting played ({duration:.1f}s)")

            # Dialog loop
            while self.active and self.turn < 6:
                # Wait for recording
                recording = self._wait_for_recording(timeout=25)
                if not recording:
                    log.info("No recording detected, ending dialog")
                    break

                # Transcribe
                text = transcribe(recording)
                if not text or len(text) < 3:
                    log.info("No speech detected in recording")
                    continue

                self.transcript.append({"role": "user", "content": text})
                log.info(f"👤 {text[:80]}")

                # Check for disinterest
                if any(w in text.lower() for w in ["не интересно", "не надо", "отказ", "до свидания", "не продаем"]):
                    response = "Спасибо за время. Если будут вопросы — мы на связи. До свидания!"
                    self._respond(response)
                    break

                # Generate response
                response = generate_response(self.transcript)
                if not response:
                    response = "Извините, не расслышал. Повторите, пожалуйста."

                self.transcript.append({"role": "assistant", "content": response})
                self._respond(response)
                self.turn += 1

        except Exception as e:
            log.error(f"Dialog error: {e}")
        finally:
            self.active = False
            play_silence_via_fifo()  # Back to silence
            self._save()
            log.info(f"🏁 Dialog ended: {self.phone}, turns={self.turn}")

    def _respond(self, text: str):
        """Synthesize and play response."""
        wav_path = synthesize(text)
        if wav_path and os.path.exists(wav_path):
            play_wav_via_fifo(wav_path)
        else:
            log.error("TTS failed, skipping response")

    def _wait_for_recording(self, timeout: int = 25) -> str:
        """Wait for new baresip dec.wav recording."""
        start = time.time()
        while time.time() - start < timeout:
            recordings = sorted(
                RECORDINGS_DIR.glob("dump-*-dec.wav"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            for rec in recordings:
                age = time.time() - rec.stat().st_mtime
                if age < timeout and rec.stat().st_size > 1000:  # >1KB = real audio
                    # Wait a bit for writing to finish
                    time.sleep(0.5)
                    return str(rec)
            time.sleep(0.5)
        return ""

    def _save(self):
        """Save transcript."""
        path = LOG_DIR / f"dialog_{self.phone}_{int(time.time())}.json"
        with open(path, "w") as f:
            json.dump({
                "call_id": self.call_id,
                "phone": self.phone,
                "turns": self.turn,
                "transcript": self.transcript,
                "saved_at": datetime.now().isoformat(),
            }, f, ensure_ascii=False, indent=2)
        log.info(f"📁 Saved: {path}")


# === Main Loop ===

def watch_events():
    events_path = LOG_DIR / "events.jsonl"
    seen = set()

    log.info("👀 Dialog engine started, watching events...")

    while True:
        try:
            if events_path.exists():
                with open(events_path) as f:
                    for line in f:
                        line = line.strip()
                        if not line or line in seen:
                            continue
                        seen.add(line)
                        try:
                            event = json.loads(line)
                        except:
                            continue

                        if event.get("type") == "callback_connected":
                            call_id = event.get("call_id", "")
                            phone = event.get("phone", "")

                            if call_id and phone and len(phone) >= 11:
                                log.info(f"📞 New call detected: {phone}")
                                # Wait briefly then start dialog
                                time.sleep(2)
                                session = DialogSession(call_id, phone)
                                t = threading.Thread(target=session.run, daemon=True)
                                t.start()
            time.sleep(1)
        except Exception as e:
            log.error(f"Watch: {e}")
            time.sleep(5)


if __name__ == "__main__":
    watch_events()
