#!/usr/bin/env python3
"""
🎯 Content Outcomes Grader — Quality Gate для Шекспира
═══════════════════════════════════════════════════════
Вдохновлено Claude Managed Agents: Outcomes.
Отдельный grader оценивает контент по E-E-A-T рубрике.
Grader НЕ видит reasoning автора — только финальный текст.

Использование:
    python3 tools/content_grader.py --file draft.md
    python3 tools/content_grader.py --text "Текст для проверки"
    python3 tools/content_grader.py --file draft.md --rubric vk_farm
    python3 tools/content_grader.py --file draft.md --fix
    cat draft.md | python3 tools/content_grader.py --stdin

Рубрики:
    eeat         — E-E-A-T полный (статьи, блог)
    vk_farm      — ВК фермерский контент
    geo          — GEO/AEO оптимизация
    human_first  — Антидетект AI-контента
    all          — Все рубрики

Выход:
    0 — PASS (≥70 баллов)
    1 — FAIL (<70 баллов)
    2 — WARN (70-80, условный pass)
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Optional

# ============ РУБРИКИ ============

@dataclass
class GradeResult:
    """Результат оценки по одному критерию."""
    name: str
    score: int  # 0-10
    max_score: int  # обычно 10
    passed: bool
    details: str
    suggestions: list = field(default_factory=list)


@dataclass
class RubricResult:
    """Итог оценки по рубрике."""
    rubric_name: str
    grades: list  # list[GradeResult]
    total_score: int
    max_total: int
    percentage: float
    passed: bool
    verdict: str
    critical_fails: list = field(default_factory=list)


# ============ AI-МАРКЕРЫ ============

AI_MARKERS_RU = [
    "в современном быстро меняющемся мире",
    "давайте рассмотрим",
    "давайте разберёмся",
    "важно отметить, что",
    "таким образом, можно сделать вывод",
    "не секрет, что",
    "безусловно",
    "несомненно",
    "в заключение хотелось бы отметить",
    "является",
    "осуществлять",
    "данный",
    "в рамках",
    "на сегодняшний день",
    "в настоящее время",
    "рады поделиться",
    "с уверенностью можно сказать",
    "стоит подчеркнуть",
    "необходимо учитывать",
    "следует обратить внимание",
]

AI_MARKERS_EN = [
    "in today's fast-paced world",
    "delve into",
    "dive deep",
    "it's worth noting",
    "revolutionize",
    "game-changer",
    "cutting-edge",
    "harness the power",
    "navigate the complexities",
    "testament to",
    "seamlessly",
    "robust",
    "leverage",
    "excited to share",
    "let's explore",
]

HYPE_WORDS_RU = [
    "революционный", "уникальный", "лучший", "идеальный",
    "невероятный", "потрясающий", "феноменальный", "беспрецедентный",
    "инновационный", "прорывной",
]

VK_BANNED_EMOJI = ["🟢", "🟡", "🔵", "🟠", "🔴", "🟤", "🟣", "⬛", "⬜", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]


# ============ ГРЕЙДЕРЫ ============

def grade_eeat(text: str) -> RubricResult:
    """E-E-A-T рубрика для экспертного контента."""
    grades = []
    
    # 1. Experience (Опыт) — есть ли реальные примеры/кейсы
    experience_markers = [
        r"(мы|я|наш[аие]?)\s+(попробовал|сделал|внедрил|тестировал|проверил|использовал|запустил)",
        r"(на практике|в нашем случае|по нашему опыту|из опыта)",
        r"\d+\s*(лет|года|месяц)",
        r"(кейс|результат|пример из|история)",
    ]
    exp_count = sum(1 for p in experience_markers if re.search(p, text, re.I))
    exp_score = min(10, exp_count * 3)
    grades.append(GradeResult(
        name="Experience (Опыт)",
        score=exp_score, max_score=10,
        passed=exp_score >= 4,
        details=f"Найдено {exp_count} маркеров опыта",
        suggestions=["Добавь конкретный пример из своей практики"] if exp_score < 4 else []
    ))
    
    # 2. Expertise (Экспертиза) — конкретные цифры, факты, технические детали
    numbers = len(re.findall(r'\d+[%₽$€кгмлшт]|\d+\.\d+|\d{2,}', text))
    tech_terms = len(re.findall(r'[A-Z]{2,}[\-\s]?\d*|[a-z]+_[a-z]+', text))
    expertise_score = min(10, numbers * 2 + tech_terms)
    grades.append(GradeResult(
        name="Expertise (Экспертиза)",
        score=expertise_score, max_score=10,
        passed=expertise_score >= 5,
        details=f"Цифр/фактов: {numbers}, тех.терминов: {tech_terms}",
        suggestions=["Добавь конкретные цифры: результаты, метрики, сроки"] if expertise_score < 5 else []
    ))
    
    # 3. Authoritativeness (Авторитетность) — ссылки на источники, цитаты
    auth_markers = [
        r"(по данным|согласно|источник|исследовани|отчёт|руководство|справочник)",
        r"(«[^»]+»|\"[^\"]+\")",  # цитаты
        r"(стр\.\s*\d+|p\.\s*\d+)",  # ссылки на страницы
        r"(эксперт|специалист|профессор|доктор|кандидат)",
    ]
    auth_count = sum(1 for p in auth_markers if re.search(p, text, re.I))
    auth_score = min(10, auth_count * 3)
    grades.append(GradeResult(
        name="Authoritativeness (Авторитетность)",
        score=auth_score, max_score=10,
        passed=auth_score >= 3,
        details=f"Маркеров авторитетности: {auth_count}",
        suggestions=["Добавь ссылку на источник или цитату эксперта"] if auth_score < 3 else []
    ))
    
    # 4. Trustworthiness (Доверие) — нет AI-маркеров, нет hype
    ai_hits = sum(1 for m in AI_MARKERS_RU + AI_MARKERS_EN if m.lower() in text.lower())
    hype_hits = sum(1 for w in HYPE_WORDS_RU if w.lower() in text.lower())
    trust_penalty = ai_hits * 2 + hype_hits
    trust_score = max(0, 10 - trust_penalty)
    fail_details = []
    if ai_hits > 0:
        found = [m for m in AI_MARKERS_RU + AI_MARKERS_EN if m.lower() in text.lower()]
        fail_details = [f"Удали AI-маркер: «{m}»" for m in found[:5]]
    if hype_hits > 0:
        found_hype = [w for w in HYPE_WORDS_RU if w.lower() in text.lower()]
        fail_details += [f"Замени hype-слово: «{w}» → конкретный факт" for w in found_hype[:3]]
    grades.append(GradeResult(
        name="Trustworthiness (Доверие)",
        score=trust_score, max_score=10,
        passed=trust_score >= 6,
        details=f"AI-маркеров: {ai_hits}, hype-слов: {hype_hits}",
        suggestions=fail_details
    ))
    
    # 5. Structure (Структура) — H2, списки, FAQ, короткие абзацы
    h2_count = len(re.findall(r'^##\s', text, re.M))
    list_count = len(re.findall(r'^[\-\*\d]+[\.\)]\s', text, re.M))
    faq = bool(re.search(r'(FAQ|вопрос|ответ|\?.*\n)', text, re.I))
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    avg_para_len = sum(len(p) for p in paragraphs) / max(len(paragraphs), 1)
    
    struct_score = min(10,
        min(h2_count, 3) * 2 +  # до 6 за заголовки
        min(list_count, 4) +     # до 4 за списки
        (2 if faq else 0) +      # 2 за FAQ
        (2 if avg_para_len < 500 else 0)  # 2 за короткие абзацы
    )
    grades.append(GradeResult(
        name="Structure (Структура)",
        score=struct_score, max_score=10,
        passed=struct_score >= 5,
        details=f"H2: {h2_count}, списков: {list_count}, FAQ: {'да' if faq else 'нет'}, ср.абзац: {avg_para_len:.0f} симв.",
        suggestions=["Добавь H2 заголовки-вопросы"] if h2_count < 2 else []
    ))
    
    # 6. Extractability (Извлекаемость для нейросетей)
    # Тест: есть ли self-contained ответы 40-60 слов
    sentences = re.split(r'[.!?]\s', text)
    extractable = [s for s in sentences if 30 <= len(s.split()) <= 80]
    definitions = re.findall(r'(—\s*.{20,100}\.)', text)
    
    extract_score = min(10,
        min(len(extractable), 3) * 2 +
        min(len(definitions), 3) * 2 +
        (2 if any(re.search(r'\d', e) for e in extractable) else 0)
    )
    grades.append(GradeResult(
        name="Extractability (Извлекаемость GEO)",
        score=extract_score, max_score=10,
        passed=extract_score >= 4,
        details=f"Извлекаемых фрагментов: {len(extractable)}, определений: {len(definitions)}",
        suggestions=["Добавь прямой ответ 40-60 слов на главный вопрос"] if extract_score < 4 else []
    ))
    
    # Итог
    total = sum(g.score for g in grades)
    max_total = sum(g.max_score for g in grades)
    pct = (total / max_total) * 100
    critical = [g for g in grades if not g.passed]
    
    return RubricResult(
        rubric_name="E-E-A-T",
        grades=grades,
        total_score=total,
        max_total=max_total,
        percentage=pct,
        passed=pct >= 70 and len(critical) <= 2,
        verdict="PASS ✅" if pct >= 80 else "WARN ⚠️" if pct >= 60 else "FAIL ❌",
        critical_fails=[g.name for g in critical]
    )


def grade_human_first(text: str) -> RubricResult:
    """Антидетект AI-контента: Perplexity + Burstiness."""
    grades = []
    
    # 1. Burstiness (вариативность длины предложений)
    sentences = re.split(r'[.!?]\s+', text)
    sentences = [s for s in sentences if len(s) > 5]
    if len(sentences) > 3:
        lengths = [len(s.split()) for s in sentences]
        short = sum(1 for l in lengths if l <= 7)
        medium = sum(1 for l in lengths if 8 <= l <= 20)
        long_ = sum(1 for l in lengths if l > 20)
        
        variety = min(short, medium, long_) > 0
        burst_score = 10 if variety else (6 if min(short, medium) > 0 else 3)
    else:
        burst_score = 5  # мало предложений для оценки
    
    grades.append(GradeResult(
        name="Burstiness (ритм)",
        score=burst_score, max_score=10,
        passed=burst_score >= 6,
        details=f"Короткие(≤7 слов): {short if len(sentences)>3 else '?'}, средние: {medium if len(sentences)>3 else '?'}, длинные(>20): {long_ if len(sentences)>3 else '?'}",
        suggestions=["Чередуй короткие фразы (3-7 слов) с длинными (20+ слов)"] if burst_score < 6 else []
    ))
    
    # 2. AI-маркеры (строгая проверка)
    ai_found = [m for m in AI_MARKERS_RU if m.lower() in text.lower()]
    ai_score = max(0, 10 - len(ai_found) * 3)
    grades.append(GradeResult(
        name="AI-маркеры",
        score=ai_score, max_score=10,
        passed=ai_score >= 7,
        details=f"Найдено: {len(ai_found)}",
        suggestions=[f"Удали: «{m}»" for m in ai_found[:5]]
    ))
    
    # 3. Живой голос (обращение к читателю, мнение автора)
    personal_markers = [
        r'\b(ты|тебе|твой|вам|вас|ваш)\b',
        r'\b(я считаю|по-моему|на мой взгляд|честно|реально|серьёзно)\b',
        r'[!?]{1,3}',
        r'[(][^)]{5,}[)]',  # уточнения в скобках
    ]
    voice_count = sum(1 for p in personal_markers if re.search(p, text, re.I))
    voice_score = min(10, voice_count * 3)
    grades.append(GradeResult(
        name="Живой голос",
        score=voice_score, max_score=10,
        passed=voice_score >= 4,
        details=f"Маркеров живого голоса: {voice_count}",
        suggestions=["Добавь личное мнение или прямое обращение к читателю"] if voice_score < 4 else []
    ))
    
    # 4. Активный залог (active voice ≥ 80%)
    passive_markers = re.findall(r'\b(был[аоие]?\s+\w+[аоие]н[аоие]?|является|осуществляется|производится)\b', text, re.I)
    passive_pct = (len(passive_markers) / max(len(sentences), 1)) * 100
    active_score = 10 if passive_pct < 10 else (7 if passive_pct < 20 else 3)
    grades.append(GradeResult(
        name="Active Voice",
        score=active_score, max_score=10,
        passed=active_score >= 6,
        details=f"Пассивных конструкций: {len(passive_markers)} ({passive_pct:.0f}%)",
        suggestions=["Перепиши пассивные конструкции в активный залог"] if active_score < 6 else []
    ))
    
    total = sum(g.score for g in grades)
    max_total = sum(g.max_score for g in grades)
    pct = (total / max_total) * 100
    critical = [g for g in grades if not g.passed]
    
    return RubricResult(
        rubric_name="Human-First",
        grades=grades,
        total_score=total,
        max_total=max_total,
        percentage=pct,
        passed=pct >= 70,
        verdict="PASS ✅" if pct >= 80 else "WARN ⚠️" if pct >= 60 else "FAIL ❌",
        critical_fails=[g.name for g in critical]
    )


def grade_vk_farm(text: str) -> RubricResult:
    """Рубрика для ВК фермерского контента."""
    grades = []
    
    # 1. Хук (первые 2 строки)
    lines = text.strip().split('\n')
    first_lines = ' '.join(lines[:2])
    has_hook = bool(re.search(r'[?!]|^\d|\b(как|почему|зачем|а вы знали|секрет|ошибк)', first_lines, re.I))
    hook_score = 10 if has_hook else 3
    grades.append(GradeResult(
        name="Хук (первые строки)",
        score=hook_score, max_score=10,
        passed=has_hook,
        details=f"Хук: {'есть' if has_hook else 'нет'} | «{first_lines[:60]}...»",
        suggestions=["Начни с вопроса, числа или провокации"] if not has_hook else []
    ))
    
    # 2. Народная мудрость (пословицы/поговорки)
    proverbs = re.findall(r'(«[^»]+»|"[^"]+")', text)
    folk_markers = re.findall(r'(пословиц|поговорк|как говори|бабушка|дед|старик)', text, re.I)
    folk_score = min(10, (len(proverbs) + len(folk_markers)) * 4)
    grades.append(GradeResult(
        name="Народная мудрость",
        score=folk_score, max_score=10,
        passed=folk_score >= 4,
        details=f"Цитат: {len(proverbs)}, фольклор-маркеров: {len(folk_markers)}",
        suggestions=["Добавь 1 пословицу или поговорку к месту"] if folk_score < 4 else []
    ))
    
    # 3. CTA (call-to-action)
    cta_markers = re.findall(r'(а у вас|делитесь|расскажите|напишите|поставьте класс|лайк|комментари|\?$)', text, re.I | re.M)
    cta_score = min(10, len(cta_markers) * 5)
    grades.append(GradeResult(
        name="CTA (призыв к действию)",
        score=cta_score, max_score=10,
        passed=len(cta_markers) > 0,
        details=f"CTA-маркеров: {len(cta_markers)}",
        suggestions=["Добавь вопрос в комментарии: «А у вас как?»"] if len(cta_markers) == 0 else []
    ))
    
    # 4. Запрещённые эмодзи VK
    banned_found = [e for e in VK_BANNED_EMOJI if e in text]
    emoji_score = 10 if not banned_found else max(0, 10 - len(banned_found) * 3)
    grades.append(GradeResult(
        name="VK эмодзи-совместимость",
        score=emoji_score, max_score=10,
        passed=not banned_found,
        details=f"Запрещённых: {len(banned_found)} {banned_found if banned_found else ''}",
        suggestions=[f"Замени {e} → см. SKILL.md (разрешённые эмодзи)" for e in banned_found[:3]]
    ))
    
    # 5. Тёплый тон (не канцелярит)
    warm_markers = re.findall(r'(😀|😊|🔥|👍|❤|😁|🐔|🐣|🌱|ахах|хех|ну|блин|классн|круто)', text, re.I)
    cold_markers = re.findall(r'(рекомендуется|необходимо|следует|является|осуществля)', text, re.I)
    warm_score = min(10, len(warm_markers) * 2 + max(0, 5 - len(cold_markers) * 2))
    grades.append(GradeResult(
        name="Тёплый тон",
        score=warm_score, max_score=10,
        passed=warm_score >= 5,
        details=f"Тёплых: {len(warm_markers)}, канцеляризмов: {len(cold_markers)}",
        suggestions=["Убери канцеляризмы, добавь эмодзи и живой язык"] if warm_score < 5 else []
    ))
    
    total = sum(g.score for g in grades)
    max_total = sum(g.max_score for g in grades)
    pct = (total / max_total) * 100
    critical = [g for g in grades if not g.passed]
    
    return RubricResult(
        rubric_name="VK Farm",
        grades=grades,
        total_score=total,
        max_total=max_total,
        percentage=pct,
        passed=pct >= 70,
        verdict="PASS ✅" if pct >= 80 else "WARN ⚠️" if pct >= 60 else "FAIL ❌",
        critical_fails=[g.name for g in critical]
    )


# ============ ФОРМАТИРОВАНИЕ ============

def format_result(result: RubricResult) -> str:
    """Форматирует результат в читаемый markdown."""
    lines = [
        f"## 🎯 Рубрика: {result.rubric_name}",
        f"### Вердикт: {result.verdict} ({result.total_score}/{result.max_total} = {result.percentage:.0f}%)",
        "",
        "| Критерий | Балл | Статус |",
        "|----------|:----:|:------:|",
    ]
    
    for g in result.grades:
        status = "✅" if g.passed else "❌"
        lines.append(f"| {g.name} | {g.score}/{g.max_score} | {status} |")
    
    lines.append("")
    
    # Детали
    for g in result.grades:
        if g.details:
            lines.append(f"- **{g.name}:** {g.details}")
    
    lines.append("")
    
    # Рекомендации (только для проваленных)
    suggestions = []
    for g in result.grades:
        if g.suggestions:
            for s in g.suggestions:
                suggestions.append(f"  - {s}")
    
    if suggestions:
        lines.append("### 🔧 Рекомендации")
        lines.extend(suggestions)
    
    if result.critical_fails:
        lines.append(f"\n### ⚠️ Критические провалы: {', '.join(result.critical_fails)}")
    
    return '\n'.join(lines)


# ============ MAIN ============

def main():
    parser = argparse.ArgumentParser(description="🎯 Content Outcomes Grader")
    parser.add_argument('--file', '-f', help='Путь к файлу с контентом')
    parser.add_argument('--text', '-t', help='Текст для проверки')
    parser.add_argument('--stdin', action='store_true', help='Читать из stdin')
    parser.add_argument('--rubric', '-r', default='all',
                       choices=['eeat', 'vk_farm', 'human_first', 'geo', 'all'],
                       help='Рубрика для оценки (default: all)')
    parser.add_argument('--json', action='store_true', help='Вывод в JSON')
    parser.add_argument('--threshold', type=int, default=70, help='Порог прохождения (default: 70)')
    parser.add_argument('--fix', action='store_true', help='Показать конкретные исправления')
    
    args = parser.parse_args()
    
    # Получаем текст
    text = ""
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read()
    elif args.text:
        text = args.text
    elif args.stdin:
        text = sys.stdin.read()
    else:
        parser.print_help()
        sys.exit(1)
    
    if len(text.strip()) < 50:
        print("❌ Текст слишком короткий для оценки (минимум 50 символов)")
        sys.exit(1)
    
    # Выбираем рубрики
    rubrics = {
        'eeat': grade_eeat,
        'human_first': grade_human_first,
        'vk_farm': grade_vk_farm,
    }
    
    if args.rubric == 'all':
        selected = rubrics
    elif args.rubric == 'geo':
        selected = {'eeat': grade_eeat}  # GEO включает E-E-A-T
    else:
        selected = {args.rubric: rubrics[args.rubric]}
    
    # Оценка
    results = {}
    all_passed = True
    
    print("=" * 60)
    print("🎯 CONTENT OUTCOMES GRADER v1.0")
    print(f"📝 Текст: {len(text)} символов, {len(text.split())} слов")
    print("=" * 60)
    print()
    
    for name, grader in selected.items():
        result = grader(text)
        results[name] = result
        
        if not result.passed:
            all_passed = False
        
        print(format_result(result))
        print()
    
    # Общий вердикт
    avg_pct = sum(r.percentage for r in results.values()) / len(results)
    print("=" * 60)
    if avg_pct >= 80:
        print(f"🏆 ИТОГО: PASS ({avg_pct:.0f}%) — контент готов к публикации!")
    elif avg_pct >= 60:
        print(f"⚠️  ИТОГО: WARN ({avg_pct:.0f}%) — нужны правки (см. рекомендации)")
    else:
        print(f"❌ ИТОГО: FAIL ({avg_pct:.0f}%) — серьёзная доработка!")
    print("=" * 60)
    
    if args.json:
        json_out = {
            name: {
                'rubric': r.rubric_name,
                'score': r.total_score,
                'max': r.max_total,
                'pct': round(r.percentage, 1),
                'passed': r.passed,
                'verdict': r.verdict,
                'fails': r.critical_fails,
            }
            for name, r in results.items()
        }
        print(json.dumps(json_out, ensure_ascii=False, indent=2))
    
    # Exit code
    if all_passed:
        sys.exit(0)
    elif avg_pct >= 60:
        sys.exit(2)  # WARN
    else:
        sys.exit(1)  # FAIL


if __name__ == '__main__':
    main()
