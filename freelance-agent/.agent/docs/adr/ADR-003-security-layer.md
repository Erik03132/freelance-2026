# ADR-003: Security layer для агентов (guardrail + security-lint)

**Дата:** 2026-07-09
**Статус:** Accepted
**Контекст:** По чеклисту безопасности vibe-coders (источник: t.me/vibecoding_tg/3376) выбраны 2 фичи:
(1) утечки credentials/`.env` во фронтенд + секреты в логах + OWASP-аудит (пункты 7,8,5);
(2) guardrail для агентов-генераторов, чтобы сами не产出 код с утечками.
Нужен общий переиспользуемый слой статического security-сканирования + расширение Кулибина.

## Решение

Общий пакет `freelance-agent/.agent/agents/security/` (как `learning/` — shared infra, optional import):
- `scan.py` — `scan_leaks(code) -> list[str]`, `SECURITY_SMELLS` (regex-паттерны), `security_audit(code) -> dict`. Чисто статический, БЕЗ LLM (переиспользуется генераторами без ключа).

**Фича 1 — Кулибин security-lint:**
- `kulibin/security_audit.py`: `security_audit(path)` (static через `security.scan`) +
  `owasp_audit(path, api_key)` (LLM OWASP-проверка через собственный `llm_client`).
- CLI: `--sec-audit <path>` (static), `--owasp <path>` (LLM). Интеграция learning (capture + learned context).

**Фича 2 — Guardrail генераторов:**
- `artemiy/component_gen.py` + `page_gen.py`: после генерации вызывают `security.scan.scan_leaks(result)`;
  при находке — предупреждение `⚠ Possible leak` + `capture_start(..., issue="leak")`.
- `rembrandt/component_generator.py`: то же для HTML-компонентов.

## Альтернативы
- Кросс-импорт `kulibin.security_audit` из генераторов — отвергнут: создаёт жёсткую связь генератор→Кулибин;
  вместо этого вынесен нейтральный `security/` пакет (как `learning/`).
- LLM-проверка в guardrail генераторов — отвергнута: guardrail должен работать мгновенно и без ключа.

## Последствия
- Новый пакет `security/` (~2 файла).
- Кулибин: новый модуль + 2 CLI-флага.
- Артемий/Рембрандт: post-generation guardrail (warning + signal).
