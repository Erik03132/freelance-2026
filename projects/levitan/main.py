"""Основной файл запуска Levitan."""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.levitan.config import settings
from src.levitan.mango_client import MangoClient
from src.levitan.webhook_server import app
from src.levitan.campaign_manager import get_campaign_manager
from src.levitan.knowledge_base import get_knowledge_base
from src.levitan.telegram_reporter import get_telegram_reporter
from src.levitan.post_call import get_post_call_analyzer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("levitan.log")
    ]
)
logger = logging.getLogger(__name__)


class LevitanApp:
    """Основное приложение Levitan."""
    
    def __init__(self):
        self.mango_client = MangoClient(
            api_key=settings.mango.api_key,
            salt=settings.mango.salt
        )
        self.campaign_manager = get_campaign_manager()
        self.knowledge_base = get_knowledge_base()
        self.telegram_reporter = get_telegram_reporter()
        self.post_call_analyzer = get_post_call_analyzer()
        
        self._is_running = False
    
    async def start(self):
        """Запуск приложения."""
        logger.info("Starting Levitan...")
        
        # Инициализируем компоненты
        self._is_running = True
        
        # Уведомляем о запуске
        if self.telegram_reporter:
            await self.telegram_reporter.send_startup()
        
        logger.info("Levitan started successfully")
    
    async def stop(self):
        """Остановка приложения."""
        logger.info("Stopping Levitan...")
        
        self._is_running = False
        
        # Закрываем клиенты
        await self.mango_client.close()
        
        if self.telegram_reporter:
            await self.telegram_reporter.send_shutdown()
            await self.telegram_reporter.close()
        
        logger.info("Levitan stopped")
    
    async def run_campaign(self, campaign_name: str, csv_path: Path):
        """Запуск кампании обзвона."""
        logger.info(f"Running campaign: {campaign_name}")
        
        # Загружаем кампанию
        campaign = self.campaign_manager.load_campaign(campaign_name, csv_path)
        
        # Запускаем обзвон
        await self.campaign_manager.start_campaign(campaign_name)
    
    def get_stats(self) -> dict:
        """Получение статистики."""
        return self.campaign_manager.get_all_stats()


# Глобальный экземпляр приложения
_app: LevitanApp = None


def get_app() -> LevitanApp:
    """Получить глобальный экземпляр приложения."""
    global _app
    if _app is None:
        _app = LevitanApp()
    return _app


async def main():
    """Главная функция."""
    app_instance = get_app()
    
    # Обработка сигналов
    def signal_handler(sig, frame):
        logger.info("Signal received, stopping...")
        asyncio.create_task(app_instance.stop())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Запуск
    await app_instance.start()
    
    # Запуск веб-сервера
    import uvicorn
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    try:
        await server.serve()
    except KeyboardInterrupt:
        pass
    finally:
        await app_instance.stop()


if __name__ == "__main__":
    asyncio.run(main())
