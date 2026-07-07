"""Клиент Mango Office API для Levitan."""

import hashlib
import json
import logging
import time

import httpx

logger = logging.getLogger(__name__)


class MangoClient:
    """Клиент для работы с Mango Office Virtual PBX API."""

    BASE_URL = "https://api.mangosip.ru/vpbx"

    def __init__(self, api_key: str, salt: str):
        self.api_key = api_key
        self.salt = salt
        self.client = httpx.AsyncClient(timeout=30.0)

    def _generate_signature(self, timestamp: int) -> str:
        """Генерация подписи SHA-256 для API Mango."""
        raw = f"{timestamp}{self.salt}"
        return hashlib.sha256(raw.encode()).hexdigest()

    async def initiate_callback(
        self,
        number: str,
        extension: str = "22",
        sip_uri: str = "user4@vpbx400161137.mangosip.ru",
        command_id: str | None = None
    ) -> dict:
        """
        Инициировать callback-звонок через Mango Office (правильный формат).

        Args:
            number: Номер абонента (формат 7XXXXXXXXXX, без +)
            extension: Внутренний номер
            sip_uri: SIP URI для callback
            command_id: ID команды (генерируется если None)

        Returns:
            dict с результатом API
        """
        import uuid

        if command_id is None:
            command_id = f"levitan_{uuid.uuid4().hex[:8]}"

        payload = {
            "command_id": command_id,
            "from": {
                "extension": extension,
            },
            "to_number": number,
        }

        # Формат Mango: vpbx_api_key + json + sign
        j = json.dumps(payload, separators=(",", ":"))
        sign = hashlib.sha256((self.api_key + j + self.salt).encode()).hexdigest()

        try:
            response = self.client.post(
                f"{self.BASE_URL}/commands/callback",
                data={
                    "vpbx_api_key": self.api_key,
                    "json": j,
                    "sign": sign,
                }
            )
            result = response.json()
            logger.info(f"Callback initiated to {number}: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to initiate callback to {number}: {e}")
            raise

    async def play_audio(self, call_id: str, audio_file_id: str) -> dict:
        """
        Воспроизвести аудиофайл в звонке.

        Args:
            call_id: ID звонка
            audio_file_id: ID аудиофайла в Mango

        Returns:
            dict с результатом API
        """
        timestamp = int(time.time())
        signature = self._generate_signature(timestamp)

        payload = {
            "command": "play/start",
            "parameters": {
                "call_id": call_id,
                "audio_id": audio_file_id,
                "timestamp": timestamp,
                "signature": signature
            }
        }

        try:
            response = await self.client.post(
                self.BASE_URL,
                json=payload
            )
            result = response.json()
            logger.info(f"Playing audio {audio_file_id} in call {call_id}: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to play audio in call {call_id}: {e}")
            raise

    async def stop_audio(self, call_id: str) -> dict:
        """
        Остановить воспроизведение аудио в звонке.

        Args:
            call_id: ID звонка

        Returns:
            dict с результатом API
        """
        timestamp = int(time.time())
        signature = self._generate_signature(timestamp)

        payload = {
            "command": "play/stop",
            "parameters": {
                "call_id": call_id,
                "timestamp": timestamp,
                "signature": signature
            }
        }

        try:
            response = await self.client.post(
                self.BASE_URL,
                json=payload
            )
            result = response.json()
            logger.info(f"Stopped audio in call {call_id}: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to stop audio in call {call_id}: {e}")
            raise

    async def terminate_call(self, call_id: str) -> dict:
        """
        Завершить звонок.

        Args:
            call_id: ID звонка

        Returns:
            dict с результатом API
        """
        timestamp = int(time.time())
        signature = self._generate_signature(timestamp)

        payload = {
            "command": "calls/hangup",
            "parameters": {
                "call_id": call_id,
                "timestamp": timestamp,
                "signature": signature
            }
        }

        try:
            response = await self.client.post(
                self.BASE_URL,
                json=payload
            )
            result = response.json()
            logger.info(f"Terminated call {call_id}: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to terminate call {call_id}: {e}")
            raise

    async def get_balance(self) -> dict:
        """Получить баланс аккаунта."""
        timestamp = int(time.time())
        signature = self._generate_signature(timestamp)

        payload = {
            "command": "get/balance",
            "parameters": {
                "timestamp": timestamp,
                "signature": signature
            }
        }

        try:
            response = await self.client.post(
                self.BASE_URL,
                json=payload
            )
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            raise

    async def upload_audio(self, file_path: str, filename: str) -> dict:
        """
        Загрузить аудиофайл в Mango Office.

        Args:
            file_path: Путь к файлу
            filename: Имя файла

        Returns:
            dict с внутренним ID аудиофайла
        """
        timestamp = int(time.time())
        signature = self._generate_signature(timestamp)

        try:
            with open(file_path, "rb") as f:
                files = {"file": (filename, f, "audio/wav")}
                data = {
                    "timestamp": str(timestamp),
                    "signature": signature
                }
                response = await self.client.post(
                    f"{self.BASE_URL}/files/upload",
                    data=data,
                    files=files
                )
                result = response.json()
                logger.info(f"Uploaded audio {filename}: {result}")
                return result
        except Exception as e:
            logger.error(f"Failed to upload audio {filename}: {e}")
            raise

    async def close(self):
        """Закрыть HTTP-клиент."""
        await self.client.aclose()
