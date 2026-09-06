"""Humanizer for Yandex TTS — synthetic breath (вздох) + natural-voice pauses.

Stdlib-only. Used by levitan_agent.YandexTTS.
"""

import re
import struct

_WORD = re.compile(r"[\w-]+")

_PAUSE_MARKERS = [
    "что",
    "и",
    "но",
    "а",
    "если",
    "когда",
    "который",
    "которая",
    "которое",
    "которые",
    "так как",
    "потому что",
    "чтобы",
    "поэтому",
    "при этом",
    "например",
    "конечно",
    "вообще",
    "значит",
    "кстати",
    "впрочем",
    "собственно",
    "получается",
    "наверное",
    "возможно",
    "скорее всего",
    "к слову",
    "повторюсь",
    "сами понимаете",
]

_MARKER_RE = re.compile(
    r"(?<![\S-])({})(?=\s)".format("|".join(re.escape(m) for m in _PAUSE_MARKERS))
)


def count_words(text: str) -> int:
    return len(_WORD.findall(text))


def humanize_text(text: str, max_words: int = 15, max_commas: int = 2) -> str:
    """Insert natural pauses (',') before conjunctions in long clauses.

    Long monotonous sentences (no commas, > max_words) sound robotic in
    Yandex TTS. We add up to max_commas commas before pause markers.
    Short sentences and already-punctuated text are left untouched.
    Also converts standalone digits to Russian words (ES-15: TTS hygiene).
    """
    text = _ru_number_to_words(text)
    out: list[str] = []
    for sentence in re.split(r"(?<=[.!?…])\s+", text.strip()):
        if not sentence.strip():
            continue
        if count_words(sentence) <= max_words or "," in sentence or "…" in sentence:
            out.append(sentence)
            continue
        added = 0
        for _ in range(max_commas):
            match = _MARKER_RE.search(sentence)
            if match is None:
                break
            start = match.start()
            prefix = sentence[:start].rstrip()
            if prefix and not prefix.endswith((",", "(", "—")):
                sentence = prefix + ", " + sentence[start:].lstrip()
                added += 1
        out.append(sentence)
    return " ".join(out)


# --- ES-15: RU number -> words (TTS hygiene, stdlib-only) ---
_ONES = ["", "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять"]
_TENS = [
    "",
    "десять",
    "двадцать",
    "тридцать",
    "сорок",
    "пятьдесят",
    "шестьдесят",
    "семьдесят",
    "восемьдесят",
    "девяносто",
]
_HUNDREDS = [
    "",
    "сто",
    "двести",
    "триста",
    "четыреста",
    "пятьсот",
    "шестьсот",
    "семьсот",
    "восемьсот",
    "девятьсот",
]
_TEENS = [
    "десять",
    "одиннадцать",
    "двенадцать",
    "тринадцать",
    "четырнадцать",
    "пятнадцать",
    "шестнадцать",
    "семнадцать",
    "восемнадцать",
    "девятнадцать",
]
_RUBLE_UNITS = ["рубль", "рубля", "рублей"]


def _ru_triple(n: int) -> str:
    """Convert 0-999 to Russian words."""
    if n == 0:
        return ""
    parts = []
    h, rem = divmod(n, 100)
    if h:
        parts.append(_HUNDREDS[h])
    if rem < 10:
        parts.append(_ONES[rem])
    elif 10 <= rem < 20:
        parts.append(_TEENS[rem - 10])
    else:
        t, o = divmod(rem, 10)
        parts.append(_TENS[t])
        if o:
            parts.append(_ONES[o])
    return " ".join(parts)


def _ru_number_to_words(text: str) -> str:
    """Replace standalone integer amounts (e.g. '1250 рублей') with RU words."""

    def _full(n: int) -> str:
        if n == 0:
            return "ноль"
        out = []
        tho, rem = divmod(n, 1000)
        if tho:
            # simple pluralization for "тысяча"
            if tho % 10 == 1 and tho % 100 != 11:
                thou = "тысяча"
            elif 2 <= tho % 10 <= 4 and not 12 <= tho % 100 <= 14:
                thou = "тысячи"
            else:
                thou = "тысяч"
            out.append(f"{_ru_triple(tho)} {thou}")
        if rem:
            out.append(_ru_triple(rem))
        return " ".join(out)

    def repl(m):
        num = int(m.group(1))
        unit = m.group(2) or ""
        words = _full(num)
        if unit:
            if unit.startswith("рубл"):
                if num % 10 == 1 and num % 100 != 11:
                    unit = "рубль"
                elif 2 <= num % 10 <= 4 and not 12 <= num % 100 <= 14:
                    unit = "рубля"
                else:
                    unit = "рублей"  # уже содержит 'й', не добавлять
            words = f"{words} {unit}"
        else:
            words = f"{words} "  # keep trailing space before next word
        return words

    return re.sub(r"\b(\d{1,9})\b\s*(рубл[еаяй]*|голов|штук)?", repl, text).replace("  ", " ")


def breath_pcm(dur: float = 0.8, sr: int = 48000, amp: float = 0.22) -> bytes:
    """Synthetic exhalation (вздох) — pink noise with breath envelope.

    Pink noise via Paul Kellet filter, quick attack (60ms) + exponential
    decay — reads as a soft inhale/exhale before speech.
    """
    n = max(int(dur * sr), 1)
    attack = max(int(0.06 * sr), 1)
    tau = 0.30 * sr
    b0 = b1 = b2 = b3 = b4 = b5 = b6 = 0.0
    frames = bytearray()
    for i in range(n):
        white = __import__("random").random() * 2.0 - 1.0
        b0 = 0.99886 * b0 + white * 0.0555179
        b1 = 0.99332 * b1 + white * 0.0750759
        b2 = 0.96900 * b2 + white * 0.1538520
        b3 = 0.86650 * b3 + white * 0.3104856
        b4 = 0.55000 * b4 + white * 0.5329522
        b5 = -0.7616 * b5 - white * 0.0168980
        pink = b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362
        b6 = white * 0.115926
        pink *= 0.11
        env = min(i / attack, 1.0) * exp(-i / tau)
        sample = int(pink * amp * env * 32767)
        sample = max(-32768, min(32767, sample))
        frames += struct.pack("<h", sample)
    return bytes(frames)


from math import exp  # noqa: E402
