---
name: defuddle
description: Extract clean markdown content from web pages using Defuddle CLI. Removes navigation, ads, cookies, footer clutter. Use instead of web_extract when needing heavy cleanup of noisy pages (article blogs, docs, news). Saves 30-70% tokens on cluttered sites.
---

# Defuddle

Use Defuddle CLI to extract clean readable content from web pages.

**Installation (на 19.08.2026):**
```bash
npm install -g defuddle
# или для отката на стабильную: npm install -g defuddle@0.18
```

**Примечание:** на Node 26.7 defuddle 0.18.1 + 0.19.2 ломают парсинг URL напрямую (`Error: Parse Error: Expected HTTP/, RTSP/ or ICE/`). **Workaround:** сначала `curl` в файл, затем `defuddle parse file.html --md`.

**Use case:** статьи, блоги, документация с тяжёлым layout (vc.ru, Habr, Medium, dev.to). Для простых wiki/README часто `web_extract` быстрее.

## Usage (рабочий паттерн)

```bash
# 1. Скачать HTML
curl -sL "https://example.com/article" -o /tmp/page.html

# 2. Извлечь чистый markdown
defuddle parse /tmp/page.html --md -o /tmp/page.md

# 3. Прочитать результат
cat /tmp/page.md
```

## Альтернатива одной строкой (если URL-парсинг починят)

```bash
defuddle parse <url> --md
```

## Save to file / extract metadata

```bash
defuddle parse /tmp/page.html --md -o content.md
defuddle parse /tmp/page.html -p title
defuddle parse /tmp/page.html -p description
defuddle parse /tmp/page.html --json  # структурированный вывод с метаданными
```

## Когда НЕ использовать

- URL заканчивается на `.md` — уже markdown, читать напрямую (`read_file` или `curl | cat`)
- Простые API/JSON-эндпоинты — `curl` + `jq` быстрее
- Внутренние страницы, требующие авторизации — нет cookie/auth через defuddle

## Troubleshooting

- `Error: Parse Error: Expected HTTP/, RTSP/ or ICE/` — Node 26.7 incompatibility. Workaround: `curl -o file.html && defuddle parse file.html`.
- Пустой вывод — проверь что HTML не пустой (`ls -la file.html`, `head file.html`).
- Сайт блокирует — добавь User-Agent: `curl -sL -A "Mozilla/5.0 ..."`.