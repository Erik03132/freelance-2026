from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import bcrypt

from app.database import Base


class User(Base):
    """Пользователь сайта."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")  # user, admin, moderator
    
    # Профиль
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)
    
    # Ветеранский статус
    is_veteran = Column(Boolean, default=False)
    veteran_status = Column(String)  # participant, veteran, family
    
    # Даты
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Связи
    news = relationship("News", back_populates="author")
    
    def set_password(self, password: str):
        """Хеширование пароля."""
        self.password_hash = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt()
        ).decode()
    
    def check_password(self, password: str) -> bool:
        """Проверка пароля."""
        return bcrypt.checkpw(
            password.encode(), self.password_hash.encode()
        )
    
    def is_admin(self) -> bool:
        """Проверка роли администратора."""
        return self.role == "admin"


class News(Base):
    """Новость сайта."""
    
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    
    # Категория: legislative, events, grants, psychology, courses, shop, partners
    category = Column(String(50), index=True)
    
    # Автор
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="news")
    
    # Изображение
    thumbnail = Column(String(500))
    
    # Статистика
    views = Column(Integer, default=0)
    is_important = Column(Boolean, default=False)  # Важная (красная метка)
    
    # Публикация
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
