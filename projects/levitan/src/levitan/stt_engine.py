"""Движок STT на основе faster-whisper с VAD."""

import io
import logging
import tempfile
from pathlib import Path
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)


class STTEngine:
    """Движок распознавания речи на основе faster-whisper."""
    
    def __init__(
        self,
        model_size: str = "base",
        language: str = "ru",
        device: str = "cpu"
    ):
        self.model_size = model_size
        self.language = language
        self.device = device
        self._model = None
    
    def _load_model(self):
        """Ленивая загрузка модели."""
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
                self._model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type="int8" if self.device == "cpu" else "float16"
                )
                logger.info(f"Loaded Whisper model: {self.model_size}")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                raise
    
    def transcribe(
        self,
        audio_data: bytes,
        sample_rate: int = 8000
    ) -> str:
        """
        Распознавание речи из аудиоданных.
        
        Args:
            audio_data: Аудиоданные в формате WAV/PCM
            sample_rate: Частота дискретизации
            
        Returns:
            Распознанный текст
        """
        self._load_model()
        
        try:
            # Конвертируем в numpy array
            audio_array = self._bytes_to_numpy(audio_data, sample_rate)
            
            # Распознавание
            segments, info = self._model.transcribe(
                audio_array,
                language=self.language,
                beam_size=5,
                vad_filter=True,
                vad_parameters=dict(
                    min_silence_duration_ms=500,
                    speech_pad_ms=200
                )
            )
            
            # Объединяем сегменты
            text = " ".join([segment.text for segment in segments])
            logger.debug(f"STT result: {text}")
            return text.strip()
            
        except Exception as e:
            logger.error(f"STT transcription failed: {e}")
            return ""
    
    def transcribe_file(self, file_path: Path) -> str:
        """
        Распознавание речи из аудиофайла.
        
        Args:
            file_path: Путь к аудиофайлу
            
        Returns:
            Распознанный текст
        """
        self._load_model()
        
        try:
            segments, info = self._model.transcribe(
                str(file_path),
                language=self.language,
                beam_size=5,
                vad_filter=True
            )
            
            text = " ".join([segment.text for segment in segments])
            logger.debug(f"STT result from file: {text}")
            return text.strip()
            
        except Exception as e:
            logger.error(f"STT file transcription failed: {e}")
            return ""
    
    def _bytes_to_numpy(self, audio_data: bytes, sample_rate: int) -> np.ndarray:
        """Конвертация байтов в numpy array."""
        try:
            import wave
            
            # Пробуем прочитать как WAV
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name
            
            with wave.open(tmp_path, "rb") as wav:
                frames = wav.readframes(wav.getnframes())
                audio_array = np.frombuffer(frames, dtype=np.int16)
                audio_array = audio_array.astype(np.float32) / 32768.0
            
            Path(tmp_path).unlink()
            return audio_array
            
        except Exception:
            # Если не WAV, пробуем как raw PCM
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            return audio_array.astype(np.float32) / 32768.0
    
    def is_speech(self, audio_data: bytes, threshold: float = 0.5) -> bool:
        """
        Определение наличия речи в аудио.
        
        Args:
            audio_data: Аудиоданные
            threshold: Порог энергии
            
        Returns:
            True если обнаружена речь
        """
        try:
            audio_array = self._bytes_to_numpy(audio_data, 8000)
            energy = np.mean(audio_array ** 2)
            return energy > threshold
        except Exception:
            return False


# Глобальный экземпляр
_stt_engine: Optional[STTEngine] = None


def get_stt_engine() -> STTEngine:
    """Получить глобальный экземпляр STT движка."""
    global _stt_engine
    if _stt_engine is None:
        _stt_engine = STTEngine()
    return _stt_engine
