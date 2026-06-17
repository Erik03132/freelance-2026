#!/usr/bin/env python3
"""
voice_angela_web.py — веб-интерфейс для тестирования Voice Angela.

Запуск: python3 agent-lab/voice_angela_web.py
Открыть: http://127.0.0.1:9090

Печатаешь вопрос -> Angela отвечает -> TTS озвучивает ответ в браузере.
"""
from __future__ import annotations

import html as html_module
import json
import os
import subprocess
from pathlib import Path

import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

load_dotenv(Path(__file__).parent.parent / ".env", override=True)

# Clear proxies for direct APIs (OpenRouter) — they work without proxy from US
for p in ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "https_proxy", "http_proxy", "all_proxy"):
    os.environ.pop(p, None)

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
SR = 24000

app = FastAPI(title="Voice Angela Web")

# ── Price context ──────────────────────────────────────────────────────────────
_PRICE_CTX: str | None = None


def load_prices() -> str:
    global _PRICE_CTX
    if _PRICE_CTX:
        return _PRICE_CTX
    pp = Path(__file__).parent.parent / "ai-eggs" / "config" / "prices.json"
    if not pp.exists():
        _PRICE_CTX = ""
        return ""
    with open(pp) as f:
        data = json.load(f)
    cats = data.get("categories", {})
    lines = ["Прайс-лист ВезёмЦыплят:"]
    for cv in cats.values():
        if not isinstance(cv, dict):
            continue
        lbl = cv.get("label", "")
        lines.append(f"\n{lbl}:")
        for name, info in cv.get("items", {}).items():
            p = info.get("price", "?")
            desc = info.get("description", "")[:80]
            lines.append(f"  {name}: {p}₽ — {desc}")
    contacts = data.get("contacts", {})
    lines.append(f"\nТелефон: {contacts.get('phone_primary', '')}")
    lines.append(f"Доставка: {data.get('delivery', {}).get('days', '')}")
    _PRICE_CTX = "\n".join(lines)
    return _PRICE_CTX


# ── Angela ────────────────────────────────────────────────────────────────────


def angela_answer(question: str, history: str = "") -> str:
    prompt = (
        "Ты — Анжела, голосовой ассистент птицеводческого бизнеса ВезёмЦыплят. "
        "Отвечай КРАТКО (1-3 предложения), естественно, по делу.\n"
        f"{load_prices()}\n{history}\n"
        "Если клиент просит оператора — ответь: 'ПЕРЕКЛЮЧАЮ_ОПЕРАТОРА'\n"
        f"Клиент: {question}"
    )
    for model in ["deepseek/deepseek-chat", "qwen/qwen-turbo"]:
        try:
            r = requests.post("https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 256,
                    "temperature": 0.3,
                },
                timeout=20,
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"  ⚠ {model}: {e}")
    return "Извините, повторите, пожалуйста."


# ── TTS ────────────────────────────────────────────────────────────────────────


def generate_tts(text: str) -> str | None:
    """Generate TTS using macOS say command, return base64 WAV."""
    try:
        out = Path("/tmp/va_web.wav")
        aiff = out.with_suffix(".aiff")
        subprocess.run(
            ["say", "-v", "Milena", "-o", str(aiff), text],
            capture_output=True, timeout=30,
        )
        if aiff.exists():
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(aiff), "-ar", str(SR), "-ac", "1",
                 "-sample_fmt", "s16", str(out)],
                capture_output=True, timeout=15,
            )
            if out.exists():
                import base64
                return base64.b64encode(out.read_bytes()).decode()
    except Exception as e:
        print(f"  ⚠ TTS: {e}")
    return None


# ── API ───────────────────────────────────────────────────────────────────────


class AskRequest(BaseModel):
    question: str
    history: str = ""


@app.post("/ask")
def ask(req: AskRequest) -> dict:
    if not req.question.strip():
        raise HTTPException(400, "Пустой вопрос")
    answer = angela_answer(req.question, req.history)
    audio_b64 = generate_tts(answer)
    return {"answer": answer, "audio_b64": audio_b64 or ""}


@app.get("/ask-form")
def ask_form(question: str = "") -> HTMLResponse:
    """No-JS fallback: returns an HTML page with answer and audio player."""
    q = question.strip()
    if not q:
        return HTMLResponse("<p>Пустой вопрос</p><a href='/'>Назад</a>")
    answer = angela_answer(q)
    audio_b64 = generate_tts(answer)
    audio_html = ""
    if audio_b64:
        audio_html = f'<audio controls src="data:audio/wav;base64,{audio_b64}"></audio>'
    body = (
        f"<h2>Вопрос: {html_module.escape(q)}</h2>"
        f"<h3>Angela: {html_module.escape(answer)}</h3>"
        f"<p>{audio_html or 'Аудио не сгенерировано'}</p>"
        f"<p><a href='/'>Задать ещё вопрос</a></p>"
    )
    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="UTF-8"><title>Angela ответила</title></head>
<body>{body}</body></html>""")


# ── Frontend ───────────────────────────────────────────────────────────────────


HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Voice Angela — тест</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f0f2f5; min-height: 100vh;
  display: flex; justify-content: center; padding: 20px;
}
.container { max-width: 640px; width: 100%; }
h1 { font-size: 22px; margin: 20px 0; color: #1a1a2e; }
.status { font-size: 13px; color: #666; margin-bottom: 12px; }
.chat {
  background: white; border-radius: 16px; box-shadow: 0 2px 12px rgba(0,0,0,.08);
  padding: 20px; margin-bottom: 16px; min-height: 300px; max-height: 60vh;
  overflow-y: auto;
}
.msg { margin-bottom: 16px; display: flex; }
.msg.client { justify-content: flex-end; }
.msg.client .bubble { background: #e3f2fd; border-radius: 16px 16px 4px 16px; }
.msg.angela .bubble { background: #f5f5f5; border-radius: 16px 16px 16px 4px; }
.bubble { max-width: 80%; padding: 12px 16px; font-size: 15px; line-height: 1.4; }
.bubble small { display: block; font-size: 11px; color: #999; margin-top: 4px; }
.quick { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
.quick button {
  padding: 8px 14px; background: #fff; color: #1976d2; border: 1px solid #1976d2;
  border-radius: 8px; font-size: 13px; cursor: pointer;
}
.quick button.reset { background: #ff7043; color: #fff; border-color: #ff7043; }
.controls { display: flex; gap: 8px; }
input {
  flex: 1; padding: 12px 16px; border: 1px solid #ddd; border-radius: 12px;
  font-size: 15px; outline: none;
}
input:focus { border-color: #1976d2; }
button[type=submit] {
  padding: 12px 24px; background: #1976d2; color: white; border: none;
  border-radius: 12px; font-size: 15px; cursor: pointer;
}
button:disabled { opacity: .6; }
button:active { transform: scale(.97); }
.waiting { color: #999; font-style: italic; padding: 8px 0; }
</style>
</head>
<body>
<div class="container">
<h1>Voice Angela — тестовый диалог</h1>
<div class="status">Сервер готов. Голос на Mac: Milena (на VPS будет Kore).</div>
<div class="chat" id="chat">
  <div class="msg angela">
    <div class="bubble">
      Привет! Я Анжела, ассистент ВезёмЦыплят. Спрашивай о ценах, породах, доставке!
      <small>Анжела</small>
    </div>
  </div>
</div>
<div class="quick">
  <button type="button" onclick="setQ('Сколько стоят бройлеры?')">Бройлеры</button>
  <button type="button" onclick="setQ('Какие породы кур есть?')">Породы</button>
  <button type="button" onclick="setQ('Расскажи про доставку')">Доставка</button>
  <button type="button" onclick="setQ('Соедините с оператором')">Оператор</button>
  <button type="button" onclick="setQ('Есть ли инкубационное яйцо?')">Яйцо</button>
  <button type="button" class="reset" onclick="resetChat()">Сбросить диалог</button>
</div>
<form id="chat-form" action="/ask-form" method="get">
  <div class="controls">
    <input id="input" name="question" placeholder="Например: сколько стоят бройлеры?" autofocus>
    <button type="submit" id="send">Отправить</button>
  </div>
</form>
</div>
<script>
var chat = document.getElementById('chat');
var input = document.getElementById('input');
var send = document.getElementById('send');
var form = document.getElementById('chat-form');
var history = '';

function addMsg(text, role, audio) {
  var div = document.createElement('div');
  div.className = 'msg ' + role;
  div.innerHTML = '<div class="bubble">' + text + '<small>' + (role === 'angela' ? 'Анжела' : 'Вы') + '</small></div>';
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  if (audio) {
    var audioEl = new Audio('data:audio/wav;base64,' + audio);
    audioEl.play();
  }
}

function ask() {
  var q = input.value.trim();
  if (!q) return false;
  addMsg(escapeHtml(q), 'client');
  input.value = '';
  send.disabled = true;

  var wait = document.createElement('div');
  wait.className = 'waiting';
  wait.id = 'waiting';
  wait.textContent = 'Анжела думает...';
  chat.appendChild(wait);
  chat.scrollTop = chat.scrollHeight;

  fetch('/ask', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({question: q, history: history})
  })
  .then(function(r) { return r.json(); })
  .then(function(data) {
    var waitingEl = document.getElementById('waiting');
    if (waitingEl) waitingEl.remove();
    if (data.answer) {
      addMsg(escapeHtml(data.answer), 'angela', data.audio_b64);
      history += 'Клиент: ' + q + '\nАнжела: ' + data.answer + '\n';
      if (history.length > 3000) history = history.slice(-2500);
    }
    send.disabled = false;
    input.focus();
  })
  .catch(function(e) {
    console.error('Voice Angela error:', e);
    var waitingEl = document.getElementById('waiting');
    if (waitingEl) waitingEl.remove();
    addMsg('Ошибка соединения', 'angela');
    send.disabled = false;
    input.focus();
  });
  return false;
}

function escapeHtml(t) {
  return t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function setQ(q) {
  input.value = q;
  ask();
}

function resetChat() {
  chat.innerHTML = '<div class="msg angela"><div class="bubble">Привет! Я Анжела, ассистент ВезёмЦыплят. Спрашивай о ценах, породах, доставке!<small>Анжела</small></div></div>';
  history = '';
  input.focus();
}

form.addEventListener('submit', function(e) {
  e.preventDefault();
  ask();
});
</script>
</body>
</html>"""


@app.get("/")
def index() -> HTMLResponse:
    return HTMLResponse(HTML)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9090)
