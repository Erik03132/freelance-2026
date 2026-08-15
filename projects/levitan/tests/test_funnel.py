"""
Локальные unit-тесты детерминированной воронки (funnel.py) без LLM.
Запуск: python3 -m pytest tests/test_funnel.py -v
"""

import os
import sys

AGENT_DIR = os.path.join(os.path.dirname(__file__), "..", "agent")
sys.path.insert(0, os.path.abspath(AGENT_DIR))

import funnel  # noqa: E402


class _FakeCtx:
    def __init__(self, items):
        self.items = items


def _user(text):
    return type("M", (), {"role": "user", "content": text})()


def _assistant(text):
    return type("M", (), {"role": "assistant", "content": text})()


class _FakeLLM:
    def __init__(self, asked_q=False, delivery=False, phone=""):
        self._asked_quantity = asked_q
        self._asked_delivery = delivery
        self._caller_phone = phone


def test_price_for_qty_tiers():
    assert funnel._price_for_qty(50) == 90
    assert funnel._price_for_qty(100) == 90
    assert funnel._price_for_qty(101) == 85
    assert funnel._price_for_qty(300) == 85
    assert funnel._price_for_qty(301) == 80
    assert funnel._price_for_qty(999) == 80
    assert funnel._price_for_qty(1000) == 75
    assert funnel._price_for_qty(5000) == 75


def test_qty_from_text_digits_and_words():
    assert funnel._qty_from_text("50 голов") == 50
    assert funnel._qty_from_text("сто голов") == 100
    assert funnel._qty_from_text("двести пятьдесят голов") == 250
    assert funnel._qty_from_text("привет") is None


def test_text_to_digits():
    assert funnel._text_to_digits("сто двадцать три") == "123"
    assert funnel._text_to_digits("пятьдесят") == "50"
    assert funnel._text_to_digits("abc") == ""


def test_phone_from_text():
    assert funnel._phone_from_text("+7 985 923 46 44") == "9859234644"
    assert funnel._phone_from_text("79859234644") == "9859234644"
    assert funnel._phone_from_text("нет") is None


def test_fmt_phone_spoken():
    assert funnel._fmt_phone_spoken("79859234644") == "7 9 8 5 9 2 3 4 6 4 4"
    assert funnel._fmt_phone_spoken("89859234644") == "7 9 8 5 9 2 3 4 6 4 4"


def test_fast_path_net():
    llm = _FakeLLM()
    ctx = _FakeCtx([_user("нет")])
    assert funnel._fast_path_reply(ctx, llm) == "Спасибо за внимание, всего хорошего!"


def test_fast_path_da_sets_asked():
    llm = _FakeLLM()
    ctx = _FakeCtx([_user("да")])
    out = funnel._fast_path_reply(ctx, llm)
    assert out == "Отлично! Сколько голов вам нужно?"
    assert llm._asked_quantity is True


def test_fast_path_quantity_price():
    llm = _FakeLLM(asked_q=True)
    ctx = _FakeCtx([_user("двести голов")])
    out = funnel._fast_path_reply(ctx, llm)
    assert out == "Для 200 голов цена 85 рублей за голову. Место доставки цыплят прежнее?"


def test_fast_path_delivery_confirm_manager():
    import asyncio

    saved = {}

    async def fake_save(phone, quantity, comment):
        saved["phone"] = phone
        saved["qty"] = quantity
        return "ok"

    funnel.save_lead_fn = fake_save
    llm = _FakeLLM(asked_q=True, delivery=True, phone="9859234644")
    ctx = _FakeCtx([_user("100 голов"), _user("да")])

    async def _run():
        out = funnel._fast_path_reply(ctx, llm)
        await asyncio.sleep(0)
        return out

    out = asyncio.run(_run())
    assert out == "С вами свяжется менеджер для уточнения заказа, всего хорошего!"
    assert saved.get("phone") == "9859234644"
    funnel.save_lead_fn = None


def test_fast_path_delivery_change_returns_none():
    llm = _FakeLLM(asked_q=True, delivery=True, phone="9859234644")
    ctx = _FakeCtx([_user("нет, в ростов")])
    assert funnel._fast_path_reply(ctx, llm) is None


def test_first_turn_question_delivery_intent():
    llm = _FakeLLM()
    ctx = _FakeCtx([_user("а сколько стоит доставка в краснодар")])
    out = funnel._fast_path_reply(ctx, llm)
    assert out == "Доставка по городу бесплатная, за город — 300 рублей."


def test_first_turn_question_schedule_intent():
    llm = _FakeLLM()
    ctx = _FakeCtx([_user("какой у вас график работы?")])
    out = funnel._fast_path_reply(ctx, llm)
    assert out == "Мы работаем ежедневно с 9 до 18, без выходных."


def test_first_turn_greeting_deterministic():
    llm = _FakeLLM()
    ctx = _FakeCtx([_user("алло")])
    out = funnel._fast_path_reply(ctx, llm)
    assert out
    assert out.lower().startswith(("здравствуйте", "алло", "добрый"))
    assert "Азовский инкубатор" in out


def test_first_turn_plain_greeting():
    llm = _FakeLLM()
    ctx = _FakeCtx([_user("здравствуйте")])
    out = funnel._fast_path_reply(ctx, llm)
    assert out and out.startswith("Здравствуйте!")


def test_first_turn_request_goes_to_llm():
    llm = _FakeLLM()
    ctx = _FakeCtx([_user("дайте контакты вашего поставщика кормов")])
    assert funnel._fast_path_reply(ctx, llm) is None


def test_intent_schedule():
    llm = _FakeLLM()
    ctx = _FakeCtx([_user("какой у вас график работы")])
    out = funnel._fast_path_reply(ctx, llm)
    assert out == "Мы работаем ежедневно с 9 до 18, без выходных."


def test_intent_delivery_price():
    llm = _FakeLLM()
    ctx = _FakeCtx([_user("сколько стоит доставка")])
    out = funnel._fast_path_reply(ctx, llm)
    assert out == "Доставка по городу бесплатная, за город — 300 рублей."


def test_intent_price():
    llm = _FakeLLM()
    ctx = _FakeCtx([_user("какая у вас цена")])
    out = funnel._fast_path_reply(ctx, llm)
    assert "90 рублей" in out


def test_intent_stock():
    llm = _FakeLLM()
    ctx = _FakeCtx([_user("есть ли цыплята в наличии")])
    out = funnel._fast_path_reply(ctx, llm)
    assert "в наличии" in out


def test_unknown_question_still_llm():
    llm = _FakeLLM()
    ctx = _FakeCtx([_user("дайте контакты вашего поставщика кормов")])
    assert funnel._fast_path_reply(ctx, llm) is None


def test_porody_known_intent():
    llm = _FakeLLM()
    ctx = _FakeCtx([_user("расскажите про породы подробнее")])
    out = funnel._fast_path_reply(ctx, llm)
    assert out is not None
    assert "90 рублей" in out


def test_next_placeholder_rotates():
    a = funnel.next_placeholder()
    b = funnel.next_placeholder()
    assert a != b
    assert a and b


def test_fast_path_greeting_first_turn():
    # первый ход (приветствие оператора) -> детерминированное приветствие без LLM
    llm = _FakeLLM()
    ctx = _FakeCtx([_user("здравствуйте вас беспокоит менеджер")])
    out = funnel._fast_path_reply(ctx, llm)
    assert out is not None
    assert "интересно" in out
    assert llm._asked_quantity is False
