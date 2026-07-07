#!/usr/bin/env python3
"""
ПОШАГОВЫЙ ГАЙД: Как использовать task-prioritizer с GitHub Issues

Этот скрипт показывает КОНКРЕТНО, как:
1. Получить issues из GitHub
2. Преобразовать их в формат для task-prioritizer
3. Ранжировать по приоритету
4. Вывести результаты

Результат: вместо 100 issues в хаосе → TOP-10 по приоритету
"""

import requests
from datetime import datetime
from task_prioritizer import TaskScorer


# ============================================================================
# ШАГ 1: ПОЛУЧИТЬ ISSUES ИЗ GITHUB
# ============================================================================

def get_github_issues(owner, repo, github_token=None):
    """
    Получить все открытые issues из GitHub репозитория.
    
    Параметры:
    - owner: имя пользователя/организации (например, "facebook")
    - repo: имя репозитория (например, "react")
    - github_token: опционально, для большего лимита запросов
    
    Возвращает: список issues в формате GitHub API
    """
    
    print(f"📥 Получаю issues из {owner}/{repo}...\n")
    
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    
    params = {
        "state": "open",
        "per_page": 100,  # максимум 100 за один запрос
    }
    
    headers = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        issues = response.json()
        print(f"✅ Получено {len(issues)} issues\n")
        return issues
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при получении issues: {e}\n")
        return []


# ============================================================================
# ШАГ 2: ПРЕОБРАЗОВАТЬ В ФОРМАТ ДЛЯ task-prioritizer
# ============================================================================

def convert_github_issues_to_tasks(github_issues):
    """
    Преобразовать GitHub issues в формат для task-prioritizer.
    
    GitHub issue:
    {
        "number": 123,
        "title": "Fix bug in authentication",
        "labels": [{"name": "bug"}, {"name": "critical"}],
        "created_at": "2026-06-29T10:00:00Z",
        "reactions": {"+1": 5, "-1": 0, ...}
    }
    
    Преобразуется в:
    {
        "id": "GH-123",
        "title": "Fix bug in authentication",
        "tags": ["bug", "critical"],
        "created_at": "2026-06-29T10:00:00Z",
        "reactions": 5
    }
    """
    
    print("🔄 Преобразую issues в формат task-prioritizer...\n")
    
    tasks = []
    
    for issue in github_issues:
        # Пропускаем pull requests
        if "pull_request" in issue:
            continue
        
        # Извлекаем labels (теги)
        tags = [label["name"] for label in issue.get("labels", [])]
        
        # Считаем реакции (👍)
        reactions = issue.get("reactions", {}).get("+1", 0)
        
        # Создаём задачу в формате task-prioritizer
        task = {
            "id": f"GH-{issue['number']}",
            "title": issue["title"],
            "tags": tags,
            "created_at": issue["created_at"],
            "reactions": reactions,
            "component": "github",  # можно парсить из labels
        }
        
        tasks.append(task)
    
    print(f"✅ Преобразовано {len(tasks)} tasks\n")
    return tasks


# ============================================================================
# ШАГ 3: ИНИЦИАЛИЗИРОВАТЬ СКОРЕР
# ============================================================================

def init_scorer():
    """Инициализировать task-prioritizer скорер"""
    
    print("⚙️  Инициализирую scorer...\n")
    
    scorer = TaskScorer(project_id="github-issues")
    scorer.load_niche_config("backend")
    
    print("✅ Scorer готов\n")
    return scorer


# ============================================================================
# ШАГ 4: РАНЖИРОВАТЬ ISSUES
# ============================================================================

def rank_issues(scorer, tasks):
    """Ранжировать issues по приоритету"""
    
    print("📊 Ранжирую issues по приоритету...\n")
    
    ranked = scorer.rank_tasks(tasks)
    
    print(f"✅ Ранжировано {len(ranked)} issues\n")
    return ranked


# ============================================================================
# ШАГ 5: ВЫВЕСТИ РЕЗУЛЬТАТЫ
# ============================================================================

def print_results(ranked, top_n=10):
    """
    Вывести результаты в красивом формате.
    
    Покажет:
    - Топ-10 issues по приоритету
    - Скор каждого issue
    - Почему он получил такой скор
    """
    
    print("=" * 100)
    print("🎯 РЕЗУЛЬТАТЫ: TOP ISSUES ПО ПРИОРИТЕТУ")
    print("=" * 100)
    print()
    
    for i, task in enumerate(ranked[:top_n], 1):
        score = task["priority_score"]
        
        # Цвет в зависимости от скора
        if score >= 80:
            priority_level = "🔴 КРИТИЧНО"
        elif score >= 60:
            priority_level = "🟠 ВЫСОКИЙ"
        elif score >= 40:
            priority_level = "🟡 СРЕДНИЙ"
        else:
            priority_level = "🟢 НИЗКИЙ"
        
        print(f"{i}. {priority_level}")
        print(f"   ID: {task['id']}")
        print(f"   Скор: {score}/100")
        print(f"   Название: {task['title']}")
        print(f"   Анализ: {task['score_breakdown']}")
        print()


# ============================================================================
# MAIN: СОБРАТЬ ВСЁ ВМЕСТЕ
# ============================================================================

def main():
    """Главная функция: получить, преобразовать, ранжировать, вывести"""
    
    print("\n")
    print("╔" + "=" * 98 + "╗")
    print("║" + " " * 20 + "ПРАКТИЧЕСКИЙ ПРИМЕР: GitHub Issues + task-prioritizer" + " " * 24 + "║")
    print("╚" + "=" * 98 + "╝")
    print()
    
    # --------
    # ВАРИАНТ 1: Реальный GitHub репозиторий
    # --------
    # Раскомментируй это, если хочешь использовать реальный репо
    
    # owner = "facebook"  # или любой другой
    # repo = "react"
    # github_token = None  # или твой GitHub token для большего лимита
    # 
    # issues = get_github_issues(owner, repo, github_token)
    # if not issues:
    #     return
    
    # --------
    # ВАРИАНТ 2: Демо-данные (для примера)
    # --------
    # Используем готовые примеры issues
    
    print("📌 Используем ДЕМО-ДАННЫЕ (примеры issues)\n")
    
    issues = [
        {
            "number": 1001,
            "title": "Production database connection timeout",
            "labels": [{"name": "bug"}, {"name": "production"}, {"name": "critical"}],
            "created_at": datetime.now().isoformat() + "Z",
            "reactions": {"+1": 12, "-1": 0},
        },
        {
            "number": 1002,
            "title": "Add dark mode feature",
            "labels": [{"name": "feature"}, {"name": "ui"}],
            "created_at": datetime.now().isoformat() + "Z",
            "reactions": {"+1": 45, "-1": 0},
        },
        {
            "number": 1003,
            "title": "Fix typo in README",
            "labels": [{"name": "documentation"}],
            "created_at": datetime.now().isoformat() + "Z",
            "reactions": {"+1": 0, "-1": 0},
        },
        {
            "number": 1004,
            "title": "Security vulnerability in authentication",
            "labels": [{"name": "security"}, {"name": "critical"}],
            "created_at": datetime.now().isoformat() + "Z",
            "reactions": {"+1": 8, "-1": 0},
        },
        {
            "number": 1005,
            "title": "API endpoint returns 500 error",
            "labels": [{"name": "bug"}, {"name": "api"}],
            "created_at": datetime.now().isoformat() + "Z",
            "reactions": {"+1": 3, "-1": 0},
        },
        {
            "number": 1006,
            "title": "Update dependencies",
            "labels": [{"name": "maintenance"}, {"name": "dependencies"}],
            "created_at": datetime.now().isoformat() + "Z",
            "reactions": {"+1": 1, "-1": 0},
        },
        {
            "number": 1007,
            "title": "Improve performance on mobile",
            "labels": [{"name": "performance"}, {"name": "mobile"}],
            "created_at": datetime.now().isoformat() + "Z",
            "reactions": {"+1": 20, "-1": 0},
        },
        {
            "number": 1008,
            "title": "Add unit tests for payment module",
            "labels": [{"name": "testing"}],
            "created_at": datetime.now().isoformat() + "Z",
            "reactions": {"+1": 2, "-1": 0},
        },
    ]
    
    # --------
    # ПРОЦЕСС
    # --------
    
    # Шаг 1: Преобразовать
    tasks = convert_github_issues_to_tasks(issues)
    
    # Шаг 2: Инициализировать скорер
    scorer = init_scorer()
    
    # Шаг 3: Ранжировать
    ranked = rank_issues(scorer, tasks)
    
    # Шаг 4: Вывести результаты
    print_results(ranked, top_n=10)
    
    # --------
    # ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ
    # --------
    
    print("=" * 100)
    print("📊 СТАТИСТИКА")
    print("=" * 100)
    print()
    
    print(f"Всего issues: {len(ranked)}")
    print(f"Критичные (скор >= 80): {len([t for t in ranked if t['priority_score'] >= 80])}")
    print(f"Высокие (скор 60-80): {len([t for t in ranked if 60 <= t['priority_score'] < 80])}")
    print(f"Средние (скор 40-60): {len([t for t in ranked if 40 <= t['priority_score'] < 60])}")
    print(f"Низкие (скор < 40): {len([t for t in ranked if t['priority_score'] < 40])}")
    print()


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/Users/igorvasin/freelance-2026/foundation/libraries/task-prioritizer")
    main()
