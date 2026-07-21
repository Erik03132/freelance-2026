from pathlib import Path
from pydantic import BaseModel

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
PROMPTS = ROOT / "prompts"
CONFIG = ROOT / "config"


class Settings(BaseModel):
    # LLM
    openrouter_api_key: str = ""
    openrouter_model: str = "deepseek/deepseek-chat"
    openrouter_base: str = "https://openrouter.ai/api/v1"

    # Matching
    skill_match_threshold: float = 0.7
    clarity_threshold: float = 0.6
    max_tasks_per_day: int = 5
    min_budget_rub: int = 1000

    # Proposal
    base_hourly_rate: int = 1500
    show_30_percent: bool = True
    watermark_enabled: bool = True

    # RAG
    chroma_db_path: str = "data/chroma"

    # Platforms
    platforms_enabled: list[str] = ["hh", "kwork", "freelance", "flru"]
