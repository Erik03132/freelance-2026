"""Интеграционный тест MCP-сервера через реальный stdio (уровень 2)."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SERVER = os.path.join(ROOT, "mcp_server", "server.py")


def _rpc(proc, method, params=None, mid=1):
    req = {"jsonrpc": "2.0", "id": mid, "method": method}
    if params is not None:
        req["params"] = params
    proc.stdin.write(json.dumps(req) + "\n")
    proc.stdin.flush()
    line = proc.stdout.readline()
    return json.loads(line)


def test_mcp_handshake_and_tools():
    env = dict(os.environ, GEEKNEURAL_SESSION="mcptest_" + os.urandom(4).hex())
    proc = subprocess.Popen(
        [sys.executable, SERVER], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env, text=True,
    )
    try:
        init = _rpc(proc, "initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {}, "clientInfo": {"name": "t", "version": "0"}})
        assert init["result"]["serverInfo"]["name"] == "geekneural"

        # notifications/initialized -> no response
        proc.stdin.write(json.dumps({"jsonrpc": "2.0",
                                     "method": "notifications/initialized"}) + "\n")
        proc.stdin.flush()

        tl = _rpc(proc, "tools/list", mid=2)
        names = [t["name"] for t in tl["result"]["tools"]]
        for expected in ("cached_read", "cached_read_text", "context_refs",
                         "session_stats", "clear_session"):
            assert expected in names, f"нет tool {expected}"

        # дедуп-чтение дважды
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "f.py")
            open(p, "w").write("data = " + "1" * 4000)
            r1 = _rpc(proc, "tools/call",
                      {"name": "cached_read", "arguments": {"path": p}}, mid=3)
            assert r1["result"]["isError"] is False
            assert "data =" in r1["result"]["content"][0]["text"]
            r2 = _rpc(proc, "tools/call",
                      {"name": "cached_read", "arguments": {"path": p}}, mid=4)
            assert "уже в контексте" in r2["result"]["content"][0]["text"]

        stats = _rpc(proc, "tools/call", {"name": "session_stats", "arguments": {}}, mid=5)
        sd = json.loads(stats["result"]["content"][0]["text"])
        assert sd["deduped"] >= 1
        assert sd["pct_saved"] > 0
        print("MCP pct_saved =", sd["pct_saved"], "tokens_saved =", sd["est_tokens_saved"])
    finally:
        proc.terminate()


if __name__ == "__main__":
    test_mcp_handshake_and_tools()
    print("MCP INTEGRATION TEST PASSED")
