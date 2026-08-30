---
name: humanizer
description: Rewrite AI-sounding text so it reads naturally without changing what it says. Use when editing prose for inflated claims, sales language, vague sources, repetitive structure, stock AI words, passive voice, filler, or chatbot artifacts. Based on Wikipedia "Signs of AI writing." Version 2.11.2 (blader/humanizer, MIT).
---

# Humanizer: remove AI writing patterns

Rewrite AI-sounding text so it reads like the writer, not a chatbot. Do not change what it says or make up details.

**Source:** Wikipedia "Signs of AI writing" (WikiProject AI Cleanup).
**Upstream:** github.com/blader/humanizer (456 строк полного SKILL.md здесь, вызывать через `skill_view(name='humanizer')` когда нужна гуманизация).

## Когда вызывать

- Контент-этап Шекспира: статьи, посты, лендинги
- Финальный проход текста перед публикацией
- Любой длинный текст >500 слов, который пойдёт к людям

## Когда НЕ вызывать

- Код, JSON, YAML, таблицы
- Технические спецификации
- Краткие сообщения в чате
- Рабочие файлы (CLAUDE.md, ACTIVE_TASKS.md) — там стиль не важен

## Главные правила

1. Не менять смысл, не добавлять фактов
2. Убирать типичные AI-маркеры (см. полный SKILL.md):
   - Inflated claims ("stands as a testament", "vital role", "broader movement")
   - Em-dashes в длинных цепочках
   - Stock transition words ("Additionally", "Moreover")
   - Sales language ("nestled", "vibrant", "breathtaking")
   - Vague sources ("Experts believe", "Industry reports")
   - -ing phrases ("highlighting", "underscoring", "emphasizing")
3. Сохранять голос автора
4. False positives: em-dash сам по себе не AI-маркер, идеальная грамматика не AI

## Как использовать в Hermes

Этот скилл не загружается в активный system prompt (29 KB) — вызывается по необходимости:
```
skill_view(name='humanizer')  # → полные правила с примерами
```
Затем применить правила к тексту.

## Быстрый чек-лист (если лень читать весь SKILL.md)

Убрать из текста:
- ❌ "stands/serves as", "is a testament to"
- ❌ "in today's fast-paced world", "evolving landscape"
- ❌ цепочки из 3+ em-dash в одном предложении
- ❌ "It's worth noting that", "It's important to mention"
- ❌ "delve into", "navigate the complexities"
- ❌ "leverage" (кроме финансов), "unlock the potential"
- ❌ "-ing phrase" в конце абзаца ("...highlighting its importance")
- ❌ "Whether you're a X or Y", "From X to Y"

Заменить на:
- ✅ Прямые глаголы (uses, makes, builds)
- ✅ Короткие предложения вперемешку с длинными
- ✅ Конкретные детали вместо общих слов
- ✅ "Это" вместо "Это свидетельствует о том, что"