#!/usr/bin/env python3
import sqlite3, json, sys, datetime
db="/root/.omniroute/storage.sqlite"
OR_KEY = sys.argv[1]
OMNI_KEY = "sk-e354fcd9a30fe0d8-88ee41-9b57cccd"
with open("/root/combos_vps.json") as f:
    combos = json.load(f)
con=sqlite3.connect(db); con.execute("PRAGMA busy_timeout=15000"); c=con.cursor()
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
for name, d in combos.items():
    blob=d.get("data","")
    sysmsg=d.get("system_message","") or ""
    tfr=d.get("tool_filter_regex","") or ""
    ccp=d.get("context_cache_protection",0)
    if name in existing:
        c.execute("UPDATE combos SET data=?, system_message=?, tool_filter_regex=?, context_cache_protection=? WHERE name=?",(blob,sysmsg,tfr,ccp,name))
        print("updated combo",name)
    else:
        cid=name.replace('/','_')+'-'+str(abs(hash(name))%100000)
        c.execute("""INSERT INTO combos (id,name,data,sort_order,created_at,updated_at,system_message,tool_filter_regex,context_cache_protection)
                     VALUES (?,?,?,0,datetime('now'),datetime('now'),?,?,?)""",(cid,name,blob,sysmsg,tfr,ccp))
        print("inserted combo",name)
con.commit(); con.close()
print("DB write OK")
