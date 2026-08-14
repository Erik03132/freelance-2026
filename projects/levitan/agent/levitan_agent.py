"""
Levitan Real-time Voice Agent — Pipecat + LiveKit SIP
Анжелла: FAQ-кэш (fast path) + OmniRoute LLM + Yandex SpeechKit TTS
"""
# ruff: noqa: E402  (load_dotenv must run before livekit imports read env)

import json
import logging
import os
import re
import time
from contextlib import asynccontextmanager
from difflib import SequenceMatcher
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

import asyncio
import math

import aiohttp
import httpx
from livekit import rtc
from livekit.agents import Agent, AgentServer, AgentSession, llm, tts
from livekit.agents.types import NOT_GIVEN, APIConnectOptions
from livekit.agents.worker import ServerOptions
from livekit.plugins import deepgram, openai
from openai import AsyncClient as OpenAIAsyncClient

LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")

LLM_BASE = os.getenv("LLM_BASE", "https://openrouter.ai/api/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek/deepseek-chat")
LLM_PROXY = os.getenv("LLM_PROXY", "http://Q3NeJXTY:dsBaWh2L@172.120.21.141:64468")

BITRIX_URL = os.getenv("BITRIX_WEBHOOK_URL", "").rstrip("/")
_last_lead = {"phone": None, "ts": 0}

YC_API_KEY = os.getenv("YC_API_KEY", "")
YC_FOLDER_ID = os.getenv("YC_FOLDER_ID", "")
TTS_VOICE = os.getenv("TTS_VOICE", "alena")

FAQ_CACHE_PATH = Path(__file__).resolve().parent / "docs" / "ANGELLA_BROILERS_FAQ_CACHE.json"
_faq_cache = {}


def load_faq_cache() -> None:
    global _faq_cache
    try:
        data = json.loads(FAQ_CACHE_PATH.read_text(encoding="utf-8"))
        _faq_cache = {k: v for k, v in data.items() if not k.startswith("_")}
        print(f"FAQ cache loaded: {len(_faq_cache)} triggers")
    except Exception as e:
        print(f"FAQ load error: {e}")


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[ёй]", lambda m: {"ё": "е", "й": "и"}.get(m.group(), m.group()), text)
    text = re.sub(r"[^а-я0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def faq_lookup(transcript_text: str) -> str | None:
    if not _faq_cache:
        return None
    norm = normalize(transcript_text)
    if len(norm) < 3:
        return None
    best_score, best_reply = 0.0, None
    for trigger, reply in _faq_cache.items():
        score = SequenceMatcher(None, norm, trigger).ratio()
        if score > best_score:
            best_score, best_reply = score, reply
    if best_score >= 0.72:
        return best_reply
    return None


@llm.function_tool
async def save_lead(
    phone: str, quantity: str = "", city: str = "", delivery_date: str = "", comment: str = ""
) -> str:
    """Сохраняет лид клиента в CRM Bitrix24: телефон (обязательно), количество голов, город, дата доставки, итог диалога. Вызвать ПОСЛЕ получения телефона."""
    if not BITRIX_URL:
        return "CRM не настроена (BITRIX_WEBHOOK_URL)"
    if _last_lead["phone"] == phone and time.time() - _last_lead["ts"] < 60:
        return "Лид уже создан"
    from datetime import datetime

    fields = {
        "TITLE": f"🐔 Цыплята {delivery_date or ''} — {phone}",
        "PHONE": [{"VALUE": phone, "VALUE_TYPE": "MOBILE"}],
        "COMMENTS": (
            f"📞 Автообзвон {datetime.now().strftime('%d.%m %H:%M')}\n"
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
            r = await client.post(f"{BITRIX_URL}/crm.lead.add", json={"fields": fields})
        res = r.json()
        if res.get("result"):
            _last_lead["phone"], _last_lead["ts"] = phone, time.time()
            return f"Лид создан: ID {res['result']}"
        return f"Ошибка CRM: {str(res.get('error', res))[:100]}"
    except Exception as e:
        return f"Ошибка CRM: {str(e)[:100]}"


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
    """Format a phone number for TTS so it is read digit-by-digit,
    not as a single magnitude (e.g. '79859234644' -> '7 9 8 5 9 2 3 4 6 4 4')."""
    digits = re.sub(r"\D", "", p or "")
    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    if not digits:
        return p or ""
    return " ".join(digits)


_session_holder = {"session": None}
_FAREWELL_MARKERS = (
    "всего хорошего",
    "всего доброго",
    "до свидания",
    "свяжется менеджер",
    "менеджер для уточнения",
    "хорошего дня",
    "благодарим за звонок",
    "спасибо за звонок",
    "всего хорош",
)


async def _terminate_after_speech(reason: str) -> None:
    sess = _session_holder.get("session")
    if not sess:
        return
    try:
        _speech_done = asyncio.Event()

        def _on_state(ev):
            if ev.new_state != "speaking":
                _speech_done.set()

        state = getattr(sess, "agent_state", None)
        if state in ("speaking", "thinking"):
            print(f"[CALL] {reason}: state={state}, waiting for final phrase...", flush=True)
            sess.on("agent_state_changed", _on_state)
            try:
                await asyncio.wait_for(_speech_done.wait(), timeout=15.0)
                print(f"[CALL] {reason}: final phrase finished", flush=True)
            except TimeoutError:
                print(
                    f"[CALL] {reason}: timeout waiting speech end, terminating anyway", flush=True
                )
            finally:
                sess.off("agent_state_changed", _on_state)
        await asyncio.sleep(0.5)
        sess.shutdown()
        print(f"[CALL] {reason}: shutdown ok", flush=True)
        try:
            _m = _session_holder.get("agent")
            _mm = getattr(_m, "_metrics", None) if _m else None
            if _mm:
                _avg = (sum(_mm["resp_lat"]) / len(_mm["resp_lat"])) if _mm["resp_lat"] else 0
                print(
                    f"[METRICS] summary: greet_dur={_mm['greet_dur']:.1f} "
                    f"turns={_mm['turns']} resp_lat={[round(x,1) for x in _mm['resp_lat']]} "
                    f"avg_resp_lat={_avg:.1f}",
                    flush=True,
                )
        except Exception as _me:
            print(f"[METRICS] summary fail {_me!r}", flush=True)
    except Exception as e:
        print(f"[CALL] {reason}: error {e!r}", flush=True)


@llm.function_tool
async def end_call(reason: str = "") -> str:
    """Завершает звонок. Вызови после отказа клиента (нет интереса) или после успешного оформления заказа."""
    print(f"[CALL] end_call requested: {reason}", flush=True)
    if not _session_holder.get("session"):
        return "Нет активной сессии"
    await _terminate_after_speech(f"end_call: {reason}")
    return "Звонок завершён"


@llm.function_tool
async def faq_lookup_tool(question: str) -> str:
    """Ищет готовый ответ в базе знаний по типовым вопросам клиентов (цена, доставка, породы, вакцинация, вес, кормление, гарантия). Возвращает ответ текстом или NOT_FOUND."""
    reply = faq_lookup(question)
    return reply if reply else "NOT_FOUND"


class YandexTTS(tts.TTS):
    """Yandex SpeechKit TTS — PCM 8000Hz mono s16le."""

    def __init__(self, api_key: str, folder_id: str, voice: str = "alena", speed: float = 1.0):
        super().__init__(
            capabilities=tts.TTSCapabilities(streaming=False, aligned_transcript=False),
            sample_rate=48000,
            num_channels=1,
        )
        self._api_key = api_key
        self._folder_id = folder_id
        self._voice = voice
        self._speed = speed
        self._req_id = 0
        self._lead_done = False
        self._lead_sec = float(os.getenv("TTS_LEAD_SILENCE_SEC", "2.5"))
        self._emotion = os.getenv("TTS_EMOTION", "good")

    @asynccontextmanager
    async def synthesize(self, text: str, *, conn_options: APIConnectOptions = None):
        import time as _t
        import re as _re

        _t0 = _t.time()
        print(f"[TTS] START len={len(text)} text={text[:60]!r}", flush=True)
        if not text.strip():
            yield
            return

        # Split into sentences so the first sentence's audio starts as soon as
        # its TTS is ready, instead of waiting for the whole reply to be synthesised.
        _sentences = [s for s in _re.split(r"(?<=[.!?…])\s+", text.strip()) if s.strip()]
        if not _sentences:
            _sentences = [text]

        async def _synth_one(sentence: str, lead: bool) -> bytes:
            form = aiohttp.FormData()
            form.add_field("text", sentence)
            form.add_field("folderId", self._folder_id)
            form.add_field("lang", "ru-RU")
            form.add_field("voice", self._voice)
            form.add_field("emotion", self._emotion)
            form.add_field("format", "lpcm")
            form.add_field("sampleRateHertz", "48000")
            form.add_field("speed", str(self._speed))
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize",
                    headers={"Authorization": f"Api-Key {self._api_key}"},
                    data=form,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    data = await resp.read()
                    if resp.status != 200 or len(data) < 1000:
                        raise RuntimeError(f"Yandex TTS {resp.status}: {data[:200]}")
            if lead and not self._lead_done and self._lead_sec > 0:
                self._lead_done = True
                import math as _m

                _sr = 48000
                _dur = min(self._lead_sec, 1.5)
                _n = int(_dur * _sr)
                _amp = int(32767 * 0.20)
                _tone = bytearray()
                for _i in range(_n):
                    _env = 0.5 - 0.5 * _m.cos(2 * _m.pi * _i / max(_n - 1, 1))
                    _s = int(_amp * _env * _m.sin(2 * _m.pi * 700 * _i / _sr))
                    _tone += int(_s).to_bytes(2, "little", signed=True)
                data = bytes(_tone) + data
                print(f"[TTS] lead-tone {_dur:.2f}s prepended (first synthesis)", flush=True)
            return data

        async def _stream():
            _chunk = 48000 * 20 // 1000  # 20ms @ 48k = 960 samples
            for _si, _s in enumerate(_sentences):
                _req = f"{self._req_id}-{_si}"
                _t1 = _t.time()
                _audio = await _synth_one(_s, lead=(_si == 0))
                print(
                    f"[TTS] sentence {_si+1}/{len(_sentences)} {len(_audio)}b in {_t.time()-_t1:.1f}s",
                    flush=True,
                )
                _n = len(_audio) // 2
                _off = 0
                _i = 0
                while _off < _n:
                    _end = min(_off + _chunk, _n)
                    _seg = _audio[_off * 2 : _end * 2]
                    _f = rtc.AudioFrame(
                        data=_seg,
                        sample_rate=48000,
                        num_channels=1,
                        samples_per_channel=len(_seg) // 2,
                    )
                    yield tts.SynthesizedAudio(
                        frame=_f,
                        request_id=_req,
                        segment_id=_req,
                        is_final=(_si == len(_sentences) - 1 and _end >= _n),
                        delta_text=_s if _i == 0 else "",
                    )
                    _off = _end
                    _i += 1

        self._req_id += 1
        print(f"[TTS] sentence-split: {len(_sentences)} parts in {_t.time()-_t0:.1f}s", flush=True)
        yield _stream()


SYSTEM_PROMPT = """Голосовой менеджер Азовского инкубатора (IncuBird). Отвечаешь клиентам по телефону про суточных цыплят бройлеров.

ТЫ ЗВОНИШЬ КЛИЕНТУ ПО ЕГО НОМЕРУ ТЕЛЕФОНА (он уже известен — НЕ называй его вслух). Просто уточни: «Место доставки прежнее?»

ТЫ ЗВОНИШЬ ПОСТОЯННОМУ КЛИЕНТУ, который ранее заказывал цыплят. Его город и телефон уже есть в базе — НЕ спрашивай «откуда вы», просто уточни «место доставки прежнее?».

КОМПАНИЯ: Азовский инкубатор, Крым, пгт Азовское, ул. Железнодорожная 42. Телефон +7 (918) 047-51-07.
Самовывоз — только Крым (Азовское, 14:00–17:00). В Москву самовывоза нет.
Доставка — по ПН и ЧТ по Крыму и Югу России, спецтранспорт с климат-контролем. Гарантия 100% выживаемости при доставке.
ГОРОДА ДОСТАВКИ (весь Крым и юг России, включая): Симферополь, Джанкой, Керчь, Феодосия, Евпатория, Ялта, Севастополь, Алушта, Судак, Бахчисарай, Саки, Красногвардейское, Нижнегорский, Советский, Кировское, Ленино, Первомайское, Раздольное, Черноморское, Сакский район и все сёла/посёлки Крыма, а также Краснодар, Ростов-на-Дону, Волгоград, Ставрополь и их области. Если клиент называет ЛЮБОЙ населённый пункт — доставка в него возможна (уточни район). НИКОГДА не говори, что доставка куда-то невозможна или что это не твоя тема.
Оплата: наличные при получении, перевод на карту, по реквизитам. Предоплата 50%.

АССОРТИМЕНТ (июль–декабрь 2026 — ТОЛЬКО бройлеры):
— РОСС-308: от 75₽/шт (до 100 голов), 101–300 — 85₽... цена ступенчатая, уточняй по объёму. Выносливый, крепкий, для дома и новичков — рекомендуем его.
— КОББ-500: дороже Росс, самый быстрорастущий, до 2.5 кг за 40 дней, мощная грудка. Для бизнеса/откорма.
Минимальный заказ — от 50 голов одной породы. От 100 голов — индивидуальная скидка.
График вывода: каждый ПН и ЧТ.

ЦЕНЫ (ступенчатая скидка, начиная от 50 голов):
— до 100 голов — 90₽/шт
— 101–300 голов — 85₽/шт
— 301–999 голов — 80₽/шт
— от 1000 голов — 75₽/шт

ВАКЦИНАЦИЯ И ЗДОРОВЬЕ: базовая вакцинация на инкубатории (Марек, Гамборо, Ньюкасл), ветсвидетельство в каждой партии.

ТИПОВЫЕ ВОПРОСЫ: если вопрос клиента типовой (цена, объём, доставка, породы, вакцинация, вес, кормление, температура, условия содержания, гарантия, оплата, график) — ответь сама по этим фактам из инструкций выше, НЕ вызывай никаких инструментов поиска.

СТИЛЬ: говори живо, тепло, как заботливая хозяйка, но по-деловому. ОЧЕНЬ КОРОТКО: 1 предложение на ответ, максимум 2. Один вопрос за раз. Никогда не повторяй приветствие и не пересказывай цены без запроса клиента.

ВОРОНКА (строго по шагам, НЕ перескакивай):
1) Ты уже представился клиенту и предложил цыплят. Если клиент ответил «Алло» или поздоровался — повтори кратко: «Здравствуйте, это Азовский инкубатор! Предлагаем Росс-308 от 75 рублей. Вам интересно?»
2) Если клиент сказал «ДА»: скажи «Отлично!» и спроси «Сколько голов вам нужно?». Узнав количество — назови только цену за голову для этого объёма (до 100 — 90₽, 101–300 — 85₽, 301–999 — 80₽, от 1000 — 75₽), НЕ считай и НЕ называй общую сумму — итог рассчитает менеджер. Затем ОДНОЙ фразой спроси: «Место доставки цыплят прежнее?»
3) Если клиент сказал «НЕТ» или не заинтересован: скажи «Спасибо за внимание, всего хорошего!». Больше ничего не добавляй.
4) Если клиент подтвердил (место доставки прежнее): вызови save_lead(phone="{caller_phone}", quantity=количество, city=город_из_диалога, comment=краткий_итог) ОТДЕЛЬНЫМ вызовом БЕЗ текста в этом сообщении. После результата скажи ОДНОЙ фразой: «С вами свяжется менеджер для уточнения заказа, всего хорошего!» — и закончи ответ, больше ничего не добавляй.
5) Если место доставки другое: запиши новые данные через save_lead ОТДЕЛЬНЫМ вызовом БЕЗ текста. После результата скажи ОДНОЙ фразой: «Записали ваши данные, с вами свяжется менеджер, всего хорошего!» — и закончи ответ.
6) ОТВЕЧАЙ КОРОТКО: 1-2 предложения. НЕ повторяйся. НЕ спрашивай слишком много за раз.
7) ВАЖНО: финальную фразу (прощание/подтверждение) произнеси ОДНИМ полным предложением и закончи ответ. НЕ вызывай end_call и НЕ добавляй текст после прощания — звонок завершится автоматически."""

GREETING = "Здравствуйте, это Азовский инкубатор, ранее вы заказывали у нас цыплят! Мы рады предложить вам сейчас породу Росс-308 от 75 рублей, вам интересно?"


class DebugLLMStream:
    def __init__(self, stream=None):
        self._s = stream
        self._n = 0
        print(
            f"[LLM] DebugLLMStream wraps {type(stream).__name__ if stream else 'lazy'} client={getattr(stream, '_client', None) and getattr(stream._client, '_base_url', '?')}",
            flush=True,
        )
        _c = getattr(stream, "_client", None) if stream else None
        _cc = getattr(_c, "chat", None)
        _cp = getattr(_cc, "completions", None)
        _orig = getattr(_cp, "create", None)
        if _orig is not None and not getattr(_orig, "_spied", False):

            async def _spy(**kw):
                try:
                    _msgs = kw.get("messages") or []
                    _brief = [(m.get("role"), str(m.get("content", ""))[:80]) for m in _msgs]
                    _tl = kw.get("tools") or []
                    if not isinstance(_tl, list):
                        _tl = []
                    _tl = [str(t.get("function", {}).get("name")) for t in _tl]
                    _drop = {}
                    for _k, _v in kw.items():
                        if _k in ("messages", "tools"):
                            continue
                        if isinstance(_v, str | int | float | bool | None):
                            _drop[_k] = _v
                        else:
                            _drop[_k] = repr(_v)[:160]
                    print(f"[LLM] REQUEST {_drop}", flush=True)
                    print(f"[LLM] MSGS {_brief}", flush=True)
                    print(f"[LLM] TOOLS {_tl}", flush=True)
                except Exception as _se:
                    print(f"[LLM] spy-fail {_se!r}", flush=True)
                return await _orig(**kw)

            _spy._spied = True
            _cp.create = _spy
            print("[LLM] spy installed", flush=True)
        _task = getattr(stream, "_task", None)
        if _task is not None:

            async def _watch():
                await asyncio.sleep(10)
                _done = _task.done()
                _exc = None
                if _done:
                    try:
                        _exc = repr(_task.exception())
                    except Exception as _e:
                        _exc = f"exc-fail {_e!r}"
                print(f"[LLM] WATCH 10s task_done={_done} exc={_exc}", flush=True)

            asyncio.ensure_future(_watch())

    def __getattr__(self, name):
        return getattr(self._s, name)

    def __aiter__(self):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        if self._s is not None:
            await self._s.__aexit__(*a)

    async def __anext__(self):
        if getattr(self, "_prefix", None) is not None:
            p, self._prefix = self._prefix, None
            return p
        if self._n == 0:
            self._n += 1
            print("[LLM] __anext__#1 waiting (first-chunk gate)", flush=True)
            await self._first_or_fallback()
            if getattr(self, "_prefix", None) is not None:
                p, self._prefix = self._prefix, None
                print("[LLM] chunk#1 got (gated)", flush=True)
                return p
        self._n += 1
        print(f"[LLM] __anext__#{self._n} waiting", flush=True)
        try:
            item = await asyncio.wait_for(self._s.__anext__(), timeout=15)
        except TimeoutError:
            _task = getattr(self._s, "_task", None)
            _state = _exc = None
            if _task is not None:
                _state = "done" if _task.done() else "running"
                if _task.done():
                    try:
                        _exc = repr(_task.exception())
                    except Exception as _e:
                        _exc = f"exc-fail {_e!r}"
            print(f"[LLM] TIMEOUT 30s task={_state} exc={_exc}", flush=True)
            raise
        except Exception as _e:
            print(f"[LLM] __anext__ EXC {_e!r}", flush=True)
            raise
        print(f"[LLM] chunk#{self._n} got {type(item).__name__}", flush=True)
        return item

    async def _first_or_fallback(self):
        models = list(dict.fromkeys(self._models))
        streams, tasks = {}, {}
        no_retry_conn = APIConnectOptions(max_retry=0, timeout=20.0)
        kwargs_no_retry = {**self._kwargs, "conn_options": no_retry_conn}
        for m in models:
            llm_for = self._llm if m == self._llm.model else self._llm._llm_for_model(m)
            _kw = dict(kwargs_no_retry)
            _kw["extra_kwargs"] = {"reasoning_effort": "none"}
            try:
                st = openai.LLM.chat(llm_for, **_kw)
                streams[m] = st
                tasks[m] = asyncio.ensure_future(asyncio.wait_for(st.__anext__(), timeout=10))
            except Exception as e:
                print(f"[LLM] first-chunk create {m}: {e!r}", flush=True)
        if not tasks:
            raise RuntimeError("no LLM models available")
        remaining = set(tasks.keys())
        winner_m, winner_chunk = None, None
        while remaining:
            wait_set = {m: tasks[m] for m in remaining}
            done, _ = await asyncio.wait(wait_set.values(), return_when=asyncio.FIRST_COMPLETED)
            found = False
            for m, t in wait_set.items():
                if t in done:
                    try:
                        winner_chunk = t.result()
                        winner_m = m
                        found = True
                        print(f"[LLM] first chunk OK model={winner_m}", flush=True)
                    except Exception as e:
                        print(f"[LLM] first-chunk fail {m}: {e!r}", flush=True)
                    remaining.discard(m)
                    break
            if found:
                break
        if winner_chunk is None:
            raise RuntimeError("all LLM models failed first chunk")
        for _m, _st in streams.items():
            if _m != winner_m:
                _t = tasks.get(_m)
                if _t is not None and not _t.done():
                    _t.cancel()
                try:
                    await _st.aclose()
                except Exception:
                    pass
        self._s = streams[winner_m]
        self._prefix = winner_chunk


class DebugLLM(openai.LLM):
    def _llm_for_model(self, model):
        cache = getattr(self, "_model_cache", None)
        if cache is None:
            cache = self._model_cache = {}
        if model not in cache:
            _opts = getattr(self, "_opts", None)
            cache[model] = openai.LLM(
                model=model,
                client=self._client,
                temperature=_opts.temperature if _opts is not None else NOT_GIVEN,
                max_completion_tokens=_opts.max_completion_tokens
                if _opts is not None
                else NOT_GIVEN,
            )
            print(f"[LLM] created extra LLM instance for model={model}", flush=True)
        return cache[model]

    def chat(self, **kwargs):
        import time as _t

        ctx = kwargs.get("chat_ctx", None)
        tools = kwargs.get("tools") or []
        n = len(ctx.items) if ctx is not None else -1
        _max_hist = int(os.getenv("LLM_MAX_HISTORY", "6"))
        if ctx is not None and len(ctx.items) > _max_hist:
            try:
                ctx = ctx.copy().truncate(max_items=_max_hist)
                kwargs = dict(kwargs)
                kwargs["chat_ctx"] = ctx
            except Exception as _e:
                print(f"[LLM] truncate failed: {_e!r}", flush=True)
        print(
            f"[LLM] chat() t={_t.time():.2f} msgs={n}(->{len(ctx.items) if ctx is not None else -1}) tools={len(tools)} kw={sorted(kwargs.keys())}",
            flush=True,
        )
        _co = kwargs.get("conn_options")
        print(f"[LLM] conn_options={_co!r} tool_choice={kwargs.get('tool_choice')!r}", flush=True)
        models = [self.model]
        _fb = os.getenv("LLM_FALLBACK_MODEL")
        if _fb and _fb not in models:
            models.append(_fb)
        if len(models) == 1:
            models.append(models[0])
        wrapped = DebugLLMStream(None)
        wrapped._models = models
        wrapped._kwargs = kwargs
        wrapped._llm = self
        return wrapped


class LevitanAgent(Agent):
    def __init__(self, instructions=None, caller_phone=""):
        super().__init__(
            instructions=instructions or SYSTEM_PROMPT,
            allow_interruptions=False,  # ответы агента не прерывать речью клиента
            tools=[save_lead, end_call],
            stt=deepgram.STT(model="nova-3", language="ru"),
            llm=DebugLLM(
                model=LLM_MODEL,
                api_key=os.getenv("OPENAI_API_KEY", "omni"),
                base_url=LLM_BASE,
                max_completion_tokens=2500,
                temperature=0.3,
                client=OpenAIAsyncClient(
                    api_key=os.getenv("OPENAI_API_KEY", "omni"),
                    base_url=LLM_BASE,
                    http_client=httpx.AsyncClient(
                        proxy=os.getenv("LLM_PROXY") or None,
                        timeout=httpx.Timeout(60.0, connect=15.0, read=60.0),
                    ),
                ),
            ),
            tts=YandexTTS(api_key=YC_API_KEY, folder_id=YC_FOLDER_ID, voice=TTS_VOICE),
        )

        self._transcripts: list[str] = []
        self._caller_phone: str = caller_phone
        self._farewell_fired: bool = False
        self._metrics = {"greet_dur": None, "turns": 0, "resp_lat": [], "last_user_t": None}

    async def _warmup_llm(self):
        try:
            import time as _t

            from livekit.agents.llm import ChatContext, ChatMessage

            ctx = ChatContext()
            ctx.items.append(ChatMessage(role="system", content=["Ответь одним словом: ок"]))
            models = [self.llm.model]
            _fb = os.getenv("LLM_FALLBACK_MODEL")
            if _fb and _fb not in models:
                models.append(_fb)
            _co = APIConnectOptions(max_retry=0, timeout=20.0)
            for m in models:
                llm_for = self.llm if m == self.llm.model else self.llm._llm_for_model(m)
                try:
                    _st = llm_for.chat(
                        chat_ctx=ctx,
                        conn_options=_co,
                        extra_kwargs={"reasoning_effort": "none"},
                    )
                    _t0 = _t.time()
                    async for _ch in _st:
                        _delta = getattr(_ch, "choices", None)
                        if _delta and _delta[0].delta.content:
                            break
                    try:
                        await _st.aclose()
                    except Exception:
                        pass
                    print(f"[WARMUP] {m} ok in {_t.time()-_t0:.1f}s", flush=True)
                except Exception as _e:
                    print(f"[WARMUP] {m} fail {_e!r}", flush=True)
        except Exception as _e:
            print(f"[WARMUP] skipped: {_e!r}", flush=True)

    async def on_enter(self):
        import asyncio
        import time as _t

        from livekit.agents.utils import wait_for_track_publication

        asyncio.ensure_future(self._warmup_llm())
        room = getattr(self, "rtc_room", None)
        if room is not None:
            try:
                for _ in range(30):
                    if room.isconnected():
                        break
                    await asyncio.sleep(0.5)
                if room.isconnected():
                    await asyncio.wait_for(
                        wait_for_track_publication(
                            room,
                            kind=rtc.TrackKind.KIND_AUDIO,
                            wait_for_subscription=True,
                        ),
                        timeout=25,
                    )
                    print("[AGENT] sip audio track ready", flush=True)
                    await asyncio.sleep(1.0)
                    print("[AGENT] media bridge settled, saying greeting", flush=True)
                    # Delay so the callee has time to answer the phone.
                    # Mango accepts the SIP leg while the phone is still ringing
                    # and only forwards the agent's audio AFTER the callee answers,
                    # so speaking immediately truncates the greeting.
                    await asyncio.sleep(7.0)
                    print("[AGENT] 7s pre-greeting delay done, saying greeting", flush=True)
                else:
                    print("[AGENT] room never connected in 15s", flush=True)
            except Exception as e:
                print(f"[AGENT] track wait: {e}", flush=True)
        print("[AGENT] on_enter called, saying greeting", flush=True)
        _t0 = _t.time()
        await self.session.say(GREETING, allow_interruptions=False)
        self._metrics["greet_dur"] = _t.time() - _t0
        print(f"[AGENT] greeting said in {self._metrics['greet_dur']:.1f}s", flush=True)

    def _on_transcribed(self, ev) -> None:
        print(f"[STT] transcript={ev.transcript!r} final={ev.is_final}", flush=True)
        mango_phrases = (
            "пожалуйста, оставайтесь на линии",
            "перезвоните позже",
            "абонент разговаривает",
            "в настоящий момент",
            "оставайтесь на линии",
            "не может ответить",
        )
        if ev.is_final and ev.transcript:
            _t_low = ev.transcript.lower()
            if any(_p in _t_low for _p in mango_phrases):
                print(f"[STT] mango-phrase ignored: {ev.transcript!r}", flush=True)
                return
            self._transcripts.append(ev.transcript)
            self._transcripts = self._transcripts[-20:]
            self._metrics["last_user_t"] = time.time()
            phone = _phone_from_text(ev.transcript)
            if phone and not (
                _last_lead["phone"] == phone and time.time() - _last_lead["ts"] < 300
            ):
                blob = " ".join(self._transcripts)
                qm = re.search(r"(\d+)\s*(?:голов|цыпл)", blob)
                cm = re.search(r"(?:в город[еа]?|город)\s+([а-яё]{2,})", blob)
                import asyncio as _asyncio2

                _asyncio2.ensure_future(
                    save_lead(
                        phone=phone,
                        quantity=qm.group(1) if qm else "",
                        city=cm.group(1) if cm else "",
                        comment=ev.transcript,
                    )
                )
                print(f"[LEAD] detected phone={phone} -> save_lead queued", flush=True)

    def _on_user_state(self, ev) -> None:
        print(f"[STT] user_state={ev.new_state}", flush=True)

    def _on_agent_state(self, ev) -> None:
        print(f"[STATE] agent={ev.new_state}", flush=True)

    def _on_item(self, ev) -> None:
        item = ev.item
        role = getattr(item, "role", "?")
        text = getattr(item, "text", "") or getattr(item, "raw_text_content", "") or ""
        print(f"[ITEM] {role}: {str(text)[:200]}", flush=True)
        if role == "assistant" and not self._farewell_fired:
            low = text.lower()
            _lu = self._metrics.get("last_user_t")
            if _lu:
                self._metrics["resp_lat"].append(time.time() - _lu)
                self._metrics["last_user_t"] = None
                self._metrics["turns"] += 1
                print(
                    f"[METRICS] turn {self._metrics['turns']} resp_lat={self._metrics['resp_lat'][-1]:.1f}s",
                    flush=True,
                )
            if any(m in low for m in _FAREWELL_MARKERS):
                self._farewell_fired = True
                print(f"[CALL] farewell marker detected: {text[:80]!r}", flush=True)
                import asyncio as _asyncio3

                _asyncio3.ensure_future(_terminate_after_speech("farewell"))

    def _on_error(self, ev) -> None:
        print(f"[ERROR] src={type(ev.source).__name__} err={ev.error!r}", flush=True)


async def entrypoint(ctx):
    caller_phone = ""
    try:
        for p in ctx.room.remote_participants.values():
            if p.identity.startswith("sip_"):
                caller_phone = p.identity.replace("sip_", "")
                break
    except Exception:
        pass
    if not caller_phone:
        import re as _re

        m = _re.search(r"(\d{10,11})", ctx.room.name)
        caller_phone = m.group(1) if m else ""
    if caller_phone:
        print(f"[AGENT] detected caller phone={caller_phone}", flush=True)
    else:
        print(f"[AGENT] WARNING: no caller phone in room={ctx.room.name}", flush=True)

    dynamic_prompt = SYSTEM_PROMPT.format(
        caller_phone=caller_phone if caller_phone else "неизвестен",
        caller_phone_spoken=_fmt_phone_spoken(caller_phone) if caller_phone else "неизвестен",
    )

    load_faq_cache()
    agent = LevitanAgent(instructions=dynamic_prompt, caller_phone=caller_phone)
    agent.rtc_room = ctx.room
    _session_holder["session"] = None
    session = AgentSession(
        turn_handling={
            "endpointing": {"min_delay": 0.25, "max_delay": 3.0},
        }
    )
    session.on("user_input_transcribed", agent._on_transcribed)
    session.on("user_state_changed", agent._on_user_state)
    session.on("agent_state_changed", agent._on_agent_state)
    session.on("conversation_item_added", agent._on_item)
    session.on("error", agent._on_error)
    _session_holder["session"] = session
    _session_holder["agent"] = agent
    await session.start(agent=agent, room=ctx.room)


opts = ServerOptions(
    entrypoint_fnc=entrypoint,
    ws_url=LIVEKIT_URL,
    api_key=LIVEKIT_API_KEY,
    api_secret=LIVEKIT_API_SECRET,
    load_threshold=math.inf,
)
server = AgentServer.from_server_options(opts)

if __name__ == "__main__":
    server.run()
