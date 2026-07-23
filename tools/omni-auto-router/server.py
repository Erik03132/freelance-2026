#!/usr/bin/env python3
"""Omni Auto-Router v2 — multi-factor classification + fallback chain."""

import json, os, re, threading, urllib.request, urllib.error, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from dataclasses import dataclass, field
from typing import Optional

OMNI_URL = os.environ.get("OMNI_URL", "http://217.149.23.113:20128/v1/chat/completions")
PORT = int(os.environ.get("PORT", 8123))

CODE_BLOCK_RX = re.compile(r"```\w*\n")
FUNC_RX = re.compile(
    r"\b(def |function |class |async def |fn |=>\s*\{|import\s+"
    r"|from\s+\w+\s+import|useState|useEffect|export\s+default)"
)
IMPERATIVE_RX = re.compile(
    r"\b(напиши|сделай|реализуй|создай|добавь|исправь|перепиши"
    r"|refactor|write|implement|create|add|fix|rewrite|build|develop"
    r"|рефактори|оптимизируй|оптимизировать|настрой|разработай)\b",
    re.IGNORECASE,
)
ANALYSIS_RX = re.compile(
    r"\b(почему|объясни|сравни|проанализируй|оцени|найди\s+ошибк"
    r"|explain|analyze|why|compare|evaluate|review|audit"
    r"|спланируй|архитектура|спроектируй|plan|design|architect)\b",
    re.IGNORECASE,
)
SIMPLE_RX = re.compile(
    r"\b(what is|how to|как\s+(сделать|написать|использовать)"
    r"|что\s+такое|ls\b|grep\b|cat\b|прочитай|найди|format)"
    r"|\?\s*$",
    re.IGNORECASE,
)
ARCHITECTURE_RX = re.compile(
    r"\b(спроектируй|архитектур|design.*system|architect"
    r"|спланируй|plan.*architecture|project.*structure)\b",
    re.IGNORECASE,
)
TOOL_PAT = re.compile(r"\"function\"\s*:|tool_calls|\"tools\"\s*:")

FREE_MODELS = [
    "openrouter/nvidia/nemotron-3-ultra-550b-a55b:free",
    "openrouter/openai/gpt-oss-20b:free",
    "openrouter/google/gemma-4-31b-it:free",
]
CHEAP_MODELS = [
    "openrouter/deepseek/deepseek-chat",
    "openrouter/openai/gpt-4o-mini",
]
SMART_MODELS = [
    "openrouter/anthropic/claude-sonnet-4.6",
    "openrouter/openai/gpt-4o",
]
PRO_MODELS = [
    "openrouter/anthropic/claude-opus-4.8",
    "openrouter/openai/gpt-5-pro",
]

TIER_CHAINS = {
    0: FREE_MODELS,
    1: CHEAP_MODELS,
    2: SMART_MODELS,
    3: PRO_MODELS,
}
TIER_LABELS = {0: "Free", 1: "Cheap", 2: "Smart", 3: "Pro"}
TIER_COST_PER_M = {
    0: {"in": 0, "out": 0},
    1: {"in": 0.0005, "out": 0.002},
    2: {"in": 0.003, "out": 0.015},
    3: {"in": 0.015, "out": 0.075},
}

stats_lock = threading.Lock()
stats = {
    "total_cost": 0.0,
    "total_requests": 0,
    "by_tier": {0: 0, 1: 0, 2: 0, 3: 0},
    "by_model": {},
    "fallbacks": 0,
    "errors": 0,
}


@dataclass
class Features:
    has_code_block: bool = False
    has_func_def: bool = False
    has_imperative: bool = False
    has_analysis: bool = False
    has_simple_q: bool = False
    has_architecture: bool = False
    has_tools: bool = False
    has_system: bool = False
    msg_count: int = 0
    total_chars: int = 0
    max_msg_chars: int = 0

    @property
    def complexity_score(self) -> float:
        s = 0.0
        if self.has_code_block:
            s += 2
        if self.has_func_def:
            s += 2
        if self.has_imperative:
            s += 1.5
        if self.has_analysis:
            s += 2
        if self.has_architecture:
            s += 2.5
        if self.has_tools:
            s += 3
        if self.has_system:
            s += 1
        if self.msg_count > 4:
            s += 1.5
        if self.msg_count > 10:
            s += 1
        if self.total_chars > 5000:
            s += 1
        if self.total_chars > 15000:
            s += 1
        if self.max_msg_chars > 2000:
            s += 0.5
        if self.has_simple_q:
            s -= 2
        return max(s, 0)

    def classify_tier(self) -> int:
        # Simple question → Free
        if self.has_simple_q and not self.has_imperative and not self.has_code_block:
            if self.total_chars < 300:
                return 0

        score = self.complexity_score

        if score >= 7:
            return 3
        if score >= 3:
            return 2
        if score >= 1.5:
            return 1
        return 0


def extract_features(messages: list) -> Features:
    f = Features()
    texts = []
    for m in messages:
        role = (m.get("role") or "").lower()
        content = m.get("content") or ""
        if isinstance(content, list):
            content = " ".join(
                c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") in ("text", "text_delta")
            )
        texts.append(content)
        if CODE_BLOCK_RX.search(content):
            f.has_code_block = True
        if FUNC_RX.search(content):
            f.has_func_def = True
        if IMPERATIVE_RX.search(content):
            f.has_imperative = True
        if ANALYSIS_RX.search(content):
            f.has_analysis = True
        if ARCHITECTURE_RX.search(content):
            f.has_architecture = True
        if SIMPLE_RX.search(content):
            f.has_simple_q = True
        if role in ("system", "developer"):
            f.has_system = True
        if len(content) > f.max_msg_chars:
            f.max_msg_chars = len(content)
    f.msg_count = len(messages)
    f.total_chars = sum(len(t) for t in texts)

    full_text = " ".join(texts).lower()
    if TOOL_PAT.search(full_text):
        f.has_tools = True
    msg_text = json.dumps(messages)
    if TOOL_PAT.search(msg_text):
        f.has_tools = True

    return f


def classify(messages: list) -> tuple:
    f = extract_features(messages)
    tier = f.classify_tier()
    details = []
    if f.has_code_block:
        details.append("code")
    if f.has_func_def:
        details.append("func")
    if f.has_imperative:
        details.append("impl")
    if f.has_analysis:
        details.append("analysis")
    if f.has_architecture:
        details.append("arch")
    if f.has_tools:
        details.append("tools")
    if f.has_simple_q:
        details.append("simple")
    if f.msg_count > 4:
        details.append(f"multi({f.msg_count})")
    return tier, f"{TIER_LABELS[tier]} [{','.join(details) if details else 'chat'}]"


def call_omni(model: str, body: dict, auth_header: Optional[str], retries=1) -> tuple:
    body["model"] = model
    data = json.dumps(body).encode()
    req = urllib.request.Request(OMNI_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if auth_header:
        req.add_header("Authorization", auth_header)
    req.add_header("User-Agent", "omni-auto-router/2.0")
    for attempt in range(retries + 1):
        try:
            resp = urllib.request.urlopen(req, timeout=120)
            return resp, model, False
        except urllib.error.HTTPError as e:
            body_text = e.read().decode()
            if attempt < retries:
                time.sleep(1)
                continue
            return None, model, body_text
        except Exception as e:
            if attempt < retries:
                time.sleep(1)
                continue
            return None, model, str(e)


class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == "/v1/models":
            self.send_json({"data": [{"id": "omni-auto", "object": "model"}]})
        elif self.path == "/stats":
            with stats_lock:
                s = dict(stats)
            s["total_cost"] = round(s["total_cost"], 6)
            s["by_tier_pct"] = {
                str(k): round(v / max(s["total_requests"], 1) * 100, 1)
                for k, v in s["by_tier"].items()
            }
            self.send_json(s)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/v1/chat/completions":
            return self.send_error(404)
        try:
            cl = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(cl))
        except Exception:
            self.send_json({"error": "bad request"}, 400)
            return

        messages = body.get("messages", [])
        stream = body.get("stream", False)
        auth = self.headers.get("Authorization")

        tier, reason = classify(messages)
        chain = TIER_CHAINS[tier]
        used_model = chain[0]
        fallback_used = False
        errors = []

        for model in chain:
            resp, used_model, err = call_omni(model, body, auth, retries=1)
            if resp is not None:
                break
            errors.append(f"{model}: {err[:100]}")
            fallback_used = True
            with stats_lock:
                stats["fallbacks"] += 1

        if resp is None:
            with stats_lock:
                stats["errors"] += 1
            return self.send_json(
                {"error": f"All models failed: {'; '.join(errors)}"},
                502,
            )

        in_tokens = sum(len(m.get("content", "") or "") for m in messages) // 2
        label = f"T{tier}→{used_model}"
        if fallback_used:
            label += f" [FB: {'→'.join(e.split(':')[0] for e in errors)}]"
        print(f"[omni-auto] {label} ({reason})")

        if stream:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            while True:
                chunk = resp.read(4096)
                if not chunk:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()
            resp.close()
            return

        try:
            resp_body = json.loads(resp.read())
        except Exception:
            resp_body = {"error": "bad upstream response"}
        resp_body["model"] = used_model
        self._log_stats(tier, used_model, in_tokens, resp_body)
        self.send_json(resp_body)

    def _log_stats(self, tier: int, model: str, in_tokens: int, resp_body: dict):
        out_tokens = (
            resp_body.get("usage", {}).get("completion_tokens", 0)
            or 0
        )
        c = TIER_COST_PER_M.get(tier, {"in": 0, "out": 0})
        cost = in_tokens / 1e6 * c["in"] + out_tokens / 1e6 * c["out"]
        with stats_lock:
            stats["total_cost"] += cost
            stats["total_requests"] += 1
            stats["by_tier"][tier] = stats["by_tier"].get(tier, 0) + 1
            stats["by_model"][model] = stats["by_model"].get(model, 0) + 1

    def send_json(self, obj, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode())

    def log_message(self, fmt, *args):
        pass


class ThreadedHTTPServer(HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def process_request(self, request, client_address):
        t = threading.Thread(
            target=self.process_request_thread,
            args=(request, client_address),
        )
        t.daemon = True
        t.start()

    def process_request_thread(self, request, client_address):
        try:
            self.finish_request(request, client_address)
        except Exception:
            self.handle_error(request, client_address)
        finally:
            self.shutdown_request(request)


if __name__ == "__main__":
    server = ThreadedHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"[omni-auto] v2 on http://127.0.0.1:{PORT}")
    print(f"[omni-auto] Tiers: {TIER_LABELS}")
    for t, models in TIER_CHAINS.items():
        print(f"  {TIER_LABELS[t]}: {' → '.join(models)}")
    print(f"[omni-auto] Stats: /stats")
    print(f"[omni-auto] Backend: {OMNI_URL}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[omni-auto] shutdown")
        server.server_close()
