#!/usr/bin/env python3
path = "/opt/mango_webhook.py"
with open(path) as f:
    content = f.read()

old = '        _maybe_play_client_leg(data)\n\n        # Detect inbound calls for voice-angela'
new = '        _maybe_play_client_leg(data)\n\n        # Auto-play greeting for inbound calls on Appeared\n        if call_id and call_state == "Appeared" and callback_initiator != "API":\n            if _is_client_number(from_num):\n                import threading as _th\n                log.info("INBOUND Appeared %s -> auto-play %s", from_num, MANGO_AUDIO_NAME)\n                _th.Thread(target=lambda: play_on_call(call_id, MANGO_AUDIO_ID, "greeting"), daemon=True).start()\n\n        # Detect inbound calls for voice-angela'

if old in content:
    content = content.replace(old, new)
    with open(path, "w") as f:
        f.write(content)
    print("OK: auto-play added")
else:
    print("NOT FOUND, searching...")
    idx = content.find("_maybe_play_client_leg(data)")
    if idx >= 0:
        print(repr(content[idx:idx+500]))
