#!/usr/bin/env python3
path = "/opt/mango_webhook.py"
with open(path, "r") as f:
    content = f.read()

old = '        dtmf = data.get("dtmf")\n        if dtmf is not None:\n            _forward_dtmf(\n                data.get("call_id", ""),\n                str(dtmf),\n                command_id,\n                str(entry_id),\n            )'

new = '        dtmf = data.get("dtmf")\n        if dtmf is not None:\n            _forward_dtmf(\n                data.get("call_id", ""),\n                str(dtmf),\n                command_id,\n                str(entry_id),\n            )\n            _write_voice_event({\n                "type": "dtmf",\n                "call_id": data.get("call_id", ""),\n                "digit": str(dtmf),\n                "timestamp": datetime.now().isoformat(),\n            })'

if old in content:
    content = content.replace(old, new)
    with open(path, "w") as f:
        f.write(content)
    print("DTMF events patched")
else:
    print("NOT FOUND")
    import re
    idx = content.find("dtmf = data.get")
    if idx >= 0:
        print(repr(content[idx:idx+300]))
