import re
path = '/opt/mango_webhook.py'
with open(path) as f:
    c = f.read()

old = '        # Auto-play greeting for inbound calls on Appeared (FIXED: moved after call_id assignment)\n        if call_id and call_state == "Appeared" and callback_initiator != "API":\n            if _is_client_number(from_num):\n                import threading as _th\n                log.info("INBOUND Appeared %s -> auto-play %s", from_num, MANGO_AUDIO_NAME)\n                _th.Thread(target=lambda cid=call_id: play_on_call(cid, MANGO_AUDIO_ID, "greeting"), daemon=True).start()'

new = '        # Auto-play greeting for inbound calls on Appeared\n        cb_cid = call_id or entry_id\n        if cb_cid and call_state == "Appeared" and callback_initiator != "API":\n            if _is_client_number(from_num):\n                import threading as _th\n                log.info("INBOUND %s -> auto-play %s (cid=%s)", from_num, MANGO_AUDIO_NAME, cb_cid[:20])\n                _th.Thread(target=lambda cid=cb_cid: play_on_call(cid, MANGO_AUDIO_ID, "greeting"), daemon=True).start()'

if old in c:
    c = c.replace(old, new)
    with open(path, 'w') as f:
        f.write(c)
    print('OK')
else:
    print('NOT FOUND')
