"""Levitan Gemini Live — вариант 2 (speech-to-speech).

Агент на LiveKit `AgentSession` + Google `RealtimeModel` (gemini-3.1-flash-live-preview).
Один модель принимает и отдаёт аудио напрямую — НЕТ каскада STT->LLM->TTS, нет VAD
(серверный turn-detection), нет кастомного fast-path/воронки перехвата (модель сама
ведёт диалог). Инструменты (save_lead/faq_lookup) — live, auto tool reply.

Бизнес-сценарий и промпт те же, что в levitan-livekit — для честного сравнения.

Статус: каркас (scaffold). Деплой на VPS + контрольный звонок + echo-cancellation
для SIP — следующий шаг. См. README.
"""

from __future__ import annotations

import asyncio
import os
import time

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import Agent, AgentServer
from livekit.agents.worker import ServerOptions

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-live-preview")
GEMINI_VOICE = os.getenv("GEMINI_VOICE", "Puck")
GEMINI_LANGUAGE = os.getenv("GEMINI_LANGUAGE", "ru-RU")

SYSTEM_PROMPT = """Голосовой менеджер Азовского инкубатора (IncuBird). Звонишь постоянному клиенту по известному номеру (НЕ называй его вслух) про суточных цыплят бройлеров. Его город и телефон уже в базе — просто уточняй «место доставки прежнее?».

КОМПАНИЯ: Азовский инкубатор, Крым, пгт Азовское, ул. Железнодорожная 42, +7 (918) 047-51-07. Самовывоз — только Крым (Азовское, 14:00–17:00). Доставка по ПН и ЧТ спецтранспортом с климат-контролем по Крыму и югу России (Симферополь, Джанкой, Керчь, Краснодар, Ростов-на-Дону и др.). НИКОГДА не отказывай в доставке. Гарантия 100% выживаемости. Оплата: наличные/карта, предоплата 50%.

АССОРТИМЕНТ (июль–декабрь 2026 — только бройлеры): РОСС-308 (от 75₽, рекомендуем); КОББ-500 (дороже, до 2.5 кг за 40 дней). Мин. заказ — 50 голов одной породы, от 100 — скидка. График вывода: ПН и ЧТ.

ЦЕНЫ (за голову, ступенчатые): до 100 — 90₽, 101–300 — 85₽, 301–999 — 80₽, от 1000 — 75₽. Общую сумму НЕ считай — её даст менеджер.

ТИПОВЫЕ ВОПРОСЫ (цена, объём, доставка, породы, вакцинация, вес, кормление, температура, содержание, гарантия, оплата, график): отвечай по фактам выше, КОРОТКО, без инструментов поиска.

СТИЛЬ: живо, тепло, по-деловому. 1–2 предложения на ответ. Один вопрос за раз.

ВОРОНКА (НЕ перескакивай шаги):
1) Приветствие/«Алло» — кратко: «Здравствуйте, это Азовский инкубатор! Предлагаем Росс-308 от 75 рублей. Вам интересно?»
2) «ДА» → «Отлично! Сколько голов вам нужно?». Если меньше 50 — «Минимальный заказ — 50 голов. Сколько голов вам нужно?» (переспроси, НЕ переходи к доставке). Иначе назови цену за голову, НЕ сумму, и спроси: «Место доставки цыплят прежнее?»
3) «НЕТ» → «Спасибо за внимание, всего хорошего!».
4) Доставка прежняя → save_lead(phone="{caller_phone}", quantity=количество, city=город, comment=итог) БЕЗ текста, затем: «С вами свяжется менеджер для уточнения заказа, всего хорошего!»
5) Доставка другая → save_lead БЕЗ текста, затем: «Сообщите менеджеру новое место доставки, всего хорошего!»
6) Финальную фразу произнеси ОДНИМ предложением и закончи. НЕ вызывай end_call и НЕ добавляй текст после прощания — звонок завершится автоматически."""

GREETING = "Здравствуйте, это Азовский инкубатор, ранее вы заказывали у нас цыплят! Мы рады предложить вам сейчас породу Росс-308 от 75 рублей, вам интересно?"

_last_lead: dict = {"phone": "", "ts": 0.0}


async def save_lead(
    phone: str, quantity: str = "", city: str = "", delivery_date: str = "", comment: str = ""
) -> str:
    """Сохраняет лид клиента в CRM Bitrix24 (тот же интерфейс, что в levitan-livekit)."""
    import httpx

    bitrix_url = os.getenv("BITRIX_WEBHOOK_URL", "")
    if not bitrix_url:
        return "CRM не настроена (BITRIX_WEBHOOK_URL)"
    if _last_lead["phone"] == phone and time.time() - _last_lead["ts"] < 60:
        return "Лид уже создан"
    from datetime import datetime

    fields = {
        "TITLE": f"🐔 Цыплята {delivery_date or ''} — {phone}",
        "PHONE": [{"VALUE": phone, "VALUE_TYPE": "MOBILE"}],
        "COMMENTS": (
            f"📞 Автообзвон (Gemini Live) {datetime.now().strftime('%d.%m %H:%M')}\n"
            f"Количество: {quantity or '—'}\n"
            f"Город: {city or '—'}\n"
            f"Дата: {delivery_date or '—'}\n"
            f"Итог: {comment or '—'}"
        ),
        "SOURCE_ID": "CALL",
        "STAGE_ID": "NEW",
    }
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(f"{bitrix_url}/crm.lead.add", json={"fields": fields})
        res = r.json()
        if res.get("result"):
            _last_lead["phone"], _last_lead["ts"] = phone, time.time()
            return f"Лид создан: ID {res['result']}"
        return f"Ошибка CRM: {str(res.get('error', res))[:100]}"
    except Exception as e:  # noqa: BLE001
        return f"Ошибка CRM: {str(e)[:100]}"


def _load_faq() -> dict[str, str]:
    """FAQ-словарь из funnel_config (общий с levitan-livekit), если доступен."""
    import json
    from pathlib import Path

    for p in (
        Path(__file__).parent / "funnel_config.json",
        Path(__file__).resolve().parents[1] / "data" / "funnel_config.json",
    ):
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8")).get("faq", {})
            except Exception:  # noqa: BLE001
                return {}
    return {}


FAQ = _load_faq()


def faq_lookup(question: str) -> str | None:
    """Ищет ответ в FAQ по подстроке."""
    q = question.lower()
    for key, val in FAQ.items():
        if str(key).lower() in q:
            return str(val)
    return None


class GeminiAgent(Agent):
    def __init__(self, instructions: str | None = None, caller_phone: str = ""):
        from livekit.plugins.google.realtime import RealtimeModel

        self.caller_phone = caller_phone
        model = RealtimeModel(
            model=GEMINI_MODEL,
            api_key=GEMINI_API_KEY,
            voice=GEMINI_VOICE,
            language=GEMINI_LANGUAGE,
            instructions=instructions or SYSTEM_PROMPT.replace("{caller_phone}", caller_phone),
        )
        super().__init__(
            instructions=instructions or SYSTEM_PROMPT.replace("{caller_phone}", caller_phone),
            llm=model,
            tools=[save_lead],
        )

    async def on_enter(self) -> None:
        print(f"[GEMINI] on_enter, saying greeting for {self.caller_phone}", flush=True)
        await self.session.say(GREETING, allow_interruptions=False)


async def entrypoint(ctx) -> None:
    sip = ctx.room.remote_participants
    caller = ""
    for rp in sip.values():
        for track in rp.track_publications.values():
            if getattr(track, "source", None) == rtc.TrackSource.SOURCE_MICROPHONE:
                caller = getattr(rp, "identity", "") or ""
                break
    print(f"[GEMINI] incoming call, caller={caller}", flush=True)
    await ctx.connect(
        agent=GeminiAgent(caller_phone=caller),
        room=ctx.room,
    )


async def main() -> None:
    if not GEMINI_API_KEY:
        raise SystemExit("FATAL: нет GEMINI_API_KEY в .env")
    server = AgentServer(
        options=ServerOptions(
            agent_name="levitan-gemini",
            port=int(os.getenv("PORT", "8081")),
        ),
    )
    await server.start(entrypoint=entrypoint)


if __name__ == "__main__":
    asyncio.run(main())
