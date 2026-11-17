#!/usr/bin/env python3
"""Пробник MCP-канала firecrawl: поднимает сервер по stdio и зовёт tools/call.

Зачем: отличить «сломан ключ/пакет» от «сломан сетевой слой клиента».
Запускает `npx -y firecrawl-mcp` в чистом окружении (прокси-переменные
вычищаются), делает initialize → tools/list → tools/call и печатает результат.

Примеры:
  python3 tools/firecrawl/probe_mcp.py --help
  python3 tools/firecrawl/probe_mcp.py --tool firecrawl_credit_usage
  python3 tools/firecrawl/probe_mcp.py --tool firecrawl_credit_usage --json
  python3 tools/firecrawl/probe_mcp.py --keep-proxy   # воспроизвести 407
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

KEY_FILE = os.path.expanduser("~/.config/opencode/.secrets/firecrawl.key")
PROXY_VARS = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
)


def build_env(keep_proxy: bool) -> tuple[dict[str, str], bool]:
    env = dict(os.environ)
    if not keep_proxy:
        for name in PROXY_VARS:
            env.pop(name, None)
        env["NO_PROXY"] = "*"
        env["no_proxy"] = "*"
    key = ""
    if os.path.exists(KEY_FILE):
        key = open(KEY_FILE, encoding="utf-8").read().strip()
    if key:
        env["FIRECRAWL_API_KEY"] = key
    return env, bool(key)


def send(proc: subprocess.Popen, payload: dict) -> None:
    assert proc.stdin is not None
    proc.stdin.write(json.dumps(payload) + "\n")
    proc.stdin.flush()


def read_reply(proc: subprocess.Popen, want_id: int, timeout: float) -> dict:
    """Читает stdout построчно до ответа с нужным id (или до таймаута)."""
    assert proc.stdout is not None
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        line = proc.stdout.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("id") == want_id:
            return msg
    raise TimeoutError(f"нет ответа на id={want_id} за {timeout}с")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Пробник MCP-канала firecrawl (stdio, чистые прокси-переменные).",
        epilog=(
            "Примеры:\n"
            "  python3 tools/firecrawl/probe_mcp.py --tool firecrawl_credit_usage\n"
            "  python3 tools/firecrawl/probe_mcp.py --tool firecrawl_credit_usage --json\n"
            "  python3 tools/firecrawl/probe_mcp.py --keep-proxy   # воспроизвести 407"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--tool", default="firecrawl_credit_usage", help="имя MCP-инструмента")
    parser.add_argument("--args", default="{}", help="JSON-аргументы для tools/call")
    parser.add_argument("--timeout", type=float, default=90.0, help="секунд на один ответ")
    parser.add_argument("--keep-proxy", action="store_true", help="не чистить прокси-переменные")
    parser.add_argument("--json", action="store_true", help="вывод одной JSON-строкой")
    parser.add_argument("--dry-run", action="store_true", help="только показать план запуска")
    args = parser.parse_args()

    env, has_key = build_env(args.keep_proxy)
    plan = {
        "command": ["npx", "-y", "firecrawl-mcp"],
        "proxy_stripped": not args.keep_proxy,
        "key_present": has_key,
        "tool": args.tool,
    }
    if args.dry_run:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0
    if not has_key:
        print(f"нет ключа: {KEY_FILE}", file=sys.stderr)
        return 2

    try:
        tool_args = json.loads(args.args)
    except json.JSONDecodeError as exc:
        print(f"битый --args: {exc}", file=sys.stderr)
        return 2

    proc = subprocess.Popen(
        plan["command"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
        bufsize=1,
    )
    result: dict = {"ok": False}
    try:
        send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "firecrawl-probe", "version": "1.0"},
                },
            },
        )
        init = read_reply(proc, 1, args.timeout)
        send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
        send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": args.tool, "arguments": tool_args},
            },
        )
        call = read_reply(proc, 2, args.timeout)
        result = {
            "ok": "result" in call and not call["result"].get("isError", False),
            "server": init.get("result", {}).get("serverInfo", {}),
            "payload": call.get("result", call.get("error")),
        }
    except (TimeoutError, BrokenPipeError) as exc:
        result = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    finally:
        proc.terminate()
        try:
            stderr = proc.communicate(timeout=5)[1]
        except subprocess.TimeoutExpired:
            proc.kill()
            stderr = ""
        if stderr and not result.get("ok"):
            result["stderr_tail"] = stderr.strip().splitlines()[-5:]

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
