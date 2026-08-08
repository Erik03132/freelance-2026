#!/bin/bash
# Levitan Voice Agent — one-shot deploy on clean Ubuntu 22.04
# Usage: bash deploy.sh
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; NC='\033[0m'
log() { echo -e "${GREEN}[DEPLOY]${NC} $*"; }
err() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ============ CONFIG ============
LIVEKIT_VERSION="1.13.4"
LIVEKIT_SIP_VERSION="1.9.0"
LIVEKIT_SIP_DEV_BACKUP_URL=""  # если есть URL к dev-билду, указать
OPENROUTER_KEY="<YOUR_OPENROUTER_KEY>"
OPENROUTER_MODEL="google/gemini-2.5-flash-lite:free"
YC_API_KEY="<YOUR_YC_API_KEY>"
YC_FOLDER_ID="<YOUR_YC_FOLDER_ID>"
DEEPGRAM_KEY="<YOUR_DEEPGRAM_KEY>"
MANGO_API_KEY="<YOUR_MANGO_VPBX_API_KEY>"  # gitleaks:allow
MANGO_API_SALT="<YOUR_MANGO_VPBX_API_SALT>"
LLM_PROXY="<YOUR_LLM_PROXY>"
LIVEKIT_HTTP="http://localhost:7880"
LIVEKIT_WS="ws://localhost:7880"

log "=== Levitan Voice Agent Deploy ==="

# ============ SYSTEM DEPS ============
log "Installing system packages..."
apt-get update -qq
apt-get install -y -qq \
  curl wget git build-essential python3 python3-pip python3-venv \
  redis-server jq netcat-openbsd unzip \
  libssl-dev libopus0 libopus-dev || err "apt failed"

# ============ LIVEKIT SERVER ============
if [ ! -f /usr/local/bin/livekit-server ]; then
  log "Installing LiveKit Server v${LIVEKIT_VERSION}..."
  LIVEKIT_URL="https://github.com/livekit/livekit/releases/download/v${LIVEKIT_VERSION}/livekit_${LIVEKIT_VERSION}_linux_amd64.tar.gz"
  curl -sL "$LIVEKIT_URL" | tar xz -C /usr/local/bin livekit-server || err "livekit download failed"
  chmod +x /usr/local/bin/livekit-server
fi

# ============ LIVEKIT SIP ============
if [ ! -f /usr/local/bin/livekit-sip ]; then
  log "Installing LiveKit SIP v${LIVEKIT_SIP_VERSION}..."
  SIP_URL="https://github.com/livekit/sip/releases/download/v${LIVEKIT_SIP_VERSION}/livekit-sip_${LIVEKIT_SIP_VERSION}_linux_amd64.tar.gz"
  curl -sL "$SIP_URL" | tar xz -C /usr/local/bin livekit-sip || err "sip download failed"
  chmod +x /usr/local/bin/livekit-sip
fi

# ============ REDIS ============
systemctl enable --now redis-server 2>/dev/null || true

# ============ DIRECTORIES ============
mkdir -p /opt/livekit /opt/pipecat-agent /opt/pipecat-agent/docs /var/log/levitan/calls

# ============ LIVEKIT CONFIG ============
log "Writing LiveKit config..."
cat > /opt/livekit/livekit.yaml <<'YAML'
port: 7880
bind_addresses:
  - "0.0.0.0"
rtc:
  port_range_start: 50000
  port_range_end: 60000
  use_external_ip: true
keys:
  devkey: secret
redis:
  address: localhost:6379
logging:
  level: info
  json: false
YAML

cat > /opt/livekit/sip.yaml <<'YAML'
api_key: devkey
api_secret: secret
ws_url: ws://localhost:7880
redis:
  address: localhost:6379
sip_port: 5060
rtp_port: 16384-32768
use_external_ip: true
logging:
  level: info
YAML

# ============ SYSTEMD: LIVEKIT SERVER ============
cat > /etc/systemd/system/livekit.service <<'UNIT'
[Unit]
Description=LiveKit Server
After=network.target redis-server.service
Requires=redis-server.service

[Service]
Type=simple
ExecStart=/usr/local/bin/livekit-server --config /opt/livekit/livekit.yaml
Restart=always
RestartSec=5
User=root
Group=root
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
UNIT

# ============ SYSTEMD: LIVEKIT SIP ============
cat > /etc/systemd/system/livekit-sip.service <<'UNIT'
[Unit]
Description=LiveKit SIP Bridge
After=network.target livekit.service
Requires=livekit.service

[Service]
Type=simple
ExecStart=/usr/local/bin/livekit-sip --config /opt/livekit/sip.yaml
Restart=always
RestartSec=5
User=root
Group=root

[Install]
WantedBy=multi-user.target
UNIT

# ============ .ENV ============
log "Writing .env..."
EXTERNAL_IP=$(curl -s ifconfig.me || echo "127.0.0.1")
cat > /opt/pipecat-agent/.env <<ENV
# LiveKit
LIVEKIT_URL=$LIVEKIT_WS

# LLM (OpenRouter)
OPENROUTER_API_KEY=$OPENROUTER_KEY
OPENROUTER_MODEL=$OPENROUTER_MODEL
LLM_BASE=https://openrouter.ai/api/v1
LLM_PROXY=$LLM_PROXY

# STT
DEEPGRAM_API_KEY=$DEEPGRAM_KEY

# Yandex TTS
YC_API_KEY=$YC_API_KEY
YC_FOLDER_ID=$YC_FOLDER_ID
TTS_VOICE=alena

# Mango Office
MANGO_VPBX_API_KEY=$MANGO_API_KEY
MANGO_VPBX_API_SALT=$MANGO_API_SALT

# Telegram
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# VPS
VPS_HOST=$EXTERNAL_IP
OMNIROUTE_MODEL=deepseek/deepseek-chat
LIVEKIT_LOG_LEVEL=debug
ENV

# ============ PYTHON VENV ============
log "Setting up Python venv..."
python3 -m venv /opt/pipecat-venv
/opt/pipecat-venv/bin/pip install --upgrade pip -q
/opt/pipecat-venv/bin/pip install -q \
  livekit-agents livekit-plugins-deepgram livekit-plugins-openai \
  aiohttp httpx python-dotenv requests || err "pip install failed"

# ============ LEVITAN AGENT ============
log "Writing levitan_agent.py..."
cat > /opt/pipecat-agent/levitan_agent.py <<'PYEOF'
"""
Levitan Real-time Voice Agent — Pipecat + LiveKit SIP
Анжелла: FAQ-кэш (fast path) + OpenRouter LLM + Yandex SpeechKit TTS
"""
import json
import logging
import os
import re
from contextlib import asynccontextmanager
from difflib import SequenceMatcher
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

import aiohttp
import httpx
from livekit import rtc
from livekit.agents import Agent, AgentSession, AgentServer, llm, tts
from livekit.agents.types import APIConnectOptions
from livekit.agents.worker import ServerOptions
from livekit.plugins import deepgram, openai
from openai import AsyncClient as OpenAIAsyncClient

LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")

LLM_BASE = os.getenv("LLM_BASE", "https://openrouter.ai/api/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek/deepseek-chat")
LLM_PROXY = os.getenv("LLM_PROXY", "")

YC_API_KEY = os.getenv("YC_API_KEY", "")
YC_FOLDER_ID = os.getenv("YC_FOLDER_ID", "")
TTS_VOICE = os.getenv("TTS_VOICE", "alena")

FAQ_CACHE_PATH = Path(__file__).resolve().parent / "docs" / "ANGELLA_BROILERS_FAQ_CACHE.json"
_faq_cache = {}


def load_faq_cache() -> None:
    global _faq_cache
    try:
        data = json.loads(FAQ_CACHE_PATH.read_text(encoding="utf-8"))
        _faq_cache = {k: v for k, v in data.items() if not k.startswith("_")}
        print(f"FAQ cache loaded: {len(_faq_cache)} triggers")
    except Exception as e:
        print(f"FAQ load error: {e}")


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[ёй]", lambda m: {"ё": "е", "й": "и"}.get(m.group(), m.group()), text)
    text = re.sub(r"[^а-я0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def faq_lookup(transcript_text: str) -> str | None:
    if not _faq_cache:
        return None
    norm = normalize(transcript_text)
    if len(norm) < 3:
        return None
    best_score, best_reply = 0.0, None
    for trigger, reply in _faq_cache.items():
        score = SequenceMatcher(None, norm, trigger).ratio()
        if score > best_score:
            best_score, best_reply = score, reply
    if best_score >= 0.72:
        return best_reply
    return None


@llm.function_tool
async def faq_lookup_tool(question: str) -> str:
    reply = faq_lookup(question)
    return reply if reply else "NOT_FOUND"


class DebugLLM(openai.LLM):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._chunk_count = 0

    async def _handle_chunk(self, chunk, *args, **kwargs):
        self._chunk_count += 1
        print(f"[LLM] chunk#{self._chunk_count}", flush=True)
        return await super()._handle_chunk(chunk, *args, **kwargs)


class YandexTTS(tts.TTS):
    def __init__(self, api_key: str, folder_id: str, voice: str = "alena", speed: float = 1.0):
        super().__init__(
            capabilities=tts.TTSCapabilities(streaming=False, aligned_transcript=False),
            sample_rate=48000,
            num_channels=1,
        )
        self._api_key = api_key
        self._folder_id = folder_id
        self._voice = voice
        self._speed = speed
        self._req_id = 0
        self._lead_done = False
        self._lead_sec = float(os.getenv("TTS_LEAD_SILENCE_SEC", "2.5"))

    @asynccontextmanager
    async def synthesize(self, text: str, *, conn_options: APIConnectOptions = None):
        import time as _t
        _t0 = _t.time()
        print(f"[TTS] START len={len(text)} text={text[:60]!r}", flush=True)
        if not text.strip():
            yield
            return
        request_id = str(self._req_id)
        self._req_id += 1
        form = aiohttp.FormData()
        form.add_field("text", text)
        form.add_field("folderId", self._folder_id)
        form.add_field("lang", "ru-RU")
        form.add_field("voice", self._voice)
        form.add_field("format", "lpcm")
        form.add_field("sampleRateHertz", "48000")
        form.add_field("speed", str(self._speed))
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize",
                headers={"Authorization": f"Api-Key {self._api_key}"},
                data=form,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                data = await resp.read()
                if resp.status != 200 or len(data) < 1000:
                    raise RuntimeError(f"Yandex TTS {resp.status}: {data[:200]}")
        print(f"[TTS] DONE {len(data)} bytes in {_t.time()-_t0:.1f}s", flush=True)
        if not self._lead_done and self._lead_sec > 0:
            self._lead_done = True
            lead_bytes = int(self._lead_sec * 48000) * 2
            data = b"\x00\x00" * (lead_bytes // 2) + data
            print(f"[TTS] lead-silence {self._lead_sec}s prepended (first synthesis)", flush=True)
        frame = rtc.AudioFrame(
            data=data,
            sample_rate=48000,
            num_channels=1,
            samples_per_channel=len(data) // 2,
        )

        async def _stream():
            yield tts.SynthesizedAudio(
                frame=frame,
                request_id=request_id,
                segment_id=request_id,
                is_final=True,
                delta_text=text,
            )

        yield _stream()


GREETING = "Здравствуйте! Предлагаем вам суточных цыплят Росс 308 по цене от 75 рублей за голову. Вам интересно?"

SYSTEM_PROMPT = """Голосовой менеджер Азовского инкубатора (IncuBird). Отвечаешь клиентам по телефону про суточных цыплят бройлеров.

КОМПАНИЯ: Азовский инкубатор, Крым, пгт Азовское, ул. Железнодорожная 42. Телефон +7 (918) 047-50-01.
Самовывоз — только Крым (Азовское, 14:00-17:00). В Москву самовывоза нет.
Доставка — по ПН и ЧТ по Крыму и Югу России (Краснодар, Ростов, Волгоград, Ставрополь), спецтранспорт с климат-контролем. Гарантия 100% выживаемости при доставке.
Оплата: наличные при получении, перевод на карту, по реквизитам. Предоплата 50%.

АССОРТИМЕНТ (июль-декабрь 2026 — ТОЛЬКО бройлеры):
— РОСС-308: от 75 руб/шт (до 100 голов), 101-300 — 85 руб. Выносливый, крепкий, для дома и новичков — рекомендуем его.
— КОББ-500: дороже Росс, самый быстрорастущий, до 2.5 кг за 40 дней, мощная грудка. Для бизнеса/откорма.
Минимальный заказ — от 50 голов одной породы. От 100 голов — индивидуальная скидка.
График вывода: каждый ПН и ЧТ.

ГРАФИК НА АВГУСТ:
Доступные даты вывода и записи: 1 августа, 15-18 августа, 25-28 августа.

Доставка по регионам. Сайт: incubird.ru"""


class LevitanAgent(Agent):
    def __init__(self) -> None:
        llm_client = None
        if LLM_PROXY:
            llm_client = OpenAIAsyncClient(
                api_key=os.getenv("OPENROUTER_API_KEY", "omni"),
                base_url=LLM_BASE,
                http_client=httpx.AsyncClient(
                    proxy=LLM_PROXY,
                    timeout=httpx.Timeout(30.0, connect=10.0),
                ),
            )
        super().__init__(
            instructions=SYSTEM_PROMPT,
            tools=[faq_lookup_tool],
            stt=deepgram.STT(model="nova-3", language="ru"),
            llm=DebugLLM(
                model=LLM_MODEL,
                api_key=os.getenv("OPENROUTER_API_KEY", "omni"),
                base_url=LLM_BASE,
                max_completion_tokens=512,
                temperature=0.3,
                client=llm_client,
            ),
            tts=YandexTTS(api_key=YC_API_KEY, folder_id=YC_FOLDER_ID, voice=TTS_VOICE),
        )

    async def on_enter(self):
        import asyncio
        import time as _t
        from livekit.agents.utils import wait_for_track_publication
        room = getattr(self, "rtc_room", None)
        if room is not None:
            try:
                for _ in range(30):
                    if room.isconnected():
                        break
                    await asyncio.sleep(0.5)
                if room.isconnected():
                    await asyncio.wait_for(
                        wait_for_track_publication(
                            room,
                            kind=rtc.TrackKind.KIND_AUDIO,
                            wait_for_subscription=True,
                        ),
                        timeout=25,
                    )
                    print("[AGENT] sip audio track ready", flush=True)
                    await asyncio.sleep(3.5)
                    print("[AGENT] media bridge settled, saying greeting", flush=True)
                else:
                    print("[AGENT] room never connected in 15s", flush=True)
            except Exception as e:
                print(f"[AGENT] track wait: {e}", flush=True)
        print(f"[AGENT] on_enter called, saying greeting", flush=True)
        _t0 = _t.time()
        await self.session.say(GREETING)
        print(f"[AGENT] greeting said in {_t.time()-_t0:.1f}s", flush=True)

    def _on_transcribed(self, ev) -> None:
        print(f"[STT] transcript={ev.transcript!r} final={ev.is_final}", flush=True)

    def _on_user_state(self, ev) -> None:
        print(f"[STT] user_state={ev.new_state}", flush=True)

    def _on_agent_state(self, ev) -> None:
        print(f"[STATE] agent={ev.new_state}", flush=True)

    def _on_item(self, ev) -> None:
        item = ev.item
        role = getattr(item, "role", "?")
        text = getattr(item, "text", "") or getattr(item, "raw_text_content", "") or ""
        print(f"[ITEM] {role}: {str(text)[:200]}", flush=True)

    def _on_error(self, ev) -> None:
        print(f"[ERROR] src={type(ev.source).__name__} err={ev.error!r}", flush=True)


async def entrypoint(ctx):
    load_faq_cache()
    agent = LevitanAgent()
    agent.rtc_room = ctx.room
    session = AgentSession()
    session.on("user_input_transcribed", agent._on_transcribed)
    session.on("user_state_changed", agent._on_user_state)
    session.on("agent_state_changed", agent._on_agent_state)
    session.on("conversation_item_added", agent._on_item)
    session.on("error", agent._on_error)
    await session.start(agent=agent, room=ctx.room)


opts = ServerOptions(
    entrypoint_fnc=entrypoint,
    ws_url=LIVEKIT_URL,
    api_key=LIVEKIT_API_KEY,
    api_secret=LIVEKIT_API_SECRET,
)
server = AgentServer.from_server_options(opts)

if __name__ == "__main__":
    server.run()
PYEOF

# ============ FAQ CACHE (empty placeholder) ============
cat > /opt/pipecat-agent/docs/ANGELLA_BROILERS_FAQ_CACHE.json <<'JSON'
{
  "_comment": "FAQ triggers for Levitan — fill with actual Q&A pairs",
  "сколько стоит цыпленок": "Цыплята РОСС-308 от 75 рублей за голову при заказе до 100 штук. При заказе от 101 до 300 голов — 85 рублей. Минимальный заказ — 50 голов.",
  "какая цена": "Цыплята РОСС-308 от 75 рублей за голову при заказе до 100 штук. Точная цена зависит от объёма заказа. Уточните, сколько голов вас интересует?",
  "доставка": "Доставка осуществляется по ПН и ЧТ по Крыму и Югу России — Краснодар, Ростов, Волгоград, Ставрополь. Транспорт с климат-контролем, гарантия 100% выживаемости.",
  "самовывоз": "Самовывоз возможен из пгт Азовское, Крым, с 14:00 до 17:00. В Москву самовывоза нет.",
  "график вывода": "График вывода цыплят — каждый понедельник и четверг."
}
JSON

# ============ SYSTEMD: LEVITAN AGENT ============
cat > /etc/systemd/system/levitan-agent.service <<'UNIT'
[Unit]
Description=Levitan Voice Agent (Pipecat + LiveKit)
After=network.target livekit.service livekit-sip.service
Requires=livekit.service

[Service]
Type=simple
WorkingDirectory=/opt/pipecat-agent
ExecStart=/opt/pipecat-venv/bin/python3 -m livekit.agents start levitan_agent.py
Restart=always
RestartSec=5
User=root
Group=root
Environment="PATH=/opt/pipecat-venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/opt/pipecat-agent/.env

[Install]
WantedBy=multi-user.target
UNIT

# ============ ENABLE & START ============
systemctl daemon-reload

log "Starting LiveKit Server..."
systemctl enable --now livekit
sleep 3

log "Starting LiveKit SIP..."
systemctl enable --now livekit-sip
sleep 2

log "Starting Levitan Agent..."
systemctl enable --now levitan-agent
sleep 3

# ============ SIP TRUNK + DISPATCH ============
log "Creating SIP trunk and dispatch rule..."
sleep 5  # wait for agent worker registration

TOKEN=$(/opt/pipecat-venv/bin/python3 -c "from livekit import api; print(api.AccessToken('devkey','secret').with_grants(api.VideoGrants(room_admin=True)).to_jwt())" 2>/dev/null)

# Create inbound trunk (no auth, allow Mango IPs: 81.88.86.11 = mangosip.ru, 10.170.19.206)
curl -sf -X POST "$LIVEKIT_HTTP/twirp/livekit.SIP/CreateSIPInboundTrunk" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"mango-inbound","numbers":["78612025110"],"allowed_numbers":["78612025110"],"allowed_addresses":["81.88.86.11","10.170.19.206"]}' \
  2>/dev/null && log "SIP trunk created" || log "SIP trunk may already exist"

# Create/update dispatch rule with trunk_ids (mandatory: rule without trunk_ids
# does NOT match user4 INVs. Write directly to Redis via protobuf, since Twirp
# List/Delete/Get SIPDispatchRule endpoints require admin perms not available here.)
/opt/pipecat-venv/bin/python3 - <<'EOF'
import subprocess
from livekit.protocol import sip as sp
trunks = subprocess.run(["redis-cli", "hkeys", "sip_inbound_trunk"], capture_output=True, text=True).stdout.split()
if not trunks:
    print("No trunks found in Redis, dispatch rule NOT updated")
    raise SystemExit(0)
info = sp.SIPDispatchRuleInfo()
info.sip_dispatch_rule_id = "SDR_levitan-inbound"
info.name = "levitan-inbound"
info.rule.dispatch_rule_individual.room_prefix = "levitan-sip-"
info.rule.dispatch_rule_individual.no_randomness = True
for t in trunks:
    if t not in info.trunk_ids:
        info.trunk_ids.append(t)
payload = info.SerializeToString()
p = subprocess.run(["redis-cli", "-x", "hset", "sip_dispatch_rule", info.sip_dispatch_rule_id], input=payload, capture_output=True)
print(f"Dispatch rule {info.sip_dispatch_rule_id} updated with trunks {trunks}, rc={p.returncode}")
EOF

# ============ UFW ============
log "Configuring firewall..."
ufw allow 22/tcp
ufw allow 7880/tcp
ufw allow 5060/udp
ufw allow 16384:32768/udp
ufw --force enable 2>/dev/null || true

# ============ STATUS ============
echo ""
log "=== DEPLOY COMPLETE ==="
echo "  LiveKit:  $(systemctl is-active livekit)"
echo "  SIP:      $(systemctl is-active livekit-sip)"
echo "  Agent:    $(systemctl is-active levitan-agent)"
echo "  External IP: $EXTERNAL_IP"
echo ""
echo "Test call: cd /opt/pipecat-agent && source .env && python3 -c \""
echo "  import hashlib,json,uuid,httpx"
echo "  c='test_'+uuid.uuid4().hex[:8]"
echo "  p={'command_id':c,'from':{'extension':'22'},'to_number':'+79859234644','timeout':30}"
echo "  j=json.dumps(p,separators=(',',':'),ensure_ascii=False)"
echo "  s=hashlib.sha256((MANGO_VPBX_API_KEY+j+MANGO_VPBX_API_SALT).encode()).hexdigest()"
echo "  r=httpx.post('https://app.mango-office.ru/vpbx/commands/callback',data={'vpbx_api_key':MANGO_VPBX_API_KEY,'json':j,'sign':s},timeout=20)"
echo "  print(r.text)"
echo "\""
