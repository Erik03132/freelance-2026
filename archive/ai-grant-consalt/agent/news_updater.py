import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем ключи
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'freelance-agent', '.env')
load_dotenv(dotenv_path=env_path)

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

pplx_client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")
or_client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")

def get_latest_finance_news():
    print("🔍 [News Agent]: Ищу актуальные финансовые и юридические новости РФ...")
    
    # Запрос к Perplexity
    query = "Find the 3 most important news about government grants (FSI, Skolkovo, Presidential), IT tax benefits, and business law changes in Russia for April 2026. Provide details and dates."
    
    try:
        search_res = pplx_client.chat.completions.create(
            model="sonar-pro",
            messages=[
                {"role": "system", "content": "You are a professional financial journalist in Russia. Find only verified and recent news for April 2026."},
                {"role": "user", "content": query}
            ]
        )
        raw_news = search_res.choices[0].message.content
        
        print("✍️ [News Agent]: Формирую сводки для сайта...")
        
        # Обработка через Gemini для красивого формата
        prompt = f"""
        Преврати этот текст в 3 краткие новости для сайта финансового консалтинга на русском языке.
        Верни строго JSON со списком объектов (title, category, excerpt, slug, published_at).
        
        raw_news: {raw_news}
        
        Категории: Гранты, Налоги, Законы.
        Slug должен быть на английском (транслит).
        published_at: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}
        """
        
        final_res = or_client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        
        news_data = json.loads(final_res.choices[0].message.content)
        return news_data.get("news", news_data.get("items", []))
        
    except Exception as e:
        print(f"❌ Ошибка генерации новостей: {e}")
        return []

def update_news():
    news = get_latest_finance_news()
    if not news:
        return
        
    # Путь к локальному JSON (как временное решение для синхронизации с фронтендом)
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'web', 'public', 'news_feed.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
        
    print(f"✅ Обновлено {len(news)} новостей. Файл: {output_path}")

if __name__ == "__main__":
    update_news()
