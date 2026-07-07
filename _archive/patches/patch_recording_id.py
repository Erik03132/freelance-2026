import re
path = "/opt/mango_webhook.py"
with open(path) as f:
    c = f.read()

old = '        # Also log call disconnect\n        if call_id and call_state in ("Disconnected", "Failed"):\n            _write_voice_event({\n                "type": "call_end",\n                "call_id": call_id,\n                "timestamp": datetime.now().isoformat(),\n            })'

new = '        # Also log call disconnect\n        if call_id and call_state in ("Disconnected", "Failed"):\n            _write_voice_event({\n                "type": "call_end",\n                "call_id": call_id,\n                "timestamp": datetime.now().isoformat(),\n            })\n\n        # Capture recording_id for post-call analysis\n        if path == "events/events/record/added":\n            rec_id = data.get("recording_id", "") or data.get("record_id", "") or entry_id\n            if rec_id and rec_id != "?":\n                _write_voice_event({\n                    "type": "recording_added",\n                    "recording_id": str(rec_id),\n                    "call_id": call_id or command_id or "",\n                    "timestamp": datetime.now().isoformat(),\n                })'

if old in c:
    c = c.replace(old, new)
    with open(path, "w") as f:
        f.write(c)
    print("recording_id capture added")
else:
    print("NOT FOUND, searching...")
    idx = c.find("Also log call disconnect")
    if idx >= 0:
        print(repr(c[idx:idx+400]))
