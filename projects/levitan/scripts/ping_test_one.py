#!/usr/bin/env python3
"""Test: ping one Adygea number via baresip+Mango to verify alive-detection."""
import os, sys, time, signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ping_checker as pc

pc.load_env()

# Start baresip bridge
bridge = pc.PingBridge()
if not bridge.start():
    print("BARESIP FAILED TO REGISTER")
    sys.exit(1)
print("baresip OK")

# Test number: a remaining Adygea number (Гиагинский - Азаров, not yet alive)
test_phone = "79184259353"
print(f"Pinging {test_phone} ...")
res = bridge.ping(test_phone)
print("RESULT:", res)
bridge.stop()
