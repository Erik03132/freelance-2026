"""
Marina Core Engine — Мозг Ульяны (AI Grant Consult)
Каскад: FAQ → Vector RAG → Perplexity (optional) → Gemini 2.0 → OpenRouter fallback
"""
import os
import time
import json
import requests
from dotenv import load_dotenv

# Абсолютные пути
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'), override=True)
if not os.getenv("GEMINI_API_KEY"):
    load_dotenv(os.path.join(BASE_DIR, '..', 'freelance-agent', '.env'), override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# --- Загрузка knowledge base при старте ---
KNOWLEDGE_DIR = os.path.join(BASE_DIR, 'knowledge-base')
NAVIGATOR_PATH = os.path.join(KNOWLEDGE_DIR, 'navigator.md')
LAWS_DIR = os.path.join(KNOWLEDGE_DIR, 'laws')

# Собираем все законы в единый контекст
_laws_context = ""
_laws_count = 0
if os.path.isdir(LAWS_DIR):
    for fname in sorted(os.listdir(LAWS_DIR)):
        if fname.endswith('.md'):
            fpath = os.path.join(LAWS_DIR, fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                _laws_context += f"\n\n--- {fname} ---\n" + f.read()
                _laws_count += 1
    print(f"✅ Laws knowledge загружен: {_laws_count} документов, {len(_laws_context)} символов")

# Навигатор
_navigator = ""
if os.path.exists(NAVIGATOR_PATH):
    with open(NAVIGATOR_PATH, 'r', encoding='utf-8') as f:
        _navigator = f.read()
    print(f"✅ Navigator загружен: {len(_navigator)} символов")

# --- Gemini ---
import google.generativeai as genai
genai.configure(api_key=GEMINI_API_KEY)

MARINA_SYSTEM_PROMPT = f"""Ты — Ульяна, топовый эксперт по налогам, грантам и банкротству в РФ.
Тебя зовут УЛЬЯНА. НЕ называй себя другими именами.
Ты работаешь в компании AI Grant Consult.

КРИТИЧЕСКИ ВАЖНО — ПРАВИЛА ОТВЕТОВ:
1. ВСЕГДА ссылайся на конкретные нормативные акты (статья НК РФ, ФЗ, ПП РФ, приказ Минцифры).
   Пример: «Согласно п. 1.15 ст. 284 НК РФ, ставка налога на прибыль для ИТ-компаний — 5%».
2. Если ты не знаешь точную статью — скажи «рекомендую уточнить у юриста номер статьи», НЕ выдумывай.
3. Мягко исправляй ошибки пользователя (например, «элигранты» → «гранты»).
4. В конце сложных ответов предлагай оставить номер телефона: «Оставьте номер — наш юрист перезвонит и уточнит детали под ваш кейс».
5. Говори уверенно, но доброжелательно. Не отправляй «к бухгалтеру».

НАВИГАТОР ПО БАЗЕ ЗНАНИЙ:
{_navigator}

БАЗА ЗАКОНОВ И НОРМАТИВОВ:
{_laws_context[:8000]}
"""

marina_model = genai.GenerativeModel(
    "gemini-2.0-flash",
    system_instruction=MARINA_SYSTEM_PROMPT
)

# --- Perplexity ---
def perplexity_research(query: str) -> str:
    """Агент-Детектив: ищет свежие законы РФ через Perplexity (real-time)."""
    if not PERPLEXITY_API_KEY:
        return "Perplexity API не настроен."

    print("🔍 [Perplexity Agent]: Ищу актуальную информацию...")
    try:
        from openai import OpenAI
        pplx_client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")
        response = pplx_client.chat.completions.create(
            model="sonar-pro",
            messages=[
                {"role": "system", "content": "You are a legal researcher. Find the most up to date russian laws, tax regulations, and grants regarding the user query. Always cite sources with article numbers."},
                {"role": "user", "content": query}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"⚠️ Perplexity error: {e}")
        return f"Perplexity временно недоступен."

# --- Определяем, нужен ли Perplexity ---
FRESHNESS_KEYWORDS = ["2026", "сейчас", "актуальн", "свежи", "новы", "последн", "изменен", "обновлен", "текущ"]

def needs_fresh_data(query: str) -> bool:
    """Определяем, нужен ли real-time поиск (Perplexity) или хватит локальной базы."""
    q = query.lower()
    return any(kw in q for kw in FRESHNESS_KEYWORDS)

# --- FAQ Router ---
from faq_router import FAQRouter
faq = FAQRouter()

# --- Vector DB ---
from vector_db import MarinaVectorDB
vdb = MarinaVectorDB()

# --- Graph RAG ---
from graph_rag import get_legal_graph
legal_graph = get_legal_graph()

def fetch_local_context(query: str) -> str:
    """Vector RAG из Neon DB."""
    if not vdb.enabled:
        return "Внутренняя база (Neon) временно недоступна."
    print(f"📚 [Vector Search]: Ищу в Neon DB...")
    try:
        results = vdb.search(query, limit=5)
        if results:
            return "\n\n".join([
                f"📦 [{r['metadata'].get('source', 'База знаний')}]: {r['content']}"
                for r in results
            ])
    except Exception as e:
        print(f"⚠️ Vector search error: {e}")
    return "В векторной базе специфических документов не найдено."

# --- LLM Cascade ---
def marina_judge(query: str, web_context: str, local_context: str, graph_context: str = "", history=None) -> str:
    """Каскад LLM: Gemini 2.0 → OpenRouter fallback."""
    
    # Попытка 1: Gemini 2.0
    try:
        print("⚖️ [Marina LLM]: Gemini 2.0 Flash...")
        chat = marina_model.start_chat(history=history or [])
        
        prompt = f"""
🏛️ НОРМАТИВНЫЙ КОНТЕКСТ (Graph RAG — связанные нормы):
{graph_context if graph_context else 'Связанных норм не найдено.'}

КОНТЕКСТ ИЗ ИНТЕРНЕТА (свежие данные):
{web_context}

КОНТЕКСТ ИЗ НАШЕЙ БАЗЫ (Vector RAG):
{local_context}

ВОПРОС КЛИЕНТА: {query}

ВАЖНО: Используй данные из НОРМАТИВНОГО КОНТЕКСТА для точного цитирования статей и пунктов НПА!
"""
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        print(f"⚠️ Gemini error: {e}")

    # Попытка 2: OpenRouter
    if OPENROUTER_API_KEY:
        try:
            print("🔄 [Marina LLM]: Фолбэк → OpenRouter...")
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "google/gemini-2.0-flash-001",
                    "messages": [
                        {"role": "system", "content": MARINA_SYSTEM_PROMPT[:4000]},
                        {"role": "user", "content": f"Контекст: {local_context[:2000]}\n\nВопрос: {query}"}
                    ],
                    "temperature": 0.3
                },
                timeout=20
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"⚠️ OpenRouter error: {e}")

    return "К сожалению, все AI-модели временно недоступны. Попробуйте повторить вопрос через минуту."


# --- Главный пайплайн ---
def main_rag_pipeline(query: str, history=None):
    """FAQ → Graph RAG → Vector → Perplexity (optional) → LLM → Self-learning."""
    
    # 1. FAQ горячий кэш
    cached_answer = faq.search_fast_lane(query)
    if cached_answer:
        return cached_answer

    # 2. Graph RAG — нормативный граф (быстрый, локальный)
    print("🏛️ [Graph RAG]: Поиск в нормативном графе...")
    graph_result = legal_graph.search(query)
    graph_context = graph_result.get("context_block", "")
    if graph_result.get("total_nodes", 0) > 0:
        print(f"   ✅ Найдено: {len(graph_result['primary_nodes'])} прямых + {len(graph_result['linked_nodes'])} связанных узлов")
    else:
        print("   ℹ️ В графе релевантных норм не найдено")

    # 3. Vector RAG (всегда)
    local_data = fetch_local_context(query)
    
    # 4. Perplexity — только если нужна свежесть
    if needs_fresh_data(query):
        web_data = perplexity_research(query)
    else:
        web_data = "Данные не запрашивались (вопрос не требует проверки актуальности)."
    
    # 5. LLM Каскад (с графовым контекстом)
    final_answer = marina_judge(query, web_data, local_data, graph_context, history)
    
    # 5. Самообучение (с фильтром качества)
    if len(final_answer) > 100 and "недоступн" not in final_answer.lower():
        faq.learn_new_answer(query, final_answer)
    
    # 6. Hermes Trace
    trace_path = os.path.join(BASE_DIR, 'data', 'traces.json')
    trace_data = {
        "timestamp": time.time(),
        "query": query,
        "answer_length": len(final_answer),
        "used_perplexity": needs_fresh_data(query),
        "web_context_length": len(web_data) if web_data else 0
    }
    try:
        traces = []
        if os.path.exists(trace_path):
            with open(trace_path, 'r', encoding='utf-8') as f:
                traces = json.load(f)
        traces.append(trace_data)
        with open(trace_path, 'w', encoding='utf-8') as f:
            json.dump(traces[-200:], f, ensure_ascii=False, indent=2)
    except:
        pass

    return final_answer


if __name__ == "__main__":
    test_query = "Какие льготы по налогу на прибыль для ИТ-компаний в 2026 году?"
    print(f"\nТест: {test_query}\n")
    answer = main_rag_pipeline(test_query)
    print(f"\nОтвет:\n{answer}")
