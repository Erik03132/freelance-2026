#!/usr/bin/env python3
"""SSH tunnel to VPS 217.149.23.113:22 via US proxy (CONNECT).
Usage: python3 ssh_tunnel.py [listen_port]
Then: ssh -p <listen_port> root@127.0.0.1
"""

import socket
import base64
import threading
import sys

PROXY_HOST = "172.120.21.141"
PROXY_PORT = 64468
PROXY_AUTH = "Q3NeJXTY:dsBaWh2L"
TARGET_HOST = "217.149.23.113"
TARGET_PORT = 22
LISTEN_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 22001


def pipe(a, b):
    try:
        while True:
            data = a.recv(65536)
            if not data:
                break
            b.sendall(data)
    except Exception:
        pass
    finally:
        for s in (a, b):
            try:
                s.close()
            except Exception:
                pass


def handle(client):
    try:
        upstream = socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=15)
        auth = base64.b64encode(PROXY_AUTH.encode()).decode()
        req = (
            f"CONNECT {TARGET_HOST}:{TARGET_PORT} HTTP/1.1\r\n"
            f"Host: {TARGET_HOST}:{TARGET_PORT}\r\n"
            f"Proxy-Authorization: Basic {auth}\r\n\r\n"
        )
        upstream.sendall(req.encode())
        resp = upstream.recv(4096)
        if b"200" not in resp.split(b"\r\n")[0]:
            client.close()
            upstream.close()
            return
        threading.Thread(target=pipe, args=(client, upstream), daemon=True).start()
        pipe(upstream, client)
    except Exception:
        try:
            client.close()
        except Exception:
            pass


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", LISTEN_PORT))
    srv.listen(50)
    print(f"Tunnel ready: ssh -p {LISTEN_PORT} root@127.0.0.1", flush=True)
    while True:
        c, _ = srv.accept()
        threading.Thread(target=handle, args=(c,), daemon=True).start()


if __name__ == "__main__":
    main()
