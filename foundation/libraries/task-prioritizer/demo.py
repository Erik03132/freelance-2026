#!/usr/bin/env python3
"""
Тестовый скрипт для демонстрации task-prioritizer скилла.
Показывает, как Шерлок может приоритизировать находки о конкурентах.
"""

import sys
from datetime import datetime
from pathlib import Path

# Добавляем путь к библиотеке
sys.path.insert(0, str(Path(__file__).parent.parent / "libraries" / "task-prioritizer"))

from task_prioritizer import TaskScorer


def demo_basic_scoring():
    """Демонстрация базового скоринга"""
    print("=" * 80)
    print("🎯 DEMO 1: Базовый скоринг задач")
    print("=" * 80)
    
    scorer = TaskScorer(project_id="demo", niche="backend")
    scorer.load_niche_config("backend")
    
    # Простой баг
    task1 = {
        "id": "T1",
        "title": "Fix typo in error message",
        "component": "frontend",
        "tags": ["bug", "low-priority"],
        "created_at": datetime.now().isoformat(),
    }
    
    score1 = scorer.score_task(task1)
    print(f"\n📌 Задача 1: {task1['title']}")
    print(f"   Скор: {score1.total}/100")
    print(f"   Объяснение: {score1.breakdown}")
    print(f"   Независимых сигналов: {score1.independent_signals}")
    
    # Production outage
    task2 = {
        "id": "T2",
        "title": "Database connection pool exhausted - API down",
        "description": "PostgreSQL connections timeout. Production outage affects all users.",
        "component": "database",
        "tags": ["production", "critical", "urgent"],
        "created_at": datetime.now().isoformat(),
        "related_issues": 5,
        "reactions": 12,
    }
    
    score2 = scorer.score_task(task2)
    print(f"\n📌 Задача 2: {task2['title']}")
    print(f"   Скор: {score2.total}/100")
    print(f"   Объяснение: {score2.breakdown}")
    print(f"   Независимых сигналов: {score2.independent_signals}")
    
    # Security issue
    task3 = {
        "id": "T3",
        "title": "XSS vulnerability in user input validation",
        "component": "auth",
        "tags": ["security", "vulnerability"],
        "created_at": datetime.now().isoformat(),
    }
    
    score3 = scorer.score_task(task3)
    print(f"\n📌 Задача 3: {task3['title']}")
    print(f"   Скор: {score3.total}/100")
    print(f"   Объяснение: {score3.breakdown}")
    print(f"   Независимых сигналов: {score3.independent_signals}")


def demo_ranking():
    """Демонстрация ранжирования"""
    print("\n" + "=" * 80)
    print("🎯 DEMO 2: Ранжирование задач по приоритету")
    print("=" * 80)
    
    scorer = TaskScorer(project_id="demo", niche="backend")
    scorer.load_niche_config("backend")
    
    tasks = [
        {
            "id": "T1",
            "title": "Add dark mode toggle",
            "component": "frontend",
            "tags": ["feature"],
            "created_at": datetime.now().isoformat(),
        },
        {
            "id": "T2",
            "title": "Fix critical memory leak in production",
            "component": "database",
            "tags": ["production", "critical", "performance"],
            "created_at": datetime.now().isoformat(),
            "related_issues": 3,
        },
        {
            "id": "T3",
            "title": "Update README documentation",
            "component": "docs",
            "tags": ["documentation"],
            "created_at": datetime.now().isoformat(),
        },
        {
            "id": "T4",
            "title": "Refactor legacy authentication module",
            "component": "auth",
            "tags": ["refactor", "tech-debt"],
            "created_at": datetime.now().isoformat(),
        },
    ]
    
    ranked = scorer.rank_tasks(tasks)
    
    print("\n📊 Отранжированные задачи (по приоритету):\n")
    for i, task in enumerate(ranked, 1):
        print(f"{i}. [{task['priority_score']:3d}] {task['id']}: {task['title']}")
        print(f"   └─ {task['score_breakdown']}\n")


def demo_trends():
    """Демонстрация детектирования трендов"""
    print("=" * 80)
    print("🎯 DEMO 3: Детектирование трендов в нише")
    print("=" * 80)
    
    scorer = TaskScorer(project_id="demo", niche="backend")
    scorer.load_niche_config("backend")
    
    # Симулируем находки о конкурентах
    competitor_findings = [
        {
            "id": "F1",
            "title": "Competitor A launched new AI feature",
            "component": "competitor_a",
            "tags": ["feature_launch", "ai"],
            "created_at": datetime.now().isoformat(),
        },
        {
            "id": "F2",
            "title": "Competitor B's API went down for 3 hours",
            "component": "competitor_b",
            "tags": ["outage", "production"],
            "created_at": datetime.now().isoformat(),
            "related_issues": 4,
        },
        {
            "id": "F3",
            "title": "Competitor C had a security breach",
            "component": "competitor_c",
            "tags": ["security", "vulnerability"],
            "created_at": datetime.now().isoformat(),
            "reactions": 8,
        },
        {
            "id": "F4",
            "title": "Competitor A's new pricing model",
            "component": "competitor_a",
            "tags": ["price_change"],
            "created_at": datetime.now().isoformat(),
        },
        {
            "id": "F5",
            "title": "Competitor B launched mobile app",
            "component": "competitor_b",
            "tags": ["feature_launch"],
            "created_at": datetime.now().isoformat(),
        },
    ]
    
    trends = scorer.detect_trend(competitor_findings)
    
    print("\n📈 Тренды в нише:\n")
    for trigger, findings in sorted(trends.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"🔥 {trigger}: {len(findings)} находок")
        for finding in findings:
            print(f"   • {finding.get('title', 'N/A')}")
        print()


def demo_competitor_research():
    """Демонстрация использования для исследования конкурентов (как в Шерлоке)"""
    print("=" * 80)
    print("🎯 DEMO 4: Исследование конкурентов (sherl-research use case)")
    print("=" * 80)
    
    scorer = TaskScorer(project_id="competitor-research", niche="market-intelligence")
    scorer.load_niche_config("backend")  # Используем backend конфиг как пример
    
    print("\n🔍 Находки о конкурентах:\n")
    
    findings = [
        {
            "id": "C1",
            "title": "Google announced new AI Overviews with real-time search",
            "component": "google",
            "tags": ["ai_feature", "competitive_threat"],
            "created_at": datetime.now().isoformat(),
            "related_issues": 7,
        },
        {
            "id": "C2",
            "title": "Perplexity raised $500M Series B funding",
            "component": "perplexity",
            "tags": ["funding", "market_expansion"],
            "created_at": datetime.now().isoformat(),
            "reactions": 15,
        },
        {
            "id": "C3",
            "title": "ChatGPT introduced new voice features",
            "component": "openai",
            "tags": ["feature_launch"],
            "created_at": datetime.now().isoformat(),
        },
    ]
    
    ranked_findings = scorer.rank_tasks(findings)
    
    print("📊 Приоритизированные находки:\n")
    for i, finding in enumerate(ranked_findings, 1):
        print(f"{i}. [{finding['priority_score']:3d}] {finding['id']}")
        print(f"   Компания: {finding['component']}")
        print(f"   Новость: {finding['title']}")
        print(f"   Анализ: {finding['score_breakdown']}\n")


def demo_freshness_decay():
    """Демонстрация множителя свежести"""
    print("=" * 80)
    print("🎯 DEMO 5: Множитель свежести (старые задачи теряют приоритет)")
    print("=" * 80)
    
    scorer = TaskScorer(project_id="demo", niche="backend")
    scorer.load_niche_config("backend")
    
    from datetime import timedelta
    
    now = datetime.now()
    
    tasks = [
        {
            "id": "T1",
            "title": "Production database down",
            "tags": ["production", "critical"],
            "component": "database",
            "created_at": now.isoformat(),  # Сейчас
        },
        {
            "id": "T2",
            "title": "Production database down (reported 12 hours ago)",
            "tags": ["production", "critical"],
            "component": "database",
            "created_at": (now - timedelta(hours=12)).isoformat(),
        },
        {
            "id": "T3",
            "title": "Production database down (reported 3 days ago)",
            "tags": ["production", "critical"],
            "component": "database",
            "created_at": (now - timedelta(days=3)).isoformat(),
        },
    ]
    
    print("\n⏰ Влияние времени на приоритет:\n")
    for task in tasks:
        score = scorer.score_task(task)
        print(f"[{score.total:3d}] {task['id']}: {task['title']}")
        print(f"      Множитель: ×{score.freshness_multiplier}\n")


def main():
    """Запустить все демонстрации"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "🚀 TASK-PRIORITIZER DEMO (из ContentCombine)" + " " * 20 + "║")
    print("╚" + "=" * 78 + "╝")
    
    try:
        demo_basic_scoring()
        demo_ranking()
        demo_trends()
        demo_competitor_research()
        demo_freshness_decay()
        
        print("\n" + "=" * 80)
        print("✅ Все демонстрации завершены успешно!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
