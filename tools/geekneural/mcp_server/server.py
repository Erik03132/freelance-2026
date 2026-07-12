#!/usr/bin/env python3
"""
GeekNeural MCP-сервер (уровень 2).

Чистый stdio JSON-RPC — без внешних зависимостей (только stdlib).
Говорит с OpenCode/Claude/Cursor по MCP-протоколу и отдаёт инструменты
дедупликации контекста поверх ядра core/dedup.py.

Протокол: https://modelcontextprotocol.io (JSON-RPC 2.0, newline-delimited).
"""
from __future__ import annotations

import json
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.dedup import DedupEngine, session_from_env  # noqa: E402

PROTOCOL_VERSION = "2024-11-05"
SESSION_ID = os.environ.get("GEEKNEURAL_SESSION") or ("mcp-" + uuid.uuid4().hex[:8])
ENGINE = DedupEngine(SESSION_ID)


def _log(msg: str) -> None:
    sys.stderr.write(f"[geekneural:{SESSION_ID}] {msg}\n")
    sys.stderr.flush()


TOOLS = [
    {
        "name": "cached_read",
        "description": (
            "Дедуп-чтение файла. При повторном обращении к тому же содержимому "
            "в рамках сессии возвращает короткую ссылку вместо полного тела файла "
            "-> экономия токенов. Логи/lock/мелкие файлы не дедуплицируются."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "путь к файлу"},
                "force": {"type": "boolean", "default": False,
                          "description": "принудительно вернуть полное содержимое"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "cached_read_text",
        "description": "Дедупликация произвольного куска текста по стабильному key.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "key": {"type": "string", "description": "стабильный идентификатор"},
                "force": {"type": "boolean", "default": False},
            },
            "required": ["text", "key"],
        },
    },
    {
        "name": "context_refs",
        "description": "Список ссылок gn:<hash>, уже находящихся в контексте сессии.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "session_stats",
        "description": "Сводка экономии токенов по сессии (reads, deduped, %, токены).",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "clear_session",
        "description": "Сброс кеша дедупликации текущей сессии.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def _tool_result(text: str) -> dict:
    return {"content": [{"type": "text", "text": text}], "isError": False}


def _dispatch_tool(name: str, args: dict) -> dict:
    if name == "cached_read":
        r = ENGINE.read(args.get("path", ""), force=bool(args.get("force", False)))
        body = r.content if not r.deduped else f"{r.content}\n[ref={r.ref}]"
        return _tool_result(body)
    if name == "cached_read_text":
        r = ENGINE.read_text(args.get("text", ""), args.get("key", ""),
                             force=bool(args.get("force", False)))
        body = r.content if not r.deduped else f"{r.content}\n[ref={r.ref}]"
        return _tool_result(body)
    if name == "context_refs":
        import sqlite3
        cur = ENGINE.conn.execute(
            "SELECT content_hash, path, ref_count FROM seen WHERE session_id=? "
            "ORDER BY ref_count DESC", (ENGINE.session_id,))
        rows = [{"ref": f"gn:{h}", "path": p, "seen": c} for h, p, c in cur.fetchall()]
        return _tool_result(json.dumps(rows, ensure_ascii=False, indent=2))
    if name == "session_stats":
        return _tool_result(json.dumps(ENGINE.stats_dict(), ensure_ascii=False, indent=2))
    if name == "clear_session":
        n = ENGINE.clear_session()
        return _tool_result(json.dumps({"cleared": n}, ensure_ascii=False))
    return {"content": [{"type": "text", "text": f"unknown tool {name}"}], "isError": True}


def _handle(msg: dict) -> dict | None:
    method = msg.get("method")
    mid = msg.get("id")
    params = msg.get("params", {}) or {}

    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": mid,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "geekneural", "version": "0.1.0"},
            },
        }
    if method == "notifications/initialized":
        return None
    if method == "ping":
        return {"jsonrpc": "2.0", "id": mid, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}}
    if method == "tools/call":
        name = params.get("name", "")
        args = params.get("arguments", {}) or {}
        try:
            res = _dispatch_tool(name, args)
        except Exception as exc:  # noqa: BLE001
            res = {"content": [{"type": "text", "text": f"error: {exc}"}],
                   "isError": True}
        return {"jsonrpc": "2.0", "id": mid, "result": res}
    # неизвестный метод
    if mid is not None:
        return {"jsonrpc": "2.0", "id": mid,
                "error": {"code": -32601, "message": f"method not found: {method}"}}
    return None


def main() -> None:
    _log("MCP server started")
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            continue
        try:
            resp = _handle(msg)
        except Exception as exc:  # noqa: BLE001
            _log(f"handler error: {exc}")
            resp = None
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    ENGINE.close()


if __name__ == "__main__":
    main()
