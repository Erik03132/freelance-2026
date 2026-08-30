#!/usr/bin/env bash
# Install Hermes profile aliases into Igor's active VPS gateway.
# Usage: bash install-hermes-profile-menu.sh [--dry-run]
set -euo pipefail

DRY=0
[[ "${1:-}" == "--dry-run" ]] && DRY=1
H=/root/.hermes
BIN=/srv/hermes/venv/bin/hermes
UNIT=hermes-gateway.service
PROFILES=(personal batrak bridge defender english-tutor femida financier health marketer sherlock)
PRIORITY='["profiles","chief","sherlock","femida","defender","marketer","financier","aibolit","english","batrak","bridge","default"]'
ALLOW='["personal","batrak","bridge","defender","english-tutor","femida","financier","health","marketer","sherlock"]'

if [[ $DRY -eq 1 ]]; then
  echo "DRY-RUN: active home=$H"
  echo "DRY-RUN: plugin=$H/plugins/hermes-profile-menu"
  echo "DRY-RUN: profiles=${PROFILES[*]}"
  echo "DRY-RUN: one systemd restart + 75s stability check"
  exit 0
fi

[[ -x "$BIN" ]] || { echo "ERROR: $BIN missing"; exit 20; }
[[ -f "$H/config.yaml" ]] || { echo "ERROR: active config $H/config.yaml missing"; exit 21; }

STAMP=$(date +%Y%m%d-%H%M%S)
BACKUP="$H/backups/profile-menu-$STAMP"
install -d -m 0700 "$BACKUP"
cp -a "$H/config.yaml" "$BACKUP/config.yaml"
[[ -d "$H/plugins/hermes-profile-menu" ]] && cp -a "$H/plugins/hermes-profile-menu" "$BACKUP/" || true

echo "=== 1/7 Profiles: migrate essentials + sanitize ==="
/srv/hermes/venv/bin/python - <<'PY'
from pathlib import Path
import shutil, yaml

names = ['personal','batrak','bridge','defender','english-tutor','femida','financier','health','marketer','sherlock']
src_root = Path('/srv/hermes/.hermes/profiles')
dst_root = Path('/root/.hermes/profiles')
dst_root.mkdir(parents=True, exist_ok=True)
missing = []

for name in names:
    src = src_root / name
    dst = dst_root / name
    if not src.is_dir():
        missing.append(f'{name} (source dir)')
        continue
    dst.mkdir(parents=True, exist_ok=True)

    # Copy only durable profile content. Never migrate runtime caches, LSP bins,
    # logs, auth pools, .env tokens, PID/lock files or Telegram credentials.
    for filename in ('config.yaml', 'SOUL.md'):
        source_file = src / filename
        target_file = dst / filename
        if source_file.is_file() and not target_file.exists():
            shutil.copy2(source_file, target_file)
            print('COPIED', name, filename)

    for dirname in ('memories', 'skills'):
        source_dir = src / dirname
        target_dir = dst / dirname
        if source_dir.is_dir() and not target_dir.exists():
            shutil.copytree(
                source_dir,
                target_dir,
                symlinks=True,
                ignore_dangling_symlinks=True,
            )
            print('COPIED', name, dirname)

    cfg_path = dst / 'config.yaml'
    soul_path = dst / 'SOUL.md'
    if not cfg_path.is_file():
        missing.append(f'{name} (config.yaml)')
        continue
    if not soul_path.is_file():
        missing.append(f'{name} (SOUL.md)')
        continue

    cfg = yaml.safe_load(cfg_path.read_text(encoding='utf-8')) or {}
    if not isinstance(cfg, dict):
        cfg = {}

    # Secondary profiles provide persona/config only. The primary gateway owns
    # Telegram. Strip every duplicate-token route before multiplex startup.
    gateway = cfg.setdefault('gateway', {})
    if not isinstance(gateway, dict):
        gateway = {}
        cfg['gateway'] = gateway
    tg = gateway.get('telegram')
    if isinstance(tg, dict):
        tg['enabled'] = False
        tg.pop('token', None)

    platforms = cfg.setdefault('platforms', {})
    if not isinstance(platforms, dict):
        platforms = {}
        cfg['platforms'] = platforms
    ptg = platforms.setdefault('telegram', {})
    if not isinstance(ptg, dict):
        ptg = {}
        platforms['telegram'] = ptg
    ptg['enabled'] = False
    ptg.pop('token', None)

    # Verified keyless provider: every menu profile can answer on this VPS.
    cfg['model'] = {
        'provider': 'opencode-free',
        'default': 'laguna-s-2.1-free',
    }
    tmp = cfg_path.with_suffix('.yaml.tmp')
    tmp.write_text(
        yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True),
        encoding='utf-8',
    )
    tmp.replace(cfg_path)
    print('READY', name)

if missing:
    raise SystemExit('ERROR missing profile essentials: ' + ', '.join(sorted(set(missing))))
PY

echo "=== 2/7 Install tested user plugin ==="
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
printf '%s' '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' | base64 -d > "$TMP/plugin.tgz"
echo "4732d73f1cd3002336ffb35dcbf08b9fa56815403cd8597c0dbe64f480001617  $TMP/plugin.tgz" | sha256sum -c -
tar -xzf "$TMP/plugin.tgz" -C "$TMP"
rm -rf "$H/plugins/hermes-profile-menu"
install -d -m 0755 "$H/plugins/hermes-profile-menu"
cp "$TMP/hermes-profile-menu/plugin.yaml" "$TMP/hermes-profile-menu/__init__.py" "$H/plugins/hermes-profile-menu/"

export HOME=/root HERMES_HOME="$H"
"$BIN" plugins enable hermes-profile-menu --no-allow-tool-override

 echo "=== 3/7 Active gateway config ==="
"$BIN" config set gateway.multiplex_profiles true
"$BIN" config set gateway.multiplex_profile_allowlist "$ALLOW"
"$BIN" config set platforms.telegram.extra.command_menu.priority "$PRIORITY"
"$BIN" config set platforms.telegram.extra.command_menu.priority_mode prepend
"$BIN" config set platforms.telegram.extra.command_menu.max_commands 60

 echo "=== 4/7 Integration check before restart ==="
/srv/hermes/venv/bin/python - <<'PY'
from hermes_cli.plugins import discover_plugins, get_plugin_commands
discover_plugins()
from hermes_cli.commands import telegram_menu_commands
expected={'profiles','chief','sherlock','femida','defender','marketer','financier','aibolit','english','batrak','bridge','default'}
plugins=set(get_plugin_commands())
rows,_=telegram_menu_commands(max_commands=60)
menu=[r[0] for r in rows]
assert expected <= plugins, sorted(expected-plugins)
assert expected <= set(menu), sorted(expected-set(menu))
assert menu[:12] == ['profiles','chief','sherlock','femida','defender','marketer','financier','aibolit','english','batrak','bridge','default'], menu[:12]
print('PLUGIN_OK commands=12')
print('MENU_PREFIX_OK',','.join(menu[:12]))
PY

 echo "=== 5/7 Single controlled restart ==="
systemctl daemon-reload
systemctl restart "$UNIT"
sleep 18
PID1=$(systemctl show "$UNIT" -p MainPID --value)
R1=$(systemctl show "$UNIT" -p NRestarts --value)
echo "START pid=$PID1 restarts=$R1"
[[ "$PID1" != 0 ]] || { journalctl -u "$UNIT" -n 80 --no-pager; exit 30; }

 echo "=== 6/7 Stability 75s ==="
sleep 75
ACTIVE=$(systemctl is-active "$UNIT" || true)
PID2=$(systemctl show "$UNIT" -p MainPID --value)
R2=$(systemctl show "$UNIT" -p NRestarts --value)
echo "FINISH active=$ACTIVE pid=$PID2 restarts=$R2"
[[ "$ACTIVE" == active && "$PID1" == "$PID2" && "$R1" == "$R2" ]] || { journalctl -u "$UNIT" --since '-3 minutes' --no-pager | tail -100; exit 31; }

 echo "=== 7/7 Decisive logs ==="
J=$(journalctl -u "$UNIT" --since '-3 minutes' --no-pager)
printf '%s
' "$J" | grep -E 'Connected to Telegram|set_my_commands OK|duplicate_credential|Profile route|No inference provider|Failed to connect|Conflict' | tail -40 || true
printf '%s
' "$J" | grep -q 'Connected to Telegram' || { echo 'ERROR no Telegram connection'; exit 32; }
printf '%s
' "$J" | grep -q 'set_my_commands OK' || { echo 'ERROR menu registration not confirmed'; exit 33; }

echo 'MENU_INSTALL_OK'
echo 'Open Telegram menu and run /profiles, then /sherlock.'
