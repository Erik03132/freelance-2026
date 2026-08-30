#!/usr/bin/env python3
"""
OmniRoute Dashboard — lightweight management UI.
Reads/writes OmniRoute config on VPS:
  - /root/.omniroute/.env          (key=value provider config)
  - /root/.omniroute/provider-credentials.json
Exposes JSON API on :8890 for the nginx /omni/ proxy.
No external deps (stdlib only).
"""
import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

OMNI_ENV = "/root/.omniroute/.env"
CRED_FILE = "/root/.omniroute/provider-credentials.json"

def read_env(path=OMNI_ENV):
    data = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                m = re.match(r"^([A-Za-z0-9_]+)=(.*)$", line)
                if m:
                    data[m.group(1)] = m.group(2)
    return data

def write_env(data, path=OMNI_ENV):
    # preserve existing file, update only known keys
    existing = read_env(path)
    existing.update(data)
    lines = [f"{k}={v}" for k, v in existing.items()]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def read_creds(path=CRED_FILE):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

class H(BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    HTML_FILE = "/var/www/html/omni_dashboard.html"

    def do_GET(self):
        if self.path.rstrip("/") in ("", "/index.html", "/dashboard"):
            try:
                with open(self.HTML_FILE, "rb") as f:
                    body = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                self._json({"error": str(e)}, 500)
            return
        if self.path.rstrip("/") in ("/api", "/api/status"):
            env = read_env()
            # mask secrets
            masked = {k: ("***" if any(s in k for s in ("KEY", "SECRET", "TOKEN", "PASSWORD")) else v)
                      for k, v in env.items()}
            self._json({
                "status": "ok",
                "omniroute_env_keys": sorted(masked.keys()),
                "env": masked,
                "credentials_present": bool(read_creds()),
            })
        elif self.path.rstrip("/") == "/api/models":
            # try to reach omni API if alive
            self._json({"note": "OmniRoute HTTP API currently unavailable on this build; manage via env/credentials."})
        else:
            self._json({"error": "unknown path"}, 404)

    def do_POST(self):
        if self.path.rstrip("/") == "/api/env":
            try:
                length = int(self.headers.get("Content-Length", 0))
                payload = json.loads(self.rfile.read(length) or b"{}")
                write_env(payload)
                self._json({"status": "saved", "keys": sorted(payload.keys())})
            except Exception as e:
                self._json({"error": str(e)}, 500)
        else:
            self._json({"error": "unknown path"}, 404)

    def log_message(self, *a):
        pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8890"))
    srv = ThreadingHTTPServer(("127.0.0.1", port), H)
    print(f"OmniRoute dashboard backend on :{port}")
    srv.serve_forever()
