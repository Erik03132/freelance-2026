#!/usr/bin/env python3
"""Greeting Bridge — управляет baresip для мгновенного подключения оператора.

Поток:
1. Mango callback ext 23 → baresip отвечает
2. Mango звонит клиенту
3. Клиент ответил → baresip переводит на ext 22 (оператор)
4. Оператор поднимает трубку → сразу говорит с клиентом

Без приветствия. Оператор НЕ слышит гудков.
"""
import asyncio
import json
import logging
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
log = logging.getLogger("greeting-bridge")

BASE_DIR = Path(__file__).resolve().parent
BARESIP_DIR = BASE_DIR
CTRL_PORT = 4444
TRANSFER_TARGET = "sip:22@vpbx400374818.mangosip.ru"


class GreetingBridge:
    def __init__(self):
        self.process: subprocess.Popen | None = None
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None
        self.active_call_id: str | None = None

    async def start_baresip(self):
        log.info("Запуск baresip...")
        self.process = await asyncio.create_subprocess_exec(
            "baresip", "-f", str(BARESIP_DIR), "-d",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        await asyncio.sleep(2)

    async def connect_ctrl(self):
        try:
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection("127.0.0.1", CTRL_PORT), timeout=5
            )
            log.info("Подключён к ctrl_tcp")
            return True
        except Exception as e:
            log.error(f"Не удалось подключиться к ctrl_tcp: {e}")
            return False

    async def send_command(self, command: str, params: str = ""):
        if not self.writer:
            return
        msg = json.dumps({
            "type": "command",
            "command": command,
            "params": params,
            "token": str(int(asyncio.get_event_loop().time() * 1000)),
        })
        self.writer.write((msg + "\n").encode())
        await self.writer.drain()

    async def read_events(self):
        while self.reader and not self.reader.at_eof():
            try:
                line = await asyncio.wait_for(self.reader.readline(), timeout=0.5)
                if not line:
                    break
                try:
                    data = json.loads(line.decode())
                    event = data.get("event", "")
                    log.info(f"Событие: {event} {data}")

                    if event == "call_incoming":
                        await self.handle_incoming(data)
                    elif event == "call_established":
                        await self.handle_established(data)
                    elif event == "call_ended":
                        await self.handle_ended(data)
                except json.JSONDecodeError:
                    log.info(f"Сырые данные: {line.decode().strip()}")
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                log.error(f"Ошибка чтения: {e}")
                break

    async def handle_incoming(self, data: dict):
        call_id = data.get("id", "")
        self.active_call_id = call_id
        log.info(f"Входящий звонок от Mango: {call_id}")
        await self.send_command("/call/answer", call_id)
        log.info(f"Отвечаю на звонок {call_id} (клиенту ещё не звоним)")

    async def handle_established(self, data: dict):
        call_id = data.get("id", "") or self.active_call_id
        log.info(f"Звонок установлен: {call_id}")
        log.info(f"Перевожу на оператора {TRANSFER_TARGET}...")
        # Мгновенный перевод — без приветствия
        await self.send_command("/call/transfer", TRANSFER_TARGET)
        log.info(f"Команда перевода отправлена")

    async def handle_ended(self, data: dict):
        log.info(f"Звонок завершён: {data}")
        self.active_call_id = None

    async def run(self):
        # Kill any existing baresip
        subprocess.run(["pkill", "-f", "baresip.*greeting_bridge"], capture_output=True)
        await asyncio.sleep(1)

        await self.start_baresip()
        connected = await self.connect_ctrl()
        if not connected:
            return

        log.info("Bridge готов (режим: мгновенное подключение без приветствия)")
        await self.read_events()

        # Cleanup
        if self.writer:
            self.writer.close()
        if self.process:
            self.process.terminate()

    def cleanup(self):
        if self.process:
            self.process.terminate()
        subprocess.run(["pkill", "-f", "baresip.*greeting_bridge"], capture_output=True)


async def main():
    bridge = GreetingBridge()
    try:
        await bridge.run()
    except KeyboardInterrupt:
        bridge.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
