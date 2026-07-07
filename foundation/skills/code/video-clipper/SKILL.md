---
name: video-clipper
description: Автонарезка видео в вертикальные ролики. Whisper для транскрибации, LLM для поиска хайлайтов, ffmpeg для нарезки. 30 мин → 5 роликов за 10 мин.
---

## Когда использовать
- Нужно нарезать длинное видео на короткие ролики
- Создание контента для TikTok/Reels/Shorts
- Автоматизация видео-маркетинга
- Поиск лучших моментов в докладах/интервью

## Установка

```bash
# В проекте agent-lab (или ai-scout)
cd projects/agent-lab

# Создаём venv
python3.12 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
pip install openai-whisper

# ffmpeg должен быть установлен (обычно есть)
which ffmpeg  # Проверка
```

## Быстрый старт

```bash
# Нарезка видео на 5 клипов
python video_clipper.py video.mp4 --highlights 5

# Только транскрибация (без нарезки)
python video_clipper.py video.mp4 --transcribe-only

# Указать модель Whisper (tiny/base/small/medium/large)
python video_clipper.py video.mp4 --model base --highlights 3
```

## Как работает

### Пайплайн
```
Видео → Whisper (STT) → LLM (хайлайты) → ffmpeg (нарезка) → Клипы
```

### 1. Транскрибация (Whisper)
```python
from video_clipper import transcribe_video

transcript = transcribe_video("video.mp4", model_size="medium")
# Возвращает: {
#   "segments": [{start: 10.5, end: 15.2, text: "Привет всем"}],
#   "text": "Полный текст видео"
# }
```

### 2. Поиск хайлайтов (LLM)
```python
from video_clipper import find_highlights_llm

highlights = find_highlights_llm(transcript, num_highlights=5)
# Возвращает: [{
#   start: 120.5,
#   end: 150.3,
#   text: "Главный тезис доклада...",
#   score: 85,
#   reason: "тезис (важно), эмоциональность"
# }]
```

### 3. Создание клипов (ffmpeg)
```python
from video_clipper import create_vertical_clip

success = create_vertical_clip(
    video_path="video.mp4",
    highlight={"start": 120.5, "end": 150.3},
    output_path="clip1.mp4"
)
```

## Критерии поиска хайлайтов

| Критерий | Баллы | Описание |
|----------|-------|----------|
| Восклицания (!) | +15 | Эмоциональные моменты |
| Вопросы (?) | +10 | Вовлечение аудитории |
| Ключевые слова | +20 | "важно", "главное", "вывод", "секрет" |
| Цитатность | +15 | Короткие яркие фразы (10-80 символов) |
| Оптимальная длина | +10 | 15-60 секунд |

**Итого:** 0-70 баллов на блок (30 сек)

## Модели Whisper

| Модель | Размер | Скорость | Качество | Использование |
|--------|--------|----------|----------|---------------|
| tiny | 39 MB | ⚡⚡⚡⚡ | ⭐⭐ | Быстрый тест |
| base | 74 MB | ⚡⚡⚡ | ⭐⭐⭐ | Баланс |
| small | 244 MB | ⚡⚡ | ⭐⭐⭐⭐ | Хорошее качество |
| medium | 769 MB | ⚡ | ⭐⭐⭐⭐⭐ | Продакшн |
| large | 1.5 GB | 🐌 | ⭐⭐⭐⭐⭐ | Максимум точности |

**Рекомендация:** `medium` для русского языка.

## Формат выходных клипов

```
Видео: 1080x1920 (9:16 вертикальное)
Кодек: H.264 (libx264)
Аудио: AAC 128kbps
Длительность: 15-60 секунд
```

## Пример вывода

```
🚀 Автонарезка: video.mp4

🎤 Загрузка Whisper модели: medium
📝 Транскрибация: video.mp4
✅ Транскрибация завершена: 245 сегментов

🔥 Найдено хайлайтов: 5
   1. [120s-150s] тезис (важно), эмоциональность (score: 85)
   2. [340s-370s] вопрос, цитатность (score: 75)
   3. [580s-610s] тезис (главное) (score: 70)
   4. [820s-850s] эмоциональность (score: 65)
   5. [1100s-1130s] цитатность (score: 60)

🎬 Создание клипов...
✅ Клип создан: clips/video_clip1.mp4
✅ Клип создан: clips/video_clip2.mp4
✅ Клип создан: clips/video_clip3.mp4
✅ Клип создан: clips/video_clip4.mp4
✅ Клип создан: clips/video_clip5.mp4

✅ Готово! Клипы в папке: clips/
```

## Интеграция с ботом

```python
# В боте Шерл
@bot.message_handler(commands=['clip'])
def handle_clip(message):
    video_url = message.text.split()[1]
    
    # Скачиваем видео
    video_path = download_video(video_url)
    
    # Нарезаем
    transcript = transcribe_video(video_path, "medium")
    highlights = find_highlights_llm(transcript, 5)
    
    clips = []
    for i, h in enumerate(highlights, 1):
        clip_path = f"clips/clip{i}.mp4"
        create_vertical_clip(video_path, h, clip_path)
        clips.append(clip_path)
    
    # Отправляем клипы
    for clip in clips:
        bot.send_video(message.chat.id, open(clip, 'rb'))
```

## Troubleshooting

**Whisper не загружается:**
```bash
# Проверь Python версию (нужна 3.12)
python --version

# Переустанови
pip uninstall openai-whisper
pip install openai-whisper
```

**ffmpeg не найден:**
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg
```

**Медленная транскрибация:**
- Используй модель `base` или `small` вместо `medium`
- Включи GPU: `device="cuda"` (если есть NVIDIA)

## Ресурсы
- Пример: `projects/ai-scout/scripts/video_clipper.py`
- [Whisper Docs](https://github.com/openai/whisper)
- [FFmpeg Docs](https://ffmpeg.org/documentation.html)
