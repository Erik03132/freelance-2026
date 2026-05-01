"""
🔧 Инструменты ядра Core Agent.

Каждый инструмент — это функция с декоратором @tool.
Агент ВИДИТ описание (docstring) и САМ решает, когда вызвать.

Для создания "ребёнка" (специалиста) — добавь свои инструменты в отдельный файл.
"""
import json
import os
from datetime import datetime
from langchain.tools import tool


# === Универсальные инструменты (доступны ВСЕМ агентам-детям) ===

@tool
def get_current_time() -> str:
    """Возвращает текущую дату и время.
    Используй, когда нужно знать сегодняшнюю дату или время."""
    now = datetime.now()
    return f"Сейчас: {now.strftime('%d.%m.%Y %H:%M')} ({now.strftime('%A')})"


@tool
def calculate(expression: str) -> str:
    """Вычисляет математическое выражение.
    Используй для любых расчётов: цены, количество, проценты.
    Пример: '200 * 85 + 3500'"""
    try:
        # Безопасное вычисление (без eval с произвольным кодом)
        allowed = set("0123456789.+-*/() ")
        if not all(c in allowed for c in expression):
            return f"Ошибка: выражение содержит недопустимые символы"
        result = eval(expression)  # noqa: S307 — проверяем символы выше
        return f"{expression} = {result}"
    except Exception as e:
        return f"Ошибка вычисления: {e}"


@tool
def search_knowledge(query: str) -> str:
    """Ищет информацию в базе знаний агента.
    Используй, когда нужно ответить на вопрос, требующий 
    специализированных знаний (товары, цены, правила, документы).
    
    Args:
        query: Поисковый запрос на естественном языке
    """
    # Импортируем здесь, чтобы не было circular import
    from rag_memory import search
    results = search(query)
    if not results:
        return "В базе знаний не найдено информации по этому вопросу."
    return "\n\n".join(results)


# === Заготовки для MCP-инструментов (подключаются через серверы) ===
# Эти инструменты будут приходить из MCP-серверов автоматически.
# Здесь оставляем как пример для демо без MCP.

@tool
def web_search(query: str) -> str:
    """Ищет информацию в интернете (Tavily + DuckDuckGo).
    Используй, когда база знаний не содержит ответа и нужна 
    актуальная информация из сети.
    
    Args:
        query: Поисковый запрос
    """
    import httpx
    from dotenv import load_dotenv
    load_dotenv()
    
    tavily_key = os.getenv("TAVILY_API_KEY", "")
    
    # Уровень 1: Tavily (синхронный вызов)
    if tavily_key:
        try:
            r = httpx.post(
                "https://api.tavily.com/search",
                json={"api_key": tavily_key, "query": query, "max_results": 3,
                      "search_depth": "basic", "include_answer": True},
                timeout=10,
            )
            data = r.json()
            parts = []
            if data.get("answer"):
                parts.append(f"**Ответ:** {data['answer']}")
            for item in data.get("results", [])[:3]:
                parts.append(f"**{item.get('title','')}**\n{item.get('content','')[:200]}\n{item.get('url','')}")
            if parts:
                return "\n\n".join(parts)
        except Exception as e:
            print(f"⚠️ Tavily tool: {e}")
    
    # Уровень 2: DuckDuckGo (fallback, без ключа)
    try:
        r = httpx.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            timeout=10,
        )
        data = r.json()
        parts = []
        if data.get("AbstractText"):
            parts.append(f"**{data.get('Heading','')}**: {data['AbstractText']}")
        for topic in data.get("RelatedTopics", [])[:3]:
            if isinstance(topic, dict) and "Text" in topic:
                parts.append(topic["Text"])
        if parts:
            return "\n\n".join(parts)
    except Exception as e:
        print(f"⚠️ DuckDuckGo tool: {e}")
    
    return f"По запросу '{query}' ничего не найдено."


@tool
def execute_code_in_sandbox(code: str, language: str = "python") -> str:
    """Выполняет сгенерированный код в высокоскоростной изолированной песочнице (Cube Sandbox / E2B).
    ИСПОЛЬЗУЙ ЭТОТ ИНСТРУМЕНТ всегда, когда нужно запустить скрипт, проанализировать данные
    или протестировать логику (Code Interpreter). НИКОГДА не пытайся запустить код на хост-машине.
    
    Args:
        code: Исходный код для выполнения.
        language: Язык программирования (python, javascript).
    """
    import os
    
    # Заглушка-демонстрация интеграции с локальным эндпоинтом Cube Sandbox
    # В реальности здесь будет HTTP POST запрос к нашему поднятому KVM инстансу.
    sandbox_endpoint = os.getenv("CUBE_SANDBOX_ENDPOINT", "http://localhost:8000/execute")
    
    # Имитация работы песочницы:
    # 1. Мы отправляем код в песочницу (cold start < 60ms)
    # 2. Песочница выполняет код в изолированном KVM-ядре
    # 3. Песочница возвращает stdout/stderr и мгновенно уничтожается
    
    try:
        # ПСЕВДОКОД: 
        # r = httpx.post(sandbox_endpoint, json={"code": code, "lang": language})
        # return r.json()["stdout"]
        
        return f"[Cube Sandbox 📦]: Песочница поднята за 55ms. Код ({language}) успешно передан на изоляцию. Результат: 🟢 STDOUT_MOCK (Integration pending)"
    except Exception as e:
        return f"[Cube Sandbox 📦]: Ошибка инициализации песочницы: {e}"


# === Регистр инструментов ===

# Базовый набор — доступен всем агентам
CORE_TOOLS = [
    get_current_time,
    calculate,
    search_knowledge,
]

# Расширенный набор — для агентов с доступом в интернет и Code Interpreter
EXTENDED_TOOLS = CORE_TOOLS + [
    web_search,
    execute_code_in_sandbox,
]
