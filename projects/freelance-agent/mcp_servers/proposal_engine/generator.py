"""
Генератор отклика на фриланс-задачу: 30% работы + дорожная карта.
"""

from pathlib import Path
import os
import sys

ROOT = Path(__file__).parent.parent.parent
PROMPTS = ROOT / "prompts"
sys.path.insert(0, str(ROOT))

from mcp_servers.proposal_engine.scout import ScoutAgent

PROMPT_TEMPLATE = """Ты — Freelance Agent. Пишешь отклик на фриланс-задачу от имени исполнителя Игоря.

## СТИЛЬ ОТКЛИКА
- Язык: русский, профессиональный, сдержанный. БЕЗ сленга и заигрывания.
- Начинай с «Здравствуйте!» и сразу к сути.
- Запрещено: «Задача понятна», «Делал аналогичные системы», «Внимательно изучил ваше ТЗ».
- Цена: базовая ставка 1500 руб/час. Итоговая цена = часы × 1500. Если указан бюджет заказчика — цена должна быть в пределах бюджета.
- Подпись: «С уважением, Игорь».
- ФОРМАТ ВЫВОДА: ТОЛЬКО чистый текст, без markdown, без #, без **, без ```, без * в начале строк.

## СТРУКТУРА ОТКЛИКА

1. Понимание задачи (2-3 предложения)
Переформулируй задачу своими словами, покажи что вник.

2. Почему я подхожу (3-5 пунктов)
Свяжи требования из задачи с реальным опытом. Конкретные технологии и проекты.

3. 30 процентов готового решения
Фрагмент работы, который доказывает что ты можешь сделать задачу.
Для кода: архитектура + ключевой фрагмент.
Для текста: план + пример.
Для бота: схема + пример диалога.
Для интеграции: архитектура + пример кода.

4. Дорожная карта
Распиши этапы столбиком (каждый с новой строки). Без часов, только название этапов и общий срок.
Формат:
Этап 1: Название
Этап 2: Название
Итого: Y дней

5. Вы получите
Конкретный список результата. Обращение напрямую к заказчику.

## ВАЖНО: НЕ ИСПОЛЬЗУЙ символы #, *, _, `, > в начале строк. Не используй markdown-разметку. Код и примеры пиши в одну строку или просто с новой строки без обратных кавычек.
ВЫВОДИ ТОЛЬКО ТЕКСТ ОТКЛИКА. Без предисловий, без пояснений, без примечаний. Только письмо.

ПРОФИЛЬ ИСПОЛНИТЕЛЯ
{candidate_profile}

## ЗАДАЧА
{task_description}

## АНАЛИЗ ЗАДАЧИ
{analysis}
"""


class ProposalGenerator:
    def __init__(self):
        self.scout = ScoutAgent()

    def build_prompt(self, task: str, title: str = "", budget: int = 0) -> str:
        analysis = self.scout.analyze(title, task, budget)
        profile_path = PROMPTS / "candidate_profile.txt"
        profile = profile_path.read_text(encoding="utf-8") if profile_path.exists() else ""

        analysis_text = "\n".join(f"{k}: {v}" for k, v in analysis.items())

        return PROMPT_TEMPLATE.format(
            candidate_profile=profile,
            task_description=task,
            analysis=analysis_text,
        )

    def generate(self, task: str, title: str = "", budget: int = 0) -> str:
        prompt = self.build_prompt(task, title, budget)

        key = os.getenv("OPENROUTER_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        if not key:
            return "[Freelance Agent] Нет API-ключа. Промпт собран:\n\n" + prompt

        return self._call_llm(prompt, key)

    def _call_llm(self, prompt: str, key: str) -> str:
        import httpx

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": "deepseek/deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        }
        resp = httpx.post(url, headers=headers, json=body, timeout=180)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
