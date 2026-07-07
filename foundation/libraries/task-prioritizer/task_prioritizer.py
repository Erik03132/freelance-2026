"""
Task Prioritizer - Система приоритизации задач на основе ContentCombine-паттернов.

Адаптация механик скоринга новостей для приоритизации задач разработки:
- Триггеры (категории событий с весами)
- Сущности (компоненты с тирами важности)
- Комбинации (событие + компонент = больше суммы частей)
- Свежесть (множитель по времени)
- Независимые сигналы (тренд = ≥2 сигнала)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import re
import json
from pathlib import Path


class EntityTier(Enum):
    """Тир важности компонента"""
    S = 30  # критичные: database, auth, payment
    A = 15  # важные: cache, queue, logging
    B = 8   # обычные: frontend, admin
    C = 3   # низкий: docs, examples


@dataclass
class TriggerConfig:
    """Конфиг триггера (категория события)"""
    name: str
    weight: int
    keys: List[str]
    category: str = ""  # для дедупликации (penalty_*, algoupd_*)


@dataclass
class EntityConfig:
    """Конфиг сущности (компонент)"""
    name: str
    tier: EntityTier
    aliases: List[str] = field(default_factory=list)


@dataclass
class ComboConfig:
    """Конфиг комбинации (событие + компонент)"""
    name: str
    triggers: List[str]  # какие триггеры активируют
    entities: List[str]  # какие сущности активируют
    bonus: int  # дополнительный скор


@dataclass
class ScoringResult:
    """Результат скоринга задачи"""
    total: int
    triggers: Dict[str, int]  # триггер → его вес
    entities: Dict[str, int]  # сущность → её буст
    combos: Dict[str, int]    # комбо → её бонус
    freshness_multiplier: float
    independent_signals: int
    breakdown: str  # человеческое объяснение


class TaskScorer:
    """Основной класс для скоринга задач"""

    def __init__(self, project_id: str, niche: str = "default"):
        self.project_id = project_id
        self.niche = niche
        
        self.triggers: Dict[str, TriggerConfig] = {}
        self.entities: Dict[str, EntityConfig] = {}
        self.combos: List[ComboConfig] = []
        
        self.max_score = 100
        self.min_signals_for_trend = 2
        
        # Статистика для обучения
        self.source_stats: Dict[str, Dict] = {}
        self.decision_history: List[Dict] = []
    
    def load_niche_config(self, niche: str) -> None:
        """Загрузить конфиг ниши (триггеры, сущности, комбо)"""
        self.niche = niche
        
        # Инициализируем дефолтный конфиг для backend
        self._init_default_config()
    
    def _init_default_config(self) -> None:
        """Инициализировать дефолтный конфиг для backend"""
        
        # Триггеры
        self.triggers = {
            "production_critical": TriggerConfig(
                name="production_critical",
                weight=40,
                keys=["production", "prod", "critical", "outage", "down", "broken"],
                category="severity"
            ),
            "performance_issue": TriggerConfig(
                name="performance_issue",
                weight=30,
                keys=["slow", "timeout", "crash", "memory leak", "cpu", "hang"],
                category="performance"
            ),
            "security_issue": TriggerConfig(
                name="security_issue",
                weight=35,
                keys=["vulnerability", "exploit", "security", "auth", "xss", "injection"],
                category="security"
            ),
            "data_loss": TriggerConfig(
                name="data_loss",
                weight=45,
                keys=["data loss", "corruption", "backup", "recovery", "lost"],
                category="severity"
            ),
            "api_breaking": TriggerConfig(
                name="api_breaking",
                weight=28,
                keys=["breaking change", "api", "deprecation", "migration"],
                category="breaking"
            ),
            "tech_debt": TriggerConfig(
                name="tech_debt",
                weight=12,
                keys=["refactor", "cleanup", "technical debt", "legacy", "rewrite"],
                category="maintenance"
            ),
            "feature_request": TriggerConfig(
                name="feature_request",
                weight=15,
                keys=["feature", "enhancement", "new", "add support", "implement"],
                category="feature"
            ),
            "documentation": TriggerConfig(
                name="documentation",
                weight=5,
                keys=["docs", "readme", "comment", "docstring", "guide"],
                category="docs"
            ),
        }
        
        # Сущности (компоненты)
        self.entities = {
            "database": EntityConfig("database", EntityTier.S, ["db", "postgres", "mysql", "mongodb"]),
            "auth": EntityConfig("auth", EntityTier.S, ["authentication", "login", "session"]),
            "payment": EntityConfig("payment", EntityTier.S, ["payment", "billing", "stripe"]),
            "api_gateway": EntityConfig("api_gateway", EntityTier.S, ["gateway", "router", "endpoint"]),
            
            "cache": EntityConfig("cache", EntityTier.A, ["redis", "memcached", "cache"]),
            "queue": EntityConfig("queue", EntityTier.A, ["queue", "celery", "rabbitmq"]),
            "logging": EntityConfig("logging", EntityTier.A, ["logging", "logs", "logger"]),
            "monitoring": EntityConfig("monitoring", EntityTier.A, ["monitoring", "metrics", "prometheus"]),
            
            "frontend": EntityConfig("frontend", EntityTier.B, ["ui", "react", "vue", "angular"]),
            "admin_panel": EntityConfig("admin_panel", EntityTier.B, ["admin", "dashboard"]),
            
            "docs": EntityConfig("docs", EntityTier.C, ["documentation", "docs", "guide"]),
            "tests": EntityConfig("tests", EntityTier.C, ["test", "spec", "unit"]),
        }
        
        # Комбинации
        self.combos = [
            ComboConfig(
                name="critical_component_issue",
                triggers=["production_critical", "data_loss"],
                entities=["database", "auth", "payment"],
                bonus=25
            ),
            ComboConfig(
                name="security_in_auth",
                triggers=["security_issue"],
                entities=["auth"],
                bonus=20
            ),
            ComboConfig(
                name="performance_in_database",
                triggers=["performance_issue"],
                entities=["database"],
                bonus=18
            ),
            ComboConfig(
                name="api_breaking_change",
                triggers=["api_breaking"],
                entities=["api_gateway"],
                bonus=15
            ),
        ]
    
    def score_task(self, task: Dict) -> ScoringResult:
        """Скорить одну задачу"""
        
        score_parts = {}
        detected_triggers = {}
        detected_entities = {}
        detected_combos = {}
        
        # 1. Детектируем триггеры
        detected_triggers = self._detect_triggers(task)
        score_parts["triggers"] = sum(detected_triggers.values())
        
        # 2. Детектируем сущности
        detected_entities = self._detect_entities(task)
        score_parts["entities"] = sum(e["boost"] for e in detected_entities.values())
        
        # 3. Ищем комбинации
        detected_combos = self._detect_combos(detected_triggers, detected_entities)
        score_parts["combos"] = sum(detected_combos.values())
        
        # 4. Множитель свежести
        freshness_mult = self._calculate_freshness_multiplier(task)
        
        # 5. Независимые сигналы
        independent_signals = self._count_independent_signals(task, detected_triggers, detected_entities)
        
        # 6. Итоговый скор
        base_score = sum(score_parts.values())
        final_score = min(int(base_score * freshness_mult), self.max_score)
        
        # 7. Объяснение
        breakdown = self._generate_breakdown(
            detected_triggers, detected_entities, detected_combos, independent_signals
        )
        
        return ScoringResult(
            total=final_score,
            triggers=detected_triggers,
            entities={k: v["boost"] for k, v in detected_entities.items()},
            combos=detected_combos,
            freshness_multiplier=freshness_mult,
            independent_signals=independent_signals,
            breakdown=breakdown
        )
    
    def _detect_triggers(self, task: Dict) -> Dict[str, int]:
        """Детектировать триггеры в задаче"""
        detected = {}
        text = self._normalize_text(task)
        
        # Группируем триггеры по категориям для дедупликации
        categories = {}
        
        for trigger_name, trigger_config in self.triggers.items():
            for key in trigger_config.keys:
                if self._match_key(key, text):
                    if trigger_config.category not in categories:
                        categories[trigger_config.category] = []
                    categories[trigger_config.category].append((trigger_name, trigger_config.weight))
                    break
        
        # Берём только самый весомый триггер из каждой категории
        for category, triggers_list in categories.items():
            best_trigger = max(triggers_list, key=lambda x: x[1])
            detected[best_trigger[0]] = best_trigger[1]
        
        return detected
    
    def _detect_entities(self, task: Dict) -> Dict[str, Dict]:
        """Детектировать сущности (компоненты) в задаче"""
        detected = {}
        text = self._normalize_text(task)
        
        for entity_name, entity_config in self.entities.items():
            # Проверяем основное имя и алиасы
            search_terms = [entity_name] + entity_config.aliases
            for term in search_terms:
                if self._match_key(term, text):
                    detected[entity_name] = {
                        "tier": entity_config.tier.name,
                        "boost": entity_config.tier.value
                    }
                    break
        
        return detected
    
    def _detect_combos(self, triggers: Dict[str, int], entities: Dict[str, Dict]) -> Dict[str, int]:
        """Детектировать комбинации (событие + компонент)"""
        detected = {}
        
        for combo in self.combos:
            # Проверяем, активирован ли триггер
            triggered = any(t in triggers for t in combo.triggers)
            # Проверяем, активирована ли сущность
            entitied = any(e in entities for e in combo.entities)
            
            if triggered and entitied:
                detected[combo.name] = combo.bonus
        
        return detected
    
    def _calculate_freshness_multiplier(self, task: Dict) -> float:
        """Рассчитать множитель свежести на основе времени"""
        
        if "created_at" not in task:
            return 1.0
        
        try:
            created = datetime.fromisoformat(task["created_at"].replace("Z", "+00:00"))
            now = datetime.now(created.tzinfo) if created.tzinfo else datetime.now()
            age = now - created
        except:
            return 1.0
        
        hours = age.total_seconds() / 3600
        
        if hours < 1:
            return 1.0
        elif hours < 6:
            return 0.95
        elif hours < 24:
            return 0.85
        elif hours < 72:  # 3 дня
            return 0.7
        elif hours < 168:  # 7 дней
            return 0.5
        else:
            return 0.3
    
    def _count_independent_signals(self, task: Dict, triggers: Dict, entities: Dict) -> int:
        """Считать независимые сигналы (тренд = ≥2)"""
        signals = 0
        
        # Сигнал 1: есть триггер
        if triggers:
            signals += 1
        
        # Сигнал 2: есть S-tier сущность
        if any(e["tier"] == "S" for e in entities.values()):
            signals += 1
        
        # Сигнал 3: задача помечена как production/critical
        tags = task.get("tags", [])
        if any(t in ["production", "critical", "urgent"] for t in tags):
            signals += 1
        
        # Сигнал 4: есть связанные задачи
        if task.get("related_issues", 0) >= 2:
            signals += 1
        
        # Сигнал 5: высокая активность (реакции, комментарии)
        if task.get("reactions", 0) >= 5 or task.get("comments", 0) >= 3:
            signals += 1
        
        return signals
    
    def _generate_breakdown(self, triggers: Dict, entities: Dict, combos: Dict, signals: int) -> str:
        """Сгенерировать человеческое объяснение скора"""
        parts = []
        
        for trigger_name, weight in triggers.items():
            parts.append(f"{trigger_name} ({weight})")
        
        for entity_name, entity_info in entities.items():
            parts.append(f"{entity_name} ({entity_info['boost']})")
        
        for combo_name, bonus in combos.items():
            parts.append(f"{combo_name} ({bonus})")
        
        if signals >= self.min_signals_for_trend:
            parts.append(f"{signals} independent signals (trend)")
        
        return " + ".join(parts) if parts else "No triggers or entities detected"
    
    def _normalize_text(self, task: Dict) -> str:
        """Нормализовать текст задачи для поиска"""
        parts = [
            task.get("title", ""),
            task.get("description", ""),
            " ".join(task.get("tags", [])),
            task.get("component", ""),
        ]
        text = " ".join(parts).lower()
        return text
    
    def _match_key(self, key: str, text: str) -> bool:
        """Проверить совпадение ключа в тексте"""
        key_lower = key.lower()
        
        # Для коротких ключей проверяем границу слова
        if len(key) <= 3:
            pattern = r'\b' + re.escape(key_lower) + r'\b'
            return bool(re.search(pattern, text))
        
        # Для длинных ключей просто подстрока
        return key_lower in text
    
    def rank_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """Отранжировать список задач по скору"""
        scored_tasks = []
        
        for task in tasks:
            score_result = self.score_task(task)
            task_with_score = task.copy()
            task_with_score["priority_score"] = score_result.total
            task_with_score["score_breakdown"] = score_result.breakdown
            scored_tasks.append(task_with_score)
        
        # Сортируем по скору (выше = важнее)
        return sorted(scored_tasks, key=lambda x: x["priority_score"], reverse=True)
    
    def detect_trend(self, tasks: List[Dict]) -> Dict[str, List[Dict]]:
        """Детектировать тренды (сгруппировать задачи по триггерам/компонентам)"""
        trends = {}
        
        for task in tasks:
            score_result = self.score_task(task)
            
            # Группируем по главному триггеру
            if score_result.triggers:
                main_trigger = max(score_result.triggers.items(), key=lambda x: x[1])[0]
                if main_trigger not in trends:
                    trends[main_trigger] = []
                trends[main_trigger].append(task)
        
        return trends
    
    def record_decision(self, task_id: str, action: str, time_to_resolution: Optional[int] = None, difficulty: Optional[str] = None) -> None:
        """Записать решение для обучения системы"""
        decision = {
            "task_id": task_id,
            "action": action,  # resolved, postponed, rejected
            "time_to_resolution": time_to_resolution,
            "difficulty": difficulty,
            "timestamp": datetime.now().isoformat(),
        }
        self.decision_history.append(decision)
        
        # TODO: Пересчитать веса на основе истории
    
    def get_source_health(self) -> Dict:
        """Получить статистику по каждому триггеру/компоненту"""
        return {
            "triggers": {name: {"weight": cfg.weight} for name, cfg in self.triggers.items()},
            "entities": {name: {"tier": cfg.tier.name} for name, cfg in self.entities.items()},
            "decision_count": len(self.decision_history),
        }


# Примеры использования
if __name__ == "__main__":
    # Инициализация
    scorer = TaskScorer(project_id="my-project", niche="backend")
    scorer.load_niche_config("backend")
    
    # Пример 1: Простой баг
    task1 = {
        "id": "T1",
        "title": "Fix typo in error message",
        "component": "frontend",
        "tags": ["bug", "low-priority"],
        "created_at": datetime.now().isoformat(),
    }
    
    score1 = scorer.score_task(task1)
    print(f"Task 1: {score1.total} - {score1.breakdown}")
    
    # Пример 2: Production outage
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
    print(f"Task 2: {score2.total} - {score2.breakdown}")
    
    # Пример 3: Ранжирование
    tasks = [task1, task2]
    ranked = scorer.rank_tasks(tasks)
    print("\nRanked tasks:")
    for task in ranked:
        print(f"  {task['id']}: {task['priority_score']} - {task.get('title', '')}")
