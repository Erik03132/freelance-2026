#!/usr/bin/env python3
"""Локальный loopback-тест Анжеллы (без Mango/baresip).

Эмулирует диалог: клиент "говорит" текстом (input()), агент отвечает
через FAQ-кэш или LLM-fallback, синтезирует TTS (Яндекс) и сохраняет WAV.
Проверяет весь пайплайн кроме реальной телефонии.

Запуск: python3 deploy/test_angel_local.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import levitan_faq_agent as a


def main():
    a.load_faq_cache()
    print("=" * 60)
    print("🐣 ЛОКАЛЬНЫЙ ТЕСТ АНЖЕЛЛЫ (loopback, без телефонии)")
    print(f"FAQ-кэш: {len(a._faq_cache)} триггеров | TTS: Яндекс ({a.TTS_VOICE})")
    print("Вводите реплики клиента. 'exit' — выход, 'call' — тест-звонок.")
    print("=" * 60)

    transcript = []
    turn = 0
    got_phone = False

    # Приветствие
    greeting = ("Здравствуйте! Это Азовский инкубатор, меня зовут Анжелла. "
                "У нас сейчас суточные бройлеры Кобб и Росс по 65 рублей за голову. Чем могу помочь?")
    wav = a.synthesize_wav(greeting)
    print(f"\n🤖 Анжелла: {greeting}")
    print(f"   [TTS] {'✅' if wav else '❌'} WAV: {wav.name if wav else 'FAIL'}")
    transcript.append({"role": "assistant", "content": greeting})

    while True:
        try:
            user_text = input("\n👤 Клиент: ").strip()
        except EOFError:
            break
        if not user_text:
            continue
        if user_text.lower() in ("exit", "quit", "q"):
            break
        if user_text.lower() == "call":
            print("📞 Эмуляция звонка: запуск FAQDialog.run() (требует Mango — пропуск)")
            continue

        transcript.append({"role": "user", "content": user_text})
        turn += 1

        # 1. FAQ-кэш
        faq_reply = a.faq_lookup(user_text)
        if faq_reply:
            response = faq_reply
            src = "FAQ-кэш (мгновенно, без LLM)"
        else:
            # 2. LLM fallback
            response = a.llm_response(transcript)
            src = "LLM/local-fallback"

        if not response:
            print("   [ERROR] пустой ответ")
            continue

        wav = a.synthesize_wav(response)
        transcript.append({"role": "assistant", "content": response})
        phone = a.extract_phone(user_text)
        if phone:
            got_phone = True
            print(f"   [PHONE] собран: {phone}")

        print(f"🤖 Анжелла: {response}")
        print(f"   [SRC] {src} | [TTS] {'✅' if wav else '❌'} WAV: {wav.name if wav else 'FAIL'}")

        if a.is_rejection(user_text):
            print("   [DIALOG] клиент отказался — завершение")
            break
        if a.is_complete(user_text, turn, got_phone):
            print("   [DIALOG] завершение (собрана вся инфа)")
            break

    print("\n" + "=" * 60)
    print(f"ИТОГ: ходов={turn} | телефон={'да' if got_phone else 'нет'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
