from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Настройки приложения."""
    
    # App
    APP_NAME: str = "ООО Ветеранов СВО"
    APP_URL: str = "http://localhost:8000"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # Security
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 дней
    
    # Email
    SMTP_HOST: str = "smtp.yandex.ru"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    SMTP_FROM: str = "ООО Ветеранов СВО <info@veterany-svo.ru>"
    
    # API Keys
    GOOGLE_API_KEY: str = ""
    GITHUB_TOKEN: str = ""
    
    # Admin
    ADMIN_EMAIL: str = "admin@veterany-svo.ru"
    ADMIN_PASSWORD: str = "admin"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Получить настройки (кэшируется)."""
    return Settings()


settings = get_settings()
