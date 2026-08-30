# HANDOFF — 2026-08-29 (VPS Telegram-боты через multiplex_profiles) [FINAL]

> SSoT для продолжения. Старый `handoff_2026-08-28_remote_control_setup.md` — ГАЛЛЮЦИНАЦИЯ
> (не существующие команды). Реальный мост: `hermes peer` + api_server.
> См. `handoff_2026-08-28_remote_control_live.md` (мост) и `split_tunnel_install.md` (VPN).

## ЧТО СДЕЛАНО (verified 29.08, end-to-end)
- На VPS `gateway.multiplex_profiles: true` (ОДИН gateway-процесс на все боты).
- `multiplex_profile_allowlist` содержит: `personal` (ПЕРВЫЙ=главный), `batrak, bridge, defender, english-tutor, femida, financier, health, marketer` + `sherlock`.
- 6 ТГ-ботов подняты и отвечают (getMe подтверждён):
  - personal   → @hermes03132_bot   (главный, default-профиль VPS) ✅
  - sherlock   → @sher03132_bot     ✅
  - marketer   → @market03132_bot   ✅
  - financier  → @finans03132_bot   ✅
  - femida     → @femida03132_bot   ✅
  - batrak     → @batrak03132_bot    ✅ (ПЕРЕСОЗДАН: был конфликт port-binding api_server)
- Токены в `profiles/<p>/.env` как `TELEGRAM_BOT_TOKEN` (записаны через SSH-форвард 2222, НЕ через чат).
- `gateway.telegram.enabled: true` + `proxy_url` в каждом профиле.
- gateway `active`, `NRestarts=0` после финального рестарта.
- Мост Mac→VPS жив (split-tunnel проверен на VPN).

## ПРОФИЛЬ ПРИ ЗАГРУЗКЕ (уточнение Игоря)
- Игорь хочет, чтобы ГЛАВНЫМ ботом был @hermes03132_bot (профиль personal/default на VPS).
  Это УЖЕ так: personal = первый в allowlist = главный на VPS.
- Локальный Mac-агент (это окно чата) = профиль `femida` — это пУЛЬТ, не бот.
  Менять его на default НЕ надо (связь Mac↔VPS через femida/personal не зависит).
- Если Игорь хочет, чтобы при загрузке Mac-десктопа открывался default (а не femida) —
  это `hermes profile use default` на Маке + возможно прописать в `~/.hermes/active_profile`.
  РЕШЕНО: оставить femida как пульт (менять не требовалось).

## КАК ОБЩАТЬСЯ
- С Игорем (Мак): это окно = агент femida (пульт).
- С ВПS-агентами: пиши боту в Telegram напрямую (@sher03132_bot и т.д.) → попадаешь
  в нужный VPS-профиль. Из Mac-окна управляй через `vps_do.sh <profile> "задача"`.

## ИЗВЕСТНЫЕ НЮАНСЫ
- `batrak` НЕ должен включать port-binding платформы (api_server) — default владеет
  HTTP-слушателем (8642, туннель 8742). При пересоздании профиля config.yaml пустой —
  копировать из соседа (sherlock) + править telegram/allowlist.
- `personal` токен в `/root/.hermes/config.yaml` замаскирован Hermes (`***`) — это норма,
  бот жив (default-профиль gateway).

## КАК ПРОДОЛЖИТЬ В НОВОЙ СЕССИИ
1. «продолжи по handoff_2026-08-29_vps_bots_setup.md» или «проверь ботов на VPS».
2. Проверка моста: `~/freelance-2026/check_bridge.sh --with-echo` или `/start-day`.
3. Перед рестартом gateway на VPS — бэкап unit:
   `cp /etc/systemd/system/hermes-gateway.service /etc/systemd/system/hermes-gateway.service.bak_<unix>`.
4. SSH на VPS: туннель Mac LaunchAgent → `ssh -p 22 root@217.149.23.113` (через 127.0.0.1:22
   только если поднят форвард; иначе `ssh -p 22 root@217.149.23.113 -i ~/freelance-2026/.ssh_agent_key`).

## ФАЙЛЫ (токены НЕ коммитить!)
- `check_bridge.sh` — проверка моста
- `vps_do.sh` — обёртка профиль+задача
- `split_tunnel_vps.sh` + `split_tunnel_install.md` — VPN+мост
- `handoff_2026-08-28_remote_control_live.md` — SSoT моста
- НЕ пушить: `~/.hermes/.env`, `state.db`, `sessions/`, `vault/` (личное)
