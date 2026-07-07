"""Smoke tests for config module."""

import os
from pathlib import Path


def test_base_dir_exists():
    """Config.BASE_DIR should point to the project root."""
    from levitan.config import BASE_DIR
    assert BASE_DIR.exists()
    assert (BASE_DIR / "src").exists()
    assert (BASE_DIR / "requirements.txt").exists()


def test_data_dirs():
    """Data directories should be correctly derived from BASE_DIR."""
    from levitan.config import DATA_DIR, CAMPAIGNS_DIR, TRANSCRIPTS_DIR
    assert str(CAMPAIGNS_DIR).startswith(str(DATA_DIR))
    assert str(TRANSCRIPTS_DIR).startswith(str(DATA_DIR))


def test_knowledge_base_path():
    from levitan.config import KNOWLEDGE_BASE_PATH
    assert KNOWLEDGE_BASE_PATH.name == "knowledge_base.json"


def test_stt_settings_defaults():
    """STT settings should have sensible defaults."""
    from levitan.config import STTSettings
    settings = STTSettings()
    assert settings.model_size == "base"
    assert settings.language == "ru"
    assert settings.device == "cpu"


def test_dialog_settings_defaults():
    """Dialog settings should have sensible defaults."""
    from levitan.config import DialogSettings
    settings = DialogSettings()
    assert settings.max_turns == 20
    assert settings.silence_timeout == 5.0
    assert settings.min_speech >= 0.3


def test_campaign_settings_defaults():
    """Campaign settings should have sensible defaults."""
    from levitan.config import CampaignSettings
    settings = CampaignSettings()
    assert settings.max_concurrent_calls == 5
    assert settings.call_hours_start == 9
    assert settings.call_hours_end == 18
    assert settings.max_retries == 3


def test_settings_nested_structure():
    """Main Settings should contain all sub-settings."""
    from levitan.config import Settings
    s = Settings()
    assert hasattr(s, "mango")
    assert hasattr(s, "openrouter")
    assert hasattr(s, "telegram")
    assert hasattr(s, "stt")
    assert hasattr(s, "tts")
    assert hasattr(s, "dialog")
    assert hasattr(s, "campaign")
