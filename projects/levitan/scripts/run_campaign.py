"""Скрипт запуска кампании обзвона."""

import asyncio
import logging
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.levitan.config import settings
from src.levitan.campaign_manager import get_campaign_manager
from src.levitan.telegram_reporter import get_telegram_reporter

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def run_campaign(campaign_name: str, csv_path: Path):
    """Запуск кампании."""
    logger.info(f"Starting campaign: {campaign_name}")
    
    # Получаем менеджер кампаний
    manager = get_campaign_manager()
    
    # Загружаем кампанию
    campaign = manager.load_campaign(campaign_name, csv_path)
    logger.info(f"Campaign loaded: {campaign.total_contacts} contacts")
    
    # Уведомляем в Telegram
    reporter = get_telegram_reporter()
    if reporter:
        await reporter.send_message(
            f"🚀 Запуск кампании: {campaign_name}\n"
            f"📞 Контактов: {campaign.total_contacts}"
        )
    
    # Запускаем обзвон
    await manager.start_campaign(campaign_name)
    
    # Ждем завершения
    try:
        while manager.active_sessions or not manager._call_queue.empty():
            await asyncio.sleep(10)
            
            # Логируем статистику
            stats = manager.get_campaign_stats(campaign_name)
            logger.info(
                f"Stats: called={stats.get('called_count', 0)}, "
                f"active={stats.get('active_sessions', 0)}"
            )
    except KeyboardInterrupt:
        logger.info("Campaign interrupted")
        manager.pause_campaign(campaign_name)
    
    # Отправляем финальную сводку
    if reporter:
        stats = manager.get_campaign_stats(campaign_name)
        await reporter.send_daily_summary({
            "total": stats.get("called_count", 0),
            "success": stats.get("success_count", 0),
            "interested": stats.get("interested_count", 0),
            "rejected": 0,
            "conversion": (
                stats.get("interested_count", 0) / max(stats.get("called_count", 1), 1) * 100
            )
        })
    
    logger.info("Campaign finished")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python run_campaign.py <campaign_name> <csv_path>")
        print("Example: python run_campaign.py rostov data/campaigns/csv/Ростовская область 2026.csv")
        sys.exit(1)
    
    campaign_name = sys.argv[1]
    csv_path = Path(sys.argv[2])
    
    if not csv_path.exists():
        print(f"CSV file not found: {csv_path}")
        sys.exit(1)
    
    asyncio.run(run_campaign(campaign_name, csv_path))
