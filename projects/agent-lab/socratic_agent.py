#!/usr/bin/env python3
"""
🏛️ Socratic Agent — агент, который задаёт вопросы вместо ответов

Сократический метод: вместо того чтобы генерировать ответ из воздуха,
агент сначала задаёт уточняющие вопросы — и только получив реальный контекст,
формулирует вывод или текст.

Три режима:
  1. CONSULT  — консультация: задаёт вопросы → выдаёт план
  2. CONTENT  — контент: задаёт вопросы → пишет текст (пост, статью)
  3. QUALIFY  — квалификация клиента (для Анжелы): задаёт вопросы → профиль клиента

Запуск демо:
  python3 agent-lab/socratic_agent.py --mode consult
  python3 agent-lab/socratic_agent.py --mode content
  python3 agent-lab/socratic_agent.py --mode qualify

Использование в коде:
  from agent_lab.socratic_agent import SocraticAgent, Mode

  agent = SocraticAgent(mode=Mode.CONTENT)
  result = await agent.run(topic="автоматизация продаж")
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

ENV_PATH = Path(__file__).parent.parent / "ai-eggs" / ".env"
load_dotenv(ENV_PATH)

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
PROXY = "socks5h://localhost:1080"


# ─── Режимы работы ────────────────────────────────────────────────────────────

class Mode(str, Enum):
    CONSULT = "consult"    # бизнес-консультация → план
    CONTENT = "content"    # сбор контекста → написать пост/статью
    QUALIFY = "qualify"    # квалификация клиента → профиль


# ─── Конфигурация сессий ──────────────────────────────────────────────────────

@dataclass
class SocraticConfig:
    """Настройки для каждого режима."""
    mode: Mode
    intro: str                     # вводная фраза агента
    max_questions: int             # сколько вопросов задать
    question_prompt: str           # промпт для генерации вопроса
    synthesis_prompt: str          # промпт для финального вывода
    model: str = "openai/gpt-4o-mini"


CONFIGS: dict[Mode, SocraticConfig] = {

    Mode.CONSULT: SocraticConfig(
        mode=Mode.CONSULT,
        intro=(
            "Привет! Я помогу тебе разобраться с задачей и составить конкретный план.\n"
            "Но сначала мне нужно понять твою ситуацию — без этого любой совет будет пустым.\n"
            "Готов? Начнём с первого вопроса."
        ),
        max_questions=5,
        question_prompt="""Ты — опытный бизнес-консультант, применяющий сократический метод.
Твоя задача: задавать уточняющие вопросы, которые помогают человеку самому прийти к ответу.

Правила:
- Задавай ОДИН вопрос за раз (не список!)
- Вопрос должен вытаскивать конкретику: цифры, имена, факты
- НЕ давай советов и оценок пока собираешь информацию
- Каждый следующий вопрос углубляет предыдущий ответ
- Вопрос должен быть коротким (1-2 предложения)

Тема: {topic}
История диалога:
{history}

Задай следующий уточняющий вопрос (только вопрос, без преамбул):""",

        synthesis_prompt="""Ты — опытный бизнес-консультант.
На основе диалога ниже составь конкретный, применимый план действий.

Тема: {topic}
Диалог:
{history}

Напиши структурированный план:
- Что КОНКРЕТНО нужно сделать (с учётом ответов)
- Почему именно это (связь с тем, что рассказал человек)
- Первые 3 шага с дедлайнами

Пиши конкретно, без воды. Используй факты из диалога.""",
    ),

    Mode.CONTENT: SocraticConfig(
        mode=Mode.CONTENT,
        intro=(
            "Буду писать для тебя контент. Но сначала — несколько вопросов.\n"
            "Хороший текст рождается из реального опыта, а не из общих фраз.\n"
            "Расскажи мне о конкретных деталях — и текст будет живым."
        ),
        max_questions=4,
        question_prompt="""Ты — копирайтер, который собирает материал перед написанием текста.
Применяй сократический метод: задавай вопросы, которые вытащат живые детали, факты, истории.

Правила:
- Один вопрос за раз
- Ищи: конкретные цифры, примеры, случаи из практики, эмоции
- НЕ пиши текст, только задавай вопрос
- Вопросы должны помочь написать убедительный, живой текст

Тема/формат: {topic}
История диалога:
{history}

Задай следующий вопрос для сбора материала (только вопрос):""",

        synthesis_prompt="""Ты — профессиональный копирайтер.
На основе собранного материала напиши текст.

Формат/тема: {topic}
Собранный материал (диалог):
{history}

Требования к тексту:
- Используй конкретные факты, цифры и примеры из диалога
- Живой язык, без клише и канцелярита
- Структура: зацепка → суть → конкретика → призыв
- Длина: оптимальная для формата

Напиши финальный текст:""",
    ),

    Mode.QUALIFY: SocraticConfig(
        mode=Mode.QUALIFY,
        intro=(
            "Здравствуйте! Расскажите о вашей задаче — я помогу подобрать решение.\n"
            "Мне важно понять вашу ситуацию, чтобы предложить именно то, что нужно."
        ),
        max_questions=5,
        question_prompt="""Ты — менеджер по продажам AI-решений. Квалифицируешь потенциального клиента.
Используй сократический метод: вытаскивай информацию вопросами.

Что нужно узнать (BANT):
- Budget: есть ли бюджет на автоматизацию?
- Authority: кто принимает решения?
- Need: какая боль/задача? Что сейчас не работает?
- Timeline: когда нужно решение?

Дополнительно: масштаб бизнеса, текущие инструменты, прошлый опыт с AI.

Правила:
- Один вопрос за раз, дружелюбно
- НЕ продавай — сначала пойми
- Переформулируй предыдущий ответ, показывая что услышал

Тема: {topic}
История диалога:
{history}

Следующий квалификационный вопрос (только вопрос):""",

        synthesis_prompt="""Ты — опытный менеджер по продажам AI-решений.
На основе диалога составь профиль клиента и рекомендации.

История диалога:
{history}

Составь структурированный профиль клиента:

**🎯 Портрет клиента:**
- Бизнес и ниша:
- Масштаб:
- Текущая боль:
- BANT-оценка: Budget / Authority / Need / Timeline

**💡 Рекомендуемое решение:**
(конкретно что предложить из наших услуг AI Bureau)

**⚡ Следующий шаг:**
(что предложить сделать прямо сейчас)

**🔴 Риски / возражения:**
(что может помешать сделке)""",
    ),
}


# ─── Сократический агент ─────────────────────────────────────────────────────

@dataclass
class SocraticAgent:
    """
    Агент сократического метода.

    Алгоритм:
      1. Приветствие + первый вопрос (генерируется LLM)
      2. Цикл: получить ответ → сгенерировать следующий вопрос
      3. После N вопросов → синтез (план / текст / профиль)
    """
    mode: Mode = Mode.CONSULT
    config: SocraticConfig = field(init=False)
    history: list[dict] = field(default_factory=list)
    topic: str = ""

    def __post_init__(self):
        self.config = CONFIGS[self.mode]

    def _format_history(self) -> str:
        """Форматирует историю диалога для промптов."""
        lines = []
        for msg in self.history:
            role = "Агент" if msg["role"] == "assistant" else "Пользователь"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)

    async def _call_llm(self, prompt: str, max_tokens: int = 300) -> str:
        """Вызов LLM через OpenRouter."""
        try:
            # Определяем прокси
            proxy = PROXY
            try:
                async with httpx.AsyncClient(proxy=proxy, timeout=4.0) as c:
                    await c.get("https://openrouter.ai")
            except Exception:
                proxy = os.getenv("ALL_PROXY", "")

            async with httpx.AsyncClient(proxy=proxy or None, timeout=45.0) as client:
                r = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://ai-bureau.pro",
                        "X-Title": "SocraticAgent",
                    },
                    json={
                        "model": self.config.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens,
                        "temperature": 0.7,
                    },
                )
                r.raise_for_status()
                data = r.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            log.error("LLM error: %s", e)
            return "Не могу сформировать ответ прямо сейчас."

    async def _generate_question(self) -> str:
        """Генерирует следующий уточняющий вопрос."""
        prompt = self.config.question_prompt.format(
            topic=self.topic,
            history=self._format_history(),
        )
        return await self._call_llm(prompt, max_tokens=150)

    async def _generate_synthesis(self) -> str:
        """Генерирует финальный вывод на основе всего диалога."""
        prompt = self.config.synthesis_prompt.format(
            topic=self.topic,
            history=self._format_history(),
        )
        return await self._call_llm(prompt, max_tokens=800)

    def _add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    async def run(self, topic: str = "", interactive: bool = True) -> dict:
        """
        Запускает сессию сократического агента.

        Args:
            topic:       тема/задача пользователя (опционально, можно ввести в процессе)
            interactive: True = интерактивный CLI, False = API-режим

        Returns:
            dict с историей диалога и финальным выводом
        """
        self.topic = topic

        # ── Приветствие ──────────────────────────────────────────────
        print(f"\n{'═'*60}")
        print(f"🏛️  СОКРАТИЧЕСКИЙ АГЕНТ [{self.mode.value.upper()}]")
        print(f"{'═'*60}\n")
        print(f"🤖 {self.config.intro}\n")

        # Если тема не задана — спрашиваем
        if not self.topic and interactive:
            self.topic = input("👤 Ты: ").strip()
            self._add_message("user", self.topic)
            print()

        # ── Цикл вопросов ────────────────────────────────────────────
        for i in range(self.config.max_questions):
            # Генерируем вопрос
            print("⏳ Думаю...", end="\r")
            question = await self._generate_question()
            print(f"                    ", end="\r")  # очистить строку

            print(f"🤖 {question}\n")
            self._add_message("assistant", question)

            if not interactive:
                break

            # Получаем ответ пользователя
            try:
                answer = input("👤 Ты: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\n⚠️ Прервано пользователем")
                break

            if answer.lower() in ("стоп", "готово", "хватит", "stop", "done"):
                break

            self._add_message("user", answer)
            print()

        # ── Финальный синтез ─────────────────────────────────────────
        print(f"\n{'─'*60}")
        print("⏳ Анализирую собранную информацию...\n")

        synthesis = await self._generate_synthesis()

        print(f"{'═'*60}")
        mode_labels = {
            Mode.CONSULT: "📋 ПЛАН ДЕЙСТВИЙ",
            Mode.CONTENT: "✍️  ГОТОВЫЙ ТЕКСТ",
            Mode.QUALIFY: "🎯 ПРОФИЛЬ КЛИЕНТА",
        }
        print(f"{mode_labels.get(self.mode, '💡 ВЫВОД')}:")
        print(f"{'═'*60}\n")
        print(synthesis)
        print(f"\n{'═'*60}\n")

        return {
            "mode": self.mode.value,
            "topic": self.topic,
            "history": self.history,
            "synthesis": synthesis,
            "questions_asked": sum(1 for m in self.history if m["role"] == "assistant"),
        }

    async def run_api(self, topic: str, user_answers: list[str]) -> dict:
        """
        API-режим: подаём тему и список ответов пользователя.
        Используется при интеграции в ботов (Анжела, telegram-бот).

        Args:
            topic:        начальная тема
            user_answers: список ответов (по одному на каждый вопрос)

        Returns:
            dict с историей и финальным выводом
        """
        self.topic = topic
        self._add_message("user", topic)

        for answer in user_answers:
            question = await self._generate_question()
            self._add_message("assistant", question)
            self._add_message("user", answer)

        synthesis = await self._generate_synthesis()

        return {
            "mode": self.mode.value,
            "topic": self.topic,
            "history": self.history,
            "synthesis": synthesis,
        }


# ─── CLI ──────────────────────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(description="Сократический агент")
    parser.add_argument(
        "--mode",
        choices=["consult", "content", "qualify"],
        default="consult",
        help="Режим агента",
    )
    parser.add_argument("--topic", default="", help="Начальная тема (опционально)")
    parser.add_argument(
        "--demo", action="store_true",
        help="Демо-режим: запустить с заготовленными ответами",
    )
    args = parser.parse_args()

    mode = Mode(args.mode)
    agent = SocraticAgent(mode=mode)

    if args.demo:
        # Демо: имитация диалога с заготовленными ответами
        demos = {
            Mode.CONSULT: {
                "topic": "хочу автоматизировать продажи в своём бизнесе",
                "answers": [
                    "Продаю цыплят бройлеров оптом, около 50 клиентов в месяц",
                    "Менеджер тратит по 2 часа в день на однотипные вопросы про цены и доставку",
                    "Примерно 30 000 рублей в месяц я готов вложить",
                    "Хочу запустить за 2 недели, клиенты в WhatsApp и Telegram",
                ],
            },
            Mode.CONTENT: {
                "topic": "пост ВКонтакте о преимуществах покупки цыплят с доставкой",
                "answers": [
                    "Доставляем по всей России, от 100 цыплят, охлаждённые в специальных боксах",
                    "Недавно клиент из Сибири заказал 500 штук, все доехали живыми — он был в шоке",
                    "Главная боль — люди боятся что птица погибнет в дороге",
                ],
            },
            Mode.QUALIFY: {
                "topic": "хочу узнать про AI-бота для моего бизнеса",
                "answers": [
                    "У меня небольшая клиника, 3 врача, около 40 пациентов в день",
                    "Я директор, сам принимаю решения",
                    "Администратор перегружен — запись, напоминания, вопросы про цены",
                    "Бюджет есть, готов обсудить, хочу запустить в следующем месяце",
                ],
            },
        }

        demo_data = demos[mode]
        result = await agent.run_api(
            topic=demo_data["topic"],
            user_answers=demo_data["answers"],
        )

        print(f"\n{'═'*60}")
        print(f"🏛️  ДЕМО [{mode.value.upper()}] — РЕЗУЛЬТАТ")
        print(f"{'═'*60}\n")
        print("📝 История диалога:")
        for msg in result["history"]:
            icon = "🤖" if msg["role"] == "assistant" else "👤"
            print(f"  {icon} {msg['content'][:100]}...")
        print(f"\n{'─'*60}")
        print("💡 Синтез:\n")
        print(result["synthesis"])
    else:
        await agent.run(topic=args.topic, interactive=True)


if __name__ == "__main__":
    asyncio.run(main())
