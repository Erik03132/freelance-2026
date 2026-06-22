# API для новостей (News Router)

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.user import News
from app.schemas.news import NewsCreate, NewsUpdate, NewsResponse

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("", response_model=List[NewsResponse])
async def get_news_list(
    category: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Получить ленту новостей с фильтрацией по категории.
    
    - **category**: legislative, events, grants, psychology, courses, shop, partners
    - **limit**: количество новостей (1-100)
    - **offset**: смещение для пагинации
    """
    query = db.query(News).filter(News.is_published == True)
    
    if category:
        query = query.filter(News.category == category)
    
    news_list = query.order_by(
        desc(News.is_important),  # Сначала важные
        desc(News.published_at)   # Потом свежие
    ).offset(offset).limit(limit).all()
    
    # Увеличиваем счётчик просмотров
    for news in news_list:
        news.views += 1
    
    db.commit()
    return news_list


@router.get("/{slug}", response_model=NewsResponse)
async def get_news_item(slug: str, db: Session = Depends(get_db)):
    """
    Получить детальную информацию о новости по slug.
    """
    news = db.query(News).filter(
        News.slug == slug,
        News.is_published == True
    ).first()
    
    if not news:
        raise HTTPException(404, "Новость не найдена")
    
    news.views += 1
    db.commit()
    db.refresh(news)
    
    return news


@router.post("", response_model=NewsResponse)
async def create_news(
    news_data: NewsCreate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_admin_user)
):
    """
    Создать новую новость (только для администраторов).
    """
    # Проверка уникальности slug
    existing = db.query(News).filter(News.slug == news_data.slug).first()
    if existing:
        raise HTTPException(400, "Такой slug уже существует")
    
    news = News(
        title=news_data.title,
        slug=news_data.slug,
        content=news_data.content,
        category=news_data.category,
        author_id=news_data.author_id,
        thumbnail=news_data.thumbnail,
        is_important=news_data.is_important,
        is_published=news_data.is_published,
        published_at=datetime.utcnow() if news_data.is_published else None
    )
    
    db.add(news)
    db.commit()
    db.refresh(news)
    
    return news


@router.put("/{id}", response_model=NewsResponse)
async def update_news(
    id: int,
    news_data: NewsUpdate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_admin_user)
):
    """
    Обновить новость (только для администраторов).
    """
    news = db.query(News).filter(News.id == id).first()
    if not news:
        raise HTTPException(404, "Новость не найдена")
    
    # Обновление полей
    update_data = news_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(news, field, value)
    
    # Если опубликовано и не было даты публикации
    if news.is_published and not news.published_at:
        news.published_at = datetime.utcnow()
    
    db.commit()
    db.refresh(news)
    
    return news


@router.delete("/{id}")
async def delete_news(
    id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_admin_user)
):
    """
    Удалить новость (только для администраторов).
    """
    news = db.query(News).filter(News.id == id).first()
    if not news:
        raise HTTPException(404, "Новость не найдена")
    
    db.delete(news)
    db.commit()
    
    return {"message": "Новость удалена"}


@router.get("/categories/list")
async def get_categories():
    """
    Получить список категорий новостей.
    """
    return {
        "categories": [
            {"id": "legislative", "name": "🏛️ Законы", "description": "Законодательные новости"},
            {"id": "events", "name": "📅 Мероприятия", "description": "Анонсы и отчёты"},
            {"id": "grants", "name": "💰 Гранты", "description": "Новости грантовых программ"},
            {"id": "psychology", "name": "🧠 Психология", "description": "Советы психолога"},
            {"id": "success", "name": "⭐ Истории успеха", "description": "Кейсы ветеранов"},
            {"id": "courses", "name": "🎓 Курсы", "description": "Новости обучения"},
            {"id": "shop", "name": "🛍️ Магазин", "description": "Новинки мерча"},
            {"id": "partners", "name": "🤝 Партнёры", "description": "Новости партнёров"},
        ]
    }


# Подписка на новости
@router.post("/subscribe")
async def subscribe_to_news(
    email: str,
    categories: Optional[str] = None,  # JSON строка или все категории
    db: Session = Depends(get_db)
):
    """
    Подписаться на новости по email.
    """
    from app.models.user import NewsSubscription
    
    # Проверка: не подписан ли уже
    existing = db.query(NewsSubscription).filter(
        NewsSubscription.email == email,
        NewsSubscription.is_active == True
    ).first()
    
    if existing:
        raise HTTPException(400, "Вы уже подписаны")
    
    subscription = NewsSubscription(
        email=email,
        categories=categories or "all",
        is_active=True
    )
    
    db.add(subscription)
    db.commit()
    
    return {"message": "Вы успешно подписаны на новости"}


@router.delete("/unsubscribe")
async def unsubscribe_from_news(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Отписаться от новостей.
    """
    from app.models.user import NewsSubscription
    
    subscription = db.query(NewsSubscription).filter(
        NewsSubscription.email == email,
        NewsSubscription.is_active == True
    ).first()
    
    if not subscription:
        raise HTTPException(404, "Подписка не найдена")
    
    subscription.is_active = False
    db.commit()
    
    return {"message": "Вы отписаны от новостей"}
```

---

## Схемы Pydantic (schemas/news.py)

```python
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class NewsBase(BaseModel):
    title: str
    slug: str
    content: str
    category: str  # legislative, events, grants, etc.
    thumbnail: Optional[str] = None
    is_important: bool = False


class NewsCreate(NewsBase):
    author_id: int
    is_published: bool = False


class NewsUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    thumbnail: Optional[str] = None
    is_important: Optional[bool] = None
    is_published: Optional[bool] = None


class NewsResponse(NewsBase):
    id: int
    author_id: int
    views: int
    is_published: bool
    published_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class NewsSubscription(BaseModel):
    email: EmailStr
    categories: Optional[str] = "all"
```

---

## Пример использования на главной странице (HTML)

```html
<!-- Блок новостей на главной -->
<section class="news-section py-12 bg-white">
    <div class="container mx-auto px-4">
        <div class="flex justify-between items-center mb-8">
            <h2 class="text-3xl font-bold text-gray-900">📰 Новости</h2>
            <a href="/news" class="text-blue-600 hover:underline">Все новости →</a>
        </div>
        
        <!-- Фильтры категорий -->
        <div class="flex flex-wrap gap-2 mb-6" x-data="{ category: 'all' }">
            <button @click="category = 'all'" 
                    :class="category === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-100'"
                    class="px-4 py-2 rounded-lg text-sm font-medium transition">
                Все
            </button>
            <button @click="category = 'legislative'"
                    :class="category === 'legislative' ? 'bg-blue-600 text-white' : 'bg-gray-100'"
                    class="px-4 py-2 rounded-lg text-sm font-medium transition">
                🏛️ Законы
            </button>
            <button @click="category = 'events'"
                    :class="category === 'events' ? 'bg-blue-600 text-white' : 'bg-gray-100'"
                    class="px-4 py-2 rounded-lg text-sm font-medium transition">
                📅 Мероприятия
            </button>
            <button @click="category = 'grants'"
                    :class="category === 'grants' ? 'bg-blue-600 text-white' : 'bg-gray-100'"
                    class="px-4 py-2 rounded-lg text-sm font-medium transition">
                💰 Гранты
            </button>
        </div>
        
        <!-- Лента новостей -->
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6" 
             x-data="{ news: [] }"
             x-init="async () => {
                 const response = await fetch('/api/news?limit=6');
                 news = await response.json();
             }">
            
            <!-- Карточка новости -->
            <template x-for="item in news" :key="item.id">
                <article class="border rounded-lg overflow-hidden hover:shadow-lg transition">
                    <!-- Метка важной новости -->
                    <div x-show="item.is_important" 
                         class="bg-red-600 text-white text-xs font-bold px-3 py-1">
                        ВАЖНО
                    </div>
                    
                    <!-- Изображение -->
                    <img x-if="item.thumbnail" 
                         :src="item.thumbnail" 
                         :alt="item.title"
                         class="w-full h-48 object-cover">
                    
                    <!-- Категория -->
                    <div class="px-4 pt-4">
                        <span class="text-xs font-medium text-blue-600" 
                              x-text="item.category"></span>
                    </div>
                    
                    <!-- Заголовок -->
                    <h3 class="px-4 py-2 text-lg font-semibold text-gray-900"
                        x-text="item.title"></h3>
                    
                    <!-- Краткое описание -->
                    <p class="px-4 pb-4 text-gray-600 text-sm line-clamp-3"
                       x-text="item.content.substring(0, 150) + '...'"></p>
                    
                    <!-- Мета -->
                    <div class="px-4 pb-4 flex justify-between items-center text-xs text-gray-500">
                        <span x-text="new Date(item.published_at).toLocaleDateString('ru-RU')"></span>
                        <span>👁️ <span x-text="item.views"></span></span>
                    </div>
                    
                    <!-- Ссылка -->
                    <a :href="'/news/' + item.slug"
                       class="block px-4 pb-4 text-blue-600 hover:underline text-sm font-medium">
                        Читать далее →
                    </a>
                </article>
            </template>
        </div>
        
        <!-- Подписка на новости -->
        <div class="mt-12 bg-blue-50 rounded-lg p-8">
            <div class="text-center mb-6">
                <h3 class="text-xl font-bold text-gray-900 mb-2">
                    📧 Получайте важные новости
                </h3>
                <p class="text-gray-600">
                    Подпишитесь на дайджест — только законы, гранты и события
                </p>
            </div>
            
            <form @submit.prevent="async (e) => {
                const formData = new FormData(e.target);
                const response = await fetch('/api/news/subscribe', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        email: formData.get('email'),
                        categories: 'legislative,events,grants'
                    })
                });
                if (response.ok) alert('Вы подписаны!');
            }" class="flex flex-col md:flex-row gap-4 max-w-md mx-auto">
                <input type="email" 
                       name="email" 
                       placeholder="Ваш email" 
                       required
                       class="flex-1 px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-600">
                <button type="submit"
                        class="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition">
                    Подписаться
                </button>
            </form>
        </div>
    </div>
</section>
```

---

## Страница новости (templates/news/item.html)

```html
{% extends "base.html" %}

{% block title %}{{ news.title }}{% endblock %}

{% block content %}
<article class="max-w-4xl mx-auto">
    <!-- Хлебные крошки -->
    <nav class="mb-6 text-sm">
        <a href="/" class="text-blue-600 hover:underline">Главная</a>
        <span class="mx-2">/</span>
        <a href="/news" class="text-blue-600 hover:underline">Новости</a>
        <span class="mx-2">/</span>
        <span class="text-gray-600">{{ news.category }}</span>
    </nav>
    
    <!-- Заголовок -->
    <header class="mb-8">
        {% if news.is_important %}
        <span class="bg-red-600 text-white text-xs font-bold px-3 py-1 rounded">
            ВАЖНО
        </span>
        {% endif %}
        
        <h1 class="text-4xl font-bold text-gray-900 mt-4 mb-4">{{ news.title }}</h1>
        
        <div class="flex items-center text-sm text-gray-600">
            <span>📅 {{ news.published_at.strftime('%d.%m.%Y') }}</span>
            <span class="mx-4">•</span>
            <span>👁️ {{ news.views }} просмотров</span>
            <span class="mx-4">•</span>
            <span class="text-blue-600">{{ news.category }}</span>
        </div>
    </header>
    
    <!-- Изображение -->
    {% if news.thumbnail %}
    <img src="{{ news.thumbnail }}" 
         alt="{{ news.title }}" 
         class="w-full h-96 object-cover rounded-lg mb-8">
    {% endif %}
    
    <!-- Контент -->
    <div class="prose prose-lg max-w-none mb-8">
        {{ news.content | safe }}
    </div>
    
    <!-- Поделиться -->
    <div class="border-t pt-8 mb-8">
        <h3 class="text-lg font-semibold mb-4">Поделиться:</h3>
        <div class="flex gap-4">
            <a href="https://t.me/share/url?url={{ request.url | urlencode }}" 
               target="_blank"
               class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                Telegram
            </a>
            <a href="https://vk.com/share.php?url={{ request.url | urlencode }}" 
               target="_blank"
               class="px-4 py-2 bg-blue-700 text-white rounded hover:bg-blue-800">
                VK
            </a>
            <a href="whatsapp://send?text={{ (news.title + ' ' + request.url) | urlencode }}" 
               target="_blank"
               class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">
                WhatsApp
            </a>
        </div>
    </div>
    
    <!-- Читайте также -->
    <aside class="border-t pt-8">
        <h3 class="text-xl font-bold mb-4">Читайте также:</h3>
        <div class="grid md:grid-cols-2 gap-4">
            {% for related in related_news %}
            <a href="/news/{{ related.slug }}" 
               class="block p-4 border rounded hover:shadow transition">
                <h4 class="font-semibold text-gray-900">{{ related.title }}</h4>
                <p class="text-sm text-gray-600 mt-2">
                    {{ related.published_at.strftime('%d.%m.%Y') }}
                </p>
            </a>
            {% endfor %}
        </div>
    </aside>
</article>
{% endblock %}
```

---

## Админка: создание/редактирование новости

```html
<!-- templates/admin/news_form.html -->
{% extends "admin/base.html" %}

{% block content %}
<div class="max-w-4xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">
        {% if news %}Редактировать новость{% else %}Новая новость{% endif %}
    </h1>
    
    <form method="POST" enctype="multipart/form-data" class="space-y-6">
        <!-- Заголовок -->
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
                Заголовок *
            </label>
            <input type="text" 
                   name="title" 
                   required
                   value="{{ news.title if news else '' }}"
                   class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-600">
        </div>
        
        <!-- Slug -->
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
                Slug (URL) *
            </label>
            <input type="text" 
                   name="slug" 
                   required
                   pattern="[a-z0-9-]+"
                   value="{{ news.slug if news else '' }}"
                   class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-600">
            <p class="text-xs text-gray-500 mt-1">Только латиница, цифры и дефисы</p>
        </div>
        
        <!-- Категория -->
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
                Категория *
            </label>
            <select name="category" 
                    required
                    class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-600">
                <option value="legislative" {% if news and news.category == 'legislative' %}selected{% endif %}>🏛️ Законы</option>
                <option value="events" {% if news and news.category == 'events' %}selected{% endif %}>📅 Мероприятия</option>
                <option value="grants" {% if news and news.category == 'grants' %}selected{% endif %}>💰 Гранты</option>
                <option value="psychology" {% if news and news.category == 'psychology' %}selected{% endif %}>🧠 Психология</option>
                <option value="success" {% if news and news.category == 'success' %}selected{% endif %}>⭐ Истории успеха</option>
                <option value="courses" {% if news and news.category == 'courses' %}selected{% endif %}>🎓 Курсы</option>
                <option value="shop" {% if news and news.category == 'shop' %}selected{% endif %}>🛍️ Магазин</option>
                <option value="partners" {% if news and news.category == 'partners' %}selected{% endif %}>🤝 Партнёры</option>
            </select>
        </div>
        
        <!-- Контент -->
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
                Контент *
            </label>
            <textarea name="content" 
                      rows="12"
                      required
                      class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-600">{{ news.content if news else '' }}</textarea>
        </div>
        
        <!-- Изображение -->
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
                Изображение (URL)
            </label>
            <input type="url" 
                   name="thumbnail" 
                   value="{{ news.thumbnail if news else '' }}"
                   class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-600">
        </div>
        
        <!-- Важная новость -->
        <div class="flex items-center">
            <input type="checkbox" 
                   name="is_important" 
                   id="is_important"
                   {% if news and news.is_important %}checked{% endif %}
                   class="w-4 h-4 text-blue-600 rounded">
            <label for="is_important" class="ml-2 text-sm text-gray-700">
                Важная новость (красная метка)
            </label>
        </div>
        
        <!-- Опубликовать -->
        <div class="flex items-center">
            <input type="checkbox" 
                   name="is_published" 
                   id="is_published"
                   {% if news and news.is_published %}checked{% endif %}
                   class="w-4 h-4 text-blue-600 rounded">
            <label for="is_published" class="ml-2 text-sm text-gray-700">
                Опубликовать сразу
            </label>
        </div>
        
        <!-- Кнопки -->
        <div class="flex gap-4 pt-4">
            <button type="submit"
                    class="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700">
                {% if news %}Сохранить{% else %}Создать{% endif %}
            </button>
            <a href="/admin/news" 
               class="px-6 py-3 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300">
                Отмена
            </a>
        </div>
    </form>
</div>
{% endblock %}
```
