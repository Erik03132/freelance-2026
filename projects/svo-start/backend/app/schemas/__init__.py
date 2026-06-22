# Schemas package
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.schemas.news import NewsCreate, NewsUpdate, NewsResponse

__all__ = [
    "UserCreate", "UserLogin", "UserResponse", "Token",
    "NewsCreate", "NewsUpdate", "NewsResponse"
]
