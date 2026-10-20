#!/usr/bin/env python3
"""DRIFT-002: свернуть 12 смысловых дублей скиллов Hermes <-> OpenCode.

Для каждого дубля:
  1) мастер в OpenCode (~/.config/opencode/skills) обогащается уникальной
     операционной конкретикой из Hermes-скилла;
  2) Hermes-скилл заменяется обёрткой-ссылкой на мастер (оригинал -> .bak).

Повторный запуск идемпотентен: enrichment не дублируется, .bak не перетирается.
"""

import shutil
import sys
from pathlib import Path

HOME = Path.home()
OC = HOME / ".config/opencode/skills"
HERMES = HOME / ".hermes/skills"
MARK = "Дополнено из Hermes (2026-10-10)"

ENRICH = {
    "agents/financier/SKILL.md": """## Дополнено из Hermes (2026-10-10)

- Формулы quick-reference: CAC = (Sales+Marketing) ÷ New Customers; LTV(sub) = ARPU × Gross Margin % ÷ Monthly Churn; LTV(trans) = AOV × Frequency × GM% × Lifetime; Contribution Margin % = (Rev − VarCosts) ÷ Rev; Payback = CAC ÷ (Monthly Revenue × GM%).
- Порог входа: LTV/CAC ≥ 3:1, payback < 12 мес; payback > 18 мес — напрягает кэш, флагать.
- Guardrails: fully-loaded CAC (все затраты привлечения, не только реклама); cohort-based LTV (средние когорты врут); консервативные допущения для новых продуктов; channel-level анализ (blended метрики прячут правду); churn 5%→4% = LTV +25%.
""",
    "agents/batrak/SKILL.md": """## Дополнено из Hermes (2026-10-10)

- Трезвая калибровка: НЕ претендуем на hardcore Senior/Lead backend (5+ лет Django/FastAPI, highload, банки), enterprise-легаси и BigTech LeetCode. Наш сегмент: AI-инженер / автоматизация (Middle/Specialist — LLM, промпты, RAG, векторные БД) + умные боты с интеграциями (Telegram aiogram + Bitrix24 + Mango voice).
- Анти-бан: HH — только ручная/полу-авто отправка, массовые авто-отклики = блок аккаунта. Kwork — 28 откликов = стоп-сигнал. Задержки между запросами; клики не автоматизировать — только готовить черновики.
""",
    "agents/sherlock/SKILL.md": """## Дополнено из Hermes (2026-10-10): 8-фазный пайплайн

SCOPE (запрос → подвопросы, режим quick/standard/deep/ultradeep) → PLAN (5–10 углов поиска, выбор источников) → RETRIEVE (параллельный сбор субагентами) → TRIANGULATE (перепроверка) → SYNTHESIZE → CRITIQUE (поиск дыр) → REFINE → PACKAGE.

- Executive summary: 2–3 абзаца, 50–250 слов; каждый finding — 300–500 слов с цитатами [1],[2]; обязательный раздел Limitations & Caveats (пробелы и неопределённость).
""",
    "expert-source-pipeline/SKILL.md": """## Дополнено из Hermes (2026-10-10)

- Разведка: 2–4 параллельных web-вызова — сначала структура репо/README, потом точечно 2–3 ключевых файла. Не читать всё насквозь.
- Вердикт — максимум 4 коротких абзаца: что это / зачем / берём-не берём (одна причина, глагол) / что делать. Продающий контент без конкретики → «продающее, шум, не берём» — без выдумывания псевдополезных сигналов.
""",
    "brand-voice/SKILL.md": """## Дополнено из Hermes (2026-10-10): таксономия AI-паттернов (humanizer)

Редактура идёт проходами по классам: личность и душа, контент-штампы, язык и грамматика, стиль, коммуникация, filler и хеджинг, ритм и риторика. Каждый класс — отдельный проход; один «массовый» проход пропускает штаммы.
""",
    "agents/ai-defender/SKILL.md": """## Дополнено из Hermes (2026-10-10): HARD RULES ротации секретов

- Новый и старый ключ никогда не выводятся в чат; работа через файл на диске (/tmp/.new_key_tmp).
- Проверка только по префиксу: `cut -c1-30`.
- Правки идут в `.env*`, не в исходный код (ключи читаются из окружения).
- Сетевые/прокси-конфиги не трогать без явного посошного аппрува.
""",
    "resolving-merge-conflicts/SKILL.md": """## Дополнено из Hermes (2026-10-10)

- Self-favoring: агент, запущенный одной из сторон конфликта, структурно предвзят — декларировать и осознанно взвешивать другую сторону.
- «Splitting the difference» даёт ничейный гибрид — выбирать одну сторону и называть её решение.
- Классифицировать по hunk-ам, а не по файлам (файл часто миксит классы); drive-by правки запрещены.
- Намерения сторон берём из completion summaries / PR bodies, а не только из commit messages.
""",
    "web-search/SKILL.md": """## Дополнено из Hermes (2026-10-10): лестница обхода блокировок

1. Wayback Machine (snapshot + timestamp) → 2. archive.today (ротация доменов .ph/.md/.li/.is) → 3. Jina Reader (только при ключе) → 4. API-pivot (/api/, /graphql, .json, RSS на том же хосте) → 5. реальный браузер — последний и самый дорогой resort.

Provenance discipline: каждый факт несёт источник и timestamp; «фейк-успехи» ответов релеев за успех не считать.
""",
    "frontend-design/SKILL.md": """## Дополнено из Hermes (2026-10-10)

- Дизайн начинается из контекста (brand docs, продуктовые ограничения, существующие паттерны), а не «с нуля по вайбам».
- Surface-first: сначала композиция поверхностей и макет, потом токены/цвета. Начинать с палитры — анти-паттерн.
""",
    "design-bridge/SKILL.md": """## Дополнено из Hermes (2026-10-10): анатомия DESIGN.md

Канонический порядок секций: Overview → Colors → Typography → Components.
Линт перед экспортом: валидация структуры, ссылок на токены и WCAG-контраста.
""",
    "finish-day/SKILL.md": """## Дополнено из Hermes (2026-10-10)

- Exit code обязателен: fire-and-forget без проверки кода выхода недопустим; только exit 0 считаем успехом (backup + restore).
- Не одним «мега-коммитом» грязное дерево: чекпоинт/архив делает сам скрипт, тематические коммиты — отдельными проверенными батчами.
""",
}

WRAPPERS = {
    "financier-unit-economics": "agents/financier",
    "jobhunter": "agents/batrak",
    "shrelock-research": "agents/sherlock",
    "productivity/expert-source-review": "expert-source-pipeline",
    "workflow/finish-day-progress": "finish-day",
    "software-development/systematic-debugging": "systematic-debugging",
    "creative/humanizer": "brand-voice",
    "security/secret-rotation": "agents/ai-defender",
    "autonomous-ai-agents/merge-reconciler": "resolving-merge-conflicts",
    "research/blocked-page-recovery": "web-search",
    "creative/claude-design": "frontend-design",
    "creative/design-md": "design-bridge",
    # импорт 2026-10-10: мастер теперь в OpenCode
    "research/grounded-citations": "grounded-citations",
    "productivity/ocr-and-documents": "ocr-and-documents",
    "creative/popular-web-designs": "popular-web-designs",
    "creative/architecture-diagram": "architecture-diagram",
    "research/competitor-news-monitor": "competitor-news-monitor",
    "research/blogwatcher": "blogwatcher",
    "text-unicode-hygiene": "text-unicode-hygiene",
}


def split_frontmatter(text: str):
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            return text[: end + 4], text[end + 4 :]
    return "", text


def enrich(rel: str, body: str) -> None:
    p = OC / rel
    if not p.exists():
        print(f"SKIP (нет мастера): {rel}")
        return
    text = p.read_text(encoding="utf-8")
    if MARK in text:
        print(f"OK (уже): {rel}")
        return
    with p.open("a", encoding="utf-8") as f:
        f.write("\n" + body if not text.endswith("\n") else "\n" + body)
    print(f"ENRICHED: {rel}")


def ensure_writable(p: Path) -> None:
    if p.is_dir() and not (p.stat().st_mode & 0o200):
        p.chmod(p.stat().st_mode | 0o700)
    if p.is_file() and not (p.stat().st_mode & 0o200):
        p.chmod(p.stat().st_mode | 0o600)


def wrap(hermes_rel: str, master: str) -> None:
    d = HERMES / hermes_rel
    f = d / "SKILL.md"
    if not f.exists():
        print(f"SKIP (нет Hermes-скилла): {hermes_rel}")
        return
    orig = f.read_text(encoding="utf-8")
    bak = d / "SKILL.md.bak-20261010"
    if not bak.exists():
        ensure_writable(d)
        ensure_writable(f)
        shutil.copy2(f, bak)
        print(f"BACKUP: {hermes_rel} -> SKILL.md.bak-20261010")
    front, _ = split_frontmatter(orig)
    if front and "master:" not in front:
        front = front[:-3] + f"master: opencode:{master}\n---"
    body = f"""
# Обёртка: мастер перенесён в OpenCode

**Мастер-скилл:** `~/.config/opencode/skills/{master}/SKILL.md`
(обогащён уникальным содержимым этого скилла 2026-10-10, drift-аудит).

Этот скилл — ссылка-обёртка для совместимости Hermes. Реальную логику
грузи из мастера; здесь она больше не дублируется.
Оригинальное содержимое: `SKILL.md.bak-20261010`.
"""
    ensure_writable(f)
    f.write_text(front + body, encoding="utf-8")
    print(f"WRAPPED: {hermes_rel} -> {master}")


def main() -> None:
    for rel, body in ENRICH.items():
        enrich(rel, body)
    for h, m in WRAPPERS.items():
        wrap(h, m)


if __name__ == "__main__":
    sys.exit(main())
