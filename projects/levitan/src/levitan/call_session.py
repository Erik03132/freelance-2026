"""Управление состоянием звонка."""

import logging
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field

from .knowledge_base import KnowledgeBase
from .llm_client import get_llm_client
from .mango_client import MangoClient
from .prompts import GREETING, SYSTEM_PROMPT, VOICE_NOT_HEARD
from .stt_engine import get_stt_engine
from .tts_engine import get_tts_engine

logger = logging.getLogger(__name__)


class TranscriptEntry(BaseModel):
    """Запись в транскрипте."""
    role: str  # "agent" или "client"
    text: str
    timestamp: datetime = Field(default_factory=datetime.now)


class CallSession:
    """Сессия звонка - управление диалогом."""

    def __init__(
        self,
        call_id: str,
        phone: str,
        mango_client: MangoClient,
        knowledge_base: KnowledgeBase,
        llm_api_key: str = ""
    ):
        self.call_id = call_id
        self.phone = phone
        self.mango_client = mango_client
        self.knowledge_base = knowledge_base

        # Компоненты
        self.stt = get_stt_engine()
        self.tts = get_tts_engine()
        self.llm = get_llm_client(llm_api_key)

        # Состояние
        self.transcript: list[TranscriptEntry] = []
        self.context: dict = {}
        self.is_active = False
        self.turn_count = 0
        self.last_agent_text = ""

        # Результат
        self.lead_info: dict = {}
        self.status: str = "initiated"

    async def start(self):
        """Начать сессию звонка."""
        self.is_active = True
        self.status = "active"

        # Отправляем приветствие
        await self._send_agent_message(GREETING)

        logger.info(f"Call session started: {self.call_id}")

    async def process_client_audio(self, audio_data: bytes) -> str:
        """
        Обработка аудио от клиента.

        Args:
            audio_data: Аудиоданные от клиента

        Returns:
            Ответ агента
        """
        if not self.is_active:
            return ""

        # Распознавание речи
        client_text = self.stt.transcribe(audio_data)

        if not client_text or len(client_text.strip()) < 2:
            # Не расслышали
            await self._send_agent_message(VOICE_NOT_HEARD)
            return VOICE_NOT_HEARD

        # Записываем в транскрипт
        self.transcript.append(TranscriptEntry(
            role="client",
            text=client_text
        ))

        # Генерируем ответ
        agent_response = await self._generate_response(client_text)

        # Отправляем ответ
        await self._send_agent_message(agent_response)

        self.turn_count += 1

        return agent_response

    async def _generate_response(self, client_text: str) -> str:
        """Генерация ответа агента."""
        # Ищем в базе знаний
        kb_context = self.knowledge_base.search(client_text)

        # Формируем контекст
        recent_history = [
            {"role": entry.role, "content": entry.text}
            for entry in self.transcript[-5:]
        ]

        # Генерируем ответ
        response = await self.llm.generate_dialog_response(
            system_prompt=SYSTEM_PROMPT,
            user_message=client_text,
            context=kb_context,
            recent_history=recent_history
        )

        if not response:
            response = "Извините, не совсем понял. Можете повторить?"

        return response

    async def _send_agent_message(self, text: str):
        """Отправить сообщение агента через TTS и Mango."""
        # Записываем в транскрипт
        self.transcript.append(TranscriptEntry(
            role="agent",
            text=text
        ))

        self.last_agent_text = text

        # Синтезируем речь
        tts_path = await self.tts.synthesize_to_wav(text, sample_rate=8000)

        # Воспроизводим через Mango
        if tts_path and tts_path.exists():
            # Загружаем аудио в Mango
            upload_result = await self.mango_client.upload_audio(
                str(tts_path),
                f"tts_{self.call_id}_{len(self.transcript)}.wav"
            )

            if "audio_id" in upload_result:
                await self.mango_client.play_audio(
                    self.call_id,
                    upload_result["audio_id"]
                )

    async def end(self, reason: str = "completed"):
        """Завершить сессию."""
        self.is_active = False
        self.status = reason

        # Сохраняем транскрипт
        await self._save_transcript()

        # Извлекаем информацию о лиде
        await self._extract_lead_info()

        logger.info(f"Call session ended: {self.call_id}, reason: {reason}")

    async def _save_transcript(self):
        """Сохранение транскрипта."""
        transcript_dir = Path("data/transcripts")
        transcript_dir.mkdir(parents=True, exist_ok=True)

        transcript_file = transcript_dir / f"{self.call_id}.json"

        data = {
            "call_id": self.call_id,
            "phone": self.phone,
            "start_time": self.transcript[0].timestamp.isoformat() if self.transcript else None,
            "end_time": self.transcript[-1].timestamp.isoformat() if self.transcript else None,
            "turn_count": self.turn_count,
            "status": self.status,
            "transcript": [
                {
                    "role": entry.role,
                    "text": entry.text,
                    "timestamp": entry.timestamp.isoformat()
                }
                for entry in self.transcript
            ]
        }

        import json
        with open(transcript_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Transcript saved: {transcript_file}")

    async def _extract_lead_info(self):
        """Извлечение информации о лиде."""
        if not self.transcript:
            return

        # Формируем транскрипт
        transcript_text = "\n".join([
            f"{'Агент' if entry.role == 'agent' else 'Клиент'}: {entry.text}"
            for entry in self.transcript
        ])

        # Извлекаем информацию
        extraction_prompt = f"""Проанализируй транскрипт разговора и извлеки информацию:

Транскрипт:
{transcript_text}

Верни JSON со следующими полями:
- has_interest: true/false (заинтересован ли клиент)
- crops: список культур
- volume: объем (текст)
- region: регион
- basis: базис поставки (CPT/FOB/DAP)
- harvest_time: сроки поставки
- contact_name: имя контакта
- best_time_to_call: удобное время для звонка
- preferred_channel: предпочтительный канал связи
- objections: список возражений
- notes: заметки
- status: лид/перезвон/не_заинтересован/отказ
"""

        self.lead_info = await self.llm.extract_lead_info(
            transcript_text,
            extraction_prompt
        )

        logger.info(f"Lead info extracted: {self.lead_info}")

    def get_transcript_text(self) -> str:
        """Получить текст транскрипта."""
        return "\n".join([
            f"{'Агент' if entry.role == 'agent' else 'Клиент'}: {entry.text}"
            for entry in self.transcript
        ])
