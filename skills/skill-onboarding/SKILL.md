---
name: skill-onboarding
description: "Онбординг нового скилла: чеклист от создания до синхронизации на VPS. Обновляет SOUL.md профиля, skill-router, бандлы, VPS."
argument-hint: "[name] [профиль(и)]"
disable-model-invocation: true
---

# Skill Onboarding — чеклист онбординга скилла

При создании нового скилла для профиля(ей) — выполни ВСЕ шаги. Иначе скилл лежит мёртвым грузом, профиль о нём не знает.

## Чеклист (обязательный)

- [ ] **1. Создать SKILL.md** в `skills/<name>/SKILL.md` (по канону Hermes: frontmatter + тело)
- [ ] **2. Скопировать в `~/.hermes/skills/<name>/SKILL.md`** — чтобы `skill_view` видел
- [ ] **3. Создать бандл** в `~/.hermes/profiles/chief/skill-bundles/<name>.yaml`:
      ```yaml
      name: <name>
      skills:
      - <name>
      ```
- [ ] **4. Обновить SOUL.md профиля** — добавь раздел "Доступные скиллы":
      ```markdown
      ## Доступные скиллы
      - `<name>` — [краткое описание]. Загружай через `skill_view(name="<name>")` для [когда].
      ```
      Для Chief: добавь строку в таблицу "Скиллы профилей".
- [ ] **5. Обновить `skill-router.md`** — добавь строку в карту скиллов:
      ```markdown
      || **Категория** | `<name>` | [описание в одно предложение] |
      ```
- [ ] **6. Синхронизировать на VPS:**
      ```bash
      # Mac → GitHub
      cd ~/freelance-2026 && bash tools/ops/sync_hermes_knowledge.sh push
      # GitHub → VPS (через туннель)
      ssh root@127.0.0.1 -p 2222 "cd /root/hermes-sync && bash sync_hermes_knowledge.sh pull"
      ```
      Если VPS недоступен по SSH — используй туннель `localhost:2222` (com.igorvasin.vps-tunnel.plist).

## VPS-специфика

- **Туннель:** `ssh root@127.0.0.1 -p 2222` (если `lsof -i :2222` показывает LISTEN)
- **Нет туннеля:** ожидай разбана IP через FWaaS TimeWeb (НЕ проси отключать VPN)
- **GitHub auth на VPS:** при `fatal: could not read Username` → `ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ''` → добавь публичный ключ в https://github.com/settings/keys

## Пример (из практики)

Создали `shrelock-research` для Sherlock:
1. ✅ `skills/shrelock-research/SKILL.md`
2. ✅ скопирован в `~/.hermes/skills/shrelock-research/SKILL.md`
3. ✅ бандл `~/.hermes/profiles/chief/skill-bundles/shrelock-research.yaml`
4. ✅ SOUL.md Sherlock: добавлен "Доступные скиллы" с shrelock-research
5. ✅ `skill-router.md`: строка "Исследование | shrelock-research"
6. ✅ `sync_hermes_knowledge.sh push` → `fc52527` → pull на VPS

## Привязка к задачам

- **ES-AUTO-COMPANY**: пилот 3 скилла — все прошли онбординг
- **T-03** (регистратор): Chief маршрутизирует на скиллы из своей таблицы
- **Ночной конвейер Kwork**: Sherlock→Thompson, Marketer→Ross
