#!/usr/bin/env python3
"""Omni Auto-Router v4 — fixed local Ollama (OpenAI-compatible) + free OpenRouter vision."""

import json, os, re, threading, urllib.request, urllib.error, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from dataclasses import dataclass
from typing import Optional

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OMNIR_VPS_URL = os.environ.get("OMNIR_VPS_URL", "http://217.149.23.113:20128/v1")
OMNIR_VPS_KEY = os.environ.get("OMNIR_VPS_KEY")
OPENROUTER_FALLBACK_URL = os.environ.get("OPENROUTER_FALLBACK_URL", "https://openrouter.ai/api/v1")
PORT = int(os.environ.get("PORT", 8123))
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/v1/chat/completions")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")

CODE_BLOCK_RX = re.compile(r"```\w*\n")
FUNC_RX = re.compile(r"\b(def |function |class |async def |fn |=>\s*\{|import\s+|from\s+\w+\s+import|useState|useEffect|export\s+default)")
IMPERATIVE_RX = re.compile(r"\b(напиши|сделай|реализуй|создай|добавь|исправь|перепиши|refactor|write|implement|create|add|fix|rewrite|build|develop|design|рефактори|оптимизируй|оптимизировать|настрой|разработай)\b", re.IGNORECASE)
ANALYSIS_RX = re.compile(r"\b(почему|объясни|сравни|проанализируй|оцени|найди\s+ошибк|explain|analyze|why|compare|evaluate|review|audit|спланируй|архитектур|спроектируй|plan|design|architect)\b", re.IGNORECASE)
SIMPLE_RX = re.compile(r"\b(what is|how to|как\s+(сделать|написать|использовать)|что\s+такое|ls\b|grep\b|cat\b|прочитай|найди|format)|\?\s*$", re.IGNORECASE)
ARCHITECTURE_RX = re.compile(r"\b(спроектируй|архитектур|architect|architecture|спланируй|design.*(system|architecture|microservice)|plan.*architecture|project.*structure)\b", re.IGNORECASE)
TOOL_PAT = re.compile(r"\"function\"\s*:|tool_calls|\"tools\"\s*:")

FREE_MODELS = [
    f"local:{OLLAMA_MODEL}",
    "openrouter/google/gemini-2.5-flash",
    "openrouter/google/gemini-2.0-flash-lite-preview-02-05:free",
    "openrouter/deepseek/deepseek-chat",
    "openrouter/moonshotai/kimi-k2",
    "openrouter/nvidia/nemotron-3-ultra-550b-a55b:free",
    "openrouter/qwen/qwen3-235b-a22b:free",
    "openrouter/meta-llama/llama-4-maverick:free",
    "openrouter/sentence-transformers/all-roles-multimodal-v2:free",
    "openrouter/cognitivecomputations/dolphin3.0-r1-mistral-24b:free",
    "openrouter/google/gemma-4-26b-a4b-it:free",
    "openrouter/google/gemma-4-31b-it:free",
    "openrouter/nvidia/nemotron-nano-12b-v2-vl:free",
    "openrouter/qwen/qwen-vl-plus:free",
    "openrouter/mistralai/mistral-large-3:free",
]

TIER_CHAINS = {
    0: FREE_MODELS[:],
    1: [f"local:{OLLAMA_MODEL}", "openrouter/deepseek/deepseek-chat", "openrouter/google/gemini-2.5-flash", "openrouter/moonshotai/kimi-k2"],
    2: [f"local:{OLLAMA_MODEL}", "openrouter/anthropic/claude-sonnet-4.6", "openrouter/openai/gpt-4o", "openrouter/google/gemini-2.5-pro"],
    3: [f"local:{OLLAMA_MODEL}", "openrouter/anthropic/claude-opus-4.8", "openrouter/anthropic/claude-fable-5", "openrouter/openai/gpt-5.6-sol"],
}

VISION_CHAINS = {
    0: [f"local:{OLLAMA_MODEL}", "openrouter/google/gemma-4-26b-a4b-it:free", "openrouter/google/gemma-4-31b-it:free", "openrouter/nvidia/nemotron-nano-12b-v2-vl:free", "openrouter/qwen/qwen-vl-plus:free", "openrouter/sentence-transformers/all-roles-multimodal-v2:free"],
    1: [f"local:{OLLAMA_MODEL}", "openrouter/google/gemma-4-26b-a4b-it:free", "openrouter/google/gemini-2.5-flash", "openrouter/openai/gpt-4o-mini"],
    2: [f"local:{OLLAMA_MODEL}", "openrouter/anthropic/claude-sonnet-4.6", "openrouter/openai/gpt-4o", "openrouter/google/gemini-2.5-pro"],
    3: [f"local:{OLLAMA_MODEL}", "openrouter/anthropic/claude-sonnet-5", "openrouter/openai/gpt-5.6-sol", "openrouter/anthropic/claude-opus-4.8"],
}

TIER_LABELS = {0: "Free", 1: "Cheap", 2: "Smart", 3: "Pro"}
TIER_COST_PER_M = {0: {"in": 0.0, "out": 0.0}, 1: {"in": 0.14, "out": 0.28}, 2: {"in": 3, "out": 15}, 3: {"in": 15, "out": 75}}

stats_lock = threading.Lock()
stats = {"total_cost": 0.0, "total_requests": 0, "by_tier": {0: 0, 1: 0, 2: 0, 3: 0}, "by_model": {}, "fallbacks": 0, "errors": 0}
vps_alive_lock = threading.Lock()
vps_alive_cache = {"alive": True, "checked_at": 0.0}
VPS_CACHE_TTL = 60

def is_vps_alive() -> bool:
    now = time.time()
    with vps_alive_lock:
        if now - vps_alive_cache["checked_at"] < VPS_CACHE_TTL:
            return vps_alive_cache["alive"]
    try:
        req = urllib.request.Request(f"{OMNIR_VPS_URL}/models", method="GET")
        req.add_header("User-Agent", "omni-auto-router/4.0")
        resp = urllib.request.urlopen(req, timeout=5)
        alive = resp.status == 200
    except Exception:
        alive = False
    with vps_alive_lock:
        vps_alive_cache["alive"] = alive
        vps_alive_cache["checked_at"] = now
    return alive

@dataclass
class Features:
    has_code_block: bool = False
    has_func_def: bool = False
    has_imperative: bool = False
    has_analysis: bool = False
    has_simple_q: bool = False
    has_architecture: bool = False
    has_image: bool = False
    has_tools: bool = False
    has_system: bool = False
    msg_count: int = 0
    total_chars: int = 0
    max_msg_chars: int = 0

    @property
    def complexity_score(self) -> float:
        s = 0.0
        if self.has_code_block: s += 2
        if self.has_func_def: s += 2
        if self.has_imperative: s += 1.5
        if self.has_analysis: s += 1.5
        if self.has_architecture: s += 2.5
        if self.has_image: s += 2
        if self.has_tools: s += 3
        if self.has_system: s += 1
        if self.msg_count > 4: s += 1.5
        if self.msg_count > 10: s += 1
        if self.total_chars > 5000: s += 1
        if self.total_chars > 15000: s += 1
        if self.max_msg_chars > 2000: s += 0.5
        if self.has_simple_q: s -= 2
        return max(s, 0)

    def classify_tier(self) -> int:
        if self.has_simple_q and not self.has_imperative and not self.has_code_block:
            if self.total_chars < 300: return 0
        if self.has_architecture and (self.has_analysis or self.has_tools): return 3
        if self.has_architecture and self.has_imperative: return 3
        if self.msg_count >= 6 and self.has_analysis: return 3
        score = self.complexity_score
        if score >= 7: return 3
        if score >= 3: return 2
        if score >= 1.5: return 1
        return 0

def extract_features(messages: list) -> Features:
    f = Features()
    texts = []
    for m in messages:
        role = (m.get("role") or "").lower()
        content = m.get("content") or ""
        if isinstance(content, list):
            parts = []
            for block in content:
                if not isinstance(block, dict): continue
                bt = block.get("type", "")
                if bt in ("image_url", "image"): f.has_image = True
                if bt in ("text", "text_delta"): parts.append(block.get("text", ""))
            content = " ".join(parts)
        texts.append(content)
        if CODE_BLOCK_RX.search(content): f.has_code_block = True
        if FUNC_RX.search(content): f.has_func_def = True
        if IMPERATIVE_RX.search(content): f.has_imperative = True
        if ANALYSIS_RX.search(content): f.has_analysis = True
        if ARCHITECTURE_RX.search(content): f.has_architecture = True
        if SIMPLE_RX.search(content): f.has_simple_q = True
        if role in ("system", "developer"): f.has_system = True
        if len(content) > f.max_msg_chars: f.max_msg_chars = len(content)
    f.msg_count = len(messages)
    f.total_chars = sum(len(t) for t in texts)
    full_text = " ".join(texts).lower()
    if TOOL_PAT.search(full_text): f.has_tools = True
    msg_text = json.dumps(messages)
    if TOOL_PAT.search(msg_text): f.has_tools = True
    return f

def classify(messages: list) -> tuple:
    f = extract_features(messages)
    tier = f.classify_tier()
    details = []
    if f.has_code_block: details.append("code")
    if f.has_func_def: details.append("func")
    if f.has_imperative: details.append("impl")
    if f.has_analysis: details.append("analysis")
    if f.has_architecture: details.append("arch")
    if f.has_image: details.append("img")
    if f.has_tools: details.append("tools")
    if f.has_simple_q: details.append("simple")
    if f.msg_count > 4: details.append(f"multi({f.msg_count})")
    return tier, f"{TIER_LABELS[tier]} [{','.join(details) if details else 'chat'}]", f.has_image

def _no_proxy_context():
    saved = {}
    for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        saved[k] = os.environ.pop(k, None)
    return saved

def _restore_proxy(saved: dict):
    for k, v in saved.items():
        if v is not None: os.environ[k] = v

def _do_request(url: str, body: dict, api_key: Optional[str], timeout: int = 120) -> tuple:
    model = body["model"]
    body.setdefault("stream", False)
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"{url}/chat/completions", data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if api_key:
        req.add_header("Authorization", api_key if api_key.startswith("Bearer ") else f"Bearer {api_key}")
    req.add_header("User-Agent", "omni-auto-router/4.0")
    saved = {}
    if "217.149.23.113" in url: saved = _no_proxy_context()
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        return resp, model, None
    except urllib.error.HTTPError as e:
        return None, model, e.read().decode()
    except Exception as e:
        return None, model, str(e)
    finally:
        _restore_proxy(saved)

def _clean_model(model: str) -> str:
    return model.lstrip("/").replace("openrouter/", "", 1)

def call_omni(model: str, body: dict, auth_header: Optional[str], retries=1) -> tuple:
    vps_key = OMNIR_VPS_KEY or OPENROUTER_API_KEY or auth_header
    if is_vps_alive():
        for attempt in range(retries + 1):
            body["model"] = _clean_model(model)
            resp, mdl, err = _do_request(OMNIR_VPS_URL, body, vps_key, timeout=30)
            if resp: return resp, mdl, False
            if attempt < retries: time.sleep(1); continue
            import sys
            print(f"[omni-auto] VPS: {err[:80]}. Fallback OpenRouter...", file=sys.stderr, flush=True)
    body["model"] = _clean_model(model)
    fallback_key = OPENROUTER_API_KEY or auth_header
    resp2, mdl2, err2 = _do_request(OPENROUTER_FALLBACK_URL, body, fallback_key, timeout=120)
    if resp2: return resp2, mdl2, not is_vps_alive()
    return None, mdl, err2

def _call_local(body: dict) -> tuple:
    """Call Ollama via OpenAI-compatible endpoint (/v1/chat/completions)."""
    body["model"] = OLLAMA_MODEL
    data = json.dumps(body).encode()
    req = urllib.request.Request(OLLAMA_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "omni-auto-router/4.0")
    try:
        resp = urllib.request.urlopen(req, timeout=120)
        return resp, OLLAMA_MODEL, None
    except urllib.error.HTTPError as e:
        return None, OLLAMA_MODEL, e.read().decode()
    except Exception as e:
        return None, OLLAMA_MODEL, str(e)

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200); self.end_headers()
    def do_GET(self):
        if self.path == "/v1/models":
            model_list = [
                {"id": "omni-auto", "object": "model", "capabilities": {"vision": True}},
                {"id": "auto", "object": "model", "capabilities": {"vision": True}},
                {"id": "free-cascade", "object": "model", "capabilities": {"vision": True}},
                {"id": "free-only", "object": "model", "capabilities": {"vision": True}},
            ]
            for m in FREE_MODELS:
                if m.startswith("openrouter/"):
                    model_list.append({"id": m, "object": "model", "capabilities": {"vision": "vl" in m or "vision" in m.lower() or "gemma" in m.lower()}})
            self.send_json({"data": model_list})
        elif self.path == "/stats":
            with stats_lock: s = dict(stats)
            s["total_cost"] = round(s["total_cost"], 6)
            s["by_tier_pct"] = {str(k): round(v / max(s["total_requests"], 1) * 100, 1) for k, v in s["by_tier"].items()}
            s["vps_alive"] = is_vps_alive()
            s["free_models"] = len(FREE_MODELS)
            self.send_json(s)
        else: self.send_error(404)
    def do_POST(self):
        if self.path != "/v1/chat/completions": return self.send_error(404)
        try:
            cl = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(cl))
        except Exception: self.send_json({"error": "bad request"}, 400); return
        messages = body.get("messages", [])
        stream = body.get("stream", False)
        auth = self.headers.get("Authorization")
        model_name = body.get("model", "auto")
        if model_name == "free-only" or model_name == "free":
            tier = 0; chain = TIER_CHAINS[0]; used_model = chain[0]; fallback_used = False; errors = []
            for model in chain:
                if model.startswith("local:"):
                    resp, used_model, err = _call_local(body)
                else:
                    resp, used_model, err = call_omni(model, body, auth, retries=1)
                if resp is not None: break
                errors.append(f"{model}: {(err or '')[:100]}"); fallback_used = True
                with stats_lock: stats["fallbacks"] += 1
            if resp is None:
                with stats_lock: stats["errors"] += 1
                return self.send_json({"error": f"All free models failed: {'; '.join(errors)}"}, 502)
            full_model = used_model
            label = f"T{tier}->{used_model}"
            if fallback_used: label += f" [FB: {'->'.join(e.split(':')[0] for e in errors)}]"
            print(f"[omni-auto] {label} (Free [forced])", flush=True)
        elif model_name == "auto" or model_name not in TIER_CHAINS:
            tier, reason, has_image = classify(messages)
            chain = VISION_CHAINS[tier] if has_image else TIER_CHAINS[tier]
            used_model = chain[0]; fallback_used = False; errors = []
            for model in chain:
                if model.startswith("local:"):
                    resp, used_model, err = _call_local(body)
                else:
                    resp, used_model, err = call_omni(model, body, auth, retries=1)
                if resp is not None: break
                errors.append(f"{model}: {(err or '')[:100]}"); fallback_used = True
                with stats_lock: stats["fallbacks"] += 1
            if resp is None and tier > 0:
                print(f"[omni-auto] T{tier} chain failed, falling back to free chain", flush=True)
                fallback_chain = VISION_CHAINS[0] if has_image else TIER_CHAINS[0]
                for model in fallback_chain:
                    if model.startswith("local:"):
                        resp, used_model, err = _call_local(body)
                    else:
                        resp, used_model, err = call_omni(model, body, auth, retries=1)
                    if resp is not None:
                        fallback_used = True
                        with stats_lock: stats["fallbacks"] += 1
                        break
                    errors.append(f"{model}: {(err or '')[:100]}")
            if resp is None:
                with stats_lock: stats["errors"] += 1
                return self.send_json({"error": f"All models failed: {'; '.join(errors)}"}, 502)
            full_model = used_model
            label = f"T{tier}->{used_model}"
            if fallback_used: label += f" [FB: {'->'.join(e.split(':')[0] for e in errors)}]"
            print(f"[omni-auto] {label} ({reason})", flush=True)
        else:
            tier = -1; full_model = model_name
            resp, full_model, err = call_omni(full_model, body, auth, retries=2)
            if resp is None:
                print(f"[omni-auto] Direct model {model_name} failed, falling back to auto", flush=True)
                body["model"] = "auto"; return self.do_POST()
            print(f"[omni-auto] {model_name} -> {full_model}", flush=True)
        if stream:
            self.send_response(200); self.send_header("Content-Type", "text/event-stream"); self.send_header("Cache-Control", "no-cache"); self.end_headers()
            while True:
                chunk = resp.read(4096)
                if not chunk: break
                self.wfile.write(chunk); self.wfile.flush()
            resp.close(); return
        try: resp_body = json.loads(resp.read())
        except Exception: resp_body = {"error": "bad upstream response"}
        resp_body["model"] = full_model
        self._log_stats(full_model, tier if tier else 0, in_tokens=sum(len(m.get("content", "") or "") for m in messages) // 2, resp_body=resp_body)
        self.send_json(resp_body)
    def _log_stats(self, model: str, tier: int, in_tokens: int, resp_body: dict):
        out_tokens = (resp_body.get("usage", {}).get("completion_tokens", 0) or 0)
        c = TIER_COST_PER_M.get(tier, {"in": 0, "out": 0})
        cost = in_tokens / 1e6 * c["in"] + out_tokens / 1e6 * c["out"]
        with stats_lock:
            stats["total_cost"] += cost; stats["total_requests"] += 1
            stats["by_tier"][tier] = stats["by_tier"].get(tier, 0) + 1
            stats["by_model"][model] = stats["by_model"].get(model, 0) + 1
    def send_json(self, obj, code=200):
        self.send_response(code); self.send_header("Content-Type", "application/json"); self.end_headers()
        self.wfile.write(json.dumps(obj).encode())
    def log_message(self, fmt, *args): pass

class ThreadedHTTPServer(HTTPServer):
    allow_reuse_address = True; daemon_threads = True
    def process_request(self, request, client_address):
        t = threading.Thread(target=self.process_request_thread, args=(request, client_address))
        t.daemon = True; t.start()
    def process_request_thread(self, request, client_address):
        try: self.finish_request(request, client_address)
        except Exception: self.handle_error(request, client_address)
        finally: self.shutdown_request(request)

if __name__ == "__main__":
    server = ThreadedHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[omni-auto] v4 on http://0.0.0.0:{PORT}", flush=True)
    print(f"[omni-auto] Tiers: {TIER_LABELS}", flush=True)
    for t, models in TIER_CHAINS.items():
        print(f"  {TIER_LABELS[t]}: {' -> '.join(models)}", flush=True)
    print(f"[omni-auto] Vision chains (free tier): {VISION_CHAINS[0]}", flush=True)
    print(f"[omni-auto] Stats: /stats", flush=True)
    print(f"[omni-auto] Backend VPS: {OMNIR_VPS_URL} | Fallback: {OPENROUTER_FALLBACK_URL}", flush=True)
    print(f"[omni-auto] Ollama: {OLLAMA_URL} (model: {OLLAMA_MODEL})", flush=True)
    print(f"[omni-auto] Key set: {bool(OPENROUTER_API_KEY)}", flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: print("\n[omni-auto] shutdown", flush=True); server.server_close()