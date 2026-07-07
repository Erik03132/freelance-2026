"""Анализ звонка после завершения."""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from .llm_client import get_llm_client
from .knowledge_base import get_knowledge_base

logger = logging.getLogger(__name__)


class PostCallAnalyzer:
    """Анализатор звонков после завершения."""
    
    def __init__(self, llm_api_key: str = ""):
        self.llm_client = get_llm_client(llm_api_key)
        self.knowledge_base = get_knowledge_base()
    
    async def analyze_call(self, transcript_path: Path) -> dict:
        """
        Анализ завершенного звонка.
        
        Args:
            transcript_path: Путь к транскрипту
            
        Returns:
            Результат анализа
        """
        try:
            # Читаем транскрипт
            with open(transcript_path, "r", encoding="utf-8") as f:
                transcript_data = json.load(f)
            
            transcript_text = "\n".join([
                f"{'Агент' if entry['role'] == 'agent' else 'Клиент'}: {entry['text']}"
                for entry in transcript_data.get("transcript", [])
            ])
            
            # Анализ с помощью LLM
            analysis = await self._analyze_with_llm(transcript_text)
            
            # Извлекаем новые FAQ
            new_faq = await self._extract_new_faq(transcript_text)
            
            # Сохраняем результат
            result = {
                "call_id": transcript_data.get("call_id"),
                "phone": transcript_data.get("phone"),
                "analysis": analysis,
                "new_faq": new_faq,
                "analyzed_at": datetime.now().isoformat()
            }
            
            # Сохраняем анализ
            analysis_path = transcript_path.parent / f"{transcript_path.stem}_analysis.json"
            with open(analysis_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Call analyzed: {transcript_data.get('call_id')}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze call: {e}")
            return {}
    
    async def _analyze_with_llm(self, transcript_text: str) -> dict:
        """Анализ транскрипта с помощью LLM."""
        analysis_prompt = f"""Проанализируй транскрипт разговора менеджера с клиентом и дай оценку:

Транскрипт:
{transcript_text}

Оцени по критериям:
1. Качество диалога (1-10)
2. Заинтересованность клиента (высокая/средняя/низкая)
3. Основные возражения
4. Что сделано хорошо
5. Что можно улучшить
6. Рекомендации для менеджера

Верни JSON с полями:
- quality_score: оценка качества (1-10)
- interest_level: высокая/средняя/низкая
- objections: список возражений
- strengths: список сильных сторон
- improvements: список улучшений
- recommendations: рекомендации для менеджера
"""
        
        try:
            response = await self.llm_client.generate(
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            # Парсим JSON
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end != 0:
                return json.loads(response[start:end])
            
            return {"raw_analysis": response}
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {}
    
    async def _extract_new_faq(self, transcript_text: str) -> list[dict]:
        """Извлечение новых FAQ из транскрипта."""
        faq_prompt = f"""Проанализируй транскрипт и извлеки новые вопросы клиентов и ответы на них:

Транскрипт:
{transcript_text}

Если есть новые вопросы, которых нет в базе знаний, верни список:
[
    {{"question": "Вопрос клиента", "answer": "Ответ агента"}}
]

Если новых вопросов нет, верни пустой список []
"""
        
        try:
            response = await self.llm_client.generate(
                messages=[{"role": "user", "content": faq_prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            # Парсим JSON
            start = response.find("[")
            end = response.rfind("]") + 1
            if start != -1 and end != 0:
                return json.loads(response[start:end])
            
            return []
            
        except Exception as e:
            logger.error(f"FAQ extraction failed: {e}")
            return []
    
    def update_knowledge_base(self, new_faq: list[dict]):
        """Обновление базы знаний новыми FAQ."""
        for item in new_faq:
            if "question" in item and "answer" in item:
                self.knowledge_base.add_faq_item(
                    item["question"],
                    item["answer"]
                )
                logger.info(f"Added new FAQ: {item['question']}")
    
    async def batch_analyze(self, transcript_dir: Path) -> list[dict]:
        """Пакетный анализ транскриптов."""
        results = []
        
        for transcript_file in transcript_dir.glob("*.json"):
            if "_analysis" not in transcript_file.name:
                result = await self.analyze_call(transcript_file)
                results.append(result)
        
        logger.info(f"Batch analyzed {len(results)} calls")
        return results


# Глобальный экземпляр
_analyzer: Optional[PostCallAnalyzer] = None


def get_post_call_analyzer() -> PostCallAnalyzer:
    """Получить глобальный экземпляр анализатора."""
    global _analyzer
    if _analyzer is None:
        from .config import settings
        _analyzer = PostCallAnalyzer(llm_api_key=settings.openrouter.api_key)
    return _analyzer
