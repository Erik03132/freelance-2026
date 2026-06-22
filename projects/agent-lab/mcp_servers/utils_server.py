"""
🔌 Демо MCP-сервер: полезные утилиты.

Это пример MCP-сервера, который любой агент может подключить.
Запускается отдельным процессом и предоставляет инструменты
по стандартному MCP-протоколу.

Запуск (для теста):
  python mcp_servers/utils_server.py

Подключение к агенту:
  Через конфигурацию в core_agent.py или напрямую:
  
  from langchain_mcp_adapters.client import MultiServerMCPClient
  client = MultiServerMCPClient({
      "utils": {
          "transport": "stdio",
          "command": "python",
          "args": ["mcp_servers/utils_server.py"]
      }
  })
"""
import os
import httpx

try:
    from fastmcp import FastMCP
    HAS_FASTMCP = True
except ImportError:
    HAS_FASTMCP = False
    print("⚠️ FastMCP не установлен: pip install fastmcp")

if HAS_FASTMCP:
    mcp = FastMCP("UtilityTools")

    @mcp.tool()
    async def get_weather(city: str) -> str:
        """
        Получает текущую погоду для города.
        
        Args:
            city: Название города (например, "Москва" или "London")
        """
        async with httpx.AsyncClient() as client:
            # Шаг 1: Геокодинг (город → координаты)
            geo = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": city, "count": 1, "language": "ru"},
                timeout=10,
            )
            geo_data = geo.json()
            if not geo_data.get("results"):
                return f"Город '{city}' не найден"

            loc = geo_data["results"][0]
            lat, lon = loc["latitude"], loc["longitude"]
            name = loc.get("name", city)

            # Шаг 2: Погода по координатам
            weather = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={"latitude": lat, "longitude": lon, "current_weather": True},
                timeout=10,
            )
            current = weather.json()["current_weather"]

            return (
                f"Погода в {name}:\n"
                f"🌡 Температура: {current['temperature']}°C\n"
                f"💨 Ветер: {current['windspeed']} км/ч\n"
            )

    @mcp.tool()
    async def get_exchange_rate(currency: str = "USD") -> str:
        """
        Получает текущий курс валюты к рублю.
        
        Args:
            currency: Код валюты (USD, EUR, CNY)
        """
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.exchangerate-api.com/v4/latest/RUB",
                    timeout=10,
                )
                data = resp.json()
                rate = data["rates"].get(currency.upper())
                if rate:
                    # API даёт курс RUB → X, нам нужен X → RUB
                    rub_rate = round(1 / rate, 2)
                    return f"1 {currency.upper()} = {rub_rate} ₽"
                return f"Валюта '{currency}' не найдена"
        except Exception as e:
            return f"Ошибка получения курса: {e}"


    if __name__ == "__main__":
        print("🔌 MCP-сервер 'UtilityTools' запущен (stdio)")
        mcp.run(transport="stdio")
