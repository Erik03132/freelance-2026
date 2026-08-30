#!/bin/bash
# OmniRoute combo guard: backs up combos to JSON, restores if DB empty.
# Idempotent, no-op safe. Run by launchd every 5 min + at load.
set -u

DB="$HOME/.omniroute/storage.sqlite"
BACKUP="$HOME/freelance-2026/omniroute_combos.json"
PORT=20128

# Wait for OmniRoute to be up (max 30s)
for i in $(seq 1 30); do
  if lsof -nP -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; then break; fi
  sleep 1
done

if ! lsof -nP -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; then
  # OmniRoute not running — nothing to guard
  exit 0
fi

if [ ! -f "$DB" ]; then exit 0; fi

COUNT=$(sqlite3 "$DB" "SELECT COUNT(*) FROM combos;" 2>/dev/null || echo 0)

if [ "$COUNT" -gt 0 ]; then
  # DB has combos -> refresh backup (capture user's latest web edits)
  python3 - "$DB" "$BACKUP" <<'PY'
import sys, json, sqlite3
db, out = sys.argv[1], sys.argv[2]
conn = sqlite3.connect(db)
rows = conn.execute("SELECT id, name, data, system_message, tool_filter_regex, context_cache_protection FROM combos").fetchall()
data = {}
for r in rows:
    cid, name, cdata, sm, tfr, ccp = r
    data[name] = {
        "id": cid,
        "data": cdata,
        "system_message": sm,
        "tool_filter_regex": tfr,
        "context_cache_protection": ccp or 0,
    }
conn.close()
with open(out, "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"BACKUP: wrote {len(data)} combos to {out}")
PY
else
  # DB empty -> restore from last backup if present
  if [ -f "$BACKUP" ]; then
    python3 - "$DB" "$BACKUP" <<'PY'
import sys, json, sqlite3
db, src = sys.argv[1], sys.argv[2]
with open(src) as f:
    combos = json.load(f)
if not combos:
    print("RESTORE: backup empty, nothing to do")
    sys.exit(0)
import datetime
now = datetime.datetime.utcnow().isoformat() + "Z"
conn = sqlite3.connect(db)
cur = conn.cursor()
n = 0
for name, obj in combos.items():
    cur.execute(
        "INSERT OR REPLACE INTO combos (id, name, data, sort_order, created_at, updated_at) VALUES (?,?,?,?,?,?)",
        (obj.get("id"), name, obj.get("data"), n, now, now)
    )
    n += 1
conn.commit()
conn.close()
print(f"RESTORE: recovered {n} combos from {src}")
PY
  else
    echo "GUARD: DB empty, no backup found — nothing to restore"
  fi
fi
