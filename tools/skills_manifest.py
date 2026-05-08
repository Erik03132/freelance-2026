#!/usr/bin/env python3
"""
🎯 Skills Manifest Generator — Progressive Disclosure для Antigravity
═══════════════════════════════════════════════════════════════════════
Вдохновлено AWS Agent Toolkit: Progressive Disclosure pattern.

Проблема: 28 скиллов × ~3700 строк = ~104K токенов при полной загрузке.
Решение: Генерируем лёгкий MANIFEST.md (~2.8K токенов) с name + description.
          Агент загружает полный скилл ТОЛЬКО когда задача матчит.

Использование:
    python3 tools/skills_manifest.py                    # генерация MANIFEST.md
    python3 tools/skills_manifest.py --format json      # JSON для автоматизации
    python3 tools/skills_manifest.py --match "SEO аудит сайта"  # поиск подходящего скилла
    python3 tools/skills_manifest.py --stats             # статистика

Вывод:
    ~/.gemini/antigravity/skills/MANIFEST.md  — читается при boot вместо всех SKILL.md
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# ============ КОНФИГУРАЦИЯ ============

SKILLS_DIR = Path.home() / ".gemini/antigravity/skills"
PROJECT_SKILLS_DIR = Path.home() / "freelance-2026/freelance-agent/.agent/skills"
MANIFEST_PATH = SKILLS_DIR / "MANIFEST.md"
MANIFEST_JSON_PATH = SKILLS_DIR / "manifest.json"


@dataclass
class SkillInfo:
    """Извлечённая информация о скилле."""
    name: str
    path: str
    description: str
    triggers: list  # ключевые слова для маршрутизации
    category: str   # core / marketing / engineering / content / meta
    size_bytes: int
    size_lines: int
    est_tokens: int
    has_references: bool
    has_scripts: bool


def extract_skill_info(skill_dir: Path) -> Optional[SkillInfo]:
    """Извлекает метаданные из SKILL.md (frontmatter + первые строки)."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return None
    
    content = skill_md.read_text(encoding='utf-8')
    lines = content.split('\n')
    size_bytes = len(content.encode('utf-8'))
    size_lines = len(lines)
    
    # Парсим YAML frontmatter
    name = skill_dir.name
    description = ""
    
    if content.startswith('---'):
        # YAML frontmatter
        end_idx = content.find('---', 3)
        if end_idx > 0:
            frontmatter = content[3:end_idx]
            # Извлекаем name
            name_match = re.search(r'^name:\s*["\']?(.+?)["\']?\s*$', frontmatter, re.M)
            if name_match:
                name = name_match.group(1).strip()
            # Извлекаем description
            desc_match = re.search(r'^description:\s*["\']?(.+?)(?:["\']?\s*$)', frontmatter, re.M)
            if desc_match:
                description = desc_match.group(1).strip()
                # Многострочное описание
                if not description:
                    desc_lines = []
                    in_desc = False
                    for line in frontmatter.split('\n'):
                        if line.strip().startswith('description:'):
                            in_desc = True
                            rest = line.split('description:', 1)[1].strip()
                            if rest and rest not in ('|', '>'):
                                desc_lines.append(rest)
                        elif in_desc:
                            if line.startswith('  ') or line.startswith('\t'):
                                desc_lines.append(line.strip())
                            else:
                                break
                    description = ' '.join(desc_lines)
    
    # Если description не в frontmatter — ищем первый абзац после заголовка
    if not description:
        for i, line in enumerate(lines):
            if line.startswith('# ') and i + 1 < len(lines):
                # Следующие непустые строки = описание
                desc_lines = []
                for j in range(i + 1, min(i + 5, len(lines))):
                    if lines[j].strip() and not lines[j].startswith('#'):
                        desc_lines.append(lines[j].strip())
                    elif not lines[j].strip() and desc_lines:
                        break
                description = ' '.join(desc_lines)
                break
    
    # Извлекаем trigger keywords
    triggers = extract_triggers(name, description, content)
    
    # Определяем категорию
    category = categorize_skill(name, description)
    
    # Проверяем наличие references/ и scripts/
    has_references = (skill_dir / "references").is_dir()
    has_scripts = (skill_dir / "scripts").is_dir()
    
    return SkillInfo(
        name=name,
        path=str(skill_md),
        description=description[:200],  # макс 200 символов
        triggers=triggers,
        category=category,
        size_bytes=size_bytes,
        size_lines=size_lines,
        est_tokens=size_bytes // 4,
        has_references=has_references,
        has_scripts=has_scripts,
    )


def extract_triggers(name: str, description: str, content: str) -> list:
    """Извлекает ключевые слова для маршрутизации задач к скиллу."""
    triggers = set()
    
    # Из описания: фразы в кавычках
    for match in re.findall(r'["\']([^"\']{3,30})["\']', description):
        triggers.add(match.lower())
    
    # Из описания: ключевые слова после "when", "use when", "Also use when"
    for match in re.findall(r'(?:when|use when|Also use when)[^.]*?["\']([^"\']+)["\']', description, re.I):
        triggers.add(match.lower())
    
    # Из имени скилла
    parts = name.replace('-', ' ').replace('_', ' ').split()
    for part in parts:
        if len(part) > 3:
            triggers.add(part.lower())
    
    # Из первых 50 строк: секции с маршрутизацией
    first_50 = '\n'.join(content.split('\n')[:50])
    for match in re.findall(r'(?:триггер|trigger|использу|use when|когда)[^.]*?:\s*(.+?)$', first_50, re.M | re.I):
        for word in match.split(','):
            word = word.strip().strip('"\'').lower()
            if 3 < len(word) < 30:
                triggers.add(word)
    
    return sorted(list(triggers))[:10]  # макс 10 триггеров


def categorize_skill(name: str, description: str) -> str:
    """Определяет категорию скилла."""
    combined = f"{name} {description}".lower()
    
    if any(w in combined for w in ['seo', 'marketing', 'content', 'copy', 'social', 'brand']):
        return 'marketing'
    if any(w in combined for w in ['engineer', 'debug', 'deploy', 'code', 'frontend', 'backend', 'bot']):
        return 'engineering'
    if any(w in combined for w in ['design', 'ui', 'ux', 'visual']):
        return 'design'
    if any(w in combined for w in ['write', 'edit', 'content', 'article', 'shakespeare']):
        return 'content'
    if any(w in combined for w in ['research', 'audit', 'analysis', 'intelligence']):
        return 'research'
    if any(w in combined for w in ['plan', 'brain', 'verif', 'skill', 'find', 'execut']):
        return 'meta'
    if any(w in combined for w in ['core', 'orchestr', 'agent']):
        return 'core'
    
    return 'other'


def generate_manifest(skills: list) -> str:
    """Генерирует MANIFEST.md для boot-загрузки."""
    # Группируем по категориям
    categories = {}
    for skill in skills:
        cat = skill.category
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(skill)
    
    # Названия категорий на русском
    cat_names = {
        'core': '🧠 Core (оркестрация)',
        'engineering': '🔧 Engineering (разработка)',
        'marketing': '📈 Marketing (продвижение)',
        'content': '✍️ Content (контент)',
        'design': '🎨 Design (дизайн)',
        'research': '🔍 Research (исследования)',
        'meta': '⚙️ Meta (утилиты)',
        'other': '📦 Other',
    }
    
    total_tokens = sum(s.est_tokens for s in skills)
    manifest_tokens = len(skills) * 50  # ~50 токенов на запись
    
    lines = [
        "# 📋 SKILLS MANIFEST — Progressive Disclosure",
        "",
        f"> **{len(skills)} скиллов** | Full: ~{total_tokens:,} токенов | Manifest: ~{manifest_tokens:,} токенов | **{total_tokens // manifest_tokens}x экономия**",
        "> При boot читай ТОЛЬКО этот файл. Загружай полный SKILL.md только когда задача матчит.",
        "",
        "## Как использовать",
        "",
        "1. **Boot:** Агент читает этот MANIFEST.md (~2.8K токенов вместо ~104K)",
        "2. **Match:** Когда задача совпадает с описанием/триггерами → `view_file` на полный SKILL.md",
        "3. **Execute:** Агент следует инструкциям скилла",
        "4. **Release:** После задачи контекст скилла не нужен",
        "",
        "---",
        "",
    ]
    
    # Категории в нужном порядке
    cat_order = ['core', 'engineering', 'marketing', 'content', 'design', 'research', 'meta', 'other']
    
    for cat in cat_order:
        if cat not in categories:
            continue
        skills_in_cat = sorted(categories[cat], key=lambda s: s.name)
        
        lines.append(f"### {cat_names.get(cat, cat)}")
        lines.append("")
        lines.append("| Скилл | Описание | Размер | Триггеры |")
        lines.append("|-------|----------|:------:|----------|")
        
        for s in skills_in_cat:
            # Обрезаем описание до 80 символов
            desc_short = s.description[:80] + ('...' if len(s.description) > 80 else '')
            size_str = f"{s.est_tokens // 1000}K" if s.est_tokens > 1000 else f"{s.est_tokens}"
            triggers_str = ', '.join(s.triggers[:5]) if s.triggers else '—'
            extras = []
            if s.has_references:
                extras.append('📚')
            if s.has_scripts:
                extras.append('⚡')
            extra_str = ' '.join(extras)
            
            lines.append(f"| **{s.name}** {extra_str} | {desc_short} | {size_str} | {triggers_str} |")
        
        lines.append("")
    
    # Полные пути для загрузки
    lines.extend([
        "---",
        "",
        "## 📂 Пути для загрузки",
        "",
        "```",
    ])
    for s in sorted(skills, key=lambda s: s.name):
        lines.append(f"{s.name}: {s.path}")
    lines.extend([
        "```",
        "",
        f"> 🤖 Сгенерировано: `tools/skills_manifest.py` | {len(skills)} скиллов",
    ])
    
    return '\n'.join(lines)


def match_skill(query: str, skills: list) -> list:
    """Находит подходящие скиллы по описанию задачи."""
    query_lower = query.lower()
    query_words = set(re.findall(r'\w{3,}', query_lower))
    
    scored = []
    for skill in skills:
        score = 0
        
        # Матч по триггерам (вес 3)
        for trigger in skill.triggers:
            trigger_words = set(trigger.split())
            overlap = query_words & trigger_words
            if overlap:
                score += len(overlap) * 3
            if trigger in query_lower:
                score += 5
        
        # Матч по описанию (вес 1)
        desc_words = set(re.findall(r'\w{3,}', skill.description.lower()))
        desc_overlap = query_words & desc_words
        score += len(desc_overlap)
        
        # Матч по имени (вес 2)
        name_words = set(skill.name.replace('-', ' ').replace('_', ' ').split())
        name_overlap = query_words & name_words
        score += len(name_overlap) * 2
        
        if score > 0:
            scored.append((score, skill))
    
    scored.sort(key=lambda x: -x[0])
    return scored[:5]  # ТОП-5


def main():
    parser = argparse.ArgumentParser(description="🎯 Skills Manifest Generator")
    parser.add_argument('--format', choices=['md', 'json'], default='md')
    parser.add_argument('--match', '-m', help='Найти скилл по описанию задачи')
    parser.add_argument('--stats', action='store_true', help='Показать статистику')
    parser.add_argument('--output', '-o', help='Путь для вывода (default: MANIFEST.md)')
    
    args = parser.parse_args()
    
    # Собираем все скиллы
    skills = []
    
    # Глобальные скиллы
    if SKILLS_DIR.exists():
        for skill_dir in sorted(SKILLS_DIR.iterdir()):
            if skill_dir.is_dir() and not skill_dir.name.startswith('.'):
                info = extract_skill_info(skill_dir)
                if info:
                    skills.append(info)
    
    if not skills:
        print("❌ Скиллы не найдены")
        sys.exit(1)
    
    # Режим поиска
    if args.match:
        results = match_skill(args.match, skills)
        if not results:
            print(f"❌ Нет подходящих скиллов для: «{args.match}»")
            sys.exit(1)
        
        print(f"🎯 Поиск: «{args.match}»\n")
        for score, skill in results:
            print(f"  [{score:2d}] {skill.name}")
            print(f"       {skill.description[:100]}")
            print(f"       📂 {skill.path}")
            print()
        
        if results:
            best = results[0][1]
            print(f"💡 Загрузи: view_file → {best.path}")
        return
    
    # Режим статистики
    if args.stats:
        total_bytes = sum(s.size_bytes for s in skills)
        total_lines = sum(s.size_lines for s in skills)
        total_tokens = sum(s.est_tokens for s in skills)
        
        cats = {}
        for s in skills:
            cats.setdefault(s.category, []).append(s)
        
        print(f"📊 Skills Statistics")
        print(f"{'='*50}")
        print(f"Всего скиллов: {len(skills)}")
        print(f"Размер: {total_bytes:,} байт ({total_bytes // 1024} KB)")
        print(f"Строк: {total_lines:,}")
        print(f"≈ Токенов (full load): {total_tokens:,}")
        print(f"≈ Токенов (manifest): {len(skills) * 50}")
        print(f"Экономия: {total_tokens // (len(skills) * 50)}x")
        print()
        print(f"По категориям:")
        for cat, cat_skills in sorted(cats.items()):
            cat_tokens = sum(s.est_tokens for s in cat_skills)
            print(f"  {cat}: {len(cat_skills)} скиллов, ~{cat_tokens:,} токенов")
        print()
        print(f"ТОП-5 тяжёлых:")
        for s in sorted(skills, key=lambda x: -x.est_tokens)[:5]:
            print(f"  {s.est_tokens:>6,} tok | {s.name}")
        return
    
    # Генерация манифеста
    if args.format == 'json':
        data = {
            "generated": "skills_manifest.py",
            "total_skills": len(skills),
            "skills": [
                {
                    "name": s.name,
                    "path": s.path,
                    "description": s.description,
                    "triggers": s.triggers,
                    "category": s.category,
                    "est_tokens": s.est_tokens,
                }
                for s in skills
            ]
        }
        output = json.dumps(data, ensure_ascii=False, indent=2)
        
        out_path = args.output or str(MANIFEST_JSON_PATH)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"📋 JSON manifest: {out_path}")
    else:
        manifest = generate_manifest(skills)
        
        out_path = args.output or str(MANIFEST_PATH)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(manifest)
        
        print(f"📋 Manifest: {out_path}")
        print(f"📊 {len(skills)} скиллов | ~{sum(s.est_tokens for s in skills):,} → ~{len(skills) * 50} токенов")


if __name__ == '__main__':
    main()
