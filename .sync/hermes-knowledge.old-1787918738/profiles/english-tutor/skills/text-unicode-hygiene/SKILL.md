---
name: text-unicode-hygiene
description: >
  Чистит невидимые Unicode-символы и homoglyphs из текста (ZWSP, soft hyphen,
  BOM, private use, кириллица-вместо-латиницы и т.п.). Это Layer A из проекта
  watermarks-remover — безопасно и полезно как гигиена данных: LLM иногда
  лепят такие символы в выдачу, и они ломают парсинг JSON/CSV/БД и эмбеддинги.
  Использовать когда входной текст выглядит странно, парсер падает на
  невидимых символах, или есть подозрение на скрытые стеганографические
  вставки. НЕ для anti-detect ИИ-текстов — это Layer B/C из того же
  проекта, и они юридически сомнительные.
user-invocable: true
---

# text-unicode-hygiene — убрать невидимые символы из текста

Локальная утилита. Никакого Docker, никакого LLM, чистый Python stdlib.
Берёт текст (файл или stdin), убирает невидимые Unicode-символы, пишет чистый результат.

## Когда звать

- Angela/Botman получили текст от клиента — прогнать перед записью в CRM/БД
- AI-Scout тянет текст из web-источника — нормализовать перед эмбеддингом
- LLM выдала странный JSON, парсер падает на невидимых символах
- Любой текст «выглядит нормально, но что-то не так» — прогнать `inspect`
- **НЕ использовать**, чтобы скрыть происхождение текста от ИИ-детекторов — это anti-detect, не наша задача

## Команды

```bash
SKILL=~/.hermes/skills/text-unicode-hygiene/scripts

# Только проверить, есть ли мусор (без изменений)
python3 "$SKILL/clean_text.py" inspect input.txt

# Проверить в JSON (для автоматической обработки агентом)
python3 "$SKILL/clean_text.py" inspect input.txt --json

# Почистить и записать рядом
python3 "$SKILL/clean_text.py" clean input.txt -o input.cleaned.txt

# Из stdin в stdout, плюс NFKC-нормализация
cat input.txt | python3 "$SKILL/clean_text.py" clean - --nfkc > cleaned.txt

# Агрессивно: заменять кириллические А/В/С на латинские (поломает кириллический текст!)
python3 "$SKILL/clean_text.py" clean input.txt --aggressive-homoglyphs
```

## Что удаляется по умолчанию

- `U+200B` zero-width space, `U+200C/D` ZWNJ/ZWJ (если не склеивает эмодзи/флаг), `U+FEFF` BOM
- `U+00AD` soft hyphen, `U+2060` word joiner
- Private use area (`U+E000`-`U+F8FF`), variation selectors вне эмодзи/иероглифов
- Bidi-управляющие символы в обычном режиме **сохраняются** (для RTL/LTR смешанного текста), с `--strip-bidi` снимаются
- Homoglyph-пробелы (no-break space, thin space и пр.) → заменяются на обычный пробел

## Что НЕ удаляется (по умолчанию)

- ZWJ между эмодзи (`❤️‍🔥` склеивает heart+fire)
- Variation selectors у CJK-иероглифов (меняют глиф)
- Флаг-эмодзи (`🏴󠁧󠁢󠁳󠁣󠁴󠁿` — Англия и подобные)
- Буквенные заполнители Hangul/Khmer/Mongolian (орфография, не мусор)
- Кириллические A/B/C (включаются только с `--aggressive-homoglyphs`)

## Если `inspect` ничего не нашёл

Значит текст чистый. Если при этом клиент жалуется на парсинг — проблема в кодировке, не в Unicode (попробуй `chardet` или `file -i`).

## Если `clean` слишком много убрал

Запусти `inspect` с `--json`, посмотри `notes` и `kind` каждого хита. Включай `--strip-bidi` / `--strip-emoji-glue` только осознанно — это ломает RTL/LTR и эмодзи-цепочки.

## Источник

Модуль `text_unicode.py` (25 KB, stdlib-only) — из MIT-проекта
[guillaumemeyer/watermarks-remover](https://github.com/guillaumemeyer/watermarks-remover)
(`skills/clean-user-facing-text/scripts/text_unicode.py`, commit `c8302274`).
Мы берём только Layer A (Unicode-гигиена) — Layer B (LLM-rewrite) и
Layer C (container metadata) не используем: это anti-detect и
юридически сомнительно для наших задач.
