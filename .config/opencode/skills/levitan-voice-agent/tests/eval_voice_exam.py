"""
LV-2: Eval suite — Экзамен голосовых сценариев (из билетов).
Билеты на основе реальных звонков: мок-режим (заглушки) + live-режим.

Запуск: python3 -m pytest tests/eval_voice_exam.py -v
"""

EXAM_TICKETS = [
    {
        "id": "T1",
        "scenario": "номер_словами",
        "action": "Клиент говорит «Восемьдесят» вместо 80",
        "expected": "парсить числительные: 'восемьдесят' → 80",
    },
    {
        "id": "T2",
        "scenario": "перебивает",
        "action": "Менеджер говорит цену, клиент перебивает: «А доставка?»",
        "expected": "Не повторять цену, ответить на вопрос о доставке",
    },
    {
        "id": "T3",
        "scenario": "молчит",
        "action": "Клиент молчит 5 секунд после вопроса менеджера",
        "expected": "Агент ждёт 3с, затем переспрашивает: «Алло, вы здесь?»",
    },
    {
        "id": "T4",
        "scenario": "обрыв",
        "action": "Звонок обрывается на полуслове клиента про город",
        "expected": "Агент определяет обрыв, записывает частичные данные, помечает для перезвона",
    },
    {
        "id": "T5",
        "scenario": "не_клиент",
        "action": "Звонящий говорит «Извините, ошибся номером»",
        "expected": "Агент вежливо завершает звонок, не пытается продать",
    },
    {
        "id": "T6",
        "scenario": "громкость",
        "action": "Клиент говорит очень тихо, еле слышно",
        "expected": "Агент просит говорить громче, не начинает продажу",
    },
    {
        "id": "T7",
        "scenario": "брань",
        "action": "Клиент матерится на цены",
        "expected": "Агент сохраняет спокойствие, предлагает альтернативу, не отвечает бранью",
    },
    {
        "id": "T8",
        "scenario": "диалект",
        "action": "Клиент на суржике: «шо це за цэны?»",
        "expected": "Агент понимает и отвечает на литературном русском",
    },
    {
        "id": "T9",
        "scenario": "дети",
        "action": "Клиент отвлёкся на ребёнка: «Подождите, я сейчас... (крики детей)»",
        "expected": "Агент ждёт 10с, затем мягко напоминает о себе",
    },
    {
        "id": "T10",
        "scenario": "диктофон",
        "action": "Клиент: «Я записываю разговор»",
        "expected": "Агент подтверждает: «Хорошо, я тоже записываю для контроля качества»",
    },
    {
        "id": "T11",
        "scenario": "конкурент",
        "action": "Клиент: «В ПтицеФерме дешевле на 10 рублей»",
        "expected": "Агент не ругает конкурента, аргументирует сервисом/качеством/доставкой",
    },
    {
        "id": "T12",
        "scenario": "возврат",
        "action": "Клиент: «В прошлый раз половина цыплят сдохла!»",
        "expected": "Агент извиняется, уточняет детали, предлагает решение (замена/скидка)",
    },
    {
        "id": "T13",
        "scenario": "срочно",
        "action": "Клиент: «Мне надо ЗАВТРА! Успеете?»",
        "expected": "Агент честно: проверяет логистику, не обещает невозможного",
    },
]


def evaluate_voice_response(ticket_id: str, agent_response: str, log: str = "") -> dict:
    ticket = next((t for t in EXAM_TICKETS if t["id"] == ticket_id), None)
    if not ticket:
        return {"ticket_id": ticket_id, "passed": False, "error": "unknown ticket"}

    expected_kw = ticket["expected"].lower().split()
    response_lower = agent_response.lower()
    matches = sum(1 for kw in expected_kw if kw in response_lower)
    passed = matches >= max(1, len(expected_kw) // 2)

    return {
        "ticket_id": ticket_id,
        "scenario": ticket["scenario"],
        "passed": passed,
        "keyword_matches": matches,
        "expected_keywords": len(expected_kw),
    }


def get_tickets() -> list[dict]:
    return EXAM_TICKETS


def get_ticket(ticket_id: str) -> dict:
    return next((t for t in EXAM_TICKETS if t["id"] == ticket_id), {})


def mock_dialog(ticket_id: str) -> dict:
    ticket = get_ticket(ticket_id)
    if not ticket:
        return {}
    return {
        "ticket": ticket,
        "mock_input": f"[MOCK] {ticket['action']}",
        "expected_behavior": ticket["expected"],
    }
