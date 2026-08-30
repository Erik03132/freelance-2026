#!/usr/bin/env bash
set -u
LOG=/root/omni_fix.log
exec > "$LOG" 2>&1
echo "=== FIX START $(date -u) ==="

# 1. Stop service + kill orphans (free port 20128)
systemctl stop omniroute.service || true
sleep 2
pkill -9 -f "omniroute/bin/omniroute.mjs" 2>/dev/null || true
pkill -9 -f "omniroute (v16" 2>/dev/null || true
sleep 3
echo "--- ports after kill ---"
(ss -ltnp 2>/dev/null | grep -E "2012|2013") || echo "PORTS FREE"

# 2. Read OpenRouter key from levitan .env (plaintext)
OR_KEY=""
if [ -r /opt/levitan/projects/levitan/.env ]; then
  OR_KEY=$(grep -E "^OPENROUTER_API_KEY=" /opt/levitan/projects/levitan/.env | head -1 | cut -d= -f2-)
fi
echo "OR_KEY len: ${#OR_KEY}"
if [ -z "$OR_KEY" ]; then echo "FATAL: no OpenRouter key in levitan .env"; fi

# 3. Write to VPS sqlite
python3 - <<PY
import sqlite3, json, datetime
db="/root/.omniroute/storage.sqlite"
OR_KEY = '${OR_KEY}'
OMNI_KEY = "sk-e354fcd9a30fe0d8-88ee41-9b57cccd"
combos = json.loads("{\"auto/super-free\": {\"id\": \"9fe79065-aa9f-45dd-8527-2605d886526e\", \"data\": \"{\\\"name\\\": \\\"auto/super-free\\\", \\\"description\\\": \\\"\\\\u041c\\\\u0415\\\\u0413\\\\u0410-\\\\u041f\\\\u0423\\\\u041b 100% \\\\u0411\\\\u0415\\\\u0421\\\\u041f\\\\u041b\\\\u0410\\\\u0422\\\\u041d\\\\u042b\\\\u0425 \\\\u041c\\\\u041e\\\\u0414\\\\u0415\\\\u041b\\\\u0415\\\\u0419 (22 \\\\u043c\\\\u043e\\\\u0434\\\\u0435\\\\u043b\\\\u0435\\\\u0439): OpenCode + OpenRouter :free + DuckDuckGo + Zen/TLLM\\\", \\\"strategy\\\": \\\"priority\\\", \\\"models\\\": [\\\"oc/deepseek-v4-flash-free\\\", \\\"oc/mimo-v2.5-free\\\", \\\"oc/nemotron-3-ultra-free\\\", \\\"oc/hy3-free\\\", \\\"oc/north-mini-code-free\\\", \\\"oc/big-pickle\\\", \\\"ddgw/gpt-5.4-mini\\\", \\\"ddgw/gpt-5.4-nano\\\", \\\"ddgw/claude-haiku-4-5\\\", \\\"ddgw/mistral-small-2603\\\", \\\"ddgw/tinfoil/gpt-oss-120b\\\", \\\"ddgw/tinfoil/gemma4-31b\\\", \\\"tllm/gemini_3_flash\\\", \\\"tllm/gemini_2_5_pro\\\", \\\"tllm/gemini_2_0_flash\\\", \\\"tllm/CLAUDE_4_6_SONNET\\\", \\\"tllm/CLAUDE_4_5_HAIKU\\\", \\\"tllm/together_deepseek_v3\\\", \\\"tllm/openrouter_deepseek_r1\\\", \\\"tllm/GPT_5_4\\\", \\\"tllm/GPT_o4_mini\\\", \\\"tllm/sonar-pro\\\"], \\\"is_active\\\": true}\", \"system_message\": null, \"tool_filter_regex\": null, \"context_cache_protection\": 0}, \"auto/free-coding\": {\"id\": \"f9e695de-65d4-4133-9f7b-fd7e4ef1c21c\", \"data\": \"{\\\"name\\\": \\\"auto/free-coding\\\", \\\"description\\\": \\\"\\\\u0411\\\\u0435\\\\u0441\\\\u043f\\\\u043b\\\\u0430\\\\u0442\\\\u043d\\\\u044b\\\\u0439 \\\\u043f\\\\u0443\\\\u043b \\\\u0441\\\\u043f\\\\u0435\\\\u0446\\\\u0438\\\\u0430\\\\u043b\\\\u044c\\\\u043d\\\\u043e \\\\u0434\\\\u043b\\\\u044f \\\\u041a\\\\u041e\\\\u0414\\\\u0410: DeepSeek V4, Nemotron 3 Ultra, Qwen 2.5 Coder, MiMo\\\", \\\"strategy\\\": \\\"priority\\\", \\\"models\\\": [\\\"oc/deepseek-v4-flash-free\\\", \\\"oc/nemotron-3-ultra-free\\\", \\\"openrouter/nvidia/nemotron-3-ultra-550b-a55b:free\\\", \\\"openrouter/nvidia/nemotron-3.5-lightning:free\\\", \\\"oc/mimo-v2.5-free\\\", \\\"openrouter/cohere/north-mini-code:free\\\", \\\"openrouter/poolside/laguna-s-2.1:free\\\", \\\"openrouter/openai/gpt-oss-20b:free\\\", \\\"tllm/CLAUDE_4_6_SONNET\\\", \\\"tllm/together_deepseek_v3\\\"], \\\"is_active\\\": true}\", \"system_message\": null, \"tool_filter_regex\": null, \"context_cache_protection\": 0}, \"auto/free-chat\": {\"id\": \"43e7fc4a-b76c-4a14-a1eb-4abe3ef33c44\", \"data\": \"{\\\"name\\\": \\\"auto/free-chat\\\", \\\"description\\\": \\\"\\\\u0411\\\\u0435\\\\u0441\\\\u043f\\\\u043b\\\\u0430\\\\u0442\\\\u043d\\\\u044b\\\\u0439 \\\\u043f\\\\u0443\\\\u043b \\\\u0434\\\\u043b\\\\u044f \\\\u0411\\\\u042b\\\\u0421\\\\u0422\\\\u0420\\\\u041e\\\\u0413\\\\u041e \\\\u041e\\\\u0411\\\\u0429\\\\u0415\\\\u041d\\\\u0418\\\\u042f \\\\u0438 \\\\u043f\\\\u043e\\\\u0438\\\\u0441\\\\u043a\\\\u0430: DuckDuckGo, Gemma, Llama, Gemini\\\", \\\"strategy\\\": \\\"priority\\\", \\\"models\\\": [\\\"ddgw/gpt-5.4-mini\\\", \\\"ddgw/claude-haiku-4-5\\\", \\\"ddgw/mistral-small-2603\\\", \\\"openrouter/google/gemma-4-31b-it:free\\\", \\\"openrouter/google/gemma-4-26b-a4b-it:free\\\", \\\"tllm/gemini_3_flash\\\", \\\"tllm/gemini_2_0_flash\\\", \\\"tllm/sonar-pro\\\", \\\"oc/hy3-free\\\"], \\\"is_active\\\": true}\", \"system_message\": null, \"tool_filter_regex\": null, \"context_cache_protection\": 0}, \"auto/free-reasoning\": {\"id\": \"c45546f3-0310-45bd-ab43-41c7fa1bdb25\", \"data\": \"{\\\"name\\\": \\\"auto/free-reasoning\\\", \\\"description\\\": \\\"\\\\u0411\\\\u0435\\\\u0441\\\\u043f\\\\u043b\\\\u0430\\\\u0442\\\\u043d\\\\u044b\\\\u0439 \\\\u043f\\\\u0443\\\\u043b \\\\u0434\\\\u043b\\\\u044f \\\\u0421\\\\u041b\\\\u041e\\\\u0416\\\\u041d\\\\u042b\\\\u0425 \\\\u0420\\\\u0410\\\\u0421\\\\u0421\\\\u0423\\\\u0416\\\\u0414\\\\u0415\\\\u041d\\\\u0418\\\\u0419: DeepSeek R1, Nemotron Reasoning, GLM\\\", \\\"strategy\\\": \\\"priority\\\", \\\"models\\\": [\\\"tllm/openrouter_deepseek_r1\\\", \\\"openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free\\\", \\\"openrouter/z-ai/glm-5.2:free\\\", \\\"openrouter/liquid/lfm-2.5-2.6b:free\\\", \\\"ddgw/tinfoil/gpt-oss-120b\\\", \\\"tllm/GPT_5_4\\\"], \\\"is_active\\\": true}\", \"system_message\": null, \"tool_filter_regex\": null, \"context_cache_protection\": 0}}")
con=sqlite3.connect(db); con.execute("PRAGMA busy_timeout=10000"); c=con.cursor()
c.execute("SELECT id FROM provider_connections WHERE provider='openrouter'")
if c.fetchone():
    c.execute("UPDATE provider_connections SET api_key=?, is_active=1 WHERE provider='openrouter'", (OR_KEY,))
    print("updated openrouter connection")
else:
    c.execute("""INSERT INTO provider_connections (id,provider,auth_type,name,email,priority,is_active,display_name,default_model,api_key)
                 VALUES ('openrouter-001','openrouter','api_key','OpenRouter','','0',1,'OpenRouter','auto/free-coding',?)""", (OR_KEY,))
    print("inserted openrouter connection")
con.commit()
c.execute("SELECT id FROM api_keys WHERE name='Hermes'")
if not c.fetchone():
    c.execute("""INSERT INTO api_keys (id,name,key,machine_id,allowed_models,no_log,created_at,revoked_at,is_active,auto_resolve)
                 VALUES ('hermes-001','Hermes',?, 'mac','*',0, datetime('now'), NULL, 1, 1)""", (OMNI_KEY,))
    print("inserted Hermes api_key")
else:
    c.execute("UPDATE api_keys SET key=?, is_active=1 WHERE name='Hermes'", (OMNI_KEY,))
    print("updated Hermes api_key")
con.commit()
c.execute("SELECT name FROM combos")
existing={r[0] for r in c.execute("SELECT name FROM combos").fetchall()}
for name, data in combos.items():
    d = data if isinstance(data, dict) else {}
    blob = d.get('data','')
    sysmsg = d.get('system_message','') or ''
    tfr = d.get('tool_filter_regex','') or ''
    ccp = d.get('context_cache_protection', 0)
    if name in existing:
        c.execute("UPDATE combos SET data=?, system_message=?, tool_filter_regex=?, context_cache_protection=? WHERE name=?", (blob,sysmsg,tfr,ccp,name))
        print("updated combo", name)
    else:
        cid = name.replace('/','_')+'-'+str(abs(hash(name))%100000)
        c.execute("""INSERT INTO combos (id,name,data,sort_order,created_at,updated_at,system_message,tool_filter_regex,context_cache_protection)
                     VALUES (?,?,?,0,datetime('now'),datetime('now'),?,?,?)""", (cid,name,blob,sysmsg,tfr,ccp))
        print("inserted combo", name)
con.commit(); con.close()
print("DB write done")
PY

# 4. Start service
systemctl start omniroute.service || true
echo "--- waiting for port ---"
up=0
for i in $(seq 1 45); do
  code=$(curl --noproxy "*" -s -o /dev/null -w "%{http_code}" --max-time 4 http://127.0.0.1:20128/ 2>/dev/null)
  if [ -n "$code" ] && [ "$code" != "000" ]; then up=1; echo "PORT ALIVE try=$i code=$code"; break; fi
  sleep 2
done
[ "$up" = "0" ] && echo "PORT NEVER CAME UP"

KEY=$(python3 -c "import sqlite3;print(sqlite3.connect('/root/.omniroute/storage.sqlite').execute(\"SELECT key FROM api_keys WHERE name='Hermes'\").fetchone()[0] or '')" 2>/dev/null)
echo "omni_key_present=$([ -n "$KEY" ] && echo yes || echo NO)"

echo "=== TEST /v1/chat auto/free-coding ==="
curl --noproxy "*" -s -w "\nHTTP=%{http_code}\n" --max-time 90 -X POST http://127.0.0.1:20128/v1/chat/completions \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"model":"auto/free-coding","messages":[{"role":"user","content":"ping"}],"max_tokens":50}' | head -c 2000
echo
echo "=== TEST /v1/models ==="
curl --noproxy "*" -s -o /dev/null -w "models_http=%{http_code}\n" --max-time 15 -H "Authorization: Bearer $KEY" http://127.0.0.1:20128/v1/models
echo "=== FIX END $(date -u) ==="
