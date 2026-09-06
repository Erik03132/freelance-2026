"""Интеграционные тесты ES-12 + ES-14 на process_client_audio (без сети/аудио).

Заменяем STT/TTS/LLM/Mango на stub-объекты, проверяем:
- ES-12: на тишине/артефакте клиент НЕ записывается в транскрипт и агент
  отвечает VOICE_NOT_HEARD (а НЕ галлюцинированной фразой);
- ES-14: до LLM-ответа проигрывается ack-фраза, и она НЕ попадает в транскрипт.
"""

import pytest

from levitan.call_session import CallSession


class _StubMango:
    def __init__(self):
        self.uploaded = []
        self.played = []

    async def upload_audio(self, path, name):
        self.uploaded.append(name)
        return {"audio_id": f"id_{len(self.uploaded)}"}

    async def play_audio(self, call_id, audio_id):
        self.played.append(audio_id)


class _StubTTS:
    async def synthesize_to_wav(self, text, sample_rate=8000):
        # Создаём реальный temp-файл: call_session проверяет tts_path.exists()
        # перед upload в Mango (иначе ack/финал не проигрываются — ES-14)
        import tempfile
        from pathlib import Path

        path = Path(tempfile.mkstemp(suffix=".wav")[1])
        path.write_bytes(b"RIFF....")
        return path


class _StubKB:
    def search(self, text):
        return ""


class _StubLLM:
    def __init__(self, reply="Да, выращиваем пшеницу"):
        self.reply = reply

    async def generate_dialog_response(self, **kwargs):
        return self.reply


class _StubSTT:
    """Настраиваемый STT: что вернуть и какой VAD-профиль у клипа."""

    def __init__(self, transcript, speech_fraction=0.5, plateau_ms=400.0):
        self._transcript = transcript
        self._speech_fraction = speech_fraction
        self._plateau_ms = plateau_ms

    def transcribe(self, audio_data, sample_rate=8000):
        return self._transcript

    def analyze_audio(self, audio_data, sample_rate=8000):
        return {
            "speech_fraction": self._speech_fraction,
            "speech_chunks": 1,
            "plateau_ms": self._plateau_ms,
            "speech_frames": 10,
            "total_frames": 20,
        }


def _make_session(stt, llm_reply="Да, выращиваем пшеницу"):
    from levitan.call_session import get_stt_engine  # noqa: F401 (ensure importable)

    sess = CallSession(
        call_id="test",
        phone="+79990000000",
        mango_client=_StubMango(),
        knowledge_base=_StubKB(),
        llm_api_key="",
    )
    sess.stt = stt
    sess.tts = _StubTTS()
    sess.llm = _StubLLM(reply=llm_reply)
    return sess


# ── ES-14: ack проигрывается до финала и не в транскрипте ─────────────────────


@pytest.mark.asyncio
async def test_ack_played_before_final_and_not_in_transcript():
    stt = _StubSTT(transcript="Выращиваете пшеницу?")
    sess = _make_session(stt)
    await sess.start()

    out = await sess.process_client_audio(b"fake-audio")
    # Финал совпадает с ответом LLM
    assert out == "Да, выращиваем пшеницу"
    # Клиент в транскрипте есть
    roles = [e.role for e in sess.transcript]
    assert "client" in roles
    # ack-фраза (Момент/Секундочку/Сейчас) НЕ в транскрипте
    agent_texts = [e.text for e in sess.transcript if e.role == "agent"]
    assert not any(t in ("Момент", "Секундочку", "Сейчас") for t in agent_texts)
    # ack проигран через Mango (один upload помимо финала)
    assert len(sess.mango_client.uploaded) >= 2


# ── ES-12: тишина отсекается (VAD-профиль не пройден) ─────────────────────────


@pytest.mark.asyncio
async def test_silence_rejected_by_vad_profile():
    # Whisper (stub) "услышал" фразу, но VAD-профиль клипа — тишина
    stt = _StubSTT(transcript="Продолжение следует", speech_fraction=0.01, plateau_ms=0.0)
    sess = _make_session(stt)
    await sess.start()

    out = await sess.process_client_audio(b"fake-silence")
    # Агент НЕ выдал галлюцинацию; вместо неё — "не расслышал"
    assert out == "Не расслышал, пожалуйста, повторите."
    client_entries = [e for e in sess.transcript if e.role == "client"]
    assert client_entries == []  # клиента нет в транскрипте


# ── ES-12: артефакт Whisper отсекается блеклистом (при прохождении профиля) ──


@pytest.mark.asyncio
async def test_artifact_rejected_by_blacklist():
    stt = _StubSTT(transcript="Продолжение следует", speech_fraction=0.6, plateau_ms=400.0)
    sess = _make_session(stt)
    await sess.start()

    out = await sess.process_client_audio(b"fake-audio")
    assert out == "Не расслышал, пожалуйста, повторите."
    client_entries = [e for e in sess.transcript if e.role == "client"]
    assert client_entries == []


# ── ES-12 НЕ мешает нормальной речи ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_real_speech_passes_through():
    stt = _StubSTT(transcript="Да, у нас 500 тонн ячменя", speech_fraction=0.6, plateau_ms=400.0)
    sess = _make_session(stt, llm_reply="Отлично, зафиксировал 500 тонн")
    await sess.start()

    out = await sess.process_client_audio(b"fake-audio")
    assert out == "Отлично, зафиксировал 500 тонн"
    client_entries = [e for e in sess.transcript if e.role == "client"]
    assert client_entries and client_entries[0].text == "Да, у нас 500 тонн ячменя"
