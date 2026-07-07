"""Тест всех компонентов Levitan."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.levitan.config import settings
from src.levitan.tts_engine import TTSEngine
from src.levitan.stt_engine import STTEngine
from src.levitan.llm_client import LLMClient
from src.levitan.knowledge_base import get_knowledge_base
from src.levitan.mango_client import MangoClient
from src.levitan.telegram_reporter import get_telegram_reporter


async def test_all():
    """Тест всех компонентов."""
    print("=" * 50)
    print("LEVITAN - Тест компонентов")
    print("=" * 50)
    
    results = []
    
    # 1. Config
    print("\n1. Testing Config...")
    try:
        print(f"   ✅ Mango API Key: {settings.mango.api_key[:15]}...")
        print(f"   ✅ OpenRouter Key: {settings.openrouter.api_key[:15]}...")
        print(f"   ✅ Telegram Token: {settings.telegram.bot_token[:15]}...")
        results.append(("Config", True))
    except Exception as e:
        print(f"   ❌ Config failed: {e}")
        results.append(("Config", False))
    
    # 2. TTS
    print("\n2. Testing TTS (edge-tts)...")
    try:
        tts = TTSEngine()
        path = await tts.synthesize("Тест синтеза речи")
        print(f"   ✅ TTS synthesized: {path.name} ({path.stat().st_size} bytes)")
        results.append(("TTS", True))
    except Exception as e:
        print(f"   ❌ TTS failed: {e}")
        results.append(("TTS", False))
    
    # 3. Knowledge Base
    print("\n3. Testing Knowledge Base...")
    try:
        kb = get_knowledge_base()
        result = kb.search("пшеница")
        print(f"   ✅ Knowledge Base: {len(kb._faq_texts)} FAQ items")
        print(f"   ✅ Search works: {result[:80]}...")
        results.append(("Knowledge Base", True))
    except Exception as e:
        print(f"   ❌ Knowledge Base failed: {e}")
        results.append(("Knowledge Base", False))
    
    # 4. LLM
    print("\n4. Testing LLM (OpenRouter)...")
    try:
        llm = LLMClient(api_key=settings.openrouter.api_key)
        response = await llm.generate(
            [{"role": "user", "content": "Привет! Ответь кратко."}],
            max_tokens=50
        )
        print(f"   ✅ LLM response: {response[:80]}...")
        await llm.close()
        results.append(("LLM", True))
    except Exception as e:
        print(f"   ❌ LLM failed: {e}")
        results.append(("LLM", False))
    
    # 5. Mango Client
    print("\n5. Testing Mango Client...")
    try:
        mango = MangoClient(
            api_key=settings.mango.api_key,
            salt=settings.mango.salt
        )
        print(f"   ✅ Mango Client created")
        print(f"   ⚠️ Balance check skipped (network)")
        await mango.close()
        results.append(("Mango", True))
    except Exception as e:
        print(f"   ❌ Mango failed: {e}")
        results.append(("Mango", False))
    
    # 6. Telegram
    print("\n6. Testing Telegram Reporter...")
    try:
        reporter = get_telegram_reporter()
        if reporter:
            print(f"   ✅ Telegram Reporter created")
            print(f"   ⚠️ Message send skipped (network)")
            results.append(("Telegram", True))
        else:
            print(f"   ⚠️ Telegram not configured")
            results.append(("Telegram", False))
    except Exception as e:
        print(f"   ❌ Telegram failed: {e}")
        results.append(("Telegram", False))
    
    # Итоги
    print("\n" + "=" * 50)
    print("RESULTS:")
    print("=" * 50)
    
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    
    for name, ok in results:
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"  {status} {name}")
    
    print(f"\nTotal: {passed}/{total} passed")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(test_all())
    sys.exit(0 if success else 1)
