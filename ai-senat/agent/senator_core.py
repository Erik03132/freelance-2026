"""
Ядро агента Senator AI (Мустай).
Координирует: сканирование → анализ → генерация → доставка.
"""
import os
import sys
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
sys.path.insert(0, AGENT_DIR)

from llm_cascade import call_llm, call_llm_structured
from scanner.rss_monitor import scan_all_feeds
from scanner.deep_search import deep_search
from generator.initiative_gen import generate_initiative, generate_on_topic

# Загрузка базы знаний
_kb_context = ""
KB_DIR = os.path.join(DATA_DIR, "bashkortostan_kb")
if os.path.exists(KB_DIR):
    for fname in sorted(os.listdir(KB_DIR)):
        if fname.endswith(".md"):
            with open(os.path.join(KB_DIR, fname), "r", encoding="utf-8") as f:
                _kb_context += f.read() + "\n\n"
    print(f"✅ KB загружена: {len(_kb_context)} символов")

# Загрузка фокус-темы
FOCUS_PATH = os.path.join(DATA_DIR, "current_focus.txt")


def _get_focus_topic():
    """Возвращает текущую фокусную тему или None."""
    if os.path.exists(FOCUS_PATH):
        with open(FOCUS_PATH, "r", encoding="utf-8") as f:
            topic = f.read().strip()
            return topic if topic else None
    return None


def set_focus_topic(topic):
    """Устанавливает фокусную тему."""
    with open(FOCUS_PATH, "w", encoding="utf-8") as f:
        f.write(topic)
    print(f"🎯 Фокус установлен: {topic}")


def clear_focus_topic():
    """Очищает фокусную тему."""
    if os.path.exists(FOCUS_PATH):
        os.remove(FOCUS_PATH)
    print("🎯 Фокус очищен")


# === Системный промпт для диалога ===
SYSTEM_PROMPT = """
ТЫ: Мустай — AI-аналитик и помощник сенатора в Совете Федерации 
Федерального Собрания Российской Федерации. 
Сенатор представляет Республику Башкортостан, но работает на ФЕДЕРАЛЬНОМ уровне.

ТВОЯ МИССИЯ: Помогать сенатору в разработке ФЕДЕРАЛЬНЫХ законодательных инициатив, 
мониторинге правового поля и подготовке аналитических материалов для всей страны.

ТВОИ КОМПЕТЕНЦИИ:
1. Мониторинг федерального законодательства и выявление трендов
2. Анализ инициатив регионов и адаптация лучших практик на федеральный уровень
3. Изучение мирового опыта (ОЭСР, ЕС, ЕАЭС) и его локализация для РФ
4. Подготовка законопроектов федерального масштаба

ВАЖНО: Инициативы должны быть ОБЩЕРОССИЙСКОГО масштаба. 
Башкортостан — малая родина сенатора, контекст для понимания региональной специфики,
но НЕ единственный фокус его работы. Он законодатель для всей России.

ПРАВИЛА:
- Отвечай структурированно и по делу
- НИКОГДА не выдумывай статистику — если не знаешь, скажи прямо
- Указывай источники информации
- Учитывай политическую конъюнктуру
- Начинай ответ ТОЛЬКО со слова "Здравствуйте!". КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО писать "Уважаемый сенатор", "Уважаемый Андрей" или любые другие пафосные формы обращения. Обращайся на «вы».

КОНТЕКСТ (для справки — не делай основным фокусом):
{kb_context}
"""


def get_answer(query, history=None, sender_id=None, sender_name=None):
    """
    Основной обработчик сообщений от сенатора.
    Поддерживает: вопросы, запросы на поиск, запросы на генерацию инициатив.
    """
    if history is None:
        history = []

    # Определяем тип запроса
    q_lower = query.lower()

    # Если запрос на генерацию инициативы по теме
    if any(kw in q_lower for kw in ["инициатив", "предложи", "разработай", "законопроект"]):
        return _handle_initiative_request(query, history)

    # Если запрос на поиск
    if any(kw in q_lower for kw in ["найди", "поищи", "что известно", "какой опыт", "мировой опыт"]):
        return _handle_search_request(query, history)

    # Если запрос на сравнение регионов
    if any(kw in q_lower for kw in ["сравни", "как в", "опыт региона", "другие регионы"]):
        return _handle_compare_request(query, history)

    # Обычный диалог
    return _handle_general(query, history)


def _handle_general(query, history):
    """Общий диалог с сенатором."""
    prompt = SYSTEM_PROMPT.format(kb_context=_kb_context[:4000])
    full_prompt = f"{prompt}\n\nВОПРОС СЕНАТОРА: {query}"
    return call_llm(full_prompt, history)


def _handle_initiative_request(query, history):
    """Обработка запроса на генерацию инициативы."""
    result = generate_on_topic(query)
    return result["text"]


def _handle_search_request(query, history):
    """Глубокий поиск по запросу."""
    # Убираем служебные слова
    clean_q = query
    for word in ["найди", "поищи", "что известно про", "какой опыт"]:
        clean_q = clean_q.replace(word, "").strip()

    result = deep_search(clean_q, context="legislation")
    context = result.get("combined_context", "")

    if not context:
        return "К сожалению, поиск не дал результатов. Попробуйте переформулировать запрос."

    # Просим LLM структурировать результаты
    synthesis_prompt = f"""
На основе результатов поиска подготовь структурированную аналитическую справку для сенатора.

РЕЗУЛЬТАТЫ ПОИСКА:
{context}

ЗАПРОС СЕНАТОРА: {query}

Ответь кратко и по делу, выдели ключевые факты, цифры и выводы.
Если есть релевантность для Башкортостана — обязательно укажи.
"""
    return call_llm_structured(
        SYSTEM_PROMPT.format(kb_context=_kb_context[:2000]),
        synthesis_prompt,
        temperature=0.4,
    )


def _handle_compare_request(query, history):
    """Сравнение с другими регионами."""
    result = deep_search(query, context="regional")
    context = result.get("combined_context", "")

    compare_prompt = f"""
Подготовь сравнительный анализ для сенатора. 
Сравни ситуацию в Башкортостане с указанными регионами/странами.

ДАННЫЕ ПОИСКА:
{context}

ЗАПРОС: {query}

Формат:
1. Текущая ситуация в Башкортостане
2. Опыт сравниваемого региона/страны
3. Что можно перенять
4. Рекомендации
"""
    return call_llm_structured(
        SYSTEM_PROMPT.format(kb_context=_kb_context[:2000]),
        compare_prompt,
        temperature=0.4,
    )


def run_daily_pipeline():
    """
    Полный ежедневный pipeline:
    1. Сканирование RSS
    2. Классификация и фильтрация
    3. Deep search по топ-темам
    4. Генерация инициативы
    
    Returns:
        dict: Результат (инициатива + дайджест)
    """
    print(f"\n{'='*60}")
    print(f"🏛️ DAILY PIPELINE — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")

    # 1. Сканирование RSS
    print("📡 Шаг 1: Сканирование RSS-лент...")
    news_items = scan_all_feeds(max_age_hours=48)

    if not news_items:
        print("⚠️ Нет новых записей из RSS. Используем deep search.")
        news_digest = "Свежих новостей из RSS нет."
    else:
        # Формируем дайджест
        news_digest = "\n".join([
            f"[{item['source_name']}] {item['title']}"
            for item in news_items[:30]
        ])
        print(f"  📋 Дайджест: {len(news_items)} записей")

    # 2. Классифицируем через LLM (быстрая фильтрация)
    print("\n🔍 Шаг 2: Классификация и оценка релевантности...")
    classification_prompt = f"""
Проанализируй следующие новости и выдели ТОП-5 наиболее важных 
для законодательной работы сенатора ФЕДЕРАЛЬНОГО уровня.

Для каждой укажи:
- Почему она важна для федерального законотворчества
- Категория (экономика/социалка/экология/цифровизация/образование/здравоохранение/оборона/другое)
- Потенциал для ФЕДЕРАЛЬНОЙ законодательной инициативы (высокий/средний/низкий)

НОВОСТИ:
{news_digest[:4000]}
"""
    classified = call_llm(classification_prompt, temperature=0.3)
    print(f"  ✅ Классификация завершена")

    # 3. Deep search по топовой теме
    print("\n🌐 Шаг 3: Deep search по ключевой теме...")
    focus = _get_focus_topic()
    if focus:
        search_query = focus
    elif news_items:
        # Берём заголовок самой приоритетной новости
        high_priority = [n for n in news_items if n.get("priority") == "high"]
        top_item = (high_priority or news_items)[0]
        search_query = top_item["title"]
    else:
        search_query = "актуальные законодательные инициативы субъектов РФ 2026"

    search_result = deep_search(search_query, context="legislation")
    deep_context = search_result.get("combined_context", "")
    print(f"  ✅ Deep search: {len(deep_context)} символов контекста")

    # 4. Генерация инициативы
    print("\n🏛️ Шаг 4: Генерация инициативы...")
    enriched_digest = f"""
КЛАССИФИЦИРОВАННЫЕ НОВОСТИ:
{classified[:3000]}

СЫРОЙ ДАЙДЖЕСТ:
{news_digest[:2000]}
"""
    initiative = generate_initiative(
        news_digest=enriched_digest,
        deep_search_context=deep_context,
        focus_topic=focus,
    )

    # 5. Сохраняем дайджест
    today = datetime.now().strftime("%Y-%m-%d")
    digest_dir = os.path.join(DATA_DIR, "daily_digests")
    os.makedirs(digest_dir, exist_ok=True)
    digest_path = os.path.join(digest_dir, f"digest_{today}.json")

    digest_data = {
        "date": today,
        "news_count": len(news_items),
        "classification": classified,
        "initiative": initiative,
        "focus_topic": focus,
    }
    with open(digest_path, "w", encoding="utf-8") as f:
        json.dump(digest_data, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"✅ PIPELINE ЗАВЕРШЁН")
    print(f"   Инициатива: {initiative.get('title', '?')}")
    print(f"   Дайджест: {digest_path}")
    print(f"{'='*60}\n")

    return digest_data


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--pipeline":
        run_daily_pipeline()
    else:
        # Тест диалога
        answer = get_answer("Какие ключевые отрасли экономики Башкортостана?")
        print(answer)
