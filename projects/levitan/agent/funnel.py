"""
Levitan funnel — детерминированная логика без LLM (fast-path).
Чистый модуль: только stdlib, без зависимости от livekit/LLM.
Конфиг данных — funnel_config.json (цены, паттерны ДА/НЕТ/количество).
Это SSoT для AVM-2 (переиспользуемый voice_manager).
"""

import json
import re
from difflib import SequenceMatcher
from pathlib import Path

_CONFIG_PATH = Path(__file__).resolve().parent / "funnel_config.json"
_CONFIG = {}


def _load_config():
    global _CONFIG
    try:
        _CONFIG = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as e:  # pragma: no cover
        print(f"[FUNNEL] config load error: {e}")
        _CONFIG = {
            "intents": [],
            "placeholders": [],
            "price_tiers": [
                {"min": 1000, "price": 75},
                {"min": 301, "price": 80},
                {"min": 101, "price": 85},
                {"min": 0, "price": 90},
            ],
            "regex": {
                "neg_full": "(нет|не надо|не интересно|не хочу|отказ[а-я]*)",
                "delivery_confirm": "\\b(да|прежнее|подтверждаю|верно|точно|правильно|хорошо)\\b",
                "pos_full": "(да|да да|конечно|интересно|беру|хорошо|ну да|да интересно|да ладно|ну конечно)",
                "quantity": "(\\d+)\\s*(?:голов|цыпл)",
            },
        }
    return _CONFIG


_load_config()

PRICE_TIERS = _CONFIG["price_tiers"]
NEG_PATTERN = _CONFIG["regex"]["neg_full"]
DELIVERY_CONFIRM_PATTERN = _CONFIG["regex"]["delivery_confirm"]
POS_PATTERN = _CONFIG["regex"]["pos_full"]
QTY_REGEX = _CONFIG["regex"]["quantity"]
INTENTS = _CONFIG.get("intents", [])
PLACEHOLDERS = _CONFIG.get("placeholders", [])
_pi = [0]

_FAQ_CACHE_PATH = (
    Path(__file__).resolve().parent.parent / "docs" / "ANGELLA_BROILERS_FAQ_CACHE.json"
)
_FAQ_CACHE = {}
try:
    _FAQ_CACHE = {
        k: v
        for k, v in json.loads(_FAQ_CACHE_PATH.read_text(encoding="utf-8")).items()
        if not k.startswith("_")
    }
    print(f"[FUNNEL] FAQ cache loaded: {len(_FAQ_CACHE)} triggers")
except Exception as e:  # pragma: no cover
    print(f"[FUNNEL] FAQ cache load error: {e}")

# Устанавливается из levitan_agent.py после определения save_lead (избегаем circular import)
save_lead_fn = None


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[ёй]", lambda m: {"ё": "е", "й": "и"}.get(m.group(), m.group()), text)
    text = re.sub(r"[^а-я0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


_QUESTION_MARKERS = re.compile(
    r"^(?:а |ну |так |у |мне )?"
    r"(сколько|как|какой|какая|какие|какое|когда|где|куда|почему|зачем|"
    r"есть ли|можно|работает|работаете|открыто|цена|сколько стоит|доставка|"
    r"график|ваканси|адрес|можно ли|есть ли у|сколько у|какой у|какая у)"
)


def _is_question(norm: str) -> bool:
    """Вопрос на первом ходу: отдаётся LLM, а не приветствием."""
    if not norm:
        return False
    if "?" in norm or norm.endswith("?"):
        return True
    return bool(_QUESTION_MARKERS.match(norm))


_GREETING_PREFIX = re.compile(
    r"^(алло|здравствуите|здраствуите|добрыи|доброе|привет|да слушаю|слушаю вас)\b"
)


def _is_greeting_only(norm: str) -> bool:
    """Первый ход, начинающийся с приветствия -> детерминированное приветствие.
    Интенты/вопросы перехватываются РАНЬШЕ (см. порядок в _fast_path_reply),
    поэтому остаётся только «чистое» приветствие или длинная вежливая фраза.
    Всё остальное -> None -> LLM."""
    if not norm:
        return False
    return bool(_GREETING_PREFIX.match(norm))


def _price_for_qty(q: int) -> int:
    """Ступенчатая шкала цен из config: до 100→90, 101-300→85, 301-999→80, от 1000→75."""
    for tier in PRICE_TIERS:
        if q >= tier["min"]:
            return tier["price"]
    return PRICE_TIERS[-1]["price"]


def _qty_from_text(norm: str, qty_regex: str = QTY_REGEX) -> int | None:
    """Извлекает количество голов из текущей реплики (цифры или слова)."""
    m = re.search(qty_regex, norm)
    if m:
        return int(m.group(1))
    digits = _text_to_digits(norm)
    if digits:
        try:
            return int(digits)
        except ValueError:
            return None
    return None


def _extract_quantity(chat_ctx, qty_regex: str = QTY_REGEX) -> str:
    """Ищет количество голов в предыдущих репликах пользователя."""
    if chat_ctx is None:
        return ""
    for it in reversed(getattr(chat_ctx, "items", []) or []):
        if getattr(it, "role", None) != "user":
            continue
        c = getattr(it, "content", None)
        if isinstance(c, str):
            txt = c
        elif isinstance(c, list):
            txt = " ".join(
                p if isinstance(p, str) else (p.get("text", "") if isinstance(p, dict) else "")
                for p in c
            )
        else:
            txt = ""
        m = re.search(qty_regex, txt)
        if m:
            return m.group(1)
    return ""


def _last_user_text(chat_ctx) -> str:
    if chat_ctx is None:
        return ""
    items = getattr(chat_ctx, "items", None) or []
    for it in reversed(items):
        if getattr(it, "role", None) == "user":
            c = getattr(it, "content", None)
            if isinstance(c, str):
                return c
            if isinstance(c, list):
                return " ".join(
                    p if isinstance(p, str) else (p.get("text", "") if isinstance(p, dict) else "")
                    for p in c
                )
            return ""
    return ""


_UNIT_WORDS = {
    "ноль": 0,
    "один": 1,
    "одна": 1,
    "два": 2,
    "две": 2,
    "три": 3,
    "четыре": 4,
    "пять": 5,
    "шесть": 6,
    "семь": 7,
    "восемь": 8,
    "девять": 9,
}
_TEEN_WORDS = {
    "десять": 10,
    "одиннадцать": 11,
    "двенадцать": 12,
    "тринадцать": 13,
    "четырнадцать": 14,
    "пятнадцать": 15,
    "шестнадцать": 16,
    "семнадцать": 17,
    "восемнадцать": 18,
    "девятнадцать": 19,
}
_TEN_WORDS = {
    "двадцать": 20,
    "тридцать": 30,
    "сорок": 40,
    "пятьдесят": 50,
    "шестьдесят": 60,
    "семьдесят": 70,
    "восемьдесят": 80,
    "девяносто": 90,
}
_HUNDRED_WORDS = {
    "сто": 100,
    "двести": 200,
    "триста": 300,
    "четыреста": 400,
    "пятьсот": 500,
    "шестьсот": 600,
    "семьсот": 700,
    "восемьсот": 800,
    "девятьсот": 900,
}


def _parse_number(tokens, start):
    total = 0
    i = start
    used_hundred = False
    used_ten = False
    used_unit = False
    while i < len(tokens):
        w = tokens[i]
        if w in _HUNDRED_WORDS and not used_hundred:
            total += _HUNDRED_WORDS[w]
            used_hundred = True
            i += 1
        elif w in _TEN_WORDS and not used_ten:
            total += _TEN_WORDS[w]
            used_ten = True
            i += 1
        elif w in _TEEN_WORDS and not used_ten:
            total += _TEEN_WORDS[w]
            used_ten = True
            i += 1
        elif w in _UNIT_WORDS and not used_unit:
            if used_ten and total % 10 != 0:
                break
            total += _UNIT_WORDS[w]
            used_unit = True
            i += 1
        else:
            break
    if i == start:
        return None, 0
    return total, i - start


def _text_to_digits(text):
    tokens = re.sub(r"[^а-я0-9\s]", " ", text.lower()).split()
    parts = []
    i = 0
    while i < len(tokens):
        w = tokens[i]
        if w.isdigit():
            parts.append(w)
            i += 1
            continue
        num, consumed = _parse_number(tokens, i)
        if consumed:
            parts.append(str(num))
            i += consumed
            continue
        i += 1
    return "".join(parts)


def _phone_from_text(text):
    raw = re.sub(r"[^0-9]", "", text)
    if len(raw) >= 10:
        return raw[-10:]
    digits = _text_to_digits(text)
    if len(digits) >= 10:
        return digits[-10:]
    return None


def _fmt_phone_spoken(p: str) -> str:
    digits = re.sub(r"\D", "", p or "")
    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    if not digits:
        return p or ""
    return " ".join(digits)


def _fast_path_reply(chat_ctx, llm_obj) -> str | None:
    """Детерминированные ветки ДА/НЕТ -> канонический ответ без обращения к LLM.
    Возвращает текст ответа или None (пропустить через обычный LLM)."""
    norm = normalize(_last_user_text(chat_ctx))
    if not norm:
        return None
    words = norm.split()
    _asked = getattr(llm_obj, "_asked_quantity", False)
    _delivery = getattr(llm_obj, "_asked_delivery", False)
    _neg = re.fullmatch(NEG_PATTERN, norm) or (
        norm.startswith("нет")
        and len(words) <= 2
        and not re.search(r"(доставк|город|адрес|улиц|в )", norm)
    )
    if _neg:
        if _delivery:
            return None  # клиент меняет адрес -> пусть обработает LLM
        return "Спасибо за внимание, всего хорошего!"
    if _asked and _delivery:
        if re.search(DELIVERY_CONFIRM_PATTERN, norm) or norm.startswith("да"):
            _q = _extract_quantity(chat_ctx)
            _ph = getattr(llm_obj, "_caller_phone", "")
            if _ph and save_lead_fn is not None:
                import asyncio

                asyncio.ensure_future(
                    save_lead_fn(
                        phone=_ph, quantity=_q, comment="fast-path: подтверждение доставки"
                    )
                )
            return "С вами свяжется менеджер для уточнения заказа, всего хорошего!"
        return None
    if _asked and not _delivery:
        _q = _qty_from_text(norm)
        if _q:
            _price = _price_for_qty(_q)
            return f"Для {_q} голов цена {_price} рублей за голову. Место доставки цыплят прежнее?"
        return None
    if not _asked:
        _pos = (
            re.fullmatch(POS_PATTERN, norm)
            or (norm.startswith("да") and len(words) <= 3)
            or (" да " in f" {norm} " and len(words) <= 3 and not norm.startswith(("нет", "не")))
        )
        if _pos:
            llm_obj._asked_quantity = True
            return "Отлично! Сколько голов вам нужно?"
        # известный вопрос (intents из funnel_config) -> шаблонный ответ без LLM
        _intent = _intent_reply(norm)
        if _intent is not None:
            return _intent
        # FAQ-слой: 238 реальных триггеров (SequenceMatcher) -> мгновенный ответ
        _faq = _faq_reply(norm)
        if _faq is not None:
            return _faq
        # первый ход: детерминированное приветствие ТОЛЬКО для чистого приветствия.
        # Вопрос/просьба/незнакомое -> None -> LLM (или заглушка на уровне агента).
        if _is_greeting_only(norm):
            return "Здравствуйте! Это Азовский инкубатор, вас интересуют суточные цыплята породы Росс-308? Вам интересно?"
        return None
    return None


_FAQ_STOP = set(
    (
        "в на по за у с до из для и а но ли не это что как то вы вас мне нам же бы или "
        "от к об о при между через который которая которые какая какой какие когда где "
        "сколько можно ли есть пожалуйста скажите подскажите хочу хотел узнать ещё еще "
        "если если бы будет буду хотите хотел бы здравствуйте здравствуите здраствуйте "
        "здраствуите алло привет добрыи доброе "
        "даите дайте контакты вашего поставщика поставщиков кормов корма корм "
        "примут примите возврат вернуть сдохнет сдохнут падеж"
    ).split()
)


def _kw(t: str) -> list:
    """Значимые слова (длина >=4, без стоп-слов) для матчинга по ключам."""
    return [w for w in t.split() if len(w) >= 4 and w not in _FAQ_STOP]


def _word_match(a: str, b: str) -> bool:
    """Слово из триггера матчит слово вопроса. Точные критерии:
    - подстрока (морфология: крым~крыму, бройлер~бройлеры);
    - длинный общий корень (>=5 символов: вакцинация~вакцинации);
    - SequenceMatcher >= 0.8 (стоит~стоят).
    НЕ матчит случайные созвучия: беспокоит~бесплатная, цыпленок~цыплята,
    поставщика~доставка (общие <5 символов и ratio < 0.8)."""
    if len(a) < 4 or len(b) < 4:
        return False
    if a in b or b in a:
        return True
    if min(len(a), len(b)) >= 5 and a[:5] == b[:5]:
        return True
    return SequenceMatcher(None, a, b).ratio() >= 0.8


def _faq_reply(norm: str) -> str | None:
    """FAQ-слой: 238 реальных триггеров -> мгновенный ответ без LLM.
    Сначала SequenceMatcher по всей фразе (0.72), затем матчинг по ключевым словам."""
    if not norm or len(norm) < 3 or not _FAQ_CACHE:
        return None
    # 1) SequenceMatcher по фразе целиком
    best_score, best_reply = 0.0, None
    for trigger, reply in _FAQ_CACHE.items():
        score = SequenceMatcher(None, norm, trigger).ratio()
        if score > best_score:
            best_score, best_reply = score, reply
    if best_score >= 0.72:
        return best_reply
    # 2) ключевые слова (морфология: гарантия~гарантии, дохнут~сдохнет)
    # Сервисные/юридические запросы (возврат, падёж, замена) — НЕ FAQ:
    # их keyword-слой не трогает, уходят в LLM.
    if re.search(r"(возврат|примут|сдохн|дохн|вернут|падеж|замен)", norm):
        return None
    q_kw = _kw(norm)
    if not q_kw:
        return None
    best_kw, best_reply_kw = 0.0, None
    for trigger, reply in _FAQ_CACHE.items():
        t_kw = _kw(trigger)
        if not t_kw:
            continue
        matched = sum(1 for tw in t_kw if any(_word_match(tw, qw) for qw in q_kw))
        score = matched / len(t_kw)
        if score > best_kw:
            best_kw, best_reply_kw = score, reply
    if best_kw >= 0.5 and best_reply_kw is not None:
        return best_reply_kw
    return None


def _intent_reply(norm: str) -> str | None:
    """Матчер intents: паттерн вопроса -> шаблонный ответ БЕЗ LLM (детерминированно).
    Возвращает текст ответа или None (нет матча -> LLM/заглушка)."""
    if not norm:
        return None
    for it in INTENTS:
        for pat in it.get("patterns", []):
            if pat in norm:
                return it.get("response")
    return None


def next_placeholder() -> str:
    """Ротация фраз-заглушек («понял, одну секунду») — сменяются в процессе диалога."""
    if not PLACEHOLDERS:
        return "Да, конечно! Сейчас отвечу"
    r = PLACEHOLDERS[_pi[0] % len(PLACEHOLDERS)]
    _pi[0] += 1
    return r


def faq_normalized_similarity(a: str, b: str) -> float:
    """Для тестов: нормализованная похожесть (SequenceMatcher)."""
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()
