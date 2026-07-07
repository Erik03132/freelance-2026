import subprocess, os, json, hashlib, time, requests

# Clean proxy
for p in list(os.environ.keys()):
    if "proxy" in p.lower() or "PROXY" in p:
        os.environ.pop(p, None)

# 1. Generate TTS greeting
text = (
    "Здравствуйте. Это Анжела, ассистент компании ВезёмЦыплят из Азова. "
    "У нас сейчас отличная акция на индюков и бройлеров. "
    "Расскажите, что вас интересует - породы, цены, доставка."
)
print("Generating TTS...")
subprocess.run(['edge-tts','--voice','ru-RU-SvetlanaNeural','--text',text,
    '--write-media','/tmp/angela_greeting.mp3'], capture_output=True, timeout=15)
subprocess.run(['ffmpeg','-y','-i','/tmp/angela_greeting.mp3',
    '-ar','8000','-ac','1','-sample_fmt','s16','/tmp/angela_greeting.wav'],
    capture_output=True, timeout=10)
print('Size:', os.path.getsize('/tmp/angela_greeting.wav'), 'bytes')

# 2. Upload to Mango
from dotenv import load_dotenv
load_dotenv("/root/antigravity/ai-eggs/.env")
k = os.getenv("MANGO_VPBX_API_KEY","")
s = os.getenv("MANGO_VPBX_API_SALT","")

ts = int(time.time() * 1000)
sign = hashlib.sha256((k + str(ts) + s).encode()).hexdigest()

with open("/tmp/angela_greeting.wav", "rb") as f:
    r = requests.post("https://app.mango-office.ru/vpbx/uploads/upload",
        data={"vpbx_api_key": k, "timestamp": str(ts), "sign": sign},
        files={"file": ("angela_greeting.wav", f, "audio/wav")},
        timeout=30)
print("Upload:", r.status_code, r.text[:300])

data = r.json() if r.text else {}
aid = data.get("audi_file_id", "") or data.get("audio_id", "") or data.get("id", "")
print("Audio ID:", aid)

# Save to env
with open("/root/antigravity/ai-eggs/.env", "r") as fe:
    env = fe.read()
if "ANGELA_GREETING_AUDIO_ID" not in env:
    env += f"\nANGELA_GREETING_AUDIO_ID={aid}\n"
    with open("/root/antigravity/ai-eggs/.env", "w") as fe:
        fe.write(env)
print("Saved ANGELA_GREETING_AUDIO_ID=" + aid)
