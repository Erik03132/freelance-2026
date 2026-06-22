from __future__ import annotations

"""
🧠 Каскадный LLM-движок v2 — ЖЕЛЕЗОБЕТОННЫЙ.

Каскад из 5 уровней, 3 из которых бесплатные:

  1. Elephant Alpha (FREE, #1 trending, 100B, tool calling ✅)
  2. OpenRouter Auto (FREE, auto-подбор модели)  
  3. Gemini 2.0 Flash (FREE tier, может блокироваться по гео)
  4. Gemini Direct API (FREE tier, обход гео)
  5. Ollama/Gemma4 (OFFLINE, локальная, работает без интернета)

Если все 5 упали → вежливый fallback. Клиент НИКОГДА не увидит ошибку.

Поиск:
  DuckDuckGo (бесплатный, без API ключа, работает из РФ)
"""
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e2b")

# ============================================================
# КАСКАД МОДЕЛЕЙ (порядок = приоритет)
# ============================================================

# Модели OpenRouter с tool calling
OPENROUTER_MODELS = [
    # Уровень 1: Deepseek — мощный кодовый LLM
    "deepseek/deepseek-coder-33b-instruct",
    
    # Уровень 2: Qwen — китайская чат‑модель
    "qwen/qwen-7b-chat",
    
    # Уровень 3: Gemini через OpenRouter (может упасть по гео)
    "google/gemini-2.0-flash-001",
]


async def _call_openrouter(
    messages: list[dict],
    model: str = None,
    tools: list[dict] = None,
) -> dict | None:
    """
    Вызов одной модели через OpenRouter.
    Возвращает dict с content и tool_calls, или None если ошибка.
    """
    if not OPENROUTER_KEY:
        return None
    
    target_model = model or OPENROUTER_MODELS[0]
    
    try:
        body = {
            "model": target_model,
            "messages": messages,
            "max_tokens": 4096,
        }
        if tools:
            body["tools"] = tools
        
        async with httpx.AsyncClient(timeout=25) as client:
            resp = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                },
                json=body,
            )
            data = resp.json()
            
            if resp.status_code == 200 and "choices" in data:
                msg = data["choices"][0]["message"]
                return {
                    "content": msg.get("content", ""),
                    "tool_calls": msg.get("tool_calls"),
                    "model_used": target_model,
                }
            
            err = data.get("error", {}).get("message", "")[:80]
            print(f"⚠️ {target_model}: {resp.status_code} — {err}")
    except Exception as e:
        print(f"⚠️ {target_model}: {e}")
    
    return None


async def call_openrouter_cascade(
    messages: list[dict],
    tools: list[dict] = None,
) -> dict | None:
    """
    Перебирает все модели OpenRouter по каскаду.
    Возвращает первый успешный ответ.
    """
    for model in OPENROUTER_MODELS:
        result = await _call_openrouter(messages, model=model, tools=tools)
        if result:
            return result
    return None


async def call_gemini_direct(messages: list[dict]) -> str | None:
    """Прямой вызов Gemini API (обход гео-ограничений OpenRouter)."""
    if not GEMINI_KEY:
        return None
    try:
        contents = []
        for msg in messages:
            if msg["role"] == "system":
                continue  # Gemini не поддерживает system как role
            role = "model" if msg["role"] == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        # Добавляем system instruction отдельно
        system_text = next((m["content"] for m in messages if m["role"] == "system"), "")

        async with httpx.AsyncClient(timeout=30) as client:
            body = {"contents": contents}
            if system_text:
                body["systemInstruction"] = {"parts": [{"text": system_text}]}
            
            resp = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}",
                json=body,
            )
            data = resp.json()
            if "candidates" in data:
                return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"⚠️ Gemini Direct: {e}")
    return None


async def call_ollama(messages: list[dict]) -> str | None:
    """Офлайн-страховка: локальная модель через Ollama."""
    try:
        ollama_msgs = []
        for msg in messages:
            ollama_msgs.append({
                "role": msg["role"] if msg["role"] != "system" else "system",
                "content": msg["content"],
            })
        
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json={"model": OLLAMA_MODEL, "messages": ollama_msgs, "stream": False},
            )
            data = resp.json()
            if "message" in data:
                print(f"✅ Ollama/{OLLAMA_MODEL} (offline)")
                return data["message"]["content"]
    except httpx.ConnectError:
        print("⚠️ Ollama не запущена")
    except Exception as e:
        print(f"⚠️ Ollama: {e}")
    return None


# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ — ЖЕЛЕЗОБЕТОННЫЙ КАСКАД
# ============================================================

async def call_llm(messages: list[dict], tools: list[dict] = None) -> str:
    """
    Железобетонный каскад LLM. 5 уровней защиты.
    
    Порядок:
      1. Elephant Alpha (бесплатная, с tool calling)
      2. OpenRouter Auto (бесплатная, auto-подбор)
      3. Gemini через OpenRouter
      4. Gemini Direct API
      5. Ollama (локальная, офлайн)
    
    Гарантия: ответ ВСЕГДА будет, даже без интернета.
    """
    # Уровни 1-3: OpenRouter каскад (с tool calling!)
    result = await call_openrouter_cascade(messages, tools=tools)
    if result:
        if result.get("content"):
            return result["content"]
        # Если пришли tool_calls — возвращаем JSON
        if result.get("tool_calls"):
            import json
            return json.dumps(result["tool_calls"], ensure_ascii=False)

    # Уровень 4: Gemini Direct (без tool calling, но стабильный)
    print("🔄 OpenRouter недоступен → Gemini Direct...")
    result = await call_gemini_direct(messages)
    if result:
        return result

    # Уровень 5: Ollama (офлайн, последняя надежда)
    print("🔌 Облачные модели недоступны → Ollama...")
    result = await call_ollama(messages)
    if result:
        return result

    return "Прости, все мои мозги сейчас на техобслуживании. Попробуй через пару минут! 🔧"


# ============================================================
# 🔍 КАСКАД ПОИСКА — 3 уровня
# 1. Perplexity Sonar (через OpenRouter, тот же ключ)
# 2. DuckDuckGo (∞ бесплатно, без ключа)
# 3. Tavily (резерв, 1000 req/мес бесплатно)
# ============================================================

TAVILY_KEY = os.getenv("TAVILY_API_KEY", "")
PERPLEXITY_KEY = os.getenv("PERPLEXITY_API_KEY", "")


async def _search_tavily(query: str, max_results: int = 3) -> list[dict]:
    """
    Уровень 1: Tavily — лучший поиск для AI-агентов.
    
    Бесплатно: 1000 запросов/мес. Возвращает чистый текст (не HTML).
    Идеально для RAG и агентов.
    """
    if not TAVILY_KEY:
        return []
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": TAVILY_KEY,
                    "query": query,
                    "max_results": max_results,
                    "search_depth": "basic",
                    "include_answer": True,
                },
            )
            data = resp.json()
            
            results = []
            # Tavily может вернуть готовый ответ
            if data.get("answer"):
                results.append({
                    "title": "Tavily AI Answer",
                    "url": "",
                    "snippet": data["answer"],
                })
            
            for item in data.get("results", [])[:max_results]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", ""),
                })
            
            if results:
                print(f"🔍 Tavily: {len(results)} результатов")
            return results
    except Exception as e:
        print(f"⚠️ Tavily: {e}")
        return []


async def _search_perplexity(query: str) -> list[dict]:
    """
    Уровень 1: Perplexity Sonar — через OpenRouter.

    Используем perplexity/sonar через OpenRouter API (тот же ключ что для LLM).
    Это обходит квоту прямого Perplexity API (401 insufficient_quota).
    """
    if not OPENROUTER_KEY:
        return []
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "perplexity/sonar",
                    "messages": [{"role": "user", "content": query}],
                    "max_tokens": 500,
                },
            )
            data = resp.json()
            
            if resp.status_code == 200 and "choices" in data:
                content = data["choices"][0]["message"]["content"]
                citations = data.get("citations", [])
                result = {
                    "title": "Perplexity Sonar (via OpenRouter)",
                    "url": citations[0] if citations else "",
                    "snippet": content,
                }
                print(f"🔍 Perplexity (OpenRouter): ответ получен")
                return [result]
            else:
                err = data.get("error", {}).get("message", "")[:60]
                print(f"⚠️ Perplexity (OpenRouter): {resp.status_code} — {err}")
    except Exception as e:
        print(f"⚠️ Perplexity (OpenRouter): {e}")
    return []


async def _search_duckduckgo(query: str, max_results: int = 3) -> list[dict]:
    """
    Уровень 2: DuckDuckGo — бесплатный fallback.

    Без API ключа, без лимитов.
    Ограничение: только Instant Answer (не полный поиск).
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            )
            data = resp.json()
            
            results = []
            if data.get("AbstractText"):
                results.append({
                    "title": data.get("Heading", ""),
                    "url": data.get("AbstractURL", ""),
                    "snippet": data["AbstractText"],
                })
            
            for topic in data.get("RelatedTopics", [])[:max_results]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append({
                        "title": topic.get("Text", "")[:80],
                        "url": topic.get("FirstURL", ""),
                        "snippet": topic.get("Text", ""),
                    })
            
            if results:
                print(f"🔍 DuckDuckGo: {len(results)} результатов")
            return results[:max_results]
    except Exception as e:
        print(f"⚠️ DuckDuckGo: {e}")
        return []


async def web_search(query: str, max_results: int = 3) -> list[dict]:
    """
    Железобетонный каскад поиска. 3 уровня:

      1. Perplexity Sonar (через OpenRouter)
      2. DuckDuckGo (∞ бесплатно, Instant Answer)
      3. Tavily (резерв, 1000 req/мес)

    Returns:
        Список {title, url, snippet}
    """
    # Уровень 1: Perplexity через OpenRouter
    results = await _search_perplexity(query)
    if results:
        return results

    # Уровень 2: DuckDuckGo (fallback)
    results = await _search_duckduckgo(query, max_results)
    if results:
        return results

    # Уровень 3: Tavily (резерв)
    results = await _search_tavily(query, max_results)
    if results:
        return results

    print(f"⚠️ Все 3 поисковика не дали результатов для: {query}")
    return []

