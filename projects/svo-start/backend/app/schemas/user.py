from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Базовая схема пользователя."""
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    is_veteran: bool = False
    veteran_status: Optional[str] = None


class UserCreate(UserBase):
    """Создание пользователя."""
    password: str


class UserLogin(BaseModel):
    """Вход пользователя."""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Ответ с данными пользователя."""
    id: int
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT токен."""
    access_token: str
    token_type: str = "bearer"
