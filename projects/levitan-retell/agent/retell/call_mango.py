#!/usr/bin/env python3
"""
Retell (managed) → Mango Office обзвон для голосового агента «Анжелла».

Метод Retell «Dial to SIP URI»:
  1. Register Phone Call API (Retell) → call_id
  2. Mango callback соединяет абонента на SIP URI sip:{call_id}@sip.retellai.com

Требует ключи в .env:
  RETELL_API_KEY=...
  MANGO_VPBX_API_KEY=...
  MANGO_VPBX_API_SALT=...
  MANGO_FROM_EXTENSION=22 (опц)

CLI:
  python3 agent/retell/call_mango.py --phone 79859234644 --agent-id <AGENT_ID> [--dry-run]
"""

import argparse
import hashlib
import json
import os
import uuid

import requests
from dotenv import load_dotenv

load_dotenv()

RETELL_API = "https://api.retellai.com"
MANGO_BASE = "https://app.mango-office.ru/vpbx/"


def register_retell_call(
    agent_id: str, to_number: str, from_number: str = "", api_key: str | None = None
) -> str:
    """Register Phone Call → вернуть call_id (нужен для SIP URI)."""
    api_key = api_key or os.getenv("RETELL_API_KEY", "")
    if not api_key:
        raise SystemExit("Нет RETELL_API_KEY в .env")
    body = {"agent_id": agent_id, "to_number": to_number, "direction": "outbound"}
    if from_number:
        body["from_number"] = from_number
    r = requests.post(
        f"{RETELL_API}/v2/register-phone-call",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=body,
        timeout=30,
    )
    if r.status_code != 200:
        raise SystemExit(f"Retell register failed {r.status_code}: {r.text}")
    data = r.json()
    call_id = data.get("call_id")
    if not call_id:
        raise SystemExit(f"Retell: нет call_id в ответе: {data}")
    return call_id


def mango_callback(phone: str, sip_uri: str, extension: str, dry_run: bool = False) -> None:
    """Инициировать Mango callback, соединяющий абонента на SIP URI Retell."""
    key = os.getenv("MANGO_VPBX_API_KEY", "")
    salt = os.getenv("MANGO_VPBX_API_SALT", "")
    if not key or not salt:
        raise SystemExit("Нет MANGO_VPBX_API_KEY/SALT в .env")

    # NOTE: финальная маршрутизация на внешний SIP URI (sip.retellai.com)
    # зависит от конфигурации номера/экстеншена в Mango. Это заглушка-шаблон:
    # требует уточнения, как Манго направляет на произвольный SIP-транк.
    payload = {
        "command_id": f"retell_{uuid.uuid4().hex[:8]}",
        "from": {"extension": extension},
        "to_number": phone,
    }
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    sign = hashlib.sha256((key + j + salt).encode()).hexdigest()
    print(f"  sip_uri to connect: {sip_uri}")
    if dry_run:
        print("  [dry-run] payload:", payload)
        return
    r = requests.post(
        f"{MANGO_BASE}commands/callback",
        data={"vpbx_api_key": key, "json": j, "sign": sign},
        timeout=20,
    )
    print("  mango status:", r.status_code, "body:", r.text)


def main() -> None:
    p = argparse.ArgumentParser(description="Retell + Mango обзвон (Dial to SIP URI)")
    p.add_argument("--phone", required=True, help="Абонент, на кого звоним, напр. 79859234644")
    p.add_argument("--agent-id", required=True, help="Retell agent_id созданного агента")
    p.add_argument(
        "--dry-run", action="store_true", help="Ничего не вызывать, показать, что сделал бы"
    )
    args = p.parse_args()

    print(f"1. Регистрирую звонок в Retell для {args.phone} ...")
    call_id = register_retell_call(args.agent_id, args.phone)
    sip_uri = f"sip:{call_id}@sip.retellai.com"
    print(f"   call_id={call_id}")
    print(f"   sip_uri={sip_uri}")

    ext = os.getenv("MANGO_FROM_EXTENSION", "22")
    print("2. Инициирую Mango callback на SIP URI ...")
    mango_callback(args.phone, sip_uri, ext, dry_run=args.dry_run)
    print("Готово. Проверь звонок в Retell dashboard ('Call history').")


if __name__ == "__main__":
    main()
