from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NewsBase(BaseModel):
    """Базовая схема новости."""
    title: str
    slug: str
    content: str
    category: str  # legislative, events, grants, psychology, courses, shop, partners
    thumbnail: Optional[str] = None
    is_important: bool = False


class NewsCreate(NewsBase):
    """Создание новости."""
    author_id: int
    is_published: bool = False


class NewsUpdate(BaseModel):
    """Обновление новости."""
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    thumbnail: Optional[str] = None
    is_important: Optional[bool] = None
    is_published: Optional[bool] = None


class NewsResponse(NewsBase):
    """Ответ с данными новости."""
    id: int
    author_id: int
    views: int
    is_published: bool
    published_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class NewsCategory(BaseModel):
    """Категория новости."""
    id: str
    name: str
    description: str
    icon: str
