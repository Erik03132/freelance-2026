#!/usr/bin/env python3
"""
QUICK START: task-prioritizer в sherl-research

Пример использования новой фичи для приоритизации находок о конкурентах.
"""

from task_prioritizer import TaskScorer
from datetime import datetime

# ============================================================================
# ПРИМЕР 1: Базовое использование
# ============================================================================

def example_basic_usage():
    """Базовый пример скоринга одной задачи"""
    print("\n" + "="*80)
    print("ПРИМЕР 1: Базовое использование")
    print("="*80 + "\n")
    
    # Инициализация скорера
    scorer = TaskScorer(project_id="my-project")
    scorer.load_niche_config("backend")
    
    # Задача для скоринга
    task = {
        "id": "TASK-001",
        "title": "Production database connection pool exhausted",
        "description": "PostgreSQL connections timeout after 100 concurrent users",
        "component": "database",
        "tags": ["production", "critical", "urgent"],
        "created_at": datetime.now().isoformat(),
        "related_issues": 3,
    }
    
    # Скорим задачу
    score = scorer.score_task(task)
    
    print(f"Задача: {task['title']}")
    print(f"Скор: {score.total}/100")
    print(f"Триггеры: {score.triggers}")
    print(f"Сущности: {score.entities}")
    print(f"Комбинации: {score.combos}")
    print(f"Множитель свежести: {score.freshness_multiplier}")
    print(f"Независимые сигналы: {score.independent_signals}")
    print(f"Объяснение: {score.breakdown}")


# ============================================================================
# ПРИМЕР 2: Ранжирование списка задач
# ============================================================================

def example_ranking():
    """Ранжирование списка задач по приоритету"""
    print("\n" + "="*80)
    print("ПРИМЕР 2: Ранжирование списка задач")
    print("="*80 + "\n")
    
    scorer = TaskScorer(project_id="my-project")
    scorer.load_niche_config("backend")
    
    # Список задач
    tasks = [
        {
            "id": "T1",
            "title": "Add dark mode feature",
            "component": "frontend",
            "tags": ["feature"],
            "created_at": datetime.now().isoformat(),
        },
        {
            "id": "T2",
            "title": "Fix critical security vulnerability in auth",
            "component": "auth",
            "tags": ["security", "critical"],
            "created_at": datetime.now().isoformat(),
            "related_issues": 2,
        },
        {
            "id": "T3",
            "title": "Update README documentation",
            "component": "docs",
            "tags": ["documentation"],
            "created_at": datetime.now().isoformat(),
        },
    ]
    
    # Ранжируем
    ranked = scorer.rank_tasks(tasks)
    
    print("Отранжированные задачи (по приоритету):\n")
    for i, task in enumerate(ranked, 1):
        print(f"{i}. [{task['priority_score']:3d}] {task['id']}: {task['title']}")
        print(f"   Объяснение: {task['score_breakdown']}\n")


# ============================================================================
# ПРИМЕР 3: Использование в sherl-research для исследования конкурентов
# ============================================================================

def example_competitor_research():
    """Использование task-prioritizer в sherl-research"""
    print("\n" + "="*80)
    print("ПРИМЕР 3: Исследование конкурентов (sherl-research)")
    print("="*80 + "\n")
    
    scorer = TaskScorer(project_id="competitor-research")
    scorer.load_niche_config("backend")
    
    # Симулируем находки о конкурентах
    findings = [
        {
            "id": "FIND-001",
            "title": "Competitor A launched AI-powered search feature",
            "component": "competitor_a",
            "tags": ["feature_launch", "ai"],
            "created_at": datetime.now().isoformat(),
        },
        {
            "id": "FIND-002",
            "title": "Competitor B's API went down for 3 hours (production outage)",
            "component": "competitor_b",
            "tags": ["outage", "production"],
            "created_at": datetime.now().isoformat(),
            "related_issues": 4,
            "reactions": 12,
        },
        {
            "id": "FIND-003",
            "title": "Competitor C discovered security breach affecting users",
            "component": "competitor_c",
            "tags": ["security", "vulnerability"],
            "created_at": datetime.now().isoformat(),
        },
    ]
    
    # Ранжируем находки по приоритету
    ranked_findings = scorer.rank_tasks(findings)
    
    print("🔍 Приоритизированные находки о конкурентах:\n")
    for i, finding in enumerate(ranked_findings, 1):
        print(f"{i}. [{finding['priority_score']:3d}] {finding['id']}")
        print(f"   Компания: {finding['component']}")
        print(f"   Новость: {finding['title']}")
        print(f"   Анализ: {finding['score_breakdown']}\n")


# ============================================================================
# ПРИМЕР 4: Детектирование трендов
# ============================================================================

def example_trend_detection():
    """Детектирование трендов в нише"""
    print("\n" + "="*80)
    print("ПРИМЕР 4: Детектирование трендов")
    print("="*80 + "\n")
    
    scorer = TaskScorer(project_id="my-project")
    scorer.load_niche_config("backend")
    
    # Много задач по разным триггерам
    tasks = [
        {"id": "T1", "title": "API down", "tags": ["production"], "component": "api", "created_at": datetime.now().isoformat()},
        {"id": "T2", "title": "Database slow", "tags": ["performance"], "component": "database", "created_at": datetime.now().isoformat()},
        {"id": "T3", "title": "API timeout", "tags": ["production"], "component": "api", "created_at": datetime.now().isoformat()},
        {"id": "T4", "title": "Memory leak", "tags": ["performance"], "component": "backend", "created_at": datetime.now().isoformat()},
    ]
    
    # Детектируем тренды
    trends = scorer.detect_trend(tasks)
    
    print("📈 Тренды в нише:\n")
    for trigger, trend_tasks in sorted(trends.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"🔥 {trigger}: {len(trend_tasks)} задач")
        for task in trend_tasks:
            print(f"   • {task.get('title', 'N/A')}")
        print()


# ============================================================================
# ПРИМЕР 5: Обучение на решениях
# ============================================================================

def example_learning():
    """Обучение системы на решениях разработчика"""
    print("\n" + "="*80)
    print("ПРИМЕР 5: Обучение на решениях")
    print("="*80 + "\n")
    
    scorer = TaskScorer(project_id="my-project")
    scorer.load_niche_config("backend")
    
    print("Регистрируем решения разработчика:\n")
    
    # Разработчик быстро решил production issue
    scorer.record_decision(
        task_id="TASK-001",
        action="resolved",
        time_to_resolution=1800,  # 30 минут
        difficulty="high"
    )
    print("✓ Решена production issue за 30 минут (высокая сложность)")
    
    # Разработчик отложил tech-debt задачу
    scorer.record_decision(
        task_id="TASK-002",
        action="postponed",
        difficulty="low"
    )
    print("✓ Отложена tech-debt задача (низкая сложность)")
    
    # Разработчик отклонил низкоприоритетную задачу
    scorer.record_decision(
        task_id="TASK-003",
        action="rejected",
        difficulty="trivial"
    )
    print("✓ Отклонена trivial задача\n")
    
    # Статистика
    health = scorer.get_source_health()
    print(f"Всего решений записано: {health['decision_count']}")
    print("\nСистема теперь знает, что разработчик:")
    print("  • Быстро решает production issues")
    print("  • Откладывает tech-debt")
    print("  • Отклоняет trivial задачи")
    print("\nВеса триггеров будут пересчитаны на основе этого! 📊")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n╔" + "="*78 + "╗")
    print("║" + " "*20 + "QUICK START: task-prioritizer в sherl-research" + " "*14 + "║")
    print("╚" + "="*78 + "╝")
    
    try:
        example_basic_usage()
        example_ranking()
        example_competitor_research()
        example_trend_detection()
        example_learning()
        
        print("\n" + "="*80)
        print("✅ Все примеры выполнены успешно!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/Users/igorvasin/freelance-2026/foundation/libraries/task-prioritizer")
    sys.exit(main())
