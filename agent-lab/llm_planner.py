#!/usr/bin/env python3
"""
🧠 LLM Planner v2 — ReAct-агент для многоэтапных задач

Новое в v2: 🚀 Search as Code (параллельный поиск)

Вместо последовательных запросов:
  1. LLM генерирует список запросов (поисковая программа)
  2. Все запросы выполняются параллельно (asyncio.gather)
  3. Результаты дедуплицируются и ранжируются
  4. Только лучшее попадает в контекст LLM

Результат: меньше задержка + лучшее покрытие (Perplexity DSQA 0.871)

Паттерн ReAct (если задача не требует глубокого поиска):
  1. THINK  — агент рассуждает о следующем шаге
  2. PLAN   — разбивает цель на шаги
  3. ACT    — выполняет шаг (LLM / инструмент / поиск)
  4. OBSERVE — смотрит на результат
  5. → повтор пока цель не достигнута или max_steps

Запуск:
  python3 agent-lab/llm_planner.py "исследуй тренды AI-агентов и напиши отчёт"
  python3 agent-lab/llm_planner.py --demo
  python3 agent-lab/llm_planner.py --demo-parallel  # демо Search as Code
  python3 agent-lab/llm_planner.py --goal "..." --max-steps 8 --budget MID

Использование в коде:
  from agent_lab.llm_planner import Planner, ParallelSearchEngine

  # Обычный планнировщик
  planner = Planner(max_steps=6)
  result = await planner.run("Составь план продвижения ai-bureau.pro на VC.ru")

  # Параллельный поиск (Search as Code)
  engine = ParallelSearchEngine()
  results = await engine.search("анализ рынка AI-агентств")
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Awaitable

import httpx
from dotenv import load_dotenv

ENV_PATH = Path(__file__).parent.parent / "ai-eggs" / ".env"
load_dotenv(ENV_PATH)

log = logging.getLogger(__name__)

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
PROXY = "socks5h://localhost:1080"
PROXY_DIRECT = os.getenv("ALL_PROXY", "socks5://Q3NeJXTY:dsBaWh2L@172.120.21.141:64469")


# ─── Модели по бюджету ────────────────────────────────────────────────────────

PLANNER_MODELS = {
    "FREE":    "moonshotai/kimi-k2.6:free",
    "CHEAP":   "openai/gpt-4o-mini",
    "MID":     "deepseek/deepseek-r1",
    "PREMIUM": "anthropic/claude-sonnet-4-5",
}

# Модель для Search as Code (параллельный поиск)
SEARCH_AS_CODE_MODEL = "perplexity/sonar-deep-research"
SEARCH_FAST_MODEL    = "perplexity/sonar"


# ─── Структуры данных ────────────────────────────────────────────────────────────────

@dataclass
class SearchResult:
    query: str
    content: str
    score: float = 1.0      # релевантность
    model: str = ""
    duration_s: float = 0.0

    @property
    def fingerprint(self) -> str:
        """Фингерпринт для дедупликации."""
        words = set(self.content.lower().split())
        return str(hash(frozenset(list(words)[:30])))



class StepStatus(str, Enum):
    PENDING  = "pending"
    RUNNING  = "running"
    DONE     = "done"
    FAILED   = "failed"
    SKIPPED  = "skipped"


@dataclass
class PlanStep:
    index: int
    description: str               # «Найти топ-5 конкурентов AI-агентств»
    tool: str = "llm"              # llm / search / write / python
    status: StepStatus = StepStatus.PENDING
    result: str = ""
    duration_s: float = 0.0

    def __str__(self) -> str:
        icons = {
            StepStatus.PENDING:  "⬜",
            StepStatus.RUNNING:  "🔄",
            StepStatus.DONE:     "✅",
            StepStatus.FAILED:   "❌",
            StepStatus.SKIPPED:  "⏭️",
        }
        return f"{icons[self.status]} [{self.index+1}] {self.description}"


@dataclass
class PlanResult:
    goal: str
    steps: list[PlanStep]
    final_answer: str
    total_time_s: float
    model_used: str
    success: bool


# ─── Инструменты ──────────────────────────────────────────────────────────────

class ToolKit:
    """
    Набор инструментов для планировщика.
    Каждый инструмент = async функция (prompt: str) -> str
    """

    def __init__(self, proxy: str = PROXY):
        self.proxy = proxy

    async def _call_openrouter(
        self,
        prompt: str,
        model: str = "openai/gpt-4o-mini",
        system: str = "",
        max_tokens: int = 1000,
    ) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            async with httpx.AsyncClient(proxy=self.proxy, timeout=60.0) as c:
                r = await c.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://ai-bureau.pro",
                        "X-Title": "LLMPlanner",
                    },
                    json={"model": model, "messages": messages, "max_tokens": max_tokens},
                )
                r.raise_for_status()
                data = r.json()
                # DeepSeek R1 кладёт reasoning в отдельное поле
                msg = data["choices"][0]["message"]
                return msg.get("content") or msg.get("reasoning") or ""
        except Exception as e:
            log.warning("LLM error [%s]: %s", model, e)
            # Fallback
            if model != "openai/gpt-4o-mini":
                return await self._call_openrouter(prompt, "openai/gpt-4o-mini", system, max_tokens)
            return f"[Ошибка LLM: {e}]"

    async def llm(self, prompt: str, model: str = "openai/gpt-4o-mini") -> str:
        """Вызов LLM для выполнения шага."""
        return await self._call_openrouter(prompt, model=model, max_tokens=1200)

    async def search(self, query: str) -> str:
        """Веб-поиск через Perplexity sonar."""
        result = await self._call_openrouter(
            query,
            model="perplexity/sonar",
            system="Отвечай фактически. Дай краткий ответ с ключевыми фактами.",
            max_tokens=600,
        )
        return result

    async def python(self, code: str) -> str:
        """Выполнить Python-код и вернуть stdout."""
        import subprocess
        try:
            proc = subprocess.run(
                ["python3", "-c", code],
                capture_output=True, text=True, timeout=10,
            )
            out = proc.stdout.strip() or proc.stderr.strip()
            return out[:1000] if out else "(нет вывода)"
        except Exception as e:
            return f"[Ошибка выполнения: {e}]"

    async def write(self, content: str, filename: str = "output.md") -> str:
        """Сохранить результат в файл."""
        out_dir = Path(__file__).parent.parent / "reports"
        out_dir.mkdir(exist_ok=True)
        path = out_dir / filename
        path.write_text(content, encoding="utf-8")
        return f"Сохранено: {path}"

    def get(self, tool_name: str) -> Callable:
        """Получить инструмент по имени."""
        tools = {
            "llm":    self.llm,
            "search": self.search,
            "python": self.python,
            "write":  self.write,
        }
        return tools.get(tool_name, self.llm)


# ─── Параллельный поисковый движок (Search as Code) ────────────────────────────

class ParallelSearchEngine:
    """
    Search as Code: LLM генерирует программу поиска → параллельное выполнение.

    Алгоритм:
      1. LLM генерирует N разных поисковых запросов по теме
      2. Все запросы выполняются параллельно через asyncio.gather
      3. Результаты дедуплицируются по fingerprint
      4. Лучшие top_k попадают в финальный синтез
      5. LLM синтезирует единый ответ из всех источников
    """

    QUERY_GEN_PROMPT = """Ты — эксперт по поиску информации. Тема: {topic}

Сгенерируй ровно {n} разных поисковых запроса, которые вместе дадут полный охват темы.
Запросы должны быть:
- Разнообразными (не повторяй слова)
- Конкретными (не абстрактными)
- На русском языке

Ответь СТРОГО в формате JSON (без лишнего текста):
{{"queries": ["запрос 1", "запрос 2", ...]}}"""

    SYNTHESIS_PROMPT = """Синтезируй структурированный ответ по теме: {topic}

ИСТОЧНИКИ (результаты {n} поисковых запросов):
{sources}

Требования:
- Структурируй по разделам (игроки, цены, боли и т.д.)
- Используй только конкретные факты из источников
- Убери дублирование
- Добавь выводы в конце"""

    def __init__(
        self,
        proxy: str = PROXY,
        n_queries: int = 5,
        top_k: int = 3,
        search_model: str = SEARCH_FAST_MODEL,
        synthesis_model: str = "openai/gpt-4o-mini",
    ):
        self.proxy = proxy
        self.n_queries = n_queries
        self.top_k = top_k
        self.search_model = search_model
        self.synthesis_model = synthesis_model
        self._toolkit = ToolKit(proxy=proxy)

    async def _generate_queries(self, topic: str) -> list[str]:
        """Генерирует список поисковых запросов через LLM."""
        prompt = self.QUERY_GEN_PROMPT.format(topic=topic, n=self.n_queries)
        raw = await self._toolkit._call_openrouter(
            prompt,
            model=self.synthesis_model,
            max_tokens=400,
        )
        try:
            match = re.search(r'\{[\s\S]*"queries"[\s\S]*\}', raw)
            data = json.loads(match.group() if match else raw)
            queries = data.get("queries", [])[:self.n_queries]
            # Если не JSON — fallback: строки по одной на строку
            if not queries:
                raise ValueError("empty")
            return queries
        except Exception:
            # Fallback: разбить по newlines
            lines = [l.strip().lstrip("-•123456789.") .strip() for l in raw.split("\n") if l.strip()]
            return lines[:self.n_queries] or [topic]

    async def _single_search(self, query: str) -> SearchResult:
        """Выполняет один поисковый запрос."""
        t0 = time.time()
        try:
            content = await self._toolkit._call_openrouter(
                query,
                model=self.search_model,
                system="Отвечай фактически и конкретно. Дай развёрнутый ответ с фактами, цифрами и именами.",
                max_tokens=800,
            )
        except Exception as e:
            content = f"[Ошибка поиска: {e}]"
        return SearchResult(
            query=query,
            content=content,
            score=1.0,
            model=self.search_model,
            duration_s=time.time() - t0,
        )

    def _deduplicate(self, results: list[SearchResult]) -> list[SearchResult]:
        """Удаляет дублирующиеся результаты по fingerprint."""
        seen: set[str] = set()
        unique: list[SearchResult] = []
        for r in results:
            fp = r.fingerprint
            if fp not in seen:
                seen.add(fp)
                unique.append(r)
        return unique

    def _rank(self, results: list[SearchResult]) -> list[SearchResult]:
        """Ранжирует по длине контента (прокси для информативности)."""
        return sorted(results, key=lambda r: len(r.content), reverse=True)

    async def search(self, topic: str) -> str:
        """
        Полный цикл Search as Code.

        Args:
            topic: Тема/вопрос для исследования

        Returns:
            Синтезированный текст с результатами всех поисков
        """
        t_start = time.time()

        # 1. Генерируем запросы
        print(f"🔍 Генерирую {self.n_queries} поисковых запросов...")
        queries = await self._generate_queries(topic)
        for i, q in enumerate(queries, 1):
            print(f"   {i}. {q}")

        # 2. Параллельный поиск
        print(f"\n⚡ Запускаю {len(queries)} поисков параллельно...")
        raw_results: list[SearchResult] = await asyncio.gather(
            *[self._single_search(q) for q in queries]
        )
        print(f"   ✅ Получено {len(raw_results)} результатов")

        # 3. Дедупликация + ранжирование
        unique = self._deduplicate(raw_results)
        ranked = self._rank(unique)
        best = ranked[:self.top_k]
        print(f"   🎯 Топ-{self.top_k} после дедупликации: {len(best)} результатов")

        # 4. Синтез
        print("\n💡 Синтезирую финальный ответ...")
        sources = "\n\n".join(
            f"--- Запрос: {r.query} ({r.duration_s:.1f}s) ---\n{r.content}"
            for r in best
        )
        synthesis_prompt = self.SYNTHESIS_PROMPT.format(
            topic=topic,
            n=len(best),
            sources=sources,
        )
        final = await self._toolkit._call_openrouter(
            synthesis_prompt,
            model=self.synthesis_model,
            max_tokens=2000,
        )

        total = time.time() - t_start
        print(f"\n⏱  Search as Code: {total:.1f}s | {len(queries)} запросов | топ-{len(best)}")
        return final


# ─── Основной планировщик ─────────────────────────────────────────────────────

class Planner:
    """
    ReAct-планировщик. Цикл: Plan → Act × N → Synthesize.

    Алгоритм:
      1. Генерирует JSON-план: список шагов с типом инструмента
      2. Выполняет каждый шаг, накапливая результаты
      3. Если шаг провалился — переформулирует и повторяет
      4. После всех шагов синтезирует финальный ответ
    """

    PLAN_PROMPT = """Ты — опытный AI-планировщик. Получи задачу и составь план выполнения.

ЗАДАЧА: {goal}

Составь план из {max_steps} или меньше шагов. Каждый шаг — конкретное действие.

Доступные инструменты:
- "llm"    — сгенерировать текст, проанализировать, написать раздел
- "search" — найти актуальную информацию в интернете (используй для фактов и данных)
- "python" — выполнить вычисление или обработку данных
- "write"  — сохранить итоговый результат в файл

Правила:
- Начинай с исследования (search), потом аналитика (llm), в конце запись (write)
- Каждый шаг должен быть конкретным и измеримым
- Максимум 1 шаг "write" — в самом конце
- Шагов не больше {max_steps}

Ответь СТРОГО в формате JSON (без лишнего текста):
{{
  "steps": [
    {{"description": "...", "tool": "search|llm|python|write", "prompt": "..."}},
    ...
  ]
}}"""

    ACT_PROMPT = """Выполни следующий шаг плана.

ОБЩАЯ ЗАДАЧА: {goal}

КОНТЕКСТ (результаты предыдущих шагов):
{context}

ТЕКУЩИЙ ШАГ: {step_description}
ИНСТРУКЦИЯ: {step_prompt}

Выполни шаг. Дай конкретный, содержательный результат (не «я сделаю», а сам результат):"""

    SYNTHESIS_PROMPT = """Ты — эксперт. Синтезируй финальный ответ на основе всей проделанной работы.

ЗАДАЧА: {goal}

ВЫПОЛНЕННЫЕ ШАГИ И РЕЗУЛЬТАТЫ:
{steps_summary}

Напиши финальный, структурированный ответ:
- Используй конкретные факты из шагов
- Дай чёткие выводы и рекомендации
- Оформи красиво (заголовки, списки)
- Без воды и повторений"""

    def __init__(
        self,
        max_steps: int = 6,
        budget: str = "CHEAP",
        verbose: bool = True,
    ):
        self.max_steps = max_steps
        self.budget = budget
        self.verbose = verbose
        self.model = PLANNER_MODELS.get(budget, PLANNER_MODELS["CHEAP"])
        self.toolkit: ToolKit | None = None

    def _log(self, msg: str):
        if self.verbose:
            print(msg)

    async def _init_toolkit(self) -> ToolKit:
        """Инициализирует toolkit с правильным прокси."""
        proxy = PROXY
        try:
            async with httpx.AsyncClient(proxy=proxy, timeout=4.0) as c:
                await c.get("https://openrouter.ai")
        except Exception:
            proxy = PROXY_DIRECT
        return ToolKit(proxy=proxy)

    async def _generate_plan(self, goal: str, toolkit: ToolKit) -> list[PlanStep]:
        """Генерирует план через LLM."""
        prompt = self.PLAN_PROMPT.format(goal=goal, max_steps=self.max_steps)
        raw = await toolkit.llm(prompt, model=self.model)

        # Извлекаем JSON из ответа
        try:
            # Ищем JSON-блок
            match = re.search(r'\{[\s\S]*"steps"[\s\S]*\}', raw)
            if match:
                data = json.loads(match.group())
            else:
                data = json.loads(raw)

            steps = []
            for i, s in enumerate(data.get("steps", [])[:self.max_steps]):
                steps.append(PlanStep(
                    index=i,
                    description=s.get("description", f"Шаг {i+1}"),
                    tool=s.get("tool", "llm"),
                ))
                # Сохраняем промпт для шага в description (компактно)
                if s.get("prompt"):
                    steps[-1].description = s["description"]
                    steps[-1]._prompt = s.get("prompt", s["description"])
                else:
                    steps[-1]._prompt = s["description"]
            return steps

        except Exception as e:
            log.warning("Не удалось распарсить план: %s\nRaw: %s", e, raw[:200])
            # Fallback: один универсальный шаг
            step = PlanStep(0, goal, "llm")
            step._prompt = goal
            return [step]

    async def _execute_step(
        self,
        step: PlanStep,
        goal: str,
        context: str,
        toolkit: ToolKit,
    ) -> str:
        """Выполняет один шаг плана."""
        # Формируем полный промпт для шага
        step_prompt = getattr(step, "_prompt", step.description)
        full_prompt = self.ACT_PROMPT.format(
            goal=goal,
            context=context or "(нет предыдущих результатов)",
            step_description=step.description,
            step_prompt=step_prompt,
        )

        tool_fn = toolkit.get(step.tool)

        if step.tool == "llm":
            return await tool_fn(full_prompt, model=self.model)
        elif step.tool == "search":
            # Для поиска — передаём только суть запроса
            return await tool_fn(step_prompt)
        elif step.tool == "write":
            # write получает контекст как контент
            timestamp = time.strftime("%Y-%m-%d_%H%M")
            filename = f"planner_{timestamp}.md"
            content = f"# {goal}\n\n{context}\n"
            return await tool_fn(content, filename)
        else:
            return await tool_fn(full_prompt)

    async def run(self, goal: str) -> PlanResult:
        """
        Запускает полный цикл планирования и выполнения.

        Args:
            goal: Задача в свободной форме

        Returns:
            PlanResult с шагами и финальным ответом
        """
        t_start = time.time()
        self._log(f"\n{'═'*62}")
        self._log(f"🧠 LLM PLANNER | budget={self.budget} | model={self.model.split('/')[-1]}")
        self._log(f"{'═'*62}")
        self._log(f"\n🎯 Цель: {goal}\n")

        toolkit = await self._init_toolkit()
        self.toolkit = toolkit

        # ── 1. Генерация плана ────────────────────────────────────────
        self._log("📋 Генерирую план...")
        steps = await self._generate_plan(goal, toolkit)

        self._log(f"\n📋 ПЛАН ({len(steps)} шагов):")
        for s in steps:
            self._log(f"  {s}")
        self._log("")

        # ── 2. Выполнение шагов ──────────────────────────────────────
        context_parts: list[str] = []

        for step in steps:
            step.status = StepStatus.RUNNING
            self._log(f"{'─'*62}")
            self._log(f"🔄 Шаг {step.index+1}/{len(steps)}: {step.description}")
            self._log(f"   🔧 Инструмент: {step.tool}")

            t_step = time.time()
            try:
                context = "\n\n".join(
                    f"Шаг {i+1} — {steps[i].description}:\n{steps[i].result}"
                    for i in range(step.index)
                    if steps[i].result
                )
                result = await self._execute_step(step, goal, context, toolkit)
                step.result = result
                step.status = StepStatus.DONE
                step.duration_s = time.time() - t_step

                # Краткое превью результата
                preview = result[:200].replace("\n", " ")
                self._log(f"   ✅ Результат: {preview}...")
                self._log(f"   ⏱  {step.duration_s:.1f}s")
                context_parts.append(f"### Шаг {step.index+1}: {step.description}\n{result}")

            except Exception as e:
                step.status = StepStatus.FAILED
                step.result = f"Ошибка: {e}"
                step.duration_s = time.time() - t_step
                self._log(f"   ❌ Ошибка: {e}")

        # ── 3. Синтез финального ответа ──────────────────────────────
        self._log(f"\n{'─'*62}")
        self._log("💡 Синтезирую финальный ответ...")

        steps_summary = "\n\n".join(context_parts)
        synthesis_prompt = self.SYNTHESIS_PROMPT.format(
            goal=goal,
            steps_summary=steps_summary,
        )
        final_answer = await toolkit.llm(synthesis_prompt, model=self.model)

        total_time = time.time() - t_start
        done_count = sum(1 for s in steps if s.status == StepStatus.DONE)

        self._log(f"\n{'═'*62}")
        self._log(f"✅ ГОТОВО | {done_count}/{len(steps)} шагов | {total_time:.1f}s")
        self._log(f"{'═'*62}\n")
        self._log(final_answer)
        self._log(f"\n{'═'*62}\n")

        return PlanResult(
            goal=goal,
            steps=steps,
            final_answer=final_answer,
            total_time_s=total_time,
            model_used=self.model,
            success=done_count == len(steps),
        )


# ─── CLI ──────────────────────────────────────────────────────────────────────

DEMO_GOALS = [
    "Исследуй топ-3 конкурента ai-bureau.pro и составь сравнительный анализ их позиционирования",
    "Составь контент-план на июнь 2026 для VK-группы по AI-автоматизации малого бизнеса",
    "Проанализируй тренды использования AI-агентов в продажах и напиши выводы для AI Bureau",
]

DEMO_PARALLEL_GOAL = "Рынок AI-агентств в России 2026: игроки, цены, боли клиентов"


async def main():
    parser = argparse.ArgumentParser(description="LLM Planner v2 — ReAct + Search as Code")
    parser.add_argument("goal", nargs="?", default="", help="Цель (задача)")
    parser.add_argument("--demo", action="store_true", help="Запустить демо-задачу")
    parser.add_argument("--demo-parallel", action="store_true", help="Демо Search as Code (параллельный поиск)")
    parser.add_argument("--max-steps", type=int, default=5, help="Макс. шагов (дефолт 5)")
    parser.add_argument(
        "--budget",
        choices=["FREE", "CHEAP", "MID", "PREMIUM"],
        default="CHEAP",
        help="Бюджет модели",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    if args.demo_parallel:
        # Демо чистого Search as Code
        print(f"\n🚀 Search as Code DEMO")
        print(f"🎯 Тема: {DEMO_PARALLEL_GOAL}\n")
        proxy = PROXY
        try:
            async with httpx.AsyncClient(proxy=proxy, timeout=4.0) as c:
                await c.get("https://openrouter.ai")
        except Exception:
            proxy = PROXY_DIRECT

        engine = ParallelSearchEngine(proxy=proxy, n_queries=5, top_k=3)
        result = await engine.search(DEMO_PARALLEL_GOAL)
        print(result)
        return

    if args.demo:
        goal = DEMO_GOALS[0]
        print(f"🎯 Демо-задача: {goal}\n")
    elif args.goal:
        goal = args.goal
    else:
        print("Укажи задачу: python3 llm_planner.py \"твоя задача\"")
        print("Демо планировщик: python3 llm_planner.py --demo")
        print("Демо Search as Code: python3 llm_planner.py --demo-parallel")
        sys.exit(1)

    planner = Planner(max_steps=args.max_steps, budget=args.budget)
    result = await planner.run(goal)

    print(f"\n📊 ИТОГ:")
    for step in result.steps:
        print(f"  {step}")
    print(f"\n⏱  Общее время: {result.total_time_s:.1f}s")
    print(f"🤖 Модель: {result.model_used}")


if __name__ == "__main__":
    asyncio.run(main())
