#!/usr/bin/env bash
# vps_do.sh — короткая обёртка: ставит задачу агенту-профилю на VPS с Mac.
# SSoT: handoff_2026-08-28_remote_control_live.md
#
# Суть: вместо длинного
#   hermes peer dm vps "hermes profile use batrak — и найди вакансии"
# пишешь просто:
#   vps_do batrak "найди вакансии на hh.ru за 3 дня"
#
# Флаги (позиционные аргументы тоже работают):
#   --list           показать профили на VPS
#   --current        какой профиль сейчас активен на VPS
#   --profile X      явно задать профиль (альтернатива позиционному)
#   --dry-run        не отправлять, только показать что отправили бы
#   --help           это сообщение
#
# Позиционно:
#   vps_do                         → меню-подсказка
#   vps_do "просто задача"         → на default-профиль
#   vps_do sherlock "найди вакансии" → на профиль sherlock
#
# Профили (актуально 28.08, проверено через peer dm):
PROFILES="default batrak bridge chief defender english-tutor femida financier health marketer personal sherlock"
#
# Выход: 0 = задача ушла (или dry-run), 1 = ошибка/неизвестный профиль.

set -u

DRY_RUN=0
SHOW_LIST=0
SHOW_CURRENT=0
EXPLICIT_PROFILE=""
POSITIONAL=()

for arg in "$@"; do
  case "$arg" in
    --list)     SHOW_LIST=1 ;;
    --current)  SHOW_CURRENT=1 ;;
    --dry-run)  DRY_RUN=1 ;;
    --help|-h)  sed -n '2,30p' "$0"; exit 0 ;;
    --profile)  : ;;  # значение берём следующим итератором ниже
    --profile=*) EXPLICIT_PROFILE="${arg#--profile=}" ;;
    *) POSITIONAL+=("$arg") ;;
  esac
done
# отдельно выкусим значение после --profile (без =)
prev=""
for arg in "$@"; do
  if [ "$prev" = "--profile" ]; then EXPLICIT_PROFILE="$arg"; fi
  prev="$arg"
done

# --list
if [ "$SHOW_LIST" -eq 1 ]; then
  echo "Профили на VPS (через peer dm):"
  for p in $PROFILES; do echo "  • $p"; done
  exit 0
fi

# --current
if [ "$SHOW_CURRENT" -eq 1 ]; then
  echo "Активный профиль на VPS:"
  hermes peer dm vps "hermes profile current — одной строкой, без пояснений." 2>&1 | tail -1
  exit 0
fi

# Определяем профиль и задачу
PROFILE="${EXPLICIT_PROFILE:-default}"
TASK=""
if [ ${#POSITIONAL[@]} -gt 0 ]; then
  first="${POSITIONAL[0]}"
  # если первый аргумент — известный профиль, считаем его переключателем
  if echo " $PROFILES " | grep -q " $first "; then
    PROFILE="$first"
    # задача = всё остальное
    TASK="${POSITIONAL[*]:1}"
  else
    TASK="${POSITIONAL[*]}"
  fi
fi

if [ -z "$TASK" ]; then
  echo "❌ Задача пустая." >&2
  echo "Используй:" >&2
  echo "  vps_do sherlock \"найди вакансии на hh.ru за 3 дня\"" >&2
  echo "  vps_do \"просто задача\"              (на default)" >&2
  echo "  vps_do --list | --current | --help" >&2
  exit 1
fi

# Валидация профиля (если задан явно и неизвестен — предупредим, но отправим)
if [ -n "$EXPLICIT_PROFILE" ] && ! echo " $PROFILES " | grep -q " $PROFILE "; then
  echo "⚠️  Профиль '$PROFILE' нет в списке известных (vps_do --list). Всё равно отправляю." >&2
fi

MSG="Переключись в профиль $PROFILE. Задача: $TASK"

if [ "$DRY_RUN" -eq 1 ]; then
  echo "[dry-run] hermes peer dm vps \"$MSG\""
  echo "[dry-run] задача НЕ отправлена."
  exit 0
fi

echo "▶ VPS / профиль: $PROFILE"
echo "▶ задача: $TASK"
echo "—— ответ VPS-агента ——"
hermes peer dm vps "$MSG" 2>&1 | tail -20
