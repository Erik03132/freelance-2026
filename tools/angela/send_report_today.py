#!/usr/bin/env python3
"""Отправка отчёта за 21 апреля Андрею в ТГ"""
import urllib.request
import urllib.parse
import json
import time

BOT_TOKEN = "8336409939:AAHr2wbuOfED5woCzCokKKM9JnkVRYepfms"
API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
ANDREY_ID = 444248782

def send(chat_id, text):
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }).encode('utf-8')
    try:
        req = urllib.request.Request(API, data=data, method='POST')
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            if result.get("ok"):
                print(f"✅ OK -> {chat_id}")
            else:
                print(f"❌ ERROR: {result}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    time.sleep(1)

# === ОТЧЁТ ===
part1 = """📊 <b>ОТЧЁТ CRM — 21 АПРЕЛЯ 2026</b>
━━━━━━━━━━━━━━━━━━━━━

🔑 <b>КЛЮЧЕВЫЕ ЦИФРЫ ДНЯ</b>

▫️ Лиды: <b>50</b>
▫️ Сделки: <b>59</b>
▫️ Общая сумма: <b>707 250 ₽</b>
▫️ Крупнейшая: <b>122 500 ₽</b> (Эльзара)
▫️ Средний чек: <b>~11 987 ₽</b>

👩‍💼 <b>МЕНЕДЖЕРЫ</b>

🥇 Марина Е — ~289 825 ₽ (~32 сделки)
🥈 Эльзара — ~272 375 ₽ (~16 сделок)
🥉 Аня — ~145 050 ₽ (~11 сделок)
▫️ Татьяна — 4 лида"""

part2 = """📞 <b>ИСТОЧНИКИ</b>
📞 Звонки: 27 (54%)
🌐 Сайт/Формы: 22 (44%)
📱 Telegram: 1

📞 <b>Всего звонков за день: 398</b>
🥇 Марина Е: 148 звонков
🥈 Эльзара: 138 звонков
🥉 Аня: 112 звонков"""

part3 = """💰 <b>ТОП-10 СДЕЛОК</b>

1. <b>122 500 ₽</b> — Эльзара (11:45)
2. <b>74 000 ₽</b> — Марина Е (16:05)
3. <b>47 500 ₽</b> — Эльзара (11:26)
4. <b>37 500 ₽</b> — Аня (10:51)
5. <b>35 000 ₽</b> — Марина Е (11:57)
6. <b>34 000 ₽</b> — Аня (11:08)
7. <b>32 000 ₽</b> — Аня (11:09)
8. <b>21 000 ₽</b> — Марина Е (13:26)
9. <b>17 550 ₽</b> — Эльзара (13:57)
10. <b>15 500 ₽</b> — Марина Е (09:11)"""

part4 = """🏆 <b>ИТОГИ ДНЯ</b>

1. День стабильный — 50 лидов, 59 сделок
2. Звонки доминируют (54%), сайт/формы набирают (44%)
3. Крупная сделка — 122 500₽ через Эльзару
4. Марина Е лидирует по объёму (290К₽) и звонкам (148)
5. Средний чек вырос до ~12 000₽ (вчера ~9 880₽)

📊 Конверсия лид→сделка: <b>118%</b> (добивают вчерашних)
⏰ Пик активности: <b>09:00–12:00</b>

<i>Отчёт сформирован Анжелочкой 🐣</i>"""

print(f"📤 Отправка отчёта Андрею ({ANDREY_ID})...")
send(ANDREY_ID, part1)
send(ANDREY_ID, part2)
send(ANDREY_ID, part3)
send(ANDREY_ID, part4)
print("🎉 Отчёт отправлен!")
