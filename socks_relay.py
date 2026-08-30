#!/usr/bin/env python3
# socks_relay.py — локальный SOCKS5-релей БЕЗ зависимостей (только stdlib).
# ЗАЧЕМ: macOS nc -X5 не умеет SOCKS-авторизацию (user:pass). OpenSSH тоже.
# Этот скрипт поднимает локальный SOCKS5 НА ВЕЗ АВТОРИЗАЦИИ (127.0.0.1:1080),
# который сам ходит на внешний RU-прокси (с user:pass) и прокидывает дальше.
# Тогда `ssh -o ProxyCommand="nc -X5 -x 127.0.0.1:1080 %h %p"` работает.
#
# SSoT: handoff_2026-08-29_vps_access_nginx_fix.md (RU SOCKS5-мост стабильности)
#
# Реквизиты RU-прокси берутся из env (см. ~/.vps-tunnel.sh / LaunchAgent):
#   VPS_RU_PROXY=socks5://USER:PASS@RU.IP:PORT
# Локальный порт: 127.0.0.1:1080 (без auth, только для localhost-туннеля).

import os, socket, struct, threading, sys, re

UPSTREAM = os.environ.get("VPS_RU_PROXY", "")
LOCAL = ("127.0.0.1", 1080)

def parse_upstream(u):
    # socks5://user:pass@host:port
    m = re.match(r'^socks5://([^:]+):([^@]+)@([^:]+):(\d+)$', u)
    if not m:
        sys.exit(f"[socks_relay] bad VPS_RU_PROXY: {u!r}\n"
                 f"Ожидается socks5://USER:PASS@RU.IP:PORT")
    return m.group(1), m.group(2), m.group(3), int(m.group(4))

def handle_client(client):
    try:
        # SOCKS5 handshake от ssh/nc (без auth ожидается, т.к. локальный)
        hdr = client.recv(2)
        if len(hdr) < 2:
            return
        ver, nmethods = hdr[0], hdr[1]
        methods = client.recv(nmethods)
        # отвечаем: no auth required
        client.sendall(b'\x05\x00')
        # request
        req = client.recv(4)
        if len(req) < 4:
            return
        ver, cmd, rsv, atyp = req[0], req[1], req[2], req[3]
        if cmd != 1:  # только CONNECT
            client.sendall(b'\x05\x07\x00\x01' + b'\x00'*6)
            return
        if atyp == 1:  # IPv4
            dst = socket.inet_ntoa(client.recv(4))
        elif atyp == 3:  # domain
            l = client.recv(1)[0]
            dst = client.recv(l).decode()
        elif atyp == 4:  # IPv6
            dst = socket.inet_ntop(socket.AF_INET6, client.recv(16))
        else:
            client.sendall(b'\x05\x08\x00\x01' + b'\x00'*6); return
        port = struct.unpack('>H', client.recv(2))[0]

        # подключаемся к UPSTREAM SOCKS5 с авторизацией
        u, p, ph, pp = parse_upstream(UPSTREAM)
        proxy = socket.create_connection((ph, pp), timeout=10)
        proxy.sendall(b'\x05\x01\x02')  # user/pass метод
        r = proxy.recv(2)
        if r[1] != 2:
            client.sendall(b'\x05\x01\x00\x01' + b'\x00'*6); proxy.close(); return
        # auth
        proxy.sendall(b'\x01' + bytes([len(u)]) + u.encode() +
                      bytes([len(p)]) + p.encode())
        ar = proxy.recv(2)
        if ar[1] != 0:
            client.sendall(b'\x05\x01\x00\x01' + b'\x00'*6); proxy.close(); return
        # запрос к цели через прокси
        proxy.sendall(b'\x05\x01\x00' + b'\x03' + bytes([len(dst)]) +
                      dst.encode() + struct.pack('>H', port))
        rep = proxy.recv(10)
        # отвечаем клиенту
        client.sendall(b'\x05\x00\x00\x01' + b'\x00'*6)
        # сращиваем потоки
        a2b = threading.Thread(target=pipe, args=(client, proxy), daemon=True)
        b2a = threading.Thread(target=pipe, args=(proxy, client), daemon=True)
        a2b.start(); b2a.start()
        a2b.join(); b2a.join()
    except Exception as e:
        try: client.sendall(b'\x05\x01\x00\x01' + b'\x00'*6)
        except Exception: pass
    finally:
        try: client.close()
        except Exception: pass

def pipe(src, dst):
    try:
        while True:
            buf = src.recv(65536)
            if not buf: break
            dst.sendall(buf)
    except Exception: pass
    finally:
        try: src.shutdown(socket.SHUT_RD)
        except Exception: pass

if __name__ == "__main__":
    if not UPSTREAM:
        sys.exit("VPS_RU_PROXY не задан. Экспортни socks5://USER:PASS@RU.IP:PORT")
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(LOCAL); srv.listen(128)
    print(f"[socks_relay] 127.0.0.1:1080 -> {UPSTREAM}", flush=True)
    while True:
        c, _ = srv.accept()
        threading.Thread(target=handle_client, args=(c,), daemon=True).start()
