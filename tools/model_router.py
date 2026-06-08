#!/usr/bin/env python3
"""
🧠 Multi-Model Router — умная маршрутизация запросов к LLM

Вместо одной модели на все случаи — выбирает оптимальную
по критериям: цена / скорость / качество под задачу.

Категории задач → модели:
  MICRO   → бесплатные (trivial, classify, short QA)
  CHEAP   → $0.02-0.1/M (summarize, extract, translate)
  MID     → $0.3-1/M    (reasoning, RAG, code review)
  PREMIUM → $3-15/M     (complex reasoning, long context, creative)

Использование:
  from tools.model_router import route, TaskType, ask, ask_deep

  # Простой вызов — роутер сам выберет модель
  answer = await ask("Переведи на английский: Привет мир")

  # С явным типом задачи
  answer = await ask("Напиши unit-тест", task=TaskType.CODE)

  # Прямой роутинг
  model, tier = route(TaskType.REASONING)

  # Search as Code (параллельный поиск, N запросов одновременно)
  report = await ask_deep("рынок AI-агентств Россия 2026")

Интеграция с habr_intelligence.py:
  Замени call_openrouter(model="perplexity/sonar", ...) на
  ask(..., task=TaskType.RESEARCH)
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Загружаем .env
ENV_PATH = Path(__file__).parent.parent / "ai-eggs" / ".env"
load_dotenv(ENV_PATH)

log = logging.getLogger(__name__)

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
PROXY_TUNNEL = "socks5h://localhost:1080"
PROXY_DIRECT = os.getenv("ALL_PROXY", "socks5://Q3NeJXTY:dsBaWh2L@172.120.21.141:64469")

# ─── Типы задач ───────────────────────────────────────────────────────────────

class TaskType(str, Enum):
    """Категория запроса — определяет какую модель выбрать."""
    TRIVIAL        = "trivial"        # yes/no, classify, 1-2 слова
    EXTRACT        = "extract"        # извлечь факты, JSON из текста
    TRANSLATE      = "translate"      # перевод текста
    SUMMARIZE      = "summarize"      # саммари, дайджест
    CHAT           = "chat"           # обычный чат, короткий ответ
    RESEARCH       = "research"       # поиск + анализ (Perplexity sonar)
    RESEARCH_DEEP  = "research_deep"  # глубокий поиск: Search as Code (параллельные запросы)
    CODE           = "code"           # написать/проверить код
    AGENT          = "agent"          # агентские задачи, MCP, terminal, SWE
    REASONING      = "reasoning"      # аналитика, рассуждения, план
    CREATIVE       = "creative"       # тексты, маркетинг, истории
    LONG           = "long"           # длинный контекст (>32K токенов)
    VISION         = "vision"         # анализ изображений


# ─── Реестр моделей ───────────────────────────────────────────────────────────

@dataclass
class ModelSpec:
    id: str                        # OpenRouter model ID
    tier: str                      # FREE / MICRO / CHEAP / MID / PREMIUM
    cost_per_m: float              # $ за 1M токенов input
    ctx_k: int                     # контекст в тысячах токенов
    strengths: list[TaskType]      # для каких задач хорош
    supports_vision: bool = False  # умеет ли картинки
    note: str = ""


# Кураторский список — лучшие на каждом ценовом уровне
MODEL_REGISTRY: list[ModelSpec] = [
    # ── FREE ─────────────────────────────────────────────────────────────────
    ModelSpec(
        id="openrouter/auto",
        tier="FREE", cost_per_m=0, ctx_k=2000,
        strengths=[TaskType.CHAT, TaskType.TRIVIAL],
        note="OpenRouter auto-роутер, бесплатный",
    ),
    ModelSpec(
        id="moonshotai/kimi-k2.6:free",
        tier="FREE", cost_per_m=0, ctx_k=131,
        strengths=[TaskType.REASONING, TaskType.CODE, TaskType.CHAT],
        note="Kimi K2 — мощный, бесплатный",
    ),
    ModelSpec(
        id="google/gemma-4-31b-it:free",
        tier="FREE", cost_per_m=0, ctx_k=131,
        strengths=[TaskType.CHAT, TaskType.SUMMARIZE, TaskType.TRANSLATE],
        note="Gemma 4 31B бесплатная",
    ),
    ModelSpec(
        id="meta-llama/llama-3.3-70b-instruct:free",
        tier="FREE", cost_per_m=0, ctx_k=131,
        strengths=[TaskType.CHAT, TaskType.REASONING, TaskType.CODE],
        note="Llama 3.3 70B бесплатная",
    ),
    ModelSpec(
        id="qwen/qwen3-coder:free",
        tier="FREE", cost_per_m=0, ctx_k=131,
        strengths=[TaskType.CODE],
        note="Qwen3 Coder бесплатный",
    ),

    # ── MICRO ($0.01-0.05/M) ─────────────────────────────────────────────────
    ModelSpec(
        id="meta-llama/llama-3.1-8b-instruct",
        tier="MICRO", cost_per_m=0.02, ctx_k=131,
        strengths=[TaskType.TRIVIAL, TaskType.EXTRACT, TaskType.TRANSLATE, TaskType.SUMMARIZE],
        note="Быстрый, дешёвый — для простых задач",
    ),
    ModelSpec(
        id="mistralai/mistral-nemo",
        tier="MICRO", cost_per_m=0.02, ctx_k=131,
        strengths=[TaskType.EXTRACT, TaskType.TRANSLATE, TaskType.CHAT],
        note="Mistral Nemo — хорош для extraction",
    ),
    ModelSpec(
        id="amazon/nova-micro-v1",
        tier="MICRO", cost_per_m=0.035, ctx_k=128,
        strengths=[TaskType.TRIVIAL, TaskType.EXTRACT],
        note="Amazon Nova Micro — самый дешёвый от AWS",
    ),

    # ── CHEAP ($0.1-0.5/M) ───────────────────────────────────────────────────
    ModelSpec(
        id="openai/gpt-4o-mini",
        tier="CHEAP", cost_per_m=0.15, ctx_k=128,
        strengths=[TaskType.CHAT, TaskType.SUMMARIZE, TaskType.EXTRACT,
                   TaskType.CODE, TaskType.TRANSLATE],
        note="GPT-4o-mini — золотая середина",
    ),
    ModelSpec(
        id="google/gemini-2.0-flash-001",
        tier="CHEAP", cost_per_m=0.1, ctx_k=1000,
        strengths=[TaskType.SUMMARIZE, TaskType.LONG, TaskType.VISION,
                   TaskType.TRANSLATE, TaskType.CHAT],
        supports_vision=True,
        note="Gemini Flash — длинный контекст, мультимодальный",
    ),
    ModelSpec(
        id="google/gemini-2.5-flash-preview",
        tier="CHEAP", cost_per_m=0.15, ctx_k=1048,
        strengths=[TaskType.REASONING, TaskType.LONG, TaskType.VISION,
                   TaskType.CODE, TaskType.SUMMARIZE],
        supports_vision=True,
        note="Gemini 2.5 Flash — лучший reasoning в классе",
    ),
    ModelSpec(
        id="deepseek/deepseek-chat-v3-0324",
        tier="CHEAP", cost_per_m=0.27, ctx_k=64,
        strengths=[TaskType.REASONING, TaskType.CODE, TaskType.CHAT],
        note="DeepSeek V3 — сильный reasoning",
    ),

    # ── MID ($0.5-2/M) ───────────────────────────────────────────────────────
    ModelSpec(
        id="minimax/minimax-m1",
        tier="MID", cost_per_m=0.4, ctx_k=1000,
        strengths=[TaskType.CODE, TaskType.AGENT, TaskType.REASONING, TaskType.LONG],
        note="MiniMax M1: SWE-Bench 59% 🏆, 1M ctx, терминал/агенты",
    ),
    ModelSpec(
        id="perplexity/sonar",
        tier="MID", cost_per_m=1.0, ctx_k=127,
        strengths=[TaskType.RESEARCH],
        note="Perplexity sonar — быстрый поиск",
    ),
    ModelSpec(
        id="perplexity/sonar-deep-research",
        tier="MID", cost_per_m=2.0, ctx_k=128,
        strengths=[TaskType.RESEARCH_DEEP, TaskType.RESEARCH],
        note="Search as Code: параллельный поиск, DSQA 0.871 🏆",
    ),
    ModelSpec(
        id="perplexity/sonar-pro",
        tier="MID", cost_per_m=3.0, ctx_k=200,
        strengths=[TaskType.RESEARCH],
        note="Perplexity Pro — глубокий research",
    ),
    ModelSpec(
        id="anthropic/claude-haiku-4.5",
        tier="MID", cost_per_m=1.0, ctx_k=200,
        strengths=[TaskType.CREATIVE, TaskType.CHAT, TaskType.EXTRACT,
                   TaskType.SUMMARIZE],
        note="Claude Haiku 4.5 — лучший для текстов",
    ),
    ModelSpec(
        id="openai/gpt-4.1-mini",
        tier="MID", cost_per_m=0.4, ctx_k=1048,
        strengths=[TaskType.CODE, TaskType.REASONING, TaskType.CHAT],
        note="GPT-4.1 Mini — хороший баланс",
    ),
    ModelSpec(
        id="deepseek/deepseek-r1",
        tier="MID", cost_per_m=0.55, ctx_k=164,
        strengths=[TaskType.REASONING, TaskType.CODE],
        note="DeepSeek R1 — думает вслух, отличный reasoning",
    ),

    # ── PREMIUM (>$3/M) ───────────────────────────────────────────────────────
    ModelSpec(
        id="anthropic/claude-sonnet-4-5",
        tier="PREMIUM", cost_per_m=3.0, ctx_k=200,
        strengths=[TaskType.CREATIVE, TaskType.REASONING, TaskType.CODE,
                   TaskType.LONG, TaskType.VISION],
        supports_vision=True,
        note="Claude Sonnet 4.5 — лучший общий",
    ),
    ModelSpec(
        id="openai/gpt-4o",
        tier="PREMIUM", cost_per_m=5.0, ctx_k=128,
        strengths=[TaskType.VISION, TaskType.REASONING, TaskType.CODE],
        supports_vision=True,
        note="GPT-4o — мультимодальный",
    ),
    ModelSpec(
        id="google/gemini-2.5-pro-preview",
        tier="PREMIUM", cost_per_m=7.5, ctx_k=1048,
        strengths=[TaskType.LONG, TaskType.REASONING, TaskType.VISION,
                   TaskType.CODE],
        supports_vision=True,
        note="Gemini 2.5 Pro — лучший для длинных текстов",
    ),
]

# Индекс для быстрого поиска по tier
_BY_TIER: dict[str, list[ModelSpec]] = {}
for _m in MODEL_REGISTRY:
    _BY_TIER.setdefault(_m.tier, []).append(_m)


# ─── Routing logic ────────────────────────────────────────────────────────────

# Приоритет тиров: по умолчанию стараемся экономить
TIER_ORDER = ["FREE", "MICRO", "CHEAP", "MID", "PREMIUM"]

# Минимальный тир для каждого типа задачи
TASK_MIN_TIER: dict[TaskType, str] = {
    TaskType.TRIVIAL:   "FREE",
    TaskType.EXTRACT:   "FREE",
    TaskType.TRANSLATE: "FREE",
    TaskType.SUMMARIZE: "FREE",
    TaskType.CHAT:      "FREE",
    TaskType.RESEARCH:       "MID",    # только Perplexity умеет web-search
    TaskType.RESEARCH_DEEP:  "MID",    # Search as Code — параллельный поиск
    TaskType.CODE:      "FREE",
    TaskType.AGENT:     "MID",    # агентские задачи — нужна мощная модель
    TaskType.REASONING: "FREE",
    TaskType.CREATIVE:  "CHEAP",  # нужен хороший текстовый LLM
    TaskType.LONG:      "CHEAP",  # нужен большой контекст
    TaskType.VISION:    "CHEAP",  # нужна мультимодальность
}


def route(
    task: TaskType,
    budget: str = "CHEAP",       # максимальный тир (FREE/MICRO/CHEAP/MID/PREMIUM)
    needs_vision: bool = False,
) -> tuple[ModelSpec, str]:
    """
    Выбирает оптимальную модель для задачи.

    Args:
        task:         тип задачи
        budget:       максимально допустимый тир расходов
        needs_vision: нужна ли мультимодальность

    Returns:
        (ModelSpec, reason) — выбранная модель и причина выбора
    """
    min_tier = TASK_MIN_TIER.get(task, "FREE")
    min_idx = TIER_ORDER.index(min_tier)
    max_idx = TIER_ORDER.index(budget)

    # Если задача требует тира выше бюджета — принудительно поднимаем
    if min_idx > max_idx:
        max_idx = min_idx

    allowed_tiers = TIER_ORDER[min_idx : max_idx + 1]

    candidates: list[ModelSpec] = []
    for tier in allowed_tiers:
        for model in _BY_TIER.get(tier, []):
            if needs_vision and not model.supports_vision:
                continue
            if task in model.strengths:
                candidates.append(model)

    # Fallback: любая модель в допустимых тирах
    if not candidates:
        for tier in allowed_tiers:
            candidates.extend(_BY_TIER.get(tier, []))

    if not candidates:
        # Последний резорт — GPT-4o-mini
        fallback = next(m for m in MODEL_REGISTRY if m.id == "openai/gpt-4o-mini")
        return fallback, "fallback (нет подходящих моделей)"

    # Выбираем самую дешёвую из подходящих
    best = min(candidates, key=lambda m: m.cost_per_m)
    reason = f"task={task.value} tier={best.tier} cost=${best.cost_per_m:.3f}/M"
    return best, reason


def auto_detect_task(prompt: str) -> TaskType:
    """
    Автоопределение типа задачи по тексту промпта.
    Простая эвристика — без вызова LLM.
    """
    p = prompt.lower()

    # Признаки задач (порядок важен — от специфичного к общему)
    if any(w in p for w in ["переведи", "перевод", "translate", "на английский", "на русский"]):
        return TaskType.TRANSLATE
    if any(w in p for w in ["код", "code", "python", "def ", "функцию", "класс", "баг", "тест"]):
        return TaskType.CODE
    if any(w in p for w in ["агент", "agent", "mcp", "инструмент", "tool", "terminal",
                             "оркестр", "pipeline", "автоматизируй задачу", "swe"]):
        return TaskType.AGENT
    if any(w in p for w in ["глубокое исследование", "детальный анализ",
                             "всесторонний обзор", "сравни все", "deep research",
                             "изучи рынок", "исследуй все"]):
        return TaskType.RESEARCH_DEEP
    if any(w in p for w in ["найди", "поищи", "что нового", "последние новости", "актуально"]):
        return TaskType.RESEARCH
    if any(w in p for w in ["напиши", "придумай", "текст для", "пост", "рекламу", "историю"]):
        return TaskType.CREATIVE
    if any(w in p for w in ["план", "стратегия", "проанализируй", "почему", "сравни", "решение"]):
        return TaskType.REASONING
    if any(w in p for w in ["извлеки", "вытащи", "json", "список", "таблицу", "структуру"]):
        return TaskType.EXTRACT
    if any(w in p for w in ["саммари", "кратко", "сократи", "резюме", "итог", "о чём"]):
        return TaskType.SUMMARIZE
    if len(prompt) > 8000:
        return TaskType.LONG
    if any(w in p for w in ["да или нет", "верно ли", "классифицируй", "какой из"]):
        return TaskType.TRIVIAL

    return TaskType.CHAT  # дефолт


# ─── API-вызов ────────────────────────────────────────────────────────────────

async def _get_proxy() -> str:
    """Проверяет SSH-туннель, fallback на прямой прокси."""
    try:
        async with httpx.AsyncClient(proxy=PROXY_TUNNEL, timeout=4.0) as c:
            await c.get("https://openrouter.ai")
            return PROXY_TUNNEL
    except Exception:
        return PROXY_DIRECT


async def call_model(
    messages: list[dict],
    model: ModelSpec,
    max_tokens: int = 1500,
    proxy: str | None = None,
) -> str | None:
    """Вызов конкретной модели через OpenRouter."""
    if not OPENROUTER_KEY:
        log.error("OPENROUTER_API_KEY не задан")
        return None

    _proxy = proxy or await _get_proxy()

    try:
        async with httpx.AsyncClient(proxy=_proxy, timeout=45.0) as client:
            r = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://ai-bureau.pro",
                    "X-Title": "ModelRouter",
                },
                json={"model": model.id, "messages": messages, "max_tokens": max_tokens},
            )
            r.raise_for_status()
            data = r.json()
            content = data["choices"][0]["message"]["content"]
            log.debug("✅ %s → %d chars", model.id, len(content or ""))
            # ── Cost tracking ──────────────────────────────────────────
            try:
                usage = data.get("usage", {})
                import sys as _sys; _sys.path.insert(0, BASE_DIR)
                from tools.cost_tracker import track as _track
                _track(
                    model=model.id,
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0),
                    source="model_router",
                )
            except Exception:
                pass  # трекинг никогда не ломает основной поток
            return content
    except Exception as e:
        log.warning("❌ %s: %s", model.id, e)
        return None


async def ask(
    prompt: str,
    task: TaskType | None = None,
    budget: str = "CHEAP",
    system: str | None = None,
    max_tokens: int = 1500,
    fallback_tiers: bool = True,
) -> str:
    """
    Главная функция: умный вызов LLM с автороутингом.

    Args:
        prompt:         текст запроса
        task:           тип задачи (если None — авто-определение)
        budget:         максимальный тир ('FREE', 'CHEAP', 'MID', 'PREMIUM')
        system:         системный промпт
        max_tokens:     максимум токенов в ответе
        fallback_tiers: при ошибке пробовать более дорогой тир

    Returns:
        Строка с ответом модели
    """
    detected_task = task or auto_detect_task(prompt)
    model_spec, reason = route(detected_task, budget=budget)

    log.info("🎯 Роутер: %s | %s", model_spec.id, reason)

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    proxy = await _get_proxy()

    # Первая попытка с выбранной моделью
    result = await call_model(messages, model_spec, max_tokens=max_tokens, proxy=proxy)
    if result:
        return result

    # Fallback: пробуем другие модели в том же тире
    log.warning("🔄 Fallback внутри тира %s...", model_spec.tier)
    for alt in _BY_TIER.get(model_spec.tier, []):
        if alt.id == model_spec.id:
            continue
        result = await call_model(messages, alt, max_tokens=max_tokens, proxy=proxy)
        if result:
            log.info("✅ Fallback сработал: %s", alt.id)
            return result

    # Fallback: поднимаемся на тир выше
    if fallback_tiers:
        curr_idx = TIER_ORDER.index(model_spec.tier)
        for tier in TIER_ORDER[curr_idx + 1:]:
            log.warning("⬆️ Поднимаем тир до %s...", tier)
            for alt in _BY_TIER.get(tier, []):
                result = await call_model(messages, alt, max_tokens=max_tokens, proxy=proxy)
                if result:
                    log.info("✅ Тир %s сработал: %s", tier, alt.id)
                    return result

    return "⚠️ Все модели недоступны. Попробуй позже."


async def ask_deep(
    topic: str,
    n_queries: int = 5,
    top_k: int = 3,
    verbose: bool = False,
) -> str:
    """
    Search as Code: параллельный поиск через llm_planner.ParallelSearchEngine.

    LLM генерирует N запросов → все выполняются параллельно →
    дедупликация → топ-K → синтез.

    Преимущество перед ask(task=RESEARCH_DEEP):
      - Полный параллелный поиск (N запросов одновременно)
      - Дедупликация и ранжирование результатов
      - Синтез LLM из лучших источников

    Args:
        topic:    Тема/вопрос для исследования
        n_queries: Кол-во параллельных запросов (default: 5)
        top_k:    Топ-K лучших результатов для синтеза (default: 3)
        verbose:  Печатать прогресс (default: False)

    Returns:
        Структурированный отчёт по теме

    Пример:
        from tools.model_router import ask_deep
        report = await ask_deep("рынок AI-агентств в России 2026")
    """
    import sys
    from pathlib import Path
    # Добавляем корень монорепозитория в sys.path если ещё нет
    _root = Path(__file__).parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))

    from agent_lab.llm_planner import ParallelSearchEngine  # type: ignore

    proxy = await _get_proxy()
    engine = ParallelSearchEngine(
        proxy=proxy,
        n_queries=n_queries,
        top_k=top_k,
    )
    if not verbose:
        # Подавляем print из engine через переопределение stdout
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            result = await engine.search(topic)
        log.debug("🔍 ask_deep stdout:\n%s", buf.getvalue())
        return result
    return await engine.search(topic)


# ─── Статистика и утилиты ─────────────────────────────────────────────────────

def print_routing_table() -> None:
    """Выводит таблицу маршрутизации для всех типов задач."""
    print("\n📊 ТАБЛИЦА МАРШРУТИЗАЦИИ (budget=CHEAP)\n")
    print(f"{'Задача':15s} {'Модель':45s} {'Тир':8s} {'Цена/M':10s} {'Примечание'}")
    print("─" * 110)
    for task in TaskType:
        model, reason = route(task, budget="CHEAP")
        print(f"{task.value:15s} {model.id:45s} {model.tier:8s} ${model.cost_per_m:<9.3f} {model.note[:35]}")

    print(f"\n📊 ТАБЛИЦА МАРШРУТИЗАЦИИ (budget=MID)\n")
    print(f"{'Задача':15s} {'Модель':45s} {'Тир':8s} {'Цена/M':10s} {'Примечание'}")
    print("─" * 110)
    for task in TaskType:
        model, reason = route(task, budget="MID")
        print(f"{task.value:15s} {model.id:45s} {model.tier:8s} ${model.cost_per_m:<9.3f} {model.note[:35]}")


def estimate_cost(prompt: str, task: TaskType | None = None, budget: str = "CHEAP") -> dict:
    """Оценивает стоимость запроса без реального вызова."""
    detected_task = task or auto_detect_task(prompt)
    model, reason = route(detected_task, budget=budget)
    tokens_est = len(prompt.split()) * 1.3  # грубая оценка
    cost_est = (tokens_est / 1_000_000) * model.cost_per_m
    return {
        "task": detected_task.value,
        "model": model.id,
        "tier": model.tier,
        "cost_per_m": model.cost_per_m,
        "tokens_estimate": int(tokens_est),
        "cost_estimate_usd": round(cost_est, 6),
        "reason": reason,
    }


# ─── CLI / Demo ───────────────────────────────────────────────────────────────

async def _demo() -> None:
    """Демонстрация роутера: 5 разных типов задач."""
    import json

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")

    test_cases = [
        ("Переведи на английский: Добрый вечер, как дела?", "CHEAP"),
        ("Напиши краткое саммари: AI-агенты используют LLM для автоматизации задач.", "CHEAP"),
        ("def fibonacci(n): напиши эту функцию на Python с кешированием", "CHEAP"),
        ("Кто такой Антон Чехов?", "FREE"),
        ("Придумай заголовок для поста о преимуществах AI-агентов для малого бизнеса", "CHEAP"),
    ]

    print("\n" + "═" * 70)
    print("🧠 MODEL ROUTER DEMO")
    print("═" * 70)

    for prompt, budget in test_cases:
        print(f"\n📝 Запрос: {prompt[:60]}...")
        info = estimate_cost(prompt, budget=budget)
        print(f"   🎯 Задача: {info['task']} | Модель: {info['model']}")
        print(f"   💰 Цена: ${info['cost_per_m']}/M | ~{info['tokens_estimate']} токенов")

        answer = await ask(prompt, budget=budget)
        print(f"   ✅ Ответ: {answer[:120]}...")
        print()
        await asyncio.sleep(0.5)

    print("\n" + "═" * 70)
    print_routing_table()


if __name__ == "__main__":
    import sys
    if "--table" in sys.argv:
        print_routing_table()
    elif "--demo" in sys.argv:
        asyncio.run(_demo())
    else:
        # Быстрый тест
        async def _quick():
            logging.basicConfig(level=logging.INFO)
            q = " ".join(sys.argv[1:]) or "Что такое LLM-роутер? Объясни в 2 предложениях."
            print(f"Запрос: {q}")
            info = estimate_cost(q)
            print(f"Роутинг: {info['task']} → {info['model']} (${info['cost_per_m']}/M)")
            ans = await ask(q)
            print(f"Ответ: {ans}")
        asyncio.run(_quick())
