# AI Components Library

Переиспользуемые компоненты для AI-проектов.

## Компоненты

### sentence_embedder.py
**Назначение:** Семантический поиск через sentence-transformers  
**Использование:** RAG, поиск по базе знаний, рекомендательные системы  
**Скилл:** `smart-rag`

```python
from sentence_embedder import SentenceTransformerEmbedder

embedder = SentenceTransformerEmbedder(model_name="all-MiniLM-L6-v2")
embeddings = embedder.encode(["Текст 1", "Текст 2"])
```

### validation_layer.py
**Назначение:** Детерминированные проверки для LLM-выводов  
**Использование:** Защита от галлюцинаций, валидация данных  
**Скилл:** `validation-layer`

```python
from validation_layer import validated

@validated(checks=[
    {"type": "range", "field": "age", "params": {"min_val": 0, "max_val": 150}}
])
def get_patient_info():
    return llm_call("Верни возраст пациента")
```

### video_clipper.py
**Назначение:** Автонарезка видео в вертикальные ролики  
**Использование:** Контент-маркетинг, TikTok/Reels/Shorts  
**Скилл:** `video-clipper`

```bash
python video_clipper.py video.mp4 --highlights 5
```

### sitemap/
**Назначение:** Быстрый SEO-аудит через sitemap.xml  
**Использование:** Анализ структуры сайта, поиск слабых посадочных  
**Скилл:** `sitemap-audit`

```bash
node sitemap/sitemap-audit.js example.com
```

## Установка

```bash
# Копируем нужный компонент в проект
cp foundation/libraries/ai-components/sentence_embedder.py projects/ai-bureau/
cp foundation/libraries/ai-components/validation_layer.py projects/agent-lab/
cp foundation/libraries/ai-components/video_clipper.py projects/ai-scout/scripts/
cp -r foundation/libraries/ai-components/sitemap projects/ai-bureau/scripts/
```

## Зависимости

### sentence_embedder.py
```bash
pip install sentence-transformers chromadb
```

### validation_layer.py
```bash
# Нет внешних зависимостей (только стандартная библиотека)
```

### video_clipper.py
```bash
pip install openai-whisper
# + ffmpeg (обычно уже установлен)
```

### sitemap/
```bash
npm install xml2js
```

## Тестирование

```bash
# Тест sentence_embedder
cd projects/agent-lab
python test_sentence_embedder.py --compare

# Тест validation_layer
python test_validation.py

# Тест video_clipper
python video_clipper.py test_video.mp4 --transcribe-only

# Тест sitemap
cd projects/ai-bureau
node scripts/sitemap-audit.js habr.com
```

## Структура

```
foundation/libraries/ai-components/
├── sentence_embedder.py      # Семантический поиск
├── validation_layer.py       # Валидация LLM-выводов
├── video_clipper.py          # Автонарезка видео
└── sitemap/                  # SEO-аудит
    ├── sitemap-parser.js
    ├── demand-matcher.js
    └── sitemap-audit.js
```

## Интеграция с проектами

| Компонент | Проект | Бот | Использование |
|-----------|--------|-----|---------------|
| sentence_embedder | ai-bureau | Игорек | RAG с семантическим поиском |
| sitemap/ | ai-bureau | Маркетолог | Быстрый SEO-аудит |
| video_clipper | ai-scout | Шерл | Автонарезка докладов |
| validation_layer | agent-lab | Кулибин | Защита от галлюцинаций |

## Обновления

При обновлении компонента:
1. Обнови код в `foundation/libraries/ai-components/`
2. Скопируй в проекты, которые его используют
3. Обнови версию в этом README
4. Запусти тесты во всех проектах

## Лицензия

Внутреннее использование freelance-2026.
