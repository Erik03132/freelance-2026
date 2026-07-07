#!/usr/bin/env python3
import re
path = "/opt/mango_webhook.py"
with open(path) as f:
    content = f.read()

# Add call_id capture to events when callback client connects
old1 = "    if call_id in played_message:\n        return"
new1 = '    if call_id in played_message:\n        return\n    _write_voice_event({\n        "type": "callback_connected",\n        "command_id": command_id,\n        "call_id": call_id,\n        "phone": _norm_phone(str(to_num)),\n        "timestamp": datetime.now().isoformat(),\n    })'

if old1 in content:
    content = content.replace(old1, new1)
    print("callback_connected event added")

# Add command_id to inbound_call events
old2 = '                _write_voice_event({\n                    "type": "inbound_call",\n                    "call_id": call_id,\n                    "phone": _norm_phone(from_num),\n                    "timestamp": datetime.now().isoformat(),\n                })'
new2 = '                _write_voice_event({\n                    "type": "inbound_call",\n                    "call_id": call_id,\n                    "phone": _norm_phone(from_num),\n                    "command_id": command_id,\n                    "timestamp": datetime.now().isoformat(),\n                })'

if old2 in content:
    content = content.replace(old2, new2)
    print("command_id added to inbound_call")
else:
    print("inbound_call block not found, searching...")
    idx = content.find('"inbound_call"')
    if idx >= 0:
        print("Found at", idx, repr(content[idx:idx+400]))

with open(path, "w") as f:
    f.write(content)
print("Done")
