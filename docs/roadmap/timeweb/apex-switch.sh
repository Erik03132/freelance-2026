#!/usr/bin/env bash
#
# Переключение apex-домена ai-bureau.online между GitHub Pages и Timeweb App 296823.
#
# Зачем: пока apex привязан к приложению, Timeweb сам держит A-запись на IP
# приложения (178.209.127.53). Если TLS-сертификат для apex не выпущен, сайт
# отдаёт ошибку сертификата. Скрипт привязывает apex, ждёт сертификат и сам
# откатывает привязку на GitHub Pages, если сертификат не появился.
#
# Примеры:
#   bash docs/roadmap/timeweb/apex-switch.sh --dry-run
#   bash docs/roadmap/timeweb/apex-switch.sh --to-app --wait-seconds 600
#   bash docs/roadmap/timeweb/apex-switch.sh --to-github
#
# Коды выхода: 0 — сертификат есть, сайт отдаёт 200; 1 — откат на GitHub Pages;
#              2 — ошибка API/токена; 4 — неверные аргументы.

set -uo pipefail

APP_IP="178.209.127.53"
GITHUB_IP="185.199.108.153"
DOMAIN="ai-bureau.online"
WWW="www.ai-bureau.online"
APP_ID="296823"
ENV_FILE="/Users/igorvasin/freelance-2026/projects/ai-marketing/.env"
API="https://timeweb.cloud/api/v1"
TARGET="app"
WAIT=600
DRY_RUN=0

usage() { sed -n '2,19p' "$0" | sed 's/^# \{0,1\}//'; }
die() { echo "ERROR: $*" >&2; exit "${2:-2}"; }

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --to-app) TARGET="app"; shift ;;
    --to-github) TARGET="github"; shift ;;
    --wait-seconds) WAIT="${2:?--wait-seconds требует число}"; shift 2 ;;
    --env-file) ENV_FILE="${2:?--env-file требует путь}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) die "неизвестный аргумент: $1" 4 ;;
  esac
done

[ -f "$ENV_FILE" ] || die "нет файла $ENV_FILE" 2
TOKEN=$(grep -m1 '^TIMEWEB_TOKEN=' "$ENV_FILE" | cut -d= -f2-)
[ -n "$TOKEN" ] || die "TIMEWEB_TOKEN не найден в $ENV_FILE" 2

api() { curl -s -H "Authorization: Bearer $TOKEN" "$API/$1"; }

# Привязка доменов к приложению: с apex — apex идёт на Timeweb, без — только www.
bind_domains() {
  local payload="$1"
  if [ "$DRY_RUN" = "1" ]; then echo "[dry-run] app domains -> $payload"; return 0; fi
  curl -s -o /dev/null -w "%{http_code}" -X PATCH \
    -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
    -d "{\"domains\":$payload}" "$API/apps/$APP_ID/domains"
}

# A-запись apex на GitHub: при отвязке Timeweb её не всегда удаляет.
point_to_github() {
  local id
  id=$(api "domains/$DOMAIN/dns-records" \
    | python3 -c "import sys,json;rs=json.load(sys.stdin).get('dns_records',[]);print(next((r['id'] for r in rs if r['type']=='A'),''))")
  if [ "$DRY_RUN" = "1" ]; then echo "[dry-run] A $DOMAIN -> $GITHUB_IP (id=${id:-new})"; return 0; fi
  if [ -n "$id" ]; then
    curl -s -o /dev/null -w "%{http_code}" -X PATCH \
      -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
      -d "{\"type\":\"A\",\"value\":\"$GITHUB_IP\",\"ttl\":120}" \
      "$API/domains/$DOMAIN/dns-records/$id"
  else
    curl -s -o /dev/null -w "%{http_code}" -X POST \
      -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
      -d "{\"subdomain\":\"@\",\"type\":\"A\",\"value\":\"$GITHUB_IP\",\"ttl\":120}" \
      "$API/domains/$DOMAIN/dns-records"
  fi
}

cert_ok() {
  echo | openssl s_client -connect "$APP_IP:443" -servername "$DOMAIN" 2>/dev/null \
    | openssl x509 -noout -subject 2>/dev/null | grep -q "CN *= *$DOMAIN"
}

site_ok() {
  [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 --resolve "$DOMAIN:443:$APP_IP" "https://$DOMAIN/")" = "200" ]
}

# После снятия привязки зона отдаёт новый IP не сразу: ждём подтверждения на NS.
wait_dns() {
  local want="$1" i=0 cur=""
  while [ $i -lt 12 ]; do
    cur=$(dig @ns1.timeweb.ru +short "$DOMAIN" 2>/dev/null | sort -u | tr '\n' ' ')
    case "$cur" in *"$want"*) echo "$cur"; return 0 ;; esac
    sleep 15
    i=$((i+1))
  done
  echo "$cur"
  return 1
}

rollback() {
  echo "откат: apex снимается с приложения, A -> GitHub Pages"
  echo "app domains: $(bind_domains "[\"$WWW\"]")"
  sleep 5
  echo "A $DOMAIN -> $GITHUB_IP: $(point_to_github)"
  if [ "$(wait_dns "$GITHUB_IP")" ] && dig @ns1.timeweb.ru +short "$DOMAIN" | grep -q "$GITHUB_IP"; then
    echo "DNS подтверждён: $DOMAIN -> GitHub Pages"
  else
    echo "ВНИМАНИЕ: зона ещё не отдаёт $GITHUB_IP — проверить панель Timeweb вручную" >&2
  fi
}

if [ "$TARGET" = "github" ]; then
  echo "app domains: $(bind_domains "[\"$WWW\"]")"
  [ "$DRY_RUN" = "1" ] && exit 0
  sleep 5
  echo "A $DOMAIN -> $GITHUB_IP: $(point_to_github)"
  exit 0
fi

echo "привязка apex к приложению: $(bind_domains "[\"$WWW\",\"$DOMAIN\"]")"
[ "$DRY_RUN" = "1" ] && exit 0

deadline=$(( $(date +%s) + WAIT ))
while [ "$(date +%s)" -lt "$deadline" ]; do
  if cert_ok && site_ok; then
    echo "OK: сертификат выпущен, https://$DOMAIN/ отдаёт 200 (App $APP_ID)"
    exit 0
  fi
  sleep 20
done

echo "FAIL: сертификат не выпущен за ${WAIT}s"
rollback
exit 1
