#!/usr/bin/env python3
"""Генерация приветствия Анжеллы для baresip aufile.

Создаёт /tmp/levitan_greeting_lead.wav (8kHz mono) с фразой приветствия.
Запуск: python3 deploy/levitan_greeting.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import levitan_faq_agent as a

GREETING_TEXT = (
    "Здравствуйте! Это Азовский инкубатор, меня зовут Анжелла. "
    "У нас сейчас суточные бройлеры Кобб и Росс от 75 рублей за голову. "
    "Чем могу помочь?"
)

if __name__ == "__main__":
    a.load_faq_cache()
    wav = a.synthesize_wav(GREETING_TEXT)
    if wav:
        target = a.GREETING_WAV
        import shutil
        from pathlib import Path

        # Добавляем lead-in тишину (1.5с), чтобы RTP-канал успел открыться
        # до начала приветствия — иначе первые секунды «съедаются».
        with_lead = Path(str(target).replace(".wav", "_lead.wav"))
        a._add_lead_silence(wav, with_lead, seconds=1.5)
        final = with_lead if with_lead.exists() else wav
        shutil.copy2(str(final), str(target))
        print(f"Greeting saved: {target}")
    else:
        print("ERROR: failed to synthesize greeting")
        sys.exit(1)
