#!/usr/bin/env bash
# check_bridge.sh — быстрая проверка моста Mac→VPS (SSoT: handoff_2026-08-28_remote_control_live.md)
#
# Флаги (позиционных аргументов нет — всё через опции):
#   --with-echo     отправить VPS-агенту тестовую задачу (побочный эффект: пишет в VPS-чат)
#   --dry-run       ничего не проверяет по сети, только покажет что сделал бы
#   --help          это сообщение + примеры
#
# Примеры:
#   ./check_bridge.sh                  # только чтение состояния (порты/health/peer)
#   ./check_bridge.sh --with-echo      # + end-to-end тест через hermes peer dm vps
#   ./check_bridge.sh --dry-run        # показать план без реальных вызовов
#
# Выход: 0 = все проверки зелёные, 1 = хотя бы одна красная (stderr + код != 0).

set -u

WITH_ECHO=0
DRY_RUN=0

for arg in "$@"; do
  case "$arg" in
    --with-echo) WITH_ECHO=1 ;;
    --dry-run)   DRY_RUN=1 ;;
    --help|-h)   sed -n '2,15p' "$0"; exit 0 ;;
    *) echo "Неизвестный аргумент: $arg (см. --help)" >&2; exit 2 ;;
  esac
done

PORT_UI=9119        # hermes serve (веб-пульт VPS)
PORT_API=8742       # api_server bridge (peer DM)
PEER_NAME=vps
PEER_HEALTH_URL="http://127.0.0.1:${PORT_API}/health"
PEER_UI_URL="http://127.0.0.1:${PORT_UI}/"

ok()   { echo "  ✅ $1"; }
bad()  { echo "  ❌ $1" >&2; FAIL=1; }
info() { echo "  • $1"; }

FAIL=0

if [ "$DRY_RUN" -eq 1 ]; then
  echo "[dry-run] План проверки моста Mac→VPS:"
  info "lsof -iTCP:${PORT_UI} -sTCP:LISTEN"
  info "lsof -iTCP:${PORT_API} -sTCP:LISTEN"
  info "curl -s -o /dev/null -w '%{http_code}' ${PEER_UI_URL}"
  info "curl -s -o /dev/null -w '%{http_code}' ${PEER_HEALTH_URL}"
  info "hermes peer list (искать ${PEER_NAME} [key set])"
  [ "$WITH_ECHO" -eq 1 ] && info "hermes peer dm ${PEER_NAME} \"Тест Mac→VPS: ответь одной фразой 'мост работает'\""
  echo "[dry-run] Реальные вызовы не выполнены."
  exit 0
fi

echo "=== Мост Mac → VPS ($(date '+%H:%M:%S')) ==="

echo "[1/4] Туннель слушает локальные порты"
if lsof -iTCP:"${PORT_UI}" -sTCP:LISTEN >/dev/null 2>&1; then
  ok "порт ${PORT_UI} (hermes serve) — LISTEN"
else
  bad "порт ${PORT_UI} не слушается (туннель упал? launchctl load ~/Library/LaunchAgents/com.user.vps-tunnel.plist)"
fi
if lsof -iTCP:"${PORT_API}" -sTCP:LISTEN >/dev/null 2>&1; then
  ok "порт ${PORT_API} (api_server bridge) — LISTEN"
else
  bad "порт ${PORT_API} не слушается (туннель упал? VPS api_server не поднят?)"
fi

echo "[2/4] HTTP-доступность мостов"
CODE_UI=$(curl -s -o /tmp/bridge_9119.txt -w '%{http_code}' --max-time 5 "${PEER_UI_URL}" 2>/dev/null || echo "000")
BODY_UI=$(cat /tmp/bridge_9119.txt 2>/dev/null)
if [ "$CODE_UI" = "000" ]; then
  bad "9119 → нет ответа (hermes serve на VPS упал?)"
elif echo "$BODY_UI" | grep -q "web UI disabled"; then
  ok "9119 → сервер живой, НО web UI отключён (headless, --skip-build). Пульт в браузере НЕ работает — use hermes dashboard (Mac) или peer dm."
else
  ok "9119 → HTTP ${CODE_UI} (сервер живой)"
fi
CODE_API=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "${PEER_HEALTH_URL}" 2>/dev/null || echo "000")
if [ "$CODE_API" = "200" ]; then
  ok "8742/health → HTTP 200 (api_server живой)"
else
  bad "8742/health → HTTP ${CODE_API} (ожидали 200)"
fi

echo "[3/4] Peer зарегистрирован"
if hermes peer list 2>/dev/null | grep -q "${PEER_NAME}.*\[key set\]"; then
  ok "peer '${PEER_NAME}' найден с ключом"
elif hermes peer list 2>/dev/null | grep -q "${PEER_NAME}"; then
  bad "peer '${PEER_NAME}' есть, но БЕЗ ключа (HERMES_PEER_VPS_KEY?)"
else
  bad "peer '${PEER_NAME}' не зарегистрирован (hermes peer add vps --url ... --key ...)"
fi

echo "[4/4] End-to-end (по желанию)"
if [ "$WITH_ECHO" -eq 1 ]; then
  RESP=$(hermes peer dm "${PEER_NAME}" "Тест Mac→VPS: ответь одной фразой 'мост работает'" 2>&1 | tail -1)
  if [ "$RESP" = "мост работает" ]; then
    ok "peer dm → VPS ответил: «${RESP}»"
  else
    bad "peer dm → ответ VPS: «${RESP}» (ожидали «мост работает»)"
  fi
else
  info "пропущен (без --with-echo). Добавь --with-echo для сквозного теста."
fi

echo "=== Итог ==="
if [ "$FAIL" -eq 0 ]; then
  echo "ВСЁ ЗЕЛЁНОЕ — мост Mac→VPS работает."
  exit 0
else
  echo "ЕСТЬ КРАСНОЕ — см. ❌ выше. SSoT: handoff_2026-08-28_remote_control_live.md" >&2
  exit 1
fi
