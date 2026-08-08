# Волт — база знаний

SSoT для документных знаний. События сессий — в claude-mem, здесь — постоянные знания.

## Разделы

- [[00-Inbox]] — приёмная: сюда скидываются файлы и ссылки (через бота Анжелочки или вручную). Ночной читатель разбирает в 02:30.
- [[01-Projects]] — знания по проектам (CONTEXT, статусы)
- [[02-Knowledge]] — доменные базы: законы ([[02-Knowledge/laws]]), гранты ([[02-Knowledge/grants]]), SEO ([[02-Knowledge/seo]]), Bitrix ([[02-Knowledge/bitrix]]), AI-агенты ([[02-Knowledge/ai-agents]])
- [[03-Lessons]] — уроки (solutions, self_improve_log)
- [[04-Decisions]] — ADR
- [[05-Audits]] — аудиты
- [[06-Library]] — личная библиотека (каталог: [[06-Library/_catalog]])
- [[10-Daily]] — daily notes

## Правила

- Агенты читают ТОЛЬКО md-версии материалов (06-Library).
- Книги → `06-Library/books/<slug>/digest.md` + исходный md.
- Видео/аудио → `06-Library/media/<slug>/summary.md` + ссылка на облако (без транскрибации).
- Новые уроки пишутся в `03-Lessons/` (tools/lesson_capture.py).
