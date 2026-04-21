"""
Deep Search — глубокий контекстный поиск через Perplexity и Tavily API.
Используется для обогащения инициатив фактами и мировым опытом.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def search_perplexity(query, focus="internet", max_tokens=1500):
    """
    Поиск через Perplexity API (sonar model).
    
    Args:
        query: Поисковый запрос
        focus: Тип поиска (internet, academic, news)
        max_tokens: Максимум токенов в ответе
    
    Returns:
        dict: {"answer": str, "sources": list[str]} или None
    """
    if not PERPLEXITY_API_KEY:
        print("⚠️ PERPLEXITY_API_KEY не задан")
        return None

    try:
        resp = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "sonar",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Ты — аналитик-эксперт по законодательству и государственному управлению. "
                            "Отвечай структурированно, с цифрами и ссылками на источники. "
                            "Фокусируйся на фактах, статистике и конкретных примерах из практики."
                        ),
                    },
                    {"role": "user", "content": query},
                ],
                "max_tokens": max_tokens,
            },
            timeout=30,
        )
        data = resp.json()
        if "choices" in data:
            answer = data["choices"][0]["message"]["content"]
            sources = data.get("citations", [])
            return {"answer": answer, "sources": sources}
        else:
            print(f"⚠️ Perplexity error: {data.get('error', data)}")
            return None
    except Exception as e:
        print(f"❌ Perplexity exception: {e}")
        return None


def search_tavily(query, search_depth="advanced", max_results=5):
    """
    Поиск через Tavily API (оптимизирован для AI-агентов).
    
    Args:
        query: Поисковый запрос
        search_depth: "basic" или "advanced"
        max_results: Количество результатов
    
    Returns:
        dict: {"answer": str, "results": list[dict]} или None
    """
    if not TAVILY_API_KEY:
        print("⚠️ TAVILY_API_KEY не задан")
        return None

    try:
        resp = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "search_depth": search_depth,
                "max_results": max_results,
                "include_answer": True,
                "include_raw_content": False,
            },
            timeout=30,
        )
        data = resp.json()
        if "results" in data:
            return {
                "answer": data.get("answer", ""),
                "results": [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "content": r.get("content", "")[:500],
                    }
                    for r in data["results"]
                ],
            }
        else:
            print(f"⚠️ Tavily error: {data}")
            return None
    except Exception as e:
        print(f"❌ Tavily exception: {e}")
        return None


def deep_search(query, context="legislation"):
    """
    Комбинированный глубокий поиск: Perplexity + Tavily.
    Возвращает объединённый результат.
    
    Args:
        query: Запрос
        context: Контекст (legislation, global_experience, regional)
    
    Returns:
        dict: {
            "perplexity": {"answer": str, "sources": list},
            "tavily": {"answer": str, "results": list},
            "combined_context": str  # Готовый контекст для LLM
        }
    """
    # Обогащаем запрос контекстом
    enriched_queries = {
        "legislation": f"Российское законодательство: {query}. Укажи номера ФЗ, даты принятия, ключевые нормы.",
        "global_experience": f"Мировой опыт и лучшие практики: {query}. Примеры конкретных стран, результаты внедрения.",
        "regional": f"Региональные инициативы субъектов РФ: {query}. Какие регионы уже внедрили, результаты.",
        "bashkortostan": f"Республика Башкортостан: {query}. Специфика региона, текущая ситуация.",
    }
    enriched = enriched_queries.get(context, query)

    result = {
        "perplexity": None,
        "tavily": None,
        "combined_context": "",
    }

    # Perplexity
    pp = search_perplexity(enriched)
    if pp:
        result["perplexity"] = pp

    # Tavily
    tv = search_tavily(query)
    if tv:
        result["tavily"] = tv

    # Собираем combined context для LLM
    parts = []
    if pp and pp.get("answer"):
        parts.append(f"[PERPLEXITY SEARCH]\n{pp['answer']}")
        if pp.get("sources"):
            parts.append("Источники: " + ", ".join(pp["sources"][:5]))
    if tv and tv.get("answer"):
        parts.append(f"\n[TAVILY SEARCH]\n{tv['answer']}")
        if tv.get("results"):
            for r in tv["results"][:3]:
                parts.append(f"  - {r['title']}: {r['content'][:200]}")

    # ФОЛЛБЭК: бесплатный поиск через DuckDuckGo если ничего не нашли
    if not parts:
        try:
            from scanner.web_search import search_web_free
            ddg_context = search_web_free(enriched, max_results=7)
            if ddg_context:
                parts.append(ddg_context)
                print(f"  🦆 DDG fallback: найдены результаты")
        except Exception as e:
            print(f"  ⚠️ DDG fallback failed: {e}")

    result["combined_context"] = "\n".join(parts)
    return result


if __name__ == "__main__":
    print("🔍 Тест Deep Search...")
    r = deep_search(
        "налоговые льготы для IT-компаний в регионах России 2025-2026",
        context="regional",
    )
    if r["combined_context"]:
        print(r["combined_context"][:2000])
    else:
        print("⚠️ Поиск не дал результатов (проверьте API-ключи)")
