# Levitan Project

**Цель**: Автоматизация обзвона сельхозпроизводителей для закупки зерновых, масличных и бобовых культур.

**Компания**: ООО «Глобал Филдс Экспорт» — экспортно-закупочная компания, работающая по всей России.

**Каналы связи**:
- Телефон: +7(918)639-30-30
- Email: info@globalfields.ru
- Сайт: https://globalfields.ru
- Telegram: https://t.me/GlobalFields
- MAX: https://web.max.ru/-76075932131944

## Структура

```
levitan/
├── agent/              # Основной код агентов
├── config/             # Конфигурационные файлы
├── data/               # Данные и датасеты
├── docs/               # Документация
├── logs/               # Логи
├── project-skills/     # Проектные скиллы
├── scripts/            # Вспомогательные скрипты
├── tests/              # Тесты
├── tools/              # Инструменты
├── .venv/              # Виртуальное окружение
├── requirements.txt    # Зависимости Python
├── AGENTS.md           # Описание агентов
├── PROJECT.md          # Описание проекта
└── STATUS.md           # Текущий статус
```

## Быстрый старт

```bash
cd /Users/igorvasin/freelance-2026/projects/levitan
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Агенты

- `agent/main.py` — точка входа
- `agent/skills/` — навыки агента

## Конфигурация

- `config/settings.yaml` — настройки
- `config/agents.yaml` — конфигурация агентов
- `.env` — секреты (не в git)

## Документация

- `docs/ARCHITECTURE.md` — архитектура
- `docs/API.md` — API документация
- `PROJECT.md` — описание проекта
- `AGENTS.md` — описание агентов
- `STATUS.md` — текущий статус

## Статус

🟢 **Активен** — проект в разработке

См. `STATUS.md` для деталей.