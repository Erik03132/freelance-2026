#!/usr/bin/env python3
"""
Levitan Main Agent — точка входа проекта.
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения
BASE_DIR = Path(__file__).resolve().parent.parent
for env_file in (BASE_DIR / ".env", BASE_DIR / "config" / ".env"):
    if env_file.exists():
        load_dotenv(env_file, override=True)
        break


class LevitanAgent:
    """Главный агент проекта Levitan."""
    
    def __init__(self):
        self.name = "Levitan"
        self.version = "0.1.0"
        self.running = False
    
    async def start(self):
        """Запуск агента."""
        self.running = True
        print(f"🚀 {self.name} v{self.version} started")
        
        # Основной цикл
        while self.running:
            await self.tick()
            await asyncio.sleep(1)
    
    async def tick(self):
        """Один тик основного цикла."""
        # Здесь будет логика агента
        pass
    
    def stop(self):
        """Остановка агента."""
        self.running = False
        print(f"🛑 {self.name} stopped")


async def main():
    """Главная функция."""
    agent = LevitanAgent()
    
    try:
        await agent.start()
    except KeyboardInterrupt:
        agent.stop()


if __name__ == "__main__":
    asyncio.run(main())