---
type: wiki
tags: [notebooklm, gemini-notebook, mcp, cli, nlm, knowledge-base]
status: done
updated: 2026-11-17
sources: [06-Library/books/20260808_notebooklm-mcp-_-pypi/digest.md, 06-Library/books/20260808_github---jacob-bd_gemini-notebook-mcp-cli_-programmatic-access-to-gemini-notebook---via-command-line-interface-cli_-mo/digest.md]
---

# Программный доступ к NotebookLM / Gemini Notebook

Источники: два дайджеста от 2026-08-09 — `books/20260808_notebooklm-mcp-_-pypi/digest.md` и `books/20260808_github---jacob-bd_gemini-notebook-mcp-cli_.../digest.md`.

## Что описано

MCP-сервер и CLI, которые дают агентам доступ к блокнотам NotebookLM (Gemini Notebook): создание блокнотов, добавление источников, генерация студийного контента, batch-операции, пайплайны, тегирование.

## Вариант из PyPI-дайджеста

- FastMCP v2, декораторная регистрация инструментов с автогенерацией JSON-схем.
- Транспорты STDIO, HTTP, SSE.
- Persistent Chrome profile: сессия Google сохраняется между запусками, после первого логина работа полностью фоновая.
- UV для зависимостей, Taskfile с 20+ задачами (deps, тесты, линт, сборка, деплой).
- Pydantic-валидация параметров, интеграция с LangGraph, CrewAI.

## Вариант из GitHub-дайджеста (jacob-bd)

- CLI `nlm` плюс MCP-сервер `notebooklm-mcp`, ~43 MCP-инструмента.
- Гибкая аутентификация: извлечение куки, профили, автообновление токенов.
- Установка pip / uv / pipx / uvx, одно-клик setup.
- Подключение Claude, Cursor, Gemini CLI и других через MCP и skills.
- Заявлена миграция с устаревших пакетов.

## Как использовать

`nlm` в пайплайнах подготовки данных: автоматически создавать и обновлять блокноты Gemini, которые служат источником знаний для агентов. MCP-инструменты подключать в агентские фреймворки как обычные tool calls.

## Оговорка

Одно имя `notebooklm-mcp` описывается двумя разными способами (Taskfile на 20+ задач против ~43 инструментов и `nlm` CLI). Вероятно, это один проект в разных версиях, но по дайджестам это не доказать. Перед установкой смотреть репозиторий, а не дайджест. Подробнее — `contradictions.md`, п.7.

## Ценность для нас

Снимает ручную работу с NotebookLM: источники и блокноты обновляются скриптом. Это же — путь к тому, чтобы книги и статьи попадали в базу знаний без человека (ср. `agentic-ai-guide` о внешней памяти).
