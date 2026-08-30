#!/usr/bin/env python3
"""
kwork_finder.py — ночной скрайпер Kwork (SPA) с многофакторным скорингом кворков.

КООРДИНАЛЬНО ПЕРЕРАБОТАННЫЙ ПОДХОД (v2):
Старый пайплайн брал всё, что попало под regex "сладкого сегмента", и игнорировал
(1) число уже поданных заявок, (2) качество/историю заказчика, (3) реальный матч
наших навыков с ТЗ (отсюда баги вроде "создать видео" в откликах).

Новый подход — скоринг по 4 осям, решение A/B/X:
  - skill_match  (0..100) : % покрытия ЯДРА требований нашим стеком (SSoT: candidate_profile.txt)
  - competition  (0..100) : чем МЕНЬШЕ заявок, тем ВЫШЕ (защита от "задавлено 80+ конкурентами")
  - client       (0..100) : кол-во заказов заказчика + рейтинг + верификация
  - budget       (0..100) : бюджет против якоря (демпинг отсекаем)
HARD_EXCLUDE: видео/монтаж/3D/логотипы/мобилка/игры/1С-внедрение → мгновенный X.

РЕШЕНИЕ:
  A = берём → пишем ЧЕРНОВИК (ждёт ручного апрува Игоря, анти-бан).
  B = кандидат на рассмотрение (матч 40-59% ИЛИ 50-80 заявок ИЛИ слабый клиент)
      → НЕ генерим черновик, только заносим в leads как "решает Игорь".
  X = отсев (причина в логе/leads).

Поток: Sherlock(поиск+скоринг) -> Batrak(черновик v3 для A) -> Chief(сборка в outbox).
РЕЖИМ: только поиск + черновик. НИКАКОЙ auto-send (анти-бан HH/Kwork).
Guard: free-only. Никаких платных LLM-вызовов. Только локальный рендер + regex.

Источники истины:
  - .hermes/profiles/batrak/JOBHUNT.md (правило 60%, сладкий сегмент)
  - projects/hh-ai-agent/prompts/candidate_profile.txt (наш стек — SSoT навыков)
  - projects/hh-ai-agent/AGENTS.md (стандарт письма v3)
  - docs/adr/007-nightly-kwork-pipeline.md
"""
from __future__ import annotations
import os, sys, re, json, sqlite3, argparse, random, time, html
from datetime import datetime, timezone

# --- Пути (SSoT) ---------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTBOX = os.path.join(ROOT, "projects", "hh-ai-agent", "docs", "outbox")
LEADS = os.path.join(ROOT, "jobhunter", "leads.md")
DB = os.path.join(ROOT, "freelance-agent", "data", "db", "freelance.db")
COOKIES = os.path.join(ROOT, "freelance-agent", "data", "cookies", "kwork.json")

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
# Пул User-Agent для ротации (анти-бан Qrator)
UA_POOL = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0 Safari/537.36",
]
def rand_ua() -> str:
    return random.choice(UA_POOL)

# ---------------------------------------------------------------------------
# КОНФИГ СКОРИНГА (все пороги — через CLI-флаги, дефолты из правила 60%)
# ---------------------------------------------------------------------------
DEFAULTS = dict(
    min_skill_a=60,        # >= -> претендуем (ядро)
    min_skill_b=40,        # 40..59 -> кандидат; <40 -> отсев
    max_proposals_x=20,    # >20 заявок -> мгновенный отсев (лимит Игоря)
    max_proposals_b=15,    # 15..20 -> кандидат (B); <=14 -> потенциально A
    min_client_orders_good=5,  # >=5 заказов у заказчика -> хорошо
    min_budget=1500,       # якорь бюджета (руб)
    rate_per_hour=1500,    # якорь цены (руб/ч) для оценки стоимости
    final_threshold_a=60,  # итоговый скор для решения A
    w_skill=0.45, w_comp=0.25, w_client=0.20, w_budget=0.10,
)

# ---------------------------------------------------------------------------
# МАТРИЦА НАВЫКОВ (SSoT: candidate_profile.txt)
# canonical_skill -> список regex-фрагментов (re.I). Что МОЖЕМ.
# ---------------------------------------------------------------------------
OUR_SKILLS = {
    "python":        [r"python", r"\bпитон\b", r"\bпайтон\b"],
    "llm":           [r"\bllm\b", r"\bgpt\b", r"chatgpt", r"нейросет", r"нейросеть",
                     r"openai", r"\bclaude\b", r"gemini", r"deepseek", r"kimi",
                     r"промпт[- ]?инж", r"prompt"],
    "rag":           [r"\brag\b", r"эмбеддинг", r"embedding", r"векторн", r"vector",
                     r"семантич", r"rerank", r"reranking"],
    "telegram_bot":  [r"telegram[- ]?бот", r"телеграм[- ]?бот", r"aiogram",
                     r"python[- ]?telegram[- ]?bot", r"чат[- ]?бот", r"chatbot",
                     r"\bбот\b", r"бота\b", r"ботов"],
    "bitrix24":      [r"bitrix", r"битрикс", r"\bcrm\b"],
    "mango_voice":   [r"mango", r"телефон", r"обзвон", r"голосов", r"\bvoip\b",
                     r"ттс", r"tts", r"стт", r"stt", r"speech"],
    "parsing":       [r"парсер", r"парсинг", r"скрейп", r"скрап", r"спарс",
                     r"выгрузк", r"сбор данн", r"парс"],
    "automation":    [r"автоматизац", r"скрипт", r"\brpa\b", r"интеграц",
                     r"автоматизир"],
    "api":           [r"\bapi\b", r"\brest\b", r"webhook", r"эндпоинт"],
    "web":           [r"лендинг", r"landing", r"\bсайт", r"веб[- ]?сайт", r"fastapi",
                     r"flask", r"дашборд", r"dashboard", r"веб[- ]?интерфейс",
                     r"вебка", r"frontend", r"фронт"],
    "sql":           [r"\bsql\b", r"база данн", r"postgres", r"sqlite", r"mongodb",
                     r"nosql", r"бд\b"],
    "docker":        [r"docker", r"контейнер"],
    "content_gen":   [r"генерац", r"постер", r"картинк", r"leonardo", r"контент",
                     r"промпт[- ]?дизайн", r"изображен"],
    "data_analysis": [r"аналитик", r"сводк", r"excel", r"google табл", r"метрик",
                     r"отчёт", r"отчет", r"дашборд"],
    "transcription": [r"транскриб", r"расшифр", r"whisper", r"транскрипц",
                     r"расшифровк", r"декодир"],
    "avito_vk":      [r"avito", r"\bвк\b", r"\bvk\b", r"маркетплейс", r"telegram[- ]?канал",
                     r"соцсет"],
    "ui_proto":      [r"stitch", r"google ai studio", r"прототип", r"макет", r"ui[- ]?макет",
                     r"figma[- ]?альтерн"],
}
# Что ТОЧНО НЕ МОЖЕМ (HARD_EXCLUDE) — мгновенный X, даже если матч высокий.
# (защита от бага "видео создавать" и пр.)
EXCLUDE_SKILLS = {
    "video":      [r"видео", r"видеоролик", r"ролик", r"reels", r"shorts",
                  r"тикток", r"монтаж", r"смонтир", r"motion", r"анимац",
                  r"ютуб", r"youtube", r"превью", r"закадров"],
    "3d":         [r"\b3d\b", r"моделирован", r"блендер", r"\bmaya\b", r"скульптур"],
    "logo_design":[r"логотип", r"logo", r"брендинг", r"фирменн", r"упаковк",
                  r"дизайн макет", r"айдентик"],
    "figma":      [r"figma", r"фотошоп", r"illustrator", r"редактор макет"],
    "mobile":     [r"мобильн", r"android", r"\bios\b", r"flutter", r"react native",
                  r"swift", r"kotlin", r"приложен"],
    "game_dev":   [r"\bигр", r"\bgame\b", r"unity", r"unreal", r"геймдев"],
    "hardcore_be":[r"senior\s+backend", r"lead\s+backend", r"hardcore", r"highload",
                  r"хайлоад", r"микросервис", r"распределён", r"enterprise",
                  r"легаси", r"legacy", r"1с\s+внедр", r"1с\s+программ",
                  r"erp\s+систем", r"bitrix24\s+коробк"],
    "copywriting":[r"копирайт", r"рерайт", r"нейминг", r"тексты для сайт"],
    "translation":[r"перевод", r"перевести текст", r"локализ"],
    "smm":        [r"\bsmm\b", r"ведение соцсет", r"таргет", r"таргетинг"],
    "photo":      [r"фотообработк", r"ретуш", r"обработк фото", r"фотошоп"],
}

COMPILED_OUR = {k: [re.compile(p, re.I) for p in v] for k, v in OUR_SKILLS.items()}
COMPILED_EXCLUDE = {k: [re.compile(p, re.I) for p in v] for k, v in EXCLUDE_SKILLS.items()}

# Внутренний якорь стоимости: 1500 руб/час.
RATE_PER_HOUR = 1500


# ---------------------------------------------------------------------------
# ИЗВЛЕЧЕНИЕ ПОЛЕЙ ИЗ ТЕКСТА КВОРКА
# ---------------------------------------------------------------------------
def extract_budget(text: str) -> float | None:
    """Ищем 'до N руб' / 'N ₽' / 'N руб' / 'N тыс'."""
    # сначала "тыс"/"к" (на Kwork часто "до 5 000" или "5к")
    m = re.search(r"(?:до\s+)?(\d[\d\s]*)\s*(?:тыс|\s*к\b)", text, re.I)
    if m:
        digits = re.sub(r"\s", "", m.group(1))
        try:
            return float(digits) * 1000
        except ValueError:
            pass
    m = re.search(r"(?:до\s+)?(\d[\d\s]*)\s*(?:руб|₽|rur)", text, re.I)
    if not m:
        return None
    digits = re.sub(r"\s", "", m.group(1))
    try:
        return float(digits)
    except ValueError:
        return None


def extract_proposals(text: str) -> int | None:
    """Число уже поданных предложений: 'Предложений: 12' / '12 предложений' / 'откликнулись N'."""
    # Kwork: "Предложений: N" или "Предложений N"
    m = re.search(r"Предложени(?:й|я|е)\s*[:\s]\s*(\d+)", text, re.I)
    if m:
        return int(m.group(1))
    # альтернативы
    m = re.search(r"(\d+)\s+предложени", text, re.I)
    if m:
        return int(m.group(1))
    m = re.search(r"откликн(?:улось|улись)\s+(\d+)", text, re.I)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)\s+отклик", text, re.I)
    if m:
        return int(m.group(1))
    return None


def extract_client_info(text: str) -> dict:
    """Качество заказчика со страницы кворка.
    Возвращает {orders, rating, verified, found}."""
    info = {"orders": None, "rating": None, "verified": False, "found": False}
    # Кол-во заказов: "Заказов на сайте: N" / "Выполнено заказов: N" / "N заказов"
    for pat in (r"Заказ(?:ов)?\s+на\s+сайте\s*[:\s]\s*(\d+)",
                r"Выполнено\s+заказ(?:ов)?\s*[:\s]\s*(\d+)",
                r"(\d+)\s+заказ(?:ов|а)?"):
        m = re.search(pat, text, re.I)
        if m:
            info["orders"] = int(m.group(1))
            info["found"] = True
            break
    # Рейтинг: ТОЛЬКО в явных конструкциях "Рейтинг: 4.8" / "★ 4.8" / "4.8 из 5",
    # чтобы не ловить числа типа "12 заказов".
    for pat in (r"рейтинг\s*[:\s]\s*(\d(?:\.\d)?)",
                r"[★â˜…]\s*(\d(?:\.\d)?)",
                r"(\d(?:\.\d)?)\s*(?:из|/)\s*5"):
        m = re.search(pat, text, re.I)
        if m:
            try:
                r = float(m.group(1))
                if 0 < r <= 5:
                    info["rating"] = r
                    info["found"] = True
                    break
            except ValueError:
                pass
    # Верификация
    if re.search(r"подтверждён", text, re.I) or re.search(r"verified", text, re.I):
        info["verified"] = True
        info["found"] = True
    return info


# ---------------------------------------------------------------------------
# СКОРИНГ
# ---------------------------------------------------------------------------
def score_skill_match(text: str) -> dict:
    """Возвращает match-метрики по ядру требований ТЗ."""
    our_hits, exclude_hits = [], []
    for skill, rxs in COMPILED_OUR.items():
        if any(rx.search(text) for rx in rxs):
            our_hits.append(skill)
    for skill, rxs in COMPILED_EXCLUDE.items():
        if any(rx.search(text) for rx in rxs):
            exclude_hits.append(skill)
    required = set(our_hits) | set(exclude_hits)
    if not required:
        # в ТЗ нет технических маркеров — неопределённо
        return {"match": None, "our": our_hits, "exclude": exclude_hits,
                "required": [], "missing": []}
    match = round(100.0 * len(our_hits) / len(required), 1)
    missing = [s for s in exclude_hits]  # то, чего нет у нас
    return {"match": match, "our": our_hits, "exclude": exclude_hits,
            "required": sorted(required), "missing": missing}


def score_competition(proposals: int | None) -> int:
    """0..100: чем меньше заявок, тем выше. None -> нейтрально 50."""
    if proposals is None:
        return 50
    if proposals <= 3:
        return 100
    if proposals <= 10:
        return 85
    if proposals <= 20:
        return 70
    if proposals <= 35:
        return 55
    if proposals <= 50:
        return 40
    if proposals <= 80:
        return 20
    return 5


def score_client(info: dict) -> int:
    """0..100 по заказам + рейтингу + верификации. Нет данных -> 50."""
    if not info.get("found"):
        return 50
    score = 40  # база за наличие данных
    orders = info.get("orders")
    if orders is not None:
        if orders >= 20:
            score += 35
        elif orders >= DEFAULTS["min_client_orders_good"]:
            score += 25
        elif orders >= 1:
            score += 10
        else:  # 0 заказов = риск
            score -= 15
    if info.get("verified"):
        score += 10
    rating = info.get("rating")
    if rating is not None:
        if rating >= 4.5:
            score += 15
        elif rating >= 4.0:
            score += 10
        elif rating < 3.0:
            score -= 20
    return max(0, min(100, score))


def score_budget(budget: float | None) -> int:
    """0..100: против якоря MIN_BUDGET. None -> 50."""
    if budget is None:
        return 50
    if budget >= DEFAULTS["min_budget"] * 3:
        return 100
    if budget >= DEFAULTS["min_budget"]:
        return 80
    if budget >= DEFAULTS["min_budget"] * 0.5:
        return 50
    return 10  # демпинг


def evaluate(job: dict, cfg: dict | None = None) -> dict:
    """Итоговый скоринг кворка -> решение A/B/X с причиной."""
    cfg = {**DEFAULTS, **(cfg or {})}
    title = job.get("title", "") or ""
    desc = job.get("desc", "") or ""
    text = (title + " " + desc)

    sm = score_skill_match(text)
    proposals = job.get("proposals")
    if proposals is None:
        proposals = extract_proposals(text)
        job["proposals"] = proposals
    client = job.get("client_info") or {}
    if not client:
        client = extract_client_info(text)
        job["client_info"] = client
    budget = job.get("budget")
    if budget is None:
        budget = extract_budget(text)
        job["budget"] = budget

    reasons = []

    # 0) HARD_EXCLUDE — мгновенный отсев (ДО защиты от ложных A)
    if sm["exclude"]:
        return _mk(
            decision="X",
            reason=f"HARD_EXCLUDE — не наш навык: {', '.join(sm['exclude'])}",
            sm=sm, proposals=proposals, client=client, budget=budget,
        )

    # 0.5) ЗАЩИТА ОТ ЛОЖНЫХ A (ADR-009): если у кворка нет реального ТЗ
    # (только заголовок, напр. "Работа без навыков"), матч недостоверен ->
    # это неопределённый матч -> B, а не фейковый A. Реальное desc
    # стягивается fetch_job_detail() в main() и переоценивается там же.
    real_desc = (job.get("desc") or "").strip()
    has_real_desc = len(real_desc) > len(title.strip()) + 20
    if not has_real_desc:
        return _mk(
            decision="B",
            reason=(f"Без реального ТЗ матч недостоверен "
                    f"({sm['match'] if sm['match'] is not None else '?'})% — на рассмотрение"),
            sm=sm, proposals=proposals, client=client, budget=budget,
        )

    # 1) матч неопределён (нет тех-маркеров)
    if sm["match"] is None:
        return _mk(
            decision="B",
            reason="ТЗ без технических маркеров — неопределённый матч, на рассмотрение",
            sm=sm, proposals=proposals, client=client, budget=budget,
        )

    # 2) матч < MIN_SKILL_B (40%) — отсев
    if sm["match"] < cfg["min_skill_b"]:
        return _mk(
            decision="X",
            reason=f"матч навыков {sm['match']:.0f}% < {cfg['min_skill_b']}% — не наш профиль",
            sm=sm, proposals=proposals, client=client, budget=budget,
        )

    # 3) задавлено конкурентами
    if proposals is not None and proposals > cfg["max_proposals_x"]:
        return _mk(
            decision="X",
            reason=f"заявок {proposals} > {cfg['max_proposals_x']} — задавлено конкурентами",
            sm=sm, proposals=proposals, client=client, budget=budget,
        )

    # 4) демпинг
    if budget is not None and budget < cfg["min_budget"] * 0.5:
        return _mk(
            decision="X",
            reason=f"бюджет {budget:.0f} ₽ — демпинг (< 50% якоря)",
            sm=sm, proposals=proposals, client=client, budget=budget,
        )

    # --- финальный скор ---
    s_skill = sm["match"]
    s_comp = score_competition(proposals)
    s_client = score_client(client)
    s_budget = score_budget(budget)
    final = (cfg["w_skill"] * s_skill + cfg["w_comp"] * s_comp +
             cfg["w_client"] * s_client + cfg["w_budget"] * s_budget)

    bad_client = (client.get("found") and
                  (client.get("orders") == 0 or
                   (client.get("rating") is not None and client["rating"] < 3.0)))

    # решение A vs B
    is_A = (
        sm["match"] >= cfg["min_skill_a"]
        and (proposals is None or proposals <= cfg["max_proposals_b"])
        and final >= cfg["final_threshold_a"]
        and not bad_client
    )
    if is_A:
        decision = "A"
        reasons.append(f"матч {s_skill:.0f}%≥{cfg['min_skill_a']}, заявок "
                       f"{proposals if proposals is not None else '?'}, "
                       f"финал {final:.0f}≥{cfg['final_threshold_a']}")
    else:
        decision = "B"
        bits = []
        if sm["match"] < cfg["min_skill_a"]:
            bits.append(f"матч {s_skill:.0f}%<{cfg['min_skill_a']}")
        if proposals is not None and proposals > cfg["max_proposals_b"]:
            bits.append(f"заявок {proposals}>{cfg['max_proposals_b']}")
        if bad_client:
            bits.append("слабый/рисковый заказчик")
        if final < cfg["final_threshold_a"]:
            bits.append(f"финал {final:.0f}<{cfg['final_threshold_a']}")
        reasons.append("кандидат: " + ", ".join(bits) + " — решает Игорь")
    reason = "; ".join(reasons)
    return _mk(decision, reason, sm, proposals, client, budget,
              final=round(final, 1))


def _decision(skill, competition, client, budget, decision, reason,
              sm, proposals, client_info, budget_val, final=None) -> dict:
    return {
        "skill": skill, "competition": competition, "client": client,
        "budget": budget, "final": final, "decision": decision,
        "reason": reason, "skill_detail": sm, "proposals": proposals,
        "client_info": client_info, "budget_val": budget_val,
    }


def _mk(decision, reason, sm, proposals, client, budget, final=None):
    """Удобная обёртка: считает числовые оси и зовёт _decision."""
    return _decision(
        skill=sm["match"], competition=score_competition(proposals),
        client=score_client(client), budget=score_budget(budget),
        decision=decision, reason=reason, sm=sm, proposals=proposals,
        client_info=client, budget_val=budget, final=final,
    )


# ---------------------------------------------------------------------------
# СКРЕЙПИНГ (Playwright headless, SPA) — анти-бан сохранён
# ---------------------------------------------------------------------------
def fetch_projects(limit_pages: int = 3, use_cookies: bool = True,
                   delay=(30, 60)) -> list[dict]:
    """Рендерим kwork.ru/projects. Возвращаем карточки с чтением proposals/client из cardText."""
    from playwright.sync_api import sync_playwright
    out = []
    launch_args = ["--no-sandbox", "--no-proxy-server", "--disable-dev-shm-usage"]
    with sync_playwright() as p:
        # NOTE: proxy=None заставляет Playwright читать системный прокси macOS
        # (часто мёртвый SOCKS) -> ERR_CONNECTION_REFUSED. Ходим напрямую
        # только через --no-proxy-server в launch_args (см. ADR-009).
        b = p.chromium.launch(headless=True, args=launch_args)
        ctx = b.new_context(user_agent=rand_ua())
        if use_cookies and os.path.exists(COOKIES):
            try:
                with open(COOKIES) as f:
                    ctx.add_cookies(json.load(f))
            except Exception as e:
                print(f"[warn] cookies load failed: {e}", file=sys.stderr)
        pg = ctx.new_page()
        for page in range(1, limit_pages + 1):
            url = "https://kwork.ru/projects" + (f"?page={page}" if page > 1 else "")
            try:
                # Kwork держит висячие запросы (онлайн-счётчик/SSE) ->
                # domcontentloaded не наступает. Ждём commit + селектор карточек.
                pg.goto(url, timeout=45000, wait_until="commit")
                pg.wait_for_selector("a[href*='/projects/']", timeout=30000)
                pg.wait_for_timeout(2500)  # SPA дорисовывает карточки
            except Exception as e:
                print(f"[warn] page {page} load: {e}", file=sys.stderr)
                break
            cards = pg.eval_on_selector_all(
                "a[href*='/projects/']",
                """els => els.map(e => {
                    const card = e.closest('[class*="card"], [class*="want"]') || e.parentElement;
                    return {
                        href: e.getAttribute('href'),
                        title: e.innerText.trim().slice(0,200),
                        cardText: (card ? card.innerText : '').slice(0,1500)
                    };
                })"""
            )
            seen = set()
            for c in cards:
                href = c.get("href") or ""
                if "/projects/" not in href:
                    continue
                if href in seen:
                    continue
                seen.add(href)
                full = href if href.startswith("http") else "https://kwork.ru" + href
                # desc = ТОЛЬКО заголовок. cardText тащит мусор со всего сайта
                # (похожие кворки, категории, футер) -> ложные 100% матча и
                # фейковые A вроде "Работа без навыков" (ADR-009). Реальное
                # описание стягивается fetch_job_detail перед решением A.
                title = (c.get("title", "") or "").strip()
                out.append({
                    "url": full,
                    "title": title,
                    "budget": None,
                    "desc": title,
                    "client": "",
                    "proposals": None,
                    "client_info": {},
                })
            if page < limit_pages:
                time.sleep(random.uniform(*delay))
        b.close()
    return out


def fetch_job_detail(url: str, use_cookies: bool = True, delay=(20, 40)) -> dict:
    """Догружаем страницу кворка: бюджет + описание + proposals + client."""
    from playwright.sync_api import sync_playwright
    out = {"budget": None, "desc": "", "proposals": None, "client_info": {}}
    launch_args = ["--no-sandbox", "--no-proxy-server", "--disable-dev-shm-usage"]
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(headless=True, args=launch_args)  # без proxy=None (см. ADR-009)
            ctx = b.new_context(user_agent=rand_ua())
            if use_cookies and os.path.exists(COOKIES):
                try:
                    with open(COOKIES) as f:
                        ctx.add_cookies(json.load(f))
                except Exception:
                    pass
            pg = ctx.new_page()
            pg.goto(url, timeout=45000, wait_until="domcontentloaded")
            pg.wait_for_timeout(3000)
            try:
                body_txt = pg.inner_text("body")
            except Exception:
                body_txt = ""
            out["budget"] = extract_budget(body_txt)
            out["proposals"] = extract_proposals(body_txt)
            out["client_info"] = extract_client_info(body_txt)
            desc = ""
            for sel in ["[class*='want']", "[class*='project']", "article", ".description"]:
                try:
                    t = pg.inner_text(sel)
                    if t and len(t) > len(desc):
                        desc = t
                except Exception:
                    continue
            if not desc:
                desc = body_txt
            for marker in ("Покупатель:", "Заказчик:", "Осталось:", "Предложений:"):
                idx = desc.find(marker)
                if idx > 200:
                    desc = desc[:idx]
                    break
            out["desc"] = desc.strip()[:1000]
            b.close()
    except Exception as e:
        print(f"[warn] detail {url}: {e}", file=sys.stderr)
    time.sleep(random.uniform(*delay))
    return out


# ---------------------------------------------------------------------------
# ДЕДУП ЧЕРЕЗ SQLITE
# ---------------------------------------------------------------------------
def seen_ids() -> set:
    ids = set()
    if os.path.exists(DB):
        try:
            c = sqlite3.connect(DB)
            for (u,) in c.execute("SELECT url FROM jobs"):
                ids.add(u)
            c.close()
        except Exception:
            pass
    return ids


def mark_seen(url: str):
    try:
        c = sqlite3.connect(DB)
        c.execute("INSERT OR IGNORE INTO jobs(platform,url,title,status) VALUES(?,?,?,?)",
                  ("kwork", url, "", "new"))
        c.commit(); c.close()
    except Exception as e:
        print(f"[warn] db mark: {e}", file=sys.stderr)


# ---------------------------------------------------------------------------
# ЗАПИСЬ ЧЕРНОВИКА (только для A) + leads
# ---------------------------------------------------------------------------
def slug(url: str) -> str:
    m = re.search(r"/projects/(\d+)", url)
    return m.group(1) if m else re.sub(r"\W+", "-", url)[:40]


def write_draft(job: dict, ev: dict):
    pid = slug(job["url"])
    path = os.path.join(OUTBOX, f"kwork-{pid}.md")
    os.makedirs(OUTBOX, exist_ok=True)
    budget = job.get("budget")
    proposals = ev.get("proposals")
    # ОЦЕНКА НАШЕЙ ЦЕНЫ (якорь 1500 ₽/ч). Грубая оценка трудозатрат по типу задачи:
    # парсер/скрипт ~3-5ч, бот ~5-8ч, RAG/LLM ~8-15ч, сайт ~10-20ч.
    est_hours = 4  # дефолт для парсера/скрипта
    matched = ev["skill_detail"]["our"]
    if "rag" in matched or "llm" in matched:
        est_hours = 10
    elif "telegram_bot" in matched or "aiogram" in matched:
        est_hours = 6
    elif "web" in matched or "сайт" in matched:
        est_hours = 12
    our_price = DEFAULTS["rate_per_hour"] * est_hours
    if budget:
        in_budget = "в рамках бюджета заказчика" if our_price <= budget * 3 else "выше желаемого, но в допустимом"
        price_note = (f"Оценка: от {our_price:.0f} ₽ (якорь 1500 ₽/ч × ~{est_hours}ч), "
                      f"{in_budget} (бюджет до {budget:.0f} ₽).")
    else:
        price_note = (f"Цена: от {our_price:.0f} ₽ (якорь 1500 ₽/ч × ~{est_hours}ч), "
                      f"по согласованию скоупа.")
    budget_line = f"{budget:.0f} ₽" if budget else "уточняется"
    proposals_line = f"{proposals}" if proposals is not None else "?"
    desc = job.get("desc", "") or ""
    desc = desc.replace(job.get("title", ""), "", 1).strip()
    desc = desc[:400] if desc else "(описание подгружается со страницы кворка)"
    title_low = job.get("title", "").lower()
    desc_low = desc.lower()
    # наше предложение (НЕ цитата ТЗ) — по матчу навыков
    matched = ev["skill_detail"]["our"]
    if "telegram_bot" in matched or "aiogram" in title_low or "telegram" in title_low:
        offer_line = "Готовы создать Telegram-бота на aiogram с интеграцией в указанные сервисы (CRM/Voice/API)."
    elif "web" in matched or "сайт" in title_low or "лендинг" in title_low:
        offer_line = "Готовы разработать сайт/лендинг под ключ: FastAPI/Flask + адаптивная вёрстка, без чистого граф-дизайна."
    elif "rag" in matched or "llm" in matched:
        offer_line = "Готовы реализовать RAG/LLM-решение: embeddings, vector search, reranking, observability-слой."
    elif "transcription" in matched:
        offer_line = "Готовы выполнить транскрибацию аудио/видео в текст (faster-whisper, локально)."
    elif "parsing" in matched or "automation" in matched:
        offer_line = "Готовы настроить парсинг/автоматизацию на Python с минимумом ручного вмешательства."
    else:
        offer_line = "Готовы выполнить задачу в соответствии с ТЗ, обеспечивая качество и сроки."
    sc = ev["skill_detail"]
    skill_note = (f"Матч навыков: {ev['skill']:.0f}% (наши: {', '.join(sc['our']) or '—'})."
                  if ev["skill"] is not None else "Матч навыков: неопределён")
    comp_note = f"Заявок уже подано: {ev['proposals'] if ev['proposals'] is not None else '?'}. Качество заказчика: {_client_str(ev['client_info'])}."
    body = f"""# Kwork: {job['title']}

- **Ссылка:** {job['url']}
- **Бюджет:** {budget_line}
- **Тип:** A (сладкий сегмент + скоринг v2)
- **Дата:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
- **Статус:** [ ] готов / [ ] отправлен — ЖДЁТ РУЧНОГО АПРУВА

---

Здравствуйте!

{offer_line}

{skill_note}
{comp_note}

Готов бесплатно сделать короткий тестовый фрагмент вашей задачи, чтобы вы оценили подход до старта.

https://github.com/Erik03132/freelance-2026

С уважением, Игорь

---
📊 **Служебное (для Игоря, не копировать в отклик):**
- Заявок уже подано: {proposals_line} (лимит Игоря: ≤20)
- Наша цена: {price_note}
"""
    with open(path, "w") as f:
        f.write(body)
    if ev["skill"] is None:
        match_str = "?"
    else:
        match_str = f"{ev['skill']:.0f}%"
    os.makedirs(os.path.dirname(LEADS), exist_ok=True)
    with open(LEADS, "a") as f:
        f.write(f"\n## {datetime.now(timezone.utc).strftime('%Y-%m-%d')} | Kwork A | [{job['title']}]({job['url']})\n"
                f"Тип: A. Матч: {match_str}. "
                f"Заявок: {ev['proposals']}. Статус: [ ] готов / [ ] отправлен.\n")
    return path


def _client_str(info: dict) -> str:
    if not info.get("found"):
        return "нет данных"
    parts = []
    if info.get("orders") is not None:
        parts.append(f"{info['orders']} заказов")
    if info.get("rating") is not None:
        parts.append(f"рейтинг {info['rating']}")
    if info.get("verified"):
        parts.append("подтверждён")
    return ", ".join(parts) if parts else "нет данных"


# ---------------------------------------------------------------------------
# DEMO (синтетика, без сети) — доказательство работы скоринга
# ---------------------------------------------------------------------------
DEMO_JOBS = [
    {"title": "Нужен Telegram-бот на aiogram с интеграцией Bitrix24",
     "desc": "Сделать бота, который забирает сделки из CRM и шлёт уведомления. Бюджет до 8000 руб.",
     "budget": 8000, "proposals": 4, "client_info": {"orders": 12, "rating": 4.8, "verified": True, "found": True}},
    {"title": "Создать видео для YouTube про наш продукт",
     "desc": "Нужен монтаж ролика 2 минуты, закадровый голос, анимация. Бюджет 5000 руб.",
     "budget": 5000, "proposals": 15, "client_info": {"orders": 3, "rating": 4.2, "verified": False, "found": True}},
    {"title": "RAG-система на базе embeddings для корпоративной базы знаний",
     "desc": "Нужен semantic search, vector store, reranking. Python, LangChain-like. Бюджет 30000 руб.",
     "budget": 30000, "proposals": 22, "client_info": {"orders": 40, "rating": 5.0, "verified": True, "found": True}},
    {"title": "Нарисовать логотип и фирменный стиль для кафе",
     "desc": "Дизайн логотипа, брендинг, упаковка. Бюджет 4000 руб.",
     "budget": 4000, "proposals": 9, "client_info": {"orders": 1, "rating": 4.0, "verified": False, "found": True}},
    {"title": "Парсер Avito на Python + выгрузка в Google Таблицы",
     "desc": "Скрипт парсинга объявлений, автоматизация. Бюджет 6000 руб.",
     "budget": 6000, "proposals": 85, "client_info": {"orders": 30, "rating": 4.9, "verified": True, "found": True}},
    {"title": "Мобильное приложение на Flutter для доставки еды",
     "desc": "iOS и Android, нативная разработка. Бюджет 50000 руб.",
     "budget": 50000, "proposals": 5, "client_info": {"orders": 8, "rating": 4.6, "verified": True, "found": True}},
    {"title": "Автоматизация отчётности через API и SQL",
     "desc": "Скрипт на Python, выгрузка из БД, сводка в Excel. Бюджет 3000 руб.",
     "budget": 3000, "proposals": 2, "client_info": {"orders": 0, "rating": None, "verified": False, "found": True}},
]


def run_demo(cfg: dict):
    print("\n=== DEMO СКОРИНГА (синтетика, без сети) ===")
    print(f"{'РЕШ':<4} {'SKILL':>6} {'COMP':>5} {'CLNT':>5} {'BUDG':>5} {'FIN':>6}  ЗАЯВ  ЗАКАЗЧИК  ТЗ")
    for job in DEMO_JOBS:
        ev = evaluate(job, cfg)
        sk = f"{ev['skill']:.0f}" if ev['skill'] is not None else "?"
        fn = f"{ev['final']:.0f}" if ev['final'] is not None else "?"
        print(f"{ev['decision']:<4} {sk:>6} {ev['competition']:>5} {ev['client']:>5} "
              f"{ev['budget']:>5} {fn:>6}  {str(ev['proposals']):>5}  "
              f"{_client_str(ev['client_info']):<18} {job['title'][:40]}")
        print(f"      └─ {ev['reason']}")
    print("=== конец DEMO ===\n")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    # сброс прокси в env (мёртвый socks5 ломает headless chromium); не трогаем .zshrc
    for k in ("http_proxy", "https_proxy", "all_proxy",
              "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"):
        os.environ.pop(k, None)
    ap = argparse.ArgumentParser(
        description="Kwork finder v2 — многофакторный скоринг кворков")
    ap.add_argument("--dry-run", action="store_true", help="только печать, не писать")
    ap.add_argument("--demo", action="store_true", help="прогнать синтетику, без сети")
    ap.add_argument("--pages", type=int, default=3)
    ap.add_argument("--no-cookies", action="store_true")
    ap.add_argument("--min-skill-a", type=float, default=DEFAULTS["min_skill_a"])
    ap.add_argument("--min-skill-b", type=float, default=DEFAULTS["min_skill_b"])
    ap.add_argument("--max-proposals-x", type=int, default=DEFAULTS["max_proposals_x"])
    ap.add_argument("--max-proposals-b", type=int, default=DEFAULTS["max_proposals_b"])
    ap.add_argument("--min-budget", type=float, default=DEFAULTS["min_budget"])
    ap.add_argument("--final-threshold-a", type=float, default=DEFAULTS["final_threshold_a"])
    args = ap.parse_args()

    cfg = dict(
        min_skill_a=args.min_skill_a, min_skill_b=args.min_skill_b,
        max_proposals_x=args.max_proposals_x, max_proposals_b=args.max_proposals_b,
        min_budget=args.min_budget, final_threshold_a=args.final_threshold_a,
    )

    if args.demo:
        run_demo(cfg)
        return

    print("[*] fetch projects...")
    jobs = fetch_projects(limit_pages=args.pages, use_cookies=not args.no_cookies)
    print(f"[*] raw cards: {len(jobs)}")

    known = seen_ids()
    counts = {"A": 0, "B": 0, "X": 0}
    drafted = 0

    # Предфильтр (без сети): оставляем только кворки, чей заголовок ЦЕПЛЯЕТ
    # наши навыки. Остальные -> сразу B (кандидат, без стягивания описания).
    def title_hits(job) -> bool:
        sm = score_skill_match(job["title"])
        return bool(sm["our"]) and not sm["exclude"]

    for job in jobs:
        if job["url"] in known:
            continue
        if not title_hits(job):
            # без маркеров наших навыков в заголовке -> кандидат B
            ev = evaluate(job, cfg)
            counts[ev["decision"]] += 1
            if ev["decision"] == "B":
                print(f"  [B] {job['title'][:55]} | {ev['reason']}")
                os.makedirs(os.path.dirname(LEADS), exist_ok=True)
                with open(LEADS, "a") as f:
                    f.write(f"\n## {datetime.now(timezone.utc).strftime('%Y-%m-%d')} | Kwork B | [{job['title']}]({job['url']})\n"
                            f"Тип: B (кандидат, без маркеров). Статус: [ ] решает Игорь.\n")
                mark_seen(job["url"])
            elif ev["decision"] == "X":
                print(f"  [X] {job['title'][:55]} | {ev['reason']}")
                mark_seen(job["url"])
            continue

        # Есть маркер нашего навыка в заголовке -> стягиваем РЕАЛЬНОЕ описание
        # и оцениваем по нему (ADR-009: без реального ТЗ решение недостоверно).
        if args.dry_run:
            print(f"  [~] {job['title'][:55]} | url={job['url']} (dry-run: описание не тянем)")
            continue
        detail = fetch_job_detail(job["url"], use_cookies=not args.no_cookies)
        if detail.get("budget") is not None:
            job["budget"] = detail["budget"]
        if detail.get("desc"):
            job["desc"] = detail["desc"]
        if detail.get("proposals") is not None:
            job["proposals"] = detail["proposals"]
        if detail.get("client_info", {}).get("found"):
            job["client_info"] = detail["client_info"]
        ev = evaluate(job, cfg)
        counts[ev["decision"]] += 1
        if ev["decision"] == "X":
            print(f"  [X] {job['title'][:55]} | {ev['reason']}")
            mark_seen(job["url"])
            continue
        if ev["decision"] == "B":
            print(f"  [B] {job['title'][:55]} | {ev['reason']}")
            os.makedirs(os.path.dirname(LEADS), exist_ok=True)
            with open(LEADS, "a") as f:
                f.write(f"\n## {datetime.now(timezone.utc).strftime('%Y-%m-%d')} | Kwork B | [{job['title']}]({job['url']})\n"
                        f"Тип: B (кандидат). {ev['reason']}. Статус: [ ] решает Игорь.\n")
            mark_seen(job["url"])
            continue
        # A
        path = write_draft(job, ev)
        mark_seen(job["url"])
        drafted += 1
        print(f"  [A] draft -> {path}")

    print(f"[*] решения: A={counts['A']} B={counts['B']} X={counts['X']}, "
          f"черновиков: {drafted}"
          + (" (DRY-RUN, ничего не записано)" if args.dry_run else ""))


if __name__ == "__main__":
    main()
