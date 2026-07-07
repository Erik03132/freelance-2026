# Handoff Examples для наших проектов

## Пример 1: HH.ru A/B тестирование

```json
{
  "project": "hh-ai-agent",
  "task": "Run A/B prompt testing on 10 calls",
  "context": """
    Установлены зависимости, созданы prompt templates (v1, v2).
    База данных настроена (analytics_events, conversion_metrics).
    Rate limiter: 20 откликов/час, 30 сек между откликами.
    
    НЕ сделано:
    - .env не настроен (TG_BOT_TOKEN, OLLAMA_URL)
    - Авторизация на HH.ru не пройдена
    - Пилот не запущен
  """,
  "files": [
    "hh-ai-agent/config.py",
    "hh-ai-agent/ai_analyzer.py",
    "hh-ai-agent/prompts/cover_letter_v1.txt",
    "hh-ai-agent/prompts/cover_letter_v2.txt",
    "hh-ai-agent/.env.example"
  ],
  "skills": ["workflow", "systematic-debugging"],
  "next_steps": [
    "1. Скопировать .env.example → .env, заполнить токены",
    "2. Запустить python main.py для авторизации (ввести код из SMS)",
    "3. Закрыть скрипт после сохранения state.json",
    "4. Запустить python main.py снова (headless режим)",
    "5. Написать боту /start в Telegram",
    "6. Дождаться 10 откликов, проверить /stats"
  ],
  "escalation": false,
  "deadline": "2026-07-05T18:00:00"
}
```

**Запуск:**
```bash
claude --bg --name "HH.ru A/B Test" "$(cat handoff_hh.json)"
```

---

## Пример 2: x.ai Voice Pilot

```json
{
  "project": "ai-eggs",
  "task": "Integrate x.ai Voice Agent with Mango",
  "context": """
    Текущая система: Mango + baresip + DTMF/STT.
    Новая система: Mango + x.ai Voice Agent (Grok).
    
    Пилот: 10 звонков, сравнение baresip vs x.ai.
    
    Стоимость: $0.05/мин ($3/час).
    API ключ нужен: x.ai ($25 кредит для пилота).
  """,
  "files": [
    "ai-eggs/agent/xai_voice_agent.py",
    "ai-eggs/agent/auto_call_pilot.py",
    "ai-eggs/agent/auto_confirm_call.py",
    "ai-eggs/docs/plans/2026-07-04-xai-voice-pilot.md"
  ],
  "skills": ["bot-development", "deployment"],
  "next_steps": [
    "1. Получить API ключ x.ai (console.x.ai)",
    "2. Создать xai_voice_agent.py (WebSocket клиент)",
    "3. Создать auto_call_pilot.py (сравнение baresip vs x.ai)",
    "4. Запустить 10 звонков, собрать результаты",
    "5. Проанализировать: конверсия, стоимость, качество"
  ],
  "escalation": false,
  "deadline": "2026-07-06T18:00:00"
}
```

**Запуск:**
```bash
claude --bg --name "x.ai Voice Pilot" "$(cat handoff_xai.json)"
```

---

## Пример 3: Angela Optimization (Эскалация)

```json
{
  "project": "ai-eggs",
  "task": "Debug Angela multi-agent system",
  "context": """
    Angela не отправляет ответы через Telegram.
    Ошибка в generator_agent.py строка 145.
    
    Архитектура: Router → KnowledgeBase → Generator
    Конфиг: USE_MULTI_AGENT=true в .env
    
    Логи: /var/log/angela.log на VPS (72.56.38.19)
  """,
  "files": [
    "ai-eggs/agent/angela_agents.py",
    "ai-eggs/agent/generator_agent.py",
    "ai-eggs/agent/angelochka_core.py"
  ],
  "skills": ["systematic-debugging", "verification-before-completion"],
  "next_steps": [
    "1. SSH на VPS: root@72.56.38.19",
    "2. Проверить логи: tail -f /var/log/angela.log",
    "3. Найти ошибку в generator_agent.py:145",
    "4. Исправить и протестировать локально",
    "5. Деплой на VPS, проверить работу"
  ],
  "escalation": true,
  "deadline": "2026-07-04T23:59:59"
}
```

**Запуск (приоритетный):**
```bash
claude --bg --name "Angela CRITICAL Fix" "$(cat handoff_angela.json)"
```

---

## Пример 4: ContentCombine (Ночная работа)

```json
{
  "project": "agent-lab",
  "task": "Collect and analyze 50 Habr articles",
  "context": """
    normalizer.py настроен для Habr HTML.
    html_to_markdown.py конвертирует статьи в Markdown.
    
    Нужно:
    - Собрать 50 статей
    - Проанализировать тренды
    - Создать дайджест для Telegram
  """,
  "files": [
    "agent-lab/normalizer.py",
    "agent-lab/html_to_markdown.py",
    "agent-lab/telegram_exporter.py"
  ],
  "skills": ["content-marketing", "brand-voice"],
  "next_steps": [
    "1. Запустить normalizer.normalize_habr_html()",
    "2. Конвертировать в Markdown (html_to_markdown.py)",
    "3. Проанализировать тренды (частота тегов, темы)",
    "4. Создать дайджест (telegram_exporter.py)",
    "5. Отправить в Telegram"
  ],
  "escalation": false,
  "deadline": "2026-07-05T08:00:00"
}
```

**Запуск (вечером):**
```bash
claude --bg --name "ContentCombine Night Job" "$(cat handoff_content.json)"
```

---

## Шаблон для использования

```python
import json
from datetime import datetime, timedelta

def create_handoff(
    project: str,
    task: str,
    context: str,
    files: list,
    skills: list,
    next_steps: list,
    escalation: bool = False,
    hours_until_deadline: int = 24
) -> str:
    """Создать handoff summary"""
    
    deadline = (datetime.now() + timedelta(hours=hours_until_deadline)).isoformat()
    
    handoff = {
        "project": project,
        "task": task,
        "context": context,
        "files": files,
        "skills": skills,
        "next_steps": next_steps,
        "escalation": escalation,
        "deadline": deadline
    }
    
    return json.dumps(handoff, indent=2, ensure_ascii=False)

# Пример использования
handoff = create_handoff(
    project="hh-ai-agent",
    task="Run A/B testing",
    context="Настроены prompt templates, нужен .env",
    files=["config.py", "ai_analyzer.py"],
    skills=["workflow"],
    next_steps=["Настроить .env", "Запустить пилот"]
)

print(handoff)
# claude --bg --name "HH.ru A/B" "$(echo '$handoff')"
```
