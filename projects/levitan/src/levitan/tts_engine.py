"""Движок TTS на основе edge-tts с кэшированием."""

import hashlib
import logging
from pathlib import Path

import edge_tts

logger = logging.getLogger(__name__)


class TTSEngine:
    """Движок текст-в-речь с кэшированием аудиофайлов."""

    def __init__(
        self,
        voice: str = "ru-RU-SvetlanaNeural",
        rate: str = "+0%",
        cache_dir: Path | None = None
    ):
        self.voice = voice
        self.rate = rate
        self.cache_dir = cache_dir or Path("data/voice_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, text: str) -> str:
        """Генерация хеша текста для кэша."""
        return hashlib.md5(f"{text}_{self.voice}_{self.rate}".encode()).hexdigest()

    def _get_cached_path(self, text: str) -> Path:
        """Путь к кэшированному аудиофайлу."""
        cache_key = self._get_cache_key(text)
        return self.cache_dir / f"{cache_key}.wav"

    async def synthesize(
        self,
        text: str,
        output_path: Path | None = None
    ) -> Path:
        """
        Синтез речи из текста.

        Args:
            text: Текст для синтеза
            output_path: Путь для сохранения (если None — используется кэш)

        Returns:
            Path к аудиофайлу
        """
        # Проверяем кэш
        cached_path = self._get_cached_path(text)
        if cached_path.exists() and output_path is None:
            logger.debug(f"Using cached TTS: {cached_path}")
            return cached_path

        # Определяем путь вывода
        target_path = output_path or cached_path

        try:
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
            await communicate.save(str(target_path))
            logger.info(f"TTS synthesized: {text[:50]}... -> {target_path}")
            return target_path
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            raise

    async def synthesize_to_wav(
        self,
        text: str,
        sample_rate: int = 8000,
        output_path: Path | None = None
    ) -> Path:
        """
        Синтез речи в WAV формате с указанным sample rate.

        Args:
            text: Текст для синтеза
            sample_rate: Частота дискретизации (8000 для телефонии)
            output_path: Путь для сохранения

        Returns:
            Path к WAV файлу
        """
        # Сначала синтезируем в MP3
        mp3_path = await self.synthesize(text)

        # Конвертируем в WAV с нужным sample rate
        wav_path = output_path or self._get_cached_path(text).with_suffix(".wav")

        try:
            import subprocess
            cmd = [
                "ffmpeg", "-i", str(mp3_path),
                "-ar", str(sample_rate),
                "-ac", "1",
                "-f", "wav",
                str(wav_path),
                "-y"
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            logger.info(f"Converted to WAV: {wav_path}")
            return wav_path
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg conversion failed: {e}")
            raise
        except FileNotFoundError:
            # Если ffmpeg не установлен, возвращаем MP3
            logger.warning("FFmpeg not found, returning MP3")
            return mp3_path

    async def synthesize_batch(
        self,
        texts: list[str],
        output_dir: Path | None = None
    ) -> list[Path]:
        """
        Пакетный синтез нескольких текстов.

        Args:
            texts: Список текстов
            output_dir: Директория для сохранения

        Returns:
            Список путей к аудиофайлам
        """
        results = []
        for text in texts:
            try:
                path = await self.synthesize(text)
                results.append(path)
            except Exception as e:
                logger.error(f"Failed to synthesize: {text[:30]}...: {e}")
                results.append(None)
        return results

    def clear_cache(self):
        """Очистить кэш аудиофайлов."""
        for file in self.cache_dir.glob("*.mp3"):
            file.unlink()
        for file in self.cache_dir.glob("*.wav"):
            file.unlink()
        logger.info("TTS cache cleared")


# Глобальный экземпляр
_tts_engine: TTSEngine | None = None


def get_tts_engine() -> TTSEngine:
    """Получить глобальный экземпляр TTS движка."""
    global _tts_engine
    if _tts_engine is None:
        _tts_engine = TTSEngine()
    return _tts_engine
