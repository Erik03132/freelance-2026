#!/usr/bin/env python3
"""
hh_parser.py — прямой парсер вакансий HH.ru через публичный HTML.
НЕ требует API-ключа и логина. Работает как fallback, когда managed
web-tools (Firecrawl через подписку Nous) недоступны или дороги.

HH отдаёт страницы с экранированным SSR-JSON (обратные слэши перед
кавычками: \\"vacancyId\\":123). Мы снимаем экранирование и парсим как JSON.

Зависимости: только stdlib.
"""
from __future__ import annotations
import argparse
import html as _html
import json
import re
import subprocess
import sys
from dataclasses import dataclass, asdict, field
from typing import Optional

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
HEADERS = {"User-Agent": UA, "Accept-Language": "ru-RU,ru;q=0.9"}


def _get(url: str, timeout: int = 30) -> str:
    hdr = " ".join(f'-H "{k}: {v}"' for k, v in HEADERS.items())
    cmd = f'curl -s -L -m {timeout} --noproxy "*" {hdr} "{url}"'
    out = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                         timeout=timeout + 10)
    if out.returncode != 0:
        raise RuntimeError(f"curl failed ({out.returncode}): {out.stderr[:200]}")
    return out.stdout


def _unescape(s: str) -> str:
    return _html.unescape(s).strip()


def _deescape_json(src: str) -> str:
    """Снимаем JSON-экранирование HH (\\" → ", \\\\ → \\), чтобы regex
    находил ключи вида "vacancyId"."""
    # Убираем экранирование обратного слэша перед кавычкой и слэшем в URL
    return src.replace('\\"', '"').replace('\\/', '/')


def _find_vacancy_ids(src: str) -> list[str]:
    """Ищем ID вакансий во всём HTML (и в чистом, и в экранированном виде)."""
    ids = set()
    # экранированный вид: \/vacancy\/123  или /vacancy/123
    for m in re.finditer(r'(?:\\?/)?vacancy(?:\\?/)(\d{6,})', src):
        ids.add(m.group(1))
    # прямой вид hh.ru/vacancy/123
    for m in re.finditer(r'hh\.ru/vacancy/(\d{6,})', src):
        ids.add(m.group(1))
    return list(ids)


@dataclass
class Vacancy:
    id: str = ""
    title: str = ""
    employer: str = ""
    salary_from: Optional[int] = None
    salary_to: Optional[int] = None
    salary_text: str = ""
    area: str = ""
    published: str = ""
    experience: str = ""
    url: str = ""
    description: str = ""
    raw: dict = field(default_factory=dict)

    @property
    def salary(self) -> str:
        if self.salary_text:
            return self.salary_text
        parts = []
        if self.salary_from:
            parts.append(f"от {self.salary_from}")
        if self.salary_to:
            parts.append(f"до {self.salary_to}")
        return " ".join(parts) if parts else ""


def parse_vacancy(src: str) -> Vacancy:
    v = Vacancy()
    d = _deescape_json(src)
    # id
    m = re.search(r'"vacancyId"\s*:\s*(\d+)', d)
    if m:
        v.id = m.group(1)
        v.url = f"https://hh.ru/vacancy/{v.id}"
    # title / employer / salary / city / experience from meta description
    # Format: "Вакансия <TITLE> в компании <EMP>. Зарплата: <SAL>. <CITY>.
    #          Требуемый опыт: <EXP>. Занятость: ... Дата публикации: <DATE>"
    mm = re.search(
        r'<meta[^>]+name="description"[^>]+content="Вакансия\s+(.*?)\s+в\s+компании\s+(.*?)\.'
        r'(?: Зарплата:\s*(.*?)\.)?(?: (.*?)\.)?\s*Требуемый опыт:\s*(.*?)\.',
        d, re.S)
    if mm:
        v.title = _unescape(mm.group(1))
        v.employer = _unescape(mm.group(2))
        if mm.group(3):
            v.salary_text = _unescape(mm.group(3))
        if mm.group(4):
            v.area = _unescape(mm.group(4))
        if mm.group(5):
            v.experience = _unescape(mm.group(5))
    else:
        mf = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]+)"', d, re.S | re.I)
        if mf:
            v.title = _unescape(re.sub(r"^Вакансия\s+", "", mf.group(1)))
    # salary (structured) — overrides text if present
    ms = re.search(r'"salary"\s*:\s*\{[^}]*\}', d)
    if ms:
        blob = ms.group(0)
        f = re.search(r'"from"\s*:\s*(\d+)', blob)
        t = re.search(r'"to"\s*:\s*(\d+)', blob)
        cur = re.search(r'"currency"\s*:\s*"([^"]+)"', blob)
        if f:
            v.salary_from = int(f.group(1))
        if t:
            v.salary_to = int(t.group(1))
        if cur:
            v.salary_text = f"{v.salary} {cur.group(1)}".strip()
    # area
    ma = re.search(r'"area"\s*:\s*\{[^}]*?"name"\s*:\s*"([^"]+)"', d)
    if ma:
        v.area = _unescape(ma.group(1))
    # experience
    mx = re.search(r'"experience"\s*:\s*\{[^}]*?"name"\s*:\s*"([^"]+)"', d)
    if mx:
        v.experience = _unescape(mx.group(1))
    # published
    mp = re.search(r'"published_at"\s*:\s*"([^"]+)"', d)
    if mp:
        v.published = mp.group(1)
    # full description (HTML) — the vacancy object stores it as
    # "description":"<html>..." with any key following
    md = re.search(r'"description"\s*:\s*"((?:[^"\\]|\\.){50,})"\s*,\s*"', d)
    if md:
        desc = re.sub(r"<[^>]+>", " ", md.group(1))
        desc = _unescape(desc)
        v.description = re.sub(r"\s+", " ", desc).strip()[:3000]
    return v


def parse_search(src: str) -> list[Vacancy]:
    """Из HTML поисковой выдачи вытаскиваем карточки вакансий."""
    out: list[Vacancy] = []
    d = _deescape_json(src)
    for vid in _find_vacancy_ids(d):
        # контекст вокруг первого упоминания ID
        m = re.search(r'(?:\\?/)?vacancy(?:\\?/)' + vid, d)
        if not m:
            continue
        start = max(0, m.start() - 4000)
        chunk = d[start:m.end() + 400]
        title = ""
        mt = re.search(r'data-qa="vacancy-serp__vacancy-title"[^>]*>(.*?)</a>', chunk, re.S)
        if not mt:
            mt = re.search(r'class="[^"]*serp-item__title[^"]*"[^>]*>(.*?)</a>', chunk, re.S)
        if mt:
            title = _unescape(re.sub(r"<[^>]+>", "", mt.group(1))).strip()
        emp = ""
        me = re.search(r'data-qa="vacancy-serp__vacancy-employer"[^>]*>(.*?)</', chunk, re.S)
        if me:
            emp = _unescape(re.sub(r"<[^>]+>", "", me.group(1))).strip()
        out.append(Vacancy(id=vid, title=title, employer=emp,
                           url=f"https://hh.ru/vacancy/{vid}"))
    seen = {}
    for v in out:
        seen[v.id] = v
    return list(seen.values())


def search(query: str, area: int = 1, days: int = 3, limit: int = 20) -> list[Vacancy]:
    import urllib.parse
    params = {
        "text": query,
        "area": area,
        "search_period": days,
        "order_by": "publication_time",
        "per_page": min(limit, 100),
        "page": 0,
    }
    url = "https://hh.ru/search/vacancy?" + urllib.parse.urlencode(params)
    src = _get(url)
    return parse_search(src)[:limit]


def vacancy(vid: str) -> Vacancy:
    url = f"https://hh.ru/vacancy/{vid}"
    src = _get(url)
    return parse_vacancy(src)


def save_to_leads(v: Vacancy, path: str = None) -> str:
    """Дописать карточку в leads.md (формат JOBHUNT.md).
    Возвращает путь к файлу. Черновик — отправку НЕ производим."""
    import datetime
    if path is None:
        path = "/Users/igorvasin/freelance-2026/jobhunter/leads.md"
    today = datetime.date.today().isoformat()
    block = (
        f"\n## {today} | HH | [{v.title}]({v.url})\n"
        f"- Работодатель: {v.employer or '—'}\n"
        f"- Зарплата: {v.salary or 'не указана'}\n"
        f"- Город: {v.area or '—'} | Опыт: {v.experience or '—'}\n"
        f"- Тип: A (черновик отклика). Статус: [ ] готов / [ ] отправлен.\n"
        f"- Описание (фрагмент): {v.description[:400]}\n"
    )
    with open(path, "a", encoding="utf-8") as f:
        f.write(block)
    return path


def main():
    ap = argparse.ArgumentParser(description="HH.ru прямой парсер (без API-ключа)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("search", help="поиск вакансий (через HTML, только 1-я карточка)")
    sp.add_argument("query")
    sp.add_argument("--area", type=int, default=1, help="1=Москва, 0=Россия")
    sp.add_argument("--days", type=int, default=3)
    sp.add_argument("--limit", type=int, default=20)
    sp.add_argument("--json", help="сохранить в JSON файл")
    vp = sub.add_parser("vacancy", help="карточка вакансии по ID")
    vp.add_argument("vid")
    vp.add_argument("--json", help="сохранить в JSON файл")
    vp.add_argument("--save", action="store_true", help="дописать в leads.md")
    bp = sub.add_parser("batch", help="несколько ID через запятую")
    bp.add_argument("ids", help="через запятую: 135794586,136703693")
    bp.add_argument("--save", action="store_true", help="дописать все в leads.md")
    bp.add_argument("--json", help="сохранить все карточки в JSON файл")
    args = ap.parse_args()

    if args.cmd == "search":
        res = search(args.query, args.area, args.days, args.limit)
        print(f"Найдено: {len(res)}\n")
        for i, v in enumerate(res, 1):
            print(f"{i}. {v.title or '[без标题]'}  [{v.employer}]")
            print(f"   {v.url}")
        if args.json:
            json.dump([asdict(v) for v in res], open(args.json, "w"),
                      ensure_ascii=False, indent=2)
            print(f"\nSaved -> {args.json}")
    elif args.cmd == "batch":
        ids = [x.strip() for x in args.ids.split(",") if x.strip()]
        for vid in ids:
            v = vacancy(vid)
            print(f"=== {v.id}: {v.title} [{v.employer}] ===")
            print(f"    {v.url} | {v.salary or 'зп не указана'}")
            if args.save:
                p = save_to_leads(v)
                print(f"    -> saved to {p}")
        if args.json:
            cards = [vacancy(x) for x in ids]
            json.dump([asdict(c) for c in cards], open(args.json, "w"),
                      ensure_ascii=False, indent=2)
            print(f"\nSaved {len(cards)} cards -> {args.json}")
    else:
        v = vacancy(args.vid)
        print(f"Вакансия: {v.title}")
        print(f"Работодатель: {v.employer}")
        print(f"Зарплата: {v.salary or 'не указана'}")
        print(f"Город: {v.area} | Опыт: {v.experience}")
        print(f"Опубликовано: {v.published}")
        print(f"URL: {v.url}")
        print(f"\nОписание:\n{v.description[:800]}")
        if args.json:
            json.dump(asdict(v), open(args.json, "w"), ensure_ascii=False, indent=2)
            print(f"\nSaved -> {args.json}")
        if args.save:
            p = save_to_leads(v)
            print(f"\n-> добавлено в {p} (черновик, не отправлено)")


if __name__ == "__main__":
    main()

