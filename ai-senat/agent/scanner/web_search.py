"""
Бесплатный веб-поиск через DuckDuckGo HTML и Google (без API-ключей).
Фоллбэк для Perplexity/Tavily когда ключи не заданы.
"""
import re
import httpx
from urllib.parse import quote_plus


def search_ddg(query, max_results=5):
    """
    Поиск через DuckDuckGo HTML (без API-ключа).
    
    Returns:
        list[dict]: [{title, url, snippet}, ...]
    """
    try:
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        resp = httpx.get(url, headers=headers, timeout=15, follow_redirects=True)
        
        if resp.status_code != 200:
            print(f"⚠️ DDG HTTP {resp.status_code}")
            return []
        
        html = resp.text
        results = []
        
        # Парсим результаты из HTML
        # DuckDuckGo HTML результаты в <a class="result__a"> и <a class="result__snippet">
        links = re.findall(
            r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
            html, re.DOTALL
        )
        snippets = re.findall(
            r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
            html, re.DOTALL
        )
        
        for i, (href, title) in enumerate(links[:max_results]):
            # Чистим HTML-теги
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            clean_snippet = ""
            if i < len(snippets):
                clean_snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()
            
            # DDG оборачивает URL в редирект
            actual_url = href
            if "uddg=" in href:
                m = re.search(r'uddg=([^&]+)', href)
                if m:
                    from urllib.parse import unquote
                    actual_url = unquote(m.group(1))
            
            results.append({
                "title": clean_title,
                "url": actual_url,
                "snippet": clean_snippet,
            })
        
        return results
        
    except Exception as e:
        print(f"❌ DDG search error: {e}")
        return []


def search_web_free(query, max_results=5):
    """
    Комбинированный бесплатный поиск.
    Возвращает форматированный контекст для LLM.
    """
    results = search_ddg(query, max_results)
    
    if not results:
        return ""
    
    parts = [f"[WEB SEARCH: {query}]"]
    for i, r in enumerate(results, 1):
        parts.append(f"{i}. **{r['title']}**")
        if r['snippet']:
            parts.append(f"   {r['snippet']}")
        parts.append(f"   URL: {r['url']}")
    
    return "\n".join(parts)


if __name__ == "__main__":
    print("🔍 Тест поиска DuckDuckGo...")
    results = search_ddg("законодательные инициативы регионов России 2026")
    for r in results:
        print(f"\n  📋 {r['title']}")
        print(f"     {r['snippet'][:100]}")
        print(f"     {r['url']}")
    
    print(f"\n📊 Найдено: {len(results)} результатов")
