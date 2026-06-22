"""
Генератор законодательных инициатив — сердце Senator AI.
На вход: дайджест новостей + база знаний.
На выход: аргументированная инициатива дня.
"""
import os
import json
import sys
from datetime import datetime

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(AGENT_DIR, "agent"))

from llm_cascade import call_llm_structured

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
HISTORY_PATH = os.path.join(DATA_DIR, "initiatives_history.json")
KB_DIR = os.path.join(DATA_DIR, "bashkortostan_kb")

# --- Загрузка базы знаний о Башкортостане ---
def _load_kb():
    """Загружает все .md файлы из базы знаний в единый контекст."""
    parts = []
    if os.path.exists(KB_DIR):
        for fname in sorted(os.listdir(KB_DIR)):
            if fname.endswith(".md"):
                fpath = os.path.join(KB_DIR, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    parts.append(f"--- {fname} ---\n{f.read()}")
    return "\n\n".join(parts)


def _load_history():
    """Загружает историю инициатив для проверки на дубли."""
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_to_history(initiative):
    """Сохраняет инициативу в историю."""
    history = _load_history()
    history.append(initiative)
    # Храним последние 365 инициатив (год)
    history = history[-365:]
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def _load_senator_profile():
    """Загружает профиль сенатора."""
    profile_path = os.path.join(DATA_DIR, "senator_profile.md")
    if os.path.exists(profile_path):
        with open(profile_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Сенатор от Республики Башкортостан. Комитеты: все."


# === Системный промпт генератора ===
GENERATOR_SYSTEM_PROMPT = """
ТЫ: Мустай — AI-аналитик и помощник сенатора в Совете Федерации 
Федерального Собрания Российской Федерации. 
Сенатор представляет Республику Башкортостан, но работает на ФЕДЕРАЛЬНОМ уровне.

ЗАДАЧА: На основе предоставленного дайджеста новостей, законодательных изменений 
и мирового опыта — сгенерировать ОДНУ конкретную, реализуемую ФЕДЕРАЛЬНУЮ 
законодательную инициативу.

ВАЖНО: Инициативы должны быть ФЕДЕРАЛЬНОГО масштаба — для всей России, а не 
только для Башкортостана. Башкортостан — это малая родина сенатора, но его 
законотворческая деятельность направлена на улучшение жизни всех граждан РФ.

ТРЕБОВАНИЯ К ИНИЦИАТИВЕ:
1. МАСШТАБ — федеральный уровень, для всей страны
2. КОНКРЕТНОСТЬ — не общие слова, а конкретный механизм (какой НПА, какие нормы)
3. ОБОСНОВАНИЕ — минимум 3 аргумента с цифрами или ссылками на прецеденты
4. ПРЕЦЕДЕНТЫ — примеры из регионов РФ или других стран
5. РЕАЛИЗУЕМОСТЬ — инициатива должна быть проходимой политически
6. УНИКАЛЬНОСТЬ — не повторять ранее предложенные инициативы

КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО:
- Выдумывать статистику и цифры
- Предлагать изменения в Конституцию (за исключением крайних случаев)
- Генерировать популистские или нереализуемые предложения
- Повторять инициативы из истории
- Сводить федеральную инициативу исключительно к одному региону

ФОРМАТ ОТВЕТА (СТРОГО СОБЛЮДАТЬ):

🏛️ ИНИЦИАТИВА ДНЯ — {дата}

📋 НАЗВАНИЕ:
{Краткое название — до 15 слов}

🎯 СУТЬ:
{2-3 предложения: что конкретно предлагается на федеральном уровне}

📊 ОБОСНОВАНИЕ:
1. {Аргумент 1 — общероссийская статистика или факт}
2. {Аргумент 2 — опыт региона или зарубежной страны}
3. {Аргумент 3 — экономический/социальный эффект для страны}

🌍 ПРЕЦЕДЕНТЫ:
- {Регион/Страна}: {что сделали → какой результат}
- {Регион/Страна}: {что сделали → какой результат}

🏗️ МЕХАНИЗМ РЕАЛИЗАЦИИ:
- Тип НПА: {ФЗ / Постановление Правительства / Поправка к ФЗ №...}
- Комитет СФ: {через какой комитет проводить}
- Сроки: {примерные сроки разработки и принятия}

💰 ФИНАНСОВАЯ ОЦЕНКА:
- Стоимость: {ориентир}
- Источник финансирования: {федеральный бюджет / ГЧП / нет затрат}
- Ожидаемый эффект: {конкретный, для всей страны}

📎 ИСТОЧНИКИ:
- {ссылка или название документа 1}
- {ссылка или название документа 2}

⚡ ОЦЕНКА:
- Актуальность: {X}/10
- Реализуемость: {X}/10
- Политическая проходимость: {X}/10
- Общероссийский импакт: {X}/10
"""


def generate_initiative(news_digest, deep_search_context="", focus_topic=None):
    """
    Генерирует инициативу дня на основе дайджеста.
    
    Args:
        news_digest: Строка с дайджестом новостей (из RSS + скана)
        deep_search_context: Доп. контекст из deep search
        focus_topic: Опциональная фокусная тема от сенатора
    
    Returns:
        dict: {
            "text": str,       # Полный текст инициативы
            "title": str,      # Краткое название
            "date": str,       # Дата генерации
            "focus": str|None  # Фокусная тема
        }
    """
    kb_context = _load_kb()
    senator_profile = _load_senator_profile()
    history = _load_history()

    # Формируем список уже предложенных тем (для антидублей)
    past_titles = "\n".join([
        f"- [{h.get('date', '?')}] {h.get('title', 'без названия')}"
        for h in history[-30:]  # Последние 30
    ]) if history else "Пока не было."

    today = datetime.now().strftime("%d %B %Y")

    user_prompt = f"""
ДАТА: {today}

ПРОФИЛЬ СЕНАТОРА:
{senator_profile}

БАЗА ЗНАНИЙ О БАШКОРТОСТАНЕ:
{kb_context[:4000]}

ДАЙДЖЕСТ НОВОСТЕЙ (за последние 48 часов):
{news_digest[:5000]}

{"РЕЗУЛЬТАТЫ ГЛУБОКОГО ПОИСКА:" + chr(10) + deep_search_context[:3000] if deep_search_context else ""}

{"ФОКУСНАЯ ТЕМА ОТ СЕНАТОРА: " + focus_topic if focus_topic else "Фокусная тема не задана — выбери самую актуальную на основе дайджеста."}

РАНЕЕ ПРЕДЛОЖЕННЫЕ ИНИЦИАТИВЫ (НЕ ПОВТОРЯТЬ):
{past_titles}

Сгенерируй инициативу дня. СТРОГО следуй формату из системного промпта.
"""

    result_text = call_llm_structured(
        GENERATOR_SYSTEM_PROMPT, user_prompt, temperature=0.6
    )

    if not result_text or "ИНИЦИАТИВА ДНЯ" not in result_text:
        print("⚠️ LLM не сгенерировал инициативу в нужном формате. Повторная попытка...")
        result_text = call_llm_structured(
            GENERATOR_SYSTEM_PROMPT,
            user_prompt + "\n\nВАЖНО: Ответь СТРОГО в формате, начиная с '🏛️ ИНИЦИАТИВА ДНЯ'!",
            temperature=0.7,
        )

    # Извлекаем название инициативы
    title = "Без названия"
    for line in result_text.split("\n"):
        if "НАЗВАНИЕ:" in line:
            title = line.split("НАЗВАНИЕ:")[-1].strip()
            break

    initiative = {
        "text": result_text,
        "title": title,
        "date": datetime.now().isoformat(),
        "focus": focus_topic,
    }

    # Сохраняем в историю
    _save_to_history(initiative)

    print(f"✅ Инициатива сгенерирована: {title}")
    return initiative


def generate_on_topic(topic):
    """
    Генерирует инициативу по конкретной теме (по запросу сенатора).
    Использует deep search для обогащения.
    """
    try:
        from scanner.deep_search import deep_search
        search_result = deep_search(topic, context="legislation")
        context = search_result.get("combined_context", "")
    except Exception as e:
        print(f"⚠️ Deep search недоступен: {e}")
        context = ""

    return generate_initiative(
        news_digest=f"Сенатор запросил инициативу по теме: {topic}",
        deep_search_context=context,
        focus_topic=topic,
    )


if __name__ == "__main__":
    print("🏛️ Тестовая генерация инициативы...")
    test_digest = """
    1. Госдума рассматривает законопроект об ограничении использования пестицидов в сельском хозяйстве.
    2. Татарстан запустил программу «Цифровой фермер» — подача заявок на субсидии онлайн.
    3. Правительство выделило 50 млрд руб. на развитие сельских территорий.
    4. В Башкортостане зафиксирован отток молодёжи из сельских районов — 2% в год.
    5. ОЭСР опубликовала доклад о лучших практиках поддержки фермеров в развитых странах.
    """
    result = generate_initiative(test_digest)
    print("\n" + result["text"])
