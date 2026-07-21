"""
ScoutAgent — анализирует задачу: категория, выполнимость, скилл-матчинг, трудоёмкость.
"""

import json
import re
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = ROOT / "config"


class ScoutResult:
    def __init__(
        self,
        category: str,
        feasible: bool,
        effort_hours: float,
        skill_coverage: float,
        hourly_rate: float,
        blockers: list[str],
        missing_skills: list[str],
        clarity_score: float,
    ):
        self.category = category
        self.feasible = feasible
        self.effort_hours = effort_hours
        self.skill_coverage = skill_coverage
        self.hourly_rate = hourly_rate
        self.blockers = blockers
        self.missing_skills = missing_skills
        self.clarity_score = clarity_score

    def to_dict(self):
        return {
            "category": self.category,
            "feasible": self.feasible,
            "effort_hours": self.effort_hours,
            "skill_coverage": self.skill_coverage,
            "hourly_rate": self.hourly_rate,
            "blockers": self.blockers,
            "missing_skills": self.missing_skills,
            "clarity_score": self.clarity_score,
        }


class ScoutAgent:
    CATEGORIES = {
        "web_fullstack": ["react", "vue", "angular", "next", "nuxt", "fullstack", "frontend", "backend", "api"],
        "telegram_bot": ["telegram", "tg bot", "aiogram", "telegram bot"],
        "parsing_scraping": ["парсинг", "scraping", "scraper", "parser", "сбор данных"],
        "ai_ml": ["ai", "ии", "нейросеть", "ml", "machine learning", "gpt", "llm", "rag", "chatbot"],
        "integration": ["интеграция", "api", "bitrix", "crm", "mango"],
        "web_dev": ["сайт", "landing", "лендинг", "web", "html", "css", "react", "vue"],
        "automation": ["автоматизация", "automation", "бот", "bot", "скрипт"],
        "design": ["дизайн", "figma", "ui", "ux", "макет"],
        "content": ["текст", "копирайтинг", "статья", "seo", "geo"],
        "consulting": ["консультация", "аудит", "стратегия", "внедрение"],
    }

    def __init__(self):
        self.profile = self._load_profile()

    def _load_profile(self) -> dict:
        import json
        path = CONFIG_DIR / "profile.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return {"skills": {}, "skill_synonyms": {}}

    def classify(self, title: str, description: str) -> str:
        text = f"{title} {description}".lower()
        scores = {}
        for cat, keywords in self.CATEGORIES.items():
            scores[cat] = sum(1 for kw in keywords if kw in text)
        if not scores or max(scores.values()) == 0:
            return "other"
        return max(scores, key=scores.get)

    def match_skills(self, description: str) -> tuple[float, list[str], list[str]]:
        text = description.lower()
        user_skills = self.profile.get("skills", {})
        synonyms = self.profile.get("skill_synonyms", {})

        matched = []
        missing = []
        for skill, weight in user_skills.items():
            if skill.lower() in text:
                matched.append(skill)
                continue
            syns = synonyms.get(skill, [])
            if any(s.lower() in text for s in syns):
                matched.append(skill)
                continue

        # Check for unknown tech mentions
        known = set(matched)
        for cat_keywords in self.CATEGORIES.values():
            for kw in cat_keywords:
                if kw in text and kw not in known:
                    # Check if it's a tech term not in our skills
                    if not any(kw in s.lower() for s in self.profile.get("skills", {})):
                        missing.append(kw)

        if not matched:
            return 0.0, [], missing

        total_weight = sum(self.profile.get("skills", {}).get(s, 0.5) for s in matched)
        max_possible = len(matched) * 1.0
        coverage = total_weight / max_possible if max_possible > 0 else 0
        return min(coverage, 1.0), matched, missing

    def score_clarity(self, description: str) -> float:
        score = 0.0
        words = description.split()
        word_count = len(words)

        if word_count >= 150:
            score += 0.2
        elif word_count >= 80:
            score += 0.1

        clarity_signals = [
            r"\bstack\b", r"\bтехнологи", r"\bpython\b", r"\bfastapi\b",
            r"\bпример", r"\bреференс", r"https?://",
            r"\bпользователь\s+(должен|может)", r"\bсценарий\b",
            r"\bтребование\b", r"\bкритерий\b",
            r"\bбюджет\b", r"\bсрок\b",
        ]
        import re
        for pattern in clarity_signals:
            if re.search(pattern, description, re.IGNORECASE):
                score += 0.15

        vague = [
            r"\bкак-нибудь\b", r"\bкрасиво\b", r"\bподумаем по ходу\b",
            r"\bсделать хорошо\b", r"\bразберемся\b"
        ]
        for pattern in vague:
            if re.search(pattern, description, re.IGNORECASE):
                score -= 0.15

        return max(0.0, min(1.0, score))

    def analyze(self, title: str, description: str, budget_rub: int = 0) -> dict:
        category = self.classify(title, description)
        coverage, matched, missing = self.match_skills(description)
        clarity = self.score_clarity(description)

        feasible = coverage >= 0.5 and clarity >= 0.4
        blockers = []
        if coverage < 0.5:
            blockers.append(f"Skill coverage too low ({coverage:.0%})")
        if clarity < 0.4:
            blockers.append(f"Clarity too low ({clarity:.0%})")

        effort_hours = self._estimate_effort(description, category)
        hourly_rate = budget_rub / effort_hours if budget_rub and effort_hours else 0

        return {
            "category": category,
            "feasible": feasible,
            "effort_hours": effort_hours,
            "skill_coverage": round(coverage, 2),
            "hourly_rate": round(hourly_rate),
            "blockers": blockers,
            "missing_skills": missing,
            "clarity_score": round(clarity, 2),
        }

    def _estimate_effort(self, description: str, category: str) -> float:
        words = len(description.split())
        base = {
            "web_fullstack": 40, "telegram_bot": 20, "parsing_scraping": 15,
            "ai_ml": 30, "integration": 20, "web_dev": 25,
            "automation": 15, "design": 10, "content": 8, "consulting": 5,
        }.get(category, 20)
        complexity = min(words / 200, 2.0)
        return round(base * complexity, 1)
