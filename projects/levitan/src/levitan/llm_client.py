"""Клиент для работы с LLM через OpenRouter API."""

import logging

import httpx

logger = logging.getLogger(__name__)


class LLMClient:
    """Клиент для работы с языковыми моделями через OpenRouter."""

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek/deepseek-chat-v3-0324",
        fallback_model: str = "qwen/qwen-2.5-7b-instruct"
    ):
        self.api_key = api_key
        self.model = model
        self.fallback_model = fallback_model
        self.client = httpx.AsyncClient(timeout=30.0)

    async def generate(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        use_fallback: bool = True
    ) -> str:
        """
        Генерация ответа LLM.

        Args:
            messages: Список сообщений [{"role": "user", "content": "..."}]
            model: Модель для использования
            temperature: Температура генерации
            max_tokens: Максимальное количество токенов
            use_fallback: Использовать fallback модель при ошибке

        Returns:
            Сгенерированный текст
        """
        model_to_use = model or self.model

        try:
            response = await self.client.post(
                f"{self.BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "https://levitan.app",
                    "X-Title": "Levitan Voice Agent"
                },
                json={
                    "model": model_to_use,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            )

            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                logger.debug(f"LLM response: {content[:100]}...")
                return content
            else:
                logger.error(f"Unexpected LLM response: {result}")
                if use_fallback:
                    return await self._fallback_generate(messages, temperature, max_tokens)
                return ""

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            if use_fallback:
                return await self._fallback_generate(messages, temperature, max_tokens)
            return ""

    async def _fallback_generate(
        self,
        messages: list[dict],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Генерация через fallback модель."""
        try:
            return await self.generate(
                messages=messages,
                model=self.fallback_model,
                temperature=temperature,
                max_tokens=max_tokens,
                use_fallback=False
            )
        except Exception as e:
            logger.error(f"Fallback LLM generation failed: {e}")
            return ""

    async def generate_dialog_response(
        self,
        system_prompt: str,
        user_message: str,
        context: str = "",
        recent_history: list[dict] = None
    ) -> str:
        """
        Генерация ответа для диалога.

        Args:
            system_prompt: Системный промпт
            user_message: Сообщение пользователя
            context: Контекст из базы знаний
            recent_history: Последние сообщения

        Returns:
            Ответ агента
        """
        messages = [{"role": "system", "content": system_prompt}]

        # Добавляем контекст
        if context:
            messages.append({
                "role": "system",
                "content": f"Дополнительная информация:\n{context}"
            })

        # Добавляем историю
        if recent_history:
            for msg in recent_history[-5:]:  # Последние 5 сообщений
                messages.append(msg)

        # Добавляем сообщение пользователя
        messages.append({"role": "user", "content": user_message})

        return await self.generate(messages, temperature=0.7, max_tokens=300)

    async def extract_lead_info(
        self,
        transcript: str,
        system_prompt: str
    ) -> dict:
        """
        Извлечение информации о лиде из транскрипта.

        Args:
            transcript: Транскрипт разговора
            system_prompt: Промпт для извлечения

        Returns:
            Словарь с информацией о лиде
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Транскрипт разговора:\n{transcript}"}
        ]

        try:
            response = await self.generate(messages, temperature=0.3, max_tokens=500)
            # Парсим JSON из ответа
            import json
            # Пробуем найти JSON в ответе
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end != 0:
                return json.loads(response[start:end])
            return {}
        except Exception as e:
            logger.error(f"Lead extraction failed: {e}")
            return {}

    async def close(self):
        """Закрыть HTTP-клиент."""
        await self.client.aclose()


# Глобальный экземпляр
_llm_client: LLMClient | None = None


def get_llm_client(api_key: str = "") -> LLMClient:
    """Получить глобальный экземпляр LLM клиента."""
    global _llm_client
    if _llm_client is None and api_key:
        _llm_client = LLMClient(api_key=api_key)
    return _llm_client
