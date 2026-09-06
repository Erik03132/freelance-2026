"""Настройки проекта Levitan."""

from pathlib import Path

from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
CAMPAIGNS_DIR = DATA_DIR / "campaigns"
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
VOICE_CACHE_DIR = DATA_DIR / "voice_cache"
KNOWLEDGE_BASE_PATH = DATA_DIR / "knowledge_base.json"
LEADS_DB_PATH = DATA_DIR / "leads.db"


class MangoSettings(BaseSettings):
    api_key: str = Field(default="", alias="MANGO_API_KEY")
    salt: str = Field(default="", alias="MANGO_SALT")
    webhook_url: str = Field(default="", alias="MANGO_WEBHOOK_URL")
    sip_user: str = Field(default="", alias="MANGO_SIP_USER")
    sip_password: str = Field(default="", alias="MANGO_SIP_PASSWORD")
    sip_host: str = Field(default="", alias="MANGO_SIP_HOST")

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class OpenRouterSettings(BaseSettings):
    api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    model: str = Field(default="deepseek/deepseek-chat-v3-0324", alias="OPENROUTER_MODEL")
    fallback_model: str = Field(
        default="qwen/qwen-2.5-7b-instruct", alias="OPENROUTER_FALLBACK_MODEL"
    )

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class TelegramSettings(BaseSettings):
    bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    chat_id: str = Field(default="", alias="TELEGRAM_CHAT_ID")

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class STTSettings(BaseSettings):
    model_size: str = Field(default="base", alias="STT_MODEL_SIZE")
    language: str = Field(default="ru", alias="STT_LANGUAGE")
    device: str = Field(default="cpu", alias="STT_DEVICE")

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class TTSSettings(BaseSettings):
    voice: str = Field(default="ru-RU-SvetlanaNeural", alias="TTS_VOICE")
    rate: str = Field(default="+0%", alias="TTS_RATE")
    cache_dir: Path = VOICE_CACHE_DIR

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class DialogSettings(BaseSettings):
    max_turns: int = Field(default=20, alias="DIALOG_MAX_TURNS")
    silence_timeout: float = Field(default=5.0, alias="DIALOG_SILENCE_TIMEOUT")
    min_speech: float = Field(default=0.3, alias="DIALOG_MIN_SPEECH")
    vad_threshold: float = Field(default=0.5, alias="DIALOG_VAD_THRESHOLD")

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class CampaignSettings(BaseSettings):
    max_concurrent_calls: int = Field(default=5, alias="CAMPAIGN_MAX_CONCURRENT")
    retry_delays: list[int] = Field(default=[15, 60, 180], alias="CAMPAIGN_RETRY_DELAYS")
    call_hours_start: int = Field(default=9, alias="CAMPAIGN_CALL_HOURS_START")
    call_hours_end: int = Field(default=18, alias="CAMPAIGN_CALL_HOURS_END")
    max_retries: int = Field(default=3, alias="CAMPAIGN_MAX_RETRIES")

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class Settings(BaseSettings):
    mango: MangoSettings = MangoSettings()
    openrouter: OpenRouterSettings = OpenRouterSettings()
    telegram: TelegramSettings = TelegramSettings()
    stt: STTSettings = STTSettings()
    tts: TTSSettings = TTSSettings()
    dialog: DialogSettings = DialogSettings()
    campaign: CampaignSettings = CampaignSettings()

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
