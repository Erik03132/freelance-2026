#!/usr/bin/env python3
"""
Скрипт приветствия для Smart Dialer — Global Fields Export.

Структура звонка:
  1. Робот: приветствие (с паузами, SSML)
  2. Робот: передаёт оператору
  3. Оператор: квалификация клиента

edge-tts поддерживает SSML для пауз:
  <break time="800ms"/> — пауза 800мс
  <break time="500ms"/> — пауза 500мс (запятая)
  <break time="1200ms"/> — пауза 1.2с (точка/точка с запятой)

Генерация:
  python3 smart_dialer_greeting.py

Выход:
  tts_cache/globalfields_greeting.wav (8 kHz, mono, для Mango)
  tts_cache/globalfields_greeting.mp3 (для отладки)
"""

from __future__ import annotations

import asyncio
import hashlib
import subprocess
import sys
from pathlib import Path

# ── Конфигурация ──────────────────────────────────────────────────────────────

VOICE = "ru-RU-SvetlanaNeural"
RATE = "+0%"
SR = 8000  # телефония Mango

# ── Текст приветствия с SSML-паузами ─────────────────────────────────────────

# Приветствие: короткое, естественное, с паузами через пунктуацию
# edge-tts не поддерживает SSML <break>, паузы через запятые/точки/многоточия
GREETING_SSML = """Здравствуйте. Компания Глобал Филдс Экспорт.
Мы закупаем сельхозпродукцию нового урожая.
Сейчас соединю вас со специалистом. Он уточнит объём и условия поставки.
Пожалуйста, не кладите трубку."""

# Альтернативное приветствие (более тёплое, для повторных звонков)
GREETING_REPEAT_SSML = """Здравствуйте.
Снова звонит Глобал Филдс Экспорт.
Мы закупаем зерновые, бобовые и масличные культуры.
Передаю вас специалисту. Пожалуйста, оставайтесь на связи."""

# Короткое приветствие (для быстрой квалификации)
GREETING_SHORT_SSML = """Здравствуйте.
Глобал Филдс Экспорт. Переключаю на специалиста.
Одну секунду."""

# Приветствие для обратного звонка (клиент ждал)
GREETING_CALLBACK_SSML = """Здравствуйте.
Вы ждали обратного звонка от Глобал Филдс Экспорт?
Соединяю вас со специалистом.
Пожалуйста, оставайтесь на связи."""

# Приветствие для напоминания (клиент планировал продажу позже)
GREETING_REMINDER_SSML = """Здравствуйте.
Глобал Филдс Экспорт.
Вы ранее планировали продажу урожая.
Мы готовы обсудить условия.
Переключаю на специалиста."""


# ── Словарь приветствий ───────────────────────────────────────────────────────

GREETINGS = {
    "default": GREETING_SSML,
    "repeat": GREETING_REPEAT_SSML,
    "short": GREETING_SHORT_SSML,
    "callback": GREETING_CALLBACK_SSML,
    "reminder": GREETING_REMINDER_SSML,
}


# ── Генерация аудио ───────────────────────────────────────────────────────────

async def generate_greeting_ssml(
    ssml_text: str,
    output_path: Path,
    voice: str = VOICE,
    rate: str = RATE,
) -> bool:
    """Генерация аудио из SSML через edge-tts."""
    try:
        import edge_tts
        communicate = edge_tts.Communicate(ssml_text, voice, rate=rate)
        mp3_path = output_path.with_suffix(".mp3")
        await communicate.save(str(mp3_path))

        # Конвертация в WAV 8 kHz для Mango
        subprocess.run(
            ["ffmpeg", "-y",
             "-i", str(mp3_path),
             "-ar", str(SR), "-ac", "1",
             "-c:a", "pcm_s16le",
             "-f", "wav",
             str(output_path)],
            capture_output=True, timeout=15
        )

        if output_path.exists():
            print(f"✅ WAV: {output_path}")
            return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    return False


async def generate_all_greetings(output_dir: Path):
    """Генерация всех вариантов приветствий."""
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, ssml in GREETINGS.items():
        wav_path = output_dir / f"globalfields_greeting_{name}.wav"
        print(f"\n🎤 Генерация: {name}")
        ok = await generate_greeting_ssml(ssml, wav_path)
        if ok:
            # Информация о длительности
            result = subprocess.run(
                ["ffprobe", "-v", "error",
                 "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1",
                 str(wav_path)],
                capture_output=True, text=True
            )
            duration = float(result.stdout.strip()) if result.stdout.strip() else 0
            print(f"   Длительность: {duration:.1f} сек")

    print("\n📋 Файлы готовы для загрузки в Mango ЛК")


# ── Чеклист оператора ─────────────────────────────────────────────────────────

OPERATOR_CHECKLIST = """
╔══════════════════════════════════════════════════════════════╗
║        ЧЕКЛИСТ ОПЕРАТОРА — Global Fields Export             ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  1. ПРИВЕТСТВИЕ                                             ║
║     Робот: «Здравствуйте. Глобал Филдс Экспорт.            ║
║     Закупаем сельхозпродукцию. Соединяю со специалистом.»   ║
║     → Вы подключаетесь                                      ║
║                                                              ║
║  2. ПЕРВЫЙ ВОПРОС                                           ║
║     «Добрый день! Подскажите, у вас сейчас есть объёмы     ║
║     к продаже или планируете реализацию урожая?»            ║
║                                                              ║
║  3. ЕСЛИ ЕСТЬ ОБЪЁМ — КВАЛИФИКАЦИЯ                          ║
║     a) Какая культура?                                      ║
║     b) Какой объём в тоннах?                                ║
║     c) Где находится партия (район, область)?               ║
║     d) Какой базис удобнее: FCA или CPT?                    ║
║     e) Есть ли анализ качества?                             ║
║     f) Какая цена вас ориентировочно интересует?             ║
║                                                              ║
║  4. ЕСЛИ НЕТ ОБЪЁМА                                         ║
║     «Понял. Когда планируете реализацию?                    ║
║     Могу поставить напоминание и перезвонить.»              ║
║                                                              ║
║  5. ВОПРОСЫ КЛИЕНТА                                         ║
║     • «Цена какая?»                                          ║
║       → Зависит от культуры, качества, объёма, базиса.      ║
║         Назовите параметры — посчитаем.                     ║
║     • «Вы кто?»                                              ║
║       → Экспортная компания. Закупаем у производителей.      ║
║         Работаем по контракту.                               ║
║     • «Оплата как?»                                          ║
║       → По контракту, официально. Условия от объёма.        ║
║     • «Самовывоз?»                                           ║
║       → Да, FCA с вашего склада. Также CPT Новороссийск.    ║
║     • «Много закупаете?»                                     ║
║       → Закупаем объёмы на постоянной основе.               ║
║                                                              ║
║  6. ФИКСАЦИЯ ДАННЫХ                                         ║
║     После звонка заполнить:                                  ║
║     - Культура: ___________                                  ║
║     - Объём (тонн): ___________                              ║
║     - Регион: ___________                                    ║
║     - Базис: ___________                                     ║
║     - Анализ качества: да / нет / есть / нет                ║
║     - Цена клиента: ___________                              ║
║     - Статус: горячий / тёплый / нет объёма / перезвон     ║
║     - Комментарий: ___________                               ║
║                                                              ║
║  7. ЗАВЕРШЕНИЕ                                               ║
║     «Спасибо! Менеджер свяжется с вами для расчёта.»        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""


# ── Запуск ────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Генерация приветствий Smart Dialer")
    parser.add_argument("--type", choices=list(GREETINGS.keys()), default="default",
                        help="Тип приветствия (default/short/repeat/callback/reminder)")
    parser.add_argument("--all", action="store_true", help="Сгенерировать все варианты")
    parser.add_argument("--checklist", action="store_true", help="Показать чеклист оператора")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "tts_cache",
                        help="Директория для выходных файлов")
    args = parser.parse_args()

    if args.checklist:
        print(OPERATOR_CHECKLIST)
        return

    if args.all:
        asyncio.run(generate_all_greetings(args.output_dir))
    else:
        ssml = GREETINGS[args.type]
        wav_path = args.output_dir / f"globalfields_greeting_{args.type}.wav"
        print(f"🎤 Генерация: {args.type}")
        asyncio.run(generate_greeting_ssml(ssml, wav_path))


if __name__ == "__main__":
    main()
