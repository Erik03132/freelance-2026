#!/usr/bin/env python3
"""
Сборка прод-версии ai-bureau.online из согласованных макетов Stitch.

Что делает:
  1. берёт 12 макетов из docs/roadmap/stitch/final/*.html;
  2. раскладывает их по адресам прода (см. PAGES);
  3. переписывает относительные ссылки (home.html и т.п.) в абсолютные пути;
  4. добавляет canonical, OG, twitter, favicon, theme-color в каждую страницу;
  5. на главной подключает ссылки «Подробнее» к страницам услуг;
  6. приводит шапку к sticky-виду и подвал к единому виду (как на ai-traffic-pro);
  7. генерирует sitemap.xml на 12 адресов.

Примеры:
  python3 docs/roadmap/stitch/build_prod.py --out /tmp/aib-prod2 --dry-run
  python3 docs/roadmap/stitch/build_prod.py --out /tmp/aib-prod2

Коды выхода: 0 — успех, 3 — нет входных файлов, 4 — неверные аргументы,
             5 — проверка результата не прошла.
"""

import argparse
import os
import re
import sys

SRC_DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "final")
BASE = "https://ai-bureau.online"

# макет -> (путь в проде, URL, заголовок для OG/sitemap)
PAGES = [
    ("home.html", "index.html", "/", "home"),
    ("agents.html", "services/ai-agents/index.html", "/services/ai-agents/", "service"),
    ("rag.html", "services/rag/index.html", "/services/rag/", "service"),
    (
        "document-automation.html",
        "services/document-automation/index.html",
        "/services/document-automation/",
        "service",
    ),
    ("chatbots.html", "services/chatbots/index.html", "/services/chatbots/", "service"),
    (
        "private-models.html",
        "services/private-models/index.html",
        "/services/private-models/",
        "service",
    ),
    ("ai-audit.html", "services/ai-audit/index.html", "/services/ai-audit/", "service"),
    ("blog.html", "blog/index.html", "/blog/", "page"),
    ("author.html", "author/index.html", "/author/", "page"),
    ("privacy.html", "privacy.html", "/privacy.html", "page"),
    ("offer.html", "offer.html", "/offer.html", "page"),
    ("consent.html", "consent.html", "/consent.html", "page"),
]

# относительные ссылки макетов -> абсолютные пути прода
LINK_MAP = {
    "home.html": "/",
    "blog.html": "/blog/",
    "author.html": "/author/",
    "privacy.html": "/privacy.html",
    "offer.html": "/offer.html",
    "consent.html": "/consent.html",
    "agents.html": "/services/ai-agents/",
    "rag.html": "/services/rag/",
    "document-automation.html": "/services/document-automation/",
    "chatbots.html": "/services/chatbots/",
    "private-models.html": "/services/private-models/",
    "ai-audit.html": "/services/ai-audit/",
}

# порядок карточек услуг на главной (совпадает с порядком в макете)
HOME_SERVICES = [
    "/services/ai-agents/",
    "/services/rag/",
    "/services/document-automation/",
    "/services/chatbots/",
    "/services/private-models/",
    "/services/ai-audit/",
]

HEAD_EXTRA = """<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="AI Bureau">
<meta property="og:locale" content="ru_RU">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{base}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#F3EFE7">
<link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48">
<link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180">
"""

HOME_VERIFY = """<meta name="google-site-verification" content="GaN9-C8adDGu08r6Tgak2g6cfiLLcZtlXLU8WQlq8XQ">
<meta name="yandex-verification" content="4ad016e79407c113">
"""

# Общие стили прода: липкая шапка и единый подвал. Вставляются в каждую страницу
# последним блоком <style>, поэтому перекрывают постраничные правила.
SITE_CSS = """<style id="site-shared">
/* шапка: фиксированная, всегда сверху */
header.topbar{position:fixed;top:0;left:0;right:0;z-index:60;background:rgba(243,239,231,.9);-webkit-backdrop-filter:saturate(160%) blur(14px);backdrop-filter:saturate(160%) blur(14px);border-bottom:1px solid var(--line,#DED7CC);padding:14px max(64px,calc((100vw - 1240px)/2))}
body{padding-top:80px}
[id]{scroll-margin-top:96px}
/* CTA: основная кнопка Telegram — бежевая, а не терракотовая */
.cta .btn--signal{background:var(--signal,#9e2a2b);color:var(--line,#DED7CC);border-color:var(--line,#DED7CC)}
.cta .btn--signal:hover{background:#fff;color:var(--ink,#1f2937)}
/* подвал */
footer{background:var(--surface,#fff);color:var(--ink,#1f2937);border-top:1px solid var(--line,#DED7CC);padding:56px 0 40px}
footer .f-grid{display:grid;grid-template-columns:5fr 4fr 3fr;gap:56px 40px}
footer .f-col{min-width:0}
footer .f-col--brand{display:flex;flex-direction:column;justify-content:space-between;gap:36px}
footer .f-brand{display:inline-flex;align-items:center;font-weight:700;letter-spacing:.12em;font-size:14px}
footer .f-brand span{display:inline-block;width:9px;height:9px;background:var(--signal,#9e2a2b);margin-right:10px}
footer .f-tag{margin-top:16px;color:var(--ink-soft,#4A4640);font-size:14px;max-width:32ch}
footer .f-copy{font:500 11px/1.5 "JetBrains Mono",ui-monospace,monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--muted,#6E675F)}
footer .f-h{display:block;font:500 11px/1.2 "JetBrains Mono",ui-monospace,monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--signal,#9e2a2b);margin-bottom:14px}
footer .f-list{display:flex;flex-direction:column;gap:9px}
footer .f-list a{font-size:14px;color:var(--ink-soft,#4A4640)}
footer .f-list a:hover,footer .f-accent:hover{color:var(--signal,#9e2a2b)}
footer .f-accent{color:var(--signal,#9e2a2b);font-size:14px}
footer .f-sub{display:flex;flex-direction:column;gap:7px;margin-top:12px}
footer .f-sub a{font-size:13px;color:var(--muted,#6E675F);padding-left:12px;border-left:1px solid var(--line,#DED7CC)}
footer .f-group{margin-top:28px}
footer .f-note{display:block;font-size:14px;line-height:1.5;color:var(--ink-soft,#4A4640)}
@media(max-width:900px){footer .f-grid{grid-template-columns:1fr 1fr}footer .f-col--brand{grid-column:1/-1;gap:24px}}
@media(max-width:640px){footer{padding:40px 0 32px}footer .f-grid{grid-template-columns:1fr;gap:32px}}
</style>"""


def title_of(html: str) -> str:
    m = re.search(r"<title>(.*?)</title>", html, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else "AI Bureau"


def desc_of(html: str) -> str:
    m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html)
    return m.group(1).strip() if m else "AI Bureau — внедрение ИИ в бизнес-процессы."


def rewrite_links(html: str) -> str:
    def sub(m):
        val = m.group(1)
        if val in LINK_MAP and not val.startswith(("http", "#", "mailto:", "tel:")):
            return f'href="{LINK_MAP[val]}"'
        base, _, frag = val.partition("#")
        if base in LINK_MAP and frag:
            return f'href="{LINK_MAP[base]}#{frag}"'
        return m.group(0)

    return re.sub(r'href="([^"]+)"', sub, html)


def strip_old_canonical(html: str) -> str:
    return re.sub(r'\n?<link rel="canonical" href="[^"]*">', "", html)


def inject_shared_css(html: str) -> str:
    """Идемпотентно вставляет общий блок стилей (липкая шапка + подвал)."""
    html = re.sub(r'<style id="site-shared">.*?</style>\n?', "", html, flags=re.S)
    return html.replace("</head>", SITE_CSS + "</head>", 1)


def inject_head(html: str, url: str, title: str, desc: str, extra: str = "") -> str:
    extra = extra or HEAD_EXTRA.format(url=BASE + url, title=title, desc=desc, base=BASE)
    html = html.replace("</head>", extra + "</head>", 1)
    return inject_shared_css(html)


def link_home_services(html: str) -> str:
    """Подставляет адреса услуг в шесть ссылок «Подробнее» в блоке услуг."""
    needle = '<a href="#contact" style="font-size: 12px; text-decoration: underline; color: var(--muted);">Подробнее</a>'
    out, pos = [], 0
    for i, slug in enumerate(HOME_SERVICES):
        found = html.find(needle, pos)
        if found < 0:
            raise SystemExit(f"ERROR: не найдена ссылка «Подробнее» №{i + 1} в блоке услуг")
        out.append(html[pos:found])
        out.append(
            needle.replace('href="#contact"', f'href="{slug}"').replace(
                ">Подробнее<", ">Подробнее об услуге<"
            )
        )
        pos = found + len(needle)
    out.append(html[pos:])
    return "".join(out)


HOME_BLOG_POSTS = [
    "/blog/#post-10",
    "/blog/#post-9",
    "/blog/#post-8",
]


def fix_home_nav(html: str) -> str:
    """Меню главной: логотип -> /, Блог -> /blog/, О нас -> /author/."""
    html = re.sub(
        r'(<header[^>]*>.*?<a class="brand" href=")#main(")',
        r"\g<1>/\g<2>",
        html,
        count=1,
        flags=re.S,
    )
    html = re.sub(
        r'(<nav[^>]*>.*?)(href="#blog")(.*?</nav>)',
        r'\g<1>href="/blog/"\g<3>',
        html,
        count=1,
        flags=re.S,
    )
    html = re.sub(
        r'(<nav[^>]*>.*?)(href="#about")(.*?</nav>)',
        r'\g<1>href="/author/"\g<3>',
        html,
        count=1,
        flags=re.S,
    )
    return html


def fix_home_blog_cards(html: str) -> str:
    """Карточки блога на главной ведут на конкретные посты; добавляет ссылку «Все разборы»."""
    m = re.search(r'(<section[^>]*\sid="blog"[^>]*>.*?</section>)', html, re.S)
    if not m:
        raise SystemExit("ERROR: не найдена секция blog на главной")
    section = m.group(1)
    cards = re.findall(r'<a class="card blog-card" href="#contact">', section)
    if len(cards) != len(HOME_BLOG_POSTS):
        raise SystemExit(
            f"ERROR: в секции blog {len(cards)} карточек, ожидалось {len(HOME_BLOG_POSTS)}"
        )

    pos = 0
    out = []
    for slug in HOME_BLOG_POSTS:
        needle = '<a class="card blog-card" href="#contact">'
        found = section.find(needle, pos)
        out.append(section[pos:found])
        out.append(f'<a class="card blog-card" href="{slug}">')
        pos = found + len(needle)
    out.append(section[pos:])
    new_section = "".join(out)

    # добавляем ссылку «Все разборы» после закрывающего </div> сетки
    new_section = re.sub(
        r"(</div>\s*)(</div>\s*</section>)",
        r'\g<1><div style="margin-top: 24px;"><a class="btn" href="/blog/" style="display: inline-flex;">Все разборы <span aria-hidden="true" style="margin-left: 6px;">→</span></a></div>\g<2>',
        new_section,
        count=1,
        flags=re.S,
    )
    return html[: m.start()] + new_section + html[m.end() :]


SERVICES = [
    ("ai-agents", "Автономные ИИ-сотрудники"),
    ("rag", "Поиск и ответы по данным"),
    ("document-automation", "OCR + RAG для договоров"),
    ("chatbots", "Боты от заявки до продажи"),
    ("private-models", "Локальные модели в контуре"),
    ("ai-audit", "Первичный аудит и карта ROI"),
]

FOOTER_SERVICES = [
    ("/services/ai-agents/", "Автономные ИИ-сотрудники"),
    ("/services/rag/", "Поиск и ответы по данным"),
    ("/services/document-automation/", "OCR + RAG для договоров"),
    ("/services/chatbots/", "Боты от заявки до продажи"),
    ("/services/private-models/", "Локальные модели в контуре"),
    ("/services/ai-audit/", "Первичный аудит и карта ROI"),
]

FOOTER_BLOG = [
    ("/blog/#post-10", "Сколько стоит ИИ-проект в 2026"),
    ("/blog/#post-9", "Поиск по документам: ответ со ссылкой"),
    ("/blog/#post-8", "Агент или бот: кто квалифицирует заявку"),
]

FOOTER_LEGAL = [
    ("/privacy.html", "Политика конфиденциальности"),
    ("/consent.html", "Согласие на обработку персональных данных"),
    ("/offer.html", "Договор-оферта"),
]


def _links(items) -> str:
    return "".join(f'<a href="{u}">{t}</a>' for u, t in items)


FOOTER_HTML = (
    '<footer>\n<div class="wrap">\n<div class="f-grid">'
    '<div class="f-col f-col--brand"><div>'
    '<a class="f-brand" href="/"><span aria-hidden="true"></span>AI BUREAU</a>'
    '<p class="f-tag">Внедряем искусственный интеллект. Освобождаем время.</p></div>'
    '<span class="f-copy">AI-BUREAU · 2026 · Все права защищены</span></div>'
    '<div class="f-col">'
    '<span class="f-h">[01 / Услуги]</span>'
    f'<nav class="f-list" aria-label="Услуги">{_links(FOOTER_SERVICES)}</nav>'
    '<div class="f-group">'
    '<a class="f-accent" href="/blog/">Блог: разборы и инструкции →</a>'
    f'<div class="f-sub">{_links(FOOTER_BLOG)}</div></div></div>'
    '<div class="f-col">'
    '<span class="f-h">[02 / Правовая информация]</span>'
    f'<nav class="f-list" aria-label="Правовая информация">{_links(FOOTER_LEGAL)}</nav>'
    '<div class="f-group"><span class="f-h">[03 / Контакты]</span><div class="f-list">'
    '<a href="https://t.me/erik03132" target="_blank" rel="noopener">Telegram: @erik03132</a>'
    '<a href="mailto:info@ai-traffic-pro.ru">Email: info@ai-traffic-pro.ru</a>'
    '<a href="tel:+74959234644">Телефон: +7 (495) 923-46-44</a></div></div>'
    '<div class="f-group"><span class="f-h">[04 / Реквизиты]</span>'
    '<span class="f-note">ИП Марченко Д. Н.</span>'
    '<span class="f-note">ИНН 770304789944 · ОГРНИП 326508100653064</span>'
    '<span class="f-note">Московская область, Раменский муниципальный округ, г. Раменское</span></div>'
    '<div class="f-group"><a class="f-accent" href="/author/">Автор материалов: Игорь Васин</a></div>'
    "</div></div></div>\n</footer>"
)


def fix_generic_nav(html: str) -> str:
    """В меню внутренних страниц пункт «Услуги» ведёт на главную к блоку услуг."""
    return re.sub(
        r'(<nav[^>]*>.*?)(<a[^>]*href=")/(")([^<]*Услуги[^<]*)(</a>.*?</nav>)',
        r"\g<1>\g<2>/#services\g<3>\g<4>\g<5>",
        html,
        count=1,
        flags=re.S,
    )


def add_crosslinks(html: str, slug: str) -> str:
    """Блок «Другие услуги» на странице услуги: переходы на соседние услуги и блог."""
    others = [(s, t) for s, t in SERVICES if s != slug]
    cards = "".join(
        f'<a class="card" href="/services/{s}/"><span class="mono eyebrow">УСЛУГА</span>'
        f'<h3>{t}</h3><span class="tags">Смотреть →</span></a>'
        for s, t in others[:5]
    )
    block = (
        '<section class="wrap" aria-labelledby="other-services">'
        '<div class="section-head"><div><span class="mono eyebrow">[ДРУГИЕ УСЛУГИ]</span>'
        '<h2 id="other-services">С чем ещё помогаем</h2></div>'
        "<p>Если задача шире одной услуги, начните с аудита процесса — он покажет, что даст эффект первым.</p></div>"
        f'<div class="grid-3">{cards}</div>'
        '<div style="margin-top:24px"><a class="btn" href="/blog/" style="display:inline-flex">'
        'Все разборы <span aria-hidden="true" style="margin-left:6px">→</span></a></div>'
        "</section>"
    )
    if '<section id="request"' in html:
        return html.replace('<section id="request"', block + '\n<section id="request"', 1)
    if "</main>" in html:
        return html.replace("</main>", block + "</main>", 1)
    raise SystemExit("ERROR: не найдено место для блока 'Другие услуги'")


def fix_cta_panel(html: str) -> str:
    """Блог/автор/юрстраницы: CTA обёрнут в .wrap (вместо .panel) и 'Все услуги' -> /#services."""
    html = re.sub(
        r'(<section[^>]*\sid="request"[^>]*>\s*)<div class="panel">',
        r'\g<1><div class="wrap">',
        html,
        count=1,
        flags=re.S,
    )
    html = re.sub(
        r'href="/">Все услуги</a>',
        r'href="/#services">Все услуги</a>',
        html,
    )
    return html


def replace_footer(html: str) -> str:
    """Ставит единый подвал (структура как на ai-traffic-pro) вместо макетного."""
    new, found = re.subn(
        r"<footer(?:\s[^>]*)?>.*?</footer>", lambda _: FOOTER_HTML, html, count=1, flags=re.S
    )
    if not found:
        raise SystemExit("ERROR: не найден <footer> для замены")
    return new


def merge_sitemap(out: str, text: str) -> str:
    """Сохраняет в sitemap адреса, которых нет в PAGES (опубликованные статьи)."""
    path = os.path.join(out, "sitemap.xml")
    if not os.path.isfile(path):
        return text
    old = open(path, encoding="utf-8").read()
    known = {BASE + url for _, _, url, _ in PAGES}
    extra = []
    for block in re.findall(r"<url>.*?</url>", old, re.S):
        m = re.search(r"<loc>([^<]+)</loc>", block)
        if m and m.group(1).strip() not in known:
            extra.append("  " + block.strip())
    if not extra:
        return text
    return text.replace("</urlset>", "\n".join(extra) + "\n</urlset>")


def build(src: str, out: str, dry: bool) -> int:
    if not os.path.isdir(src):
        print(f"ERROR: нет каталога макетов: {src}", file=sys.stderr)
        return 3
    missing = [f for f, *_ in PAGES if not os.path.isfile(os.path.join(src, f))]
    if missing:
        print(f"ERROR: нет макетов: {', '.join(missing)}", file=sys.stderr)
        return 3

    written = []
    for fname, rel, url, kind in PAGES:
        raw = open(os.path.join(src, fname), encoding="utf-8").read()
        title = title_of(raw).replace("— отдельная услуга —", "—").replace("  ", " ")
        desc = desc_of(raw)
        existing = os.path.join(out, rel)
        # опубликованные статьи живут в blog/index.html — не перезаписываем макетом
        if (
            rel == "blog/index.html"
            and os.path.isfile(existing)
            and 'id="post-live-' in open(existing, encoding="utf-8").read()
        ):
            html = inject_shared_css(
                fix_cta_panel(
                    fix_generic_nav(replace_footer(open(existing, encoding="utf-8").read()))
                )
            )
            dst = existing
            written.append((rel, url, len(html)))
            if dry:
                print(
                    f"  {fname:24} -> {rel:40} {len(html):>7} байт (есть публикации: макет не применяется)"
                )
            else:
                with open(dst, "w", encoding="utf-8") as f:
                    f.write(html)
            continue
        html = rewrite_links(strip_old_canonical(raw))
        if fname == "home.html":
            html = link_home_services(html)
            html = fix_home_nav(html)
            html = fix_home_blog_cards(html)
            html = replace_footer(html)
            html = inject_head(
                html,
                url,
                title,
                desc,
                HOME_VERIFY + HEAD_EXTRA.format(url=BASE + url, title=title, desc=desc, base=BASE),
            )
        # на /privacy.html, /offer.html, /consent.html canonical ставим заново тем же адресом
        else:
            html = fix_generic_nav(html)
            html = fix_cta_panel(html)
            html = replace_footer(html)
            if url.startswith("/services/"):
                html = add_crosslinks(html, url.strip("/").split("/")[-1])
            html = inject_head(html, url, title, desc)
        dst = os.path.join(out, rel)
        written.append((rel, url, len(html)))
        if dry:
            print(f"  {fname:24} -> {rel:40} {len(html):>7} байт")
            continue
        os.makedirs(os.path.dirname(dst) or out, exist_ok=True)
        with open(dst, "w", encoding="utf-8") as f:
            f.write(html)

    sitemap = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for _, _, url, kind in PAGES:
        prio = {"home": "1.0", "service": "0.8", "page": "0.6"}[kind]
        sitemap += [
            "  <url>",
            f"    <loc>{BASE}{url}</loc>",
            "    <lastmod>2026-11-27</lastmod>",
            "    <changefreq>monthly</changefreq>",
            f"    <priority>{prio}</priority>",
            "  </url>",
        ]
    sitemap.append("</urlset>")
    sitemap_text = "\n".join(sitemap) + "\n"

    if dry:
        print(f"  sitemap.xml: {len(PAGES)} адресов (dry-run, не записан)")
        return 0

    sitemap_text = merge_sitemap(out, sitemap_text)
    with open(os.path.join(out, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap_text)

    # favicon.ico, apple-touch-icon.png, og-image.png, robots.txt, 404.html уже в клоне
    print(f"записано страниц: {len(written)}, sitemap: {len(PAGES)} адресов")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        add_help=True, description="Сборка прод-версии ai-bureau.online из макетов Stitch"
    )
    ap.add_argument(
        "--src",
        default=SRC_DEFAULT,
        help="каталог макетов (по умолчанию docs/roadmap/stitch/final)",
    )
    ap.add_argument("--out", required=True, help="каталог назначения (клон прод-репозитория)")
    ap.add_argument("--dry-run", action="store_true", help="только показать, что будет сделано")
    a = ap.parse_args()
    if not os.path.isdir(a.out):
        print(f"ERROR: нет каталога назначения: {a.out}", file=sys.stderr)
        return 4
    return build(a.src, a.out, a.dry_run)


if __name__ == "__main__":
    sys.exit(main())
