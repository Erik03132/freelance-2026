"""Отправка отчетов в Telegram."""

import logging
from typing import Optional
import httpx

logger = logging.getLogger(__name__)


class TelegramReporter:
    """Отправка отчетов через Telegram бота."""
    
    BASE_URL = "https://api.telegram.org/bot{token}"
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = self.BASE_URL.format(token=bot_token)
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """
        Отправка сообщения.
        
        Args:
            text: Текст сообщения
            parse_mode: Режим парсинга (HTML/Markdown)
            
        Returns:
            True если успешно
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": text,
                    "parse_mode": parse_mode
                }
            )
            
            result = response.json()
            
            if result.get("ok"):
                logger.debug("Message sent to Telegram")
                return True
            else:
                logger.error(f"Telegram API error: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    async def send_call_report(
        self,
        phone: str,
        status: str,
        duration: int,
        interest: bool,
        crops: list[str] = None,
        region: str = None,
        notes: str = ""
    ):
        """Отправка отчета о звонке."""
        crops_text = ", ".join(crops) if crops else "не указано"
        
        status_emoji = {
            "лид": "🟢",
            "перезвон": "🟡",
            "не_заинтересован": "🔴",
            "отказ": "❌",
            "completed": "✅",
            "failed": "⚠️"
        }.get(status, "📞")
        
        text = f"""{status_emoji} <b>Новый звонок завершен</b>

📞 Телефон: {phone}
⏱ Длительность: {duration} сек
📊 Статус: {status}

🌾 Культуры: {crops_text}
📍 Регион: {region or "не указан"}

💬 Заметки: {notes or "нет"}"""
        
        await self.send_message(text)
    
    async def send_daily_summary(self, stats: dict):
        """Отправка ежедневной сводки."""
        text = f"""📊 <b>Ежедневная сводка</b>

📞 Всего звонков: {stats.get('total', 0)}
✅ Успешных: {stats.get('success', 0)}
🟢 Лидов: {stats.get('interested', 0)}
❌ Отказов: {stats.get('rejected', 0)}

📈 Конверсия в лиды: {stats.get('conversion', 0):.1f}%"""
        
        await self.send_message(text)
    
    async def send_error(self, error_message: str):
        """Отправка уведомления об ошибке."""
        text = f"""⚠️ <b>Ошибка системы</b>

{error_message}"""
        
        await self.send_message(text)
    
    async def send_startup(self):
        """Отправка уведомления о запуске."""
        text = """🚀 <b>Levitan запущен</b>

Голосовой агент готов к работе.
Система обзвона активирована."""
        
        await self.send_message(text)
    
    async def send_shutdown(self):
        """Отправка уведомления об остановке."""
        text = """🛑 <b>Levitan остановлен</b>

Система обзвона деактивирована."""
        
        await self.send_message(text)
    
    async def close(self):
        """Закрыть HTTP-клиент."""
        await self.client.aclose()


# Глобальный экземпляр
_reporter: Optional[TelegramReporter] = None


def get_telegram_reporter() -> Optional[TelegramReporter]:
    """Получить глобальный экземпляр репортера."""
    global _reporter
    if _reporter is None:
        from .config import settings
        if settings.telegram.bot_token and settings.telegram.chat_id:
            _reporter = TelegramReporter(
                bot_token=settings.telegram.bot_token,
                chat_id=settings.telegram.chat_id
            )
    return _reporter
