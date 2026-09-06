---
name: video-clipper
description: "Автонарезка видео в вертикальные ролики. Whisper для транскрибации, LLM для поиска хайлайтов, ffmpeg для нарезки. 30 мин → 5 роликов за 10 мин."
tools: [bash, read, write, edit]
model: standard
source: "/Users/igorvasin/freelance-2026/foundation/skills/code/video-clipper/SKILL.md"
---

# Video Clipper — Автонарезка видео

## Когда использовать
- Нужно нарезать длинное видео на короткие ролики
- Создание контента для TikTok/Reels/Shorts
- Автоматизация видео-маркетинга
- Поиск лучших моментов в докладах/интервью

## Установка
```bash
cd projects/agent-lab
python3.12 -m venv venv && source venv/bin/activate
pip install openai-whisper
which ffmpeg  # Проверка
```

## Быстрый старт
```bash
python video_clipper.py video.mp4 --highlights 5
python video_clipper.py video.mp4 --transcribe-only
python video_clipper.py video.mp4 --model base --highlights 3
```

## Пайплайн
```
Видео → Whisper (STT) → LLM (хайлайты) → ffmpeg (нарезка) → Клипы
```

### 1. Транскрибация (Whisper)
```python
transcript = transcribe_video("video.mp4", model_size="medium")
# {segments: [{start, end, text}], text: "..."}
```

### 2. Поиск хайлайтов (LLM)
```python
highlights = find_highlights_llm(transcript, num_highlights=5)
# [{start, end, text, score, reason}]
```

### 3. Создание клипов (ffmpeg)
```python
create_vertical_clip(video_path="video.mp4", highlight={...}, output_path="clip1.mp4")
```

## Критерии поиска хайлайтов
| Критерий | Баллы | Описание |
|----------|-------|----------|
| Восклицания (!) | +15 | Эмоциональные моменты |
| Вопросы (?) | +10 | Вовлечение аудитории |
| Ключевые слова | +20 | "важно", "главное", "вывод" |
| Цитатность | +15 | Короткие яркие фразы |
| Оптимальная длина | +10 | 15-60 секунд |

## Модели Whisper
| Модель | Размер | Качество |
|--------|--------|----------|
| tiny | 39 MB | ⭐⭐ |
| base | 74 MB | ⭐⭐⭐ |
| small | 244 MB | ⭐⭐⭐⭐ |
| medium | 769 MB | ⭐⭐⭐⭐⭐ |
| large | 1.5 GB | ⭐⭐⭐⭐⭐ |

**Рекомендация:** `medium` для русского языка.

## Формат выходных клипов
```
Видео: 1080x1920 (9:16), H.264, AAC 128kbps, 15-60 сек
```

## Troubleshooting
```bash
pip install openai-whisper          # Whisper не грузится
brew install ffmpeg                 # ffmpeg не найден (macOS)
```