"""
AVM-0b — проверка каскада LLM на 402/обрыв под нагрузкой.
Запуск на VPS: /opt/pipecat-venv/bin/python3 scripts/bench_cascade.py --n 12 --concurrency 12
Скрипт бьёт в OmniRoute (LLM_BASE) по primary+fallback моделям параллельно,
как это делает агент (DebugLLMStream._first_or_fallback), и ловит 402/429/обрыв.
"""
import argparse
import asyncio
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / "agent" / ".env")

from openai import AsyncClient

LLM_BASE = os.getenv("LLM_BASE", "http://127.0.0.1:20128/v1")
LLM_KEY = os.getenv("OPENAI_API_KEY", "omni")
LLM_MODEL = os.getenv("LLM_MODEL", "opencode-go/minimax-m3")
LLM_FB = os.getenv("LLM_FALLBACK_MODEL", "oc/deepseek-v4-flash-free")
LLM_PROXY = os.getenv("LLM_PROXY") or None

SYSTEM = "Ты голосовой менеджер по продаже цыплят. Отвечай максимально кратко, одной фразой."
USER_MSGS = ["да", "нет", "сколько голов цена", "доставка прежняя", "сто голов"]


async def one_call(client, i, semaphore):
    models = [LLM_MODEL, LLM_FB]
    if len(models) == 1:
        models.append(models[0])
    async with semaphore:
        t0 = time.time()
        last_err = None
        for m in models:
            try:
                stream = await asyncio.wait_for(
                    client.chat.completions.create(
                        model=m,
                        messages=[
                            {"role": "system", "content": SYSTEM},
                            {"role": "user", "content": USER_MSGS[i % len(USER_MSGS)]},
                        ],
                        max_tokens=48,
                        temperature=0.3,
                        stream=True,
                        timeout=20,
                    ),
                    timeout=22,
                )
                ttft = None
                async for chunk in stream:
                    if ttft is None:
                        ttft = time.time() - t0
                    if getattr(chunk.choices[0].delta, "content", None):
                        return {
                            "i": i,
                            "model": m,
                            "status": "ok",
                            "ttft": round(ttft, 2),
                            "err": None,
                        }
                return {"i": i, "model": m, "status": "empty", "ttft": None, "err": "no content"}
            except Exception as e:  # noqa: BLE001
                last_err = f"{type(e).__name__}: {str(e)[:120]}"
                # 402 → квота/баланс; 429 → rate limit; connection → обрыв
        return {"i": i, "model": None, "status": "fail", "ttft": None, "err": last_err}


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--concurrency", type=int, default=12)
    args = ap.parse_args()

    client = AsyncClient(api_key=LLM_KEY, base_url=LLM_BASE, timeout=30)
    sem = asyncio.Semaphore(args.concurrency)
    tasks = [one_call(client, i, sem) for i in range(args.n)]
    results = await asyncio.gather(*tasks)

    ok = [r for r in results if r["status"] == "ok"]
    fails = [r for r in results if r["status"] != "ok"]
    ttfts = [r["ttft"] for r in ok if r["ttft"]]
    err_types = {}
    for r in fails:
        key = (r["err"] or "")[:40]
        err_types[key] = err_types.get(key, 0) + 1

    print("\n=== AVM-0b SUMMARY ===")
    print(f"requests={args.n} ok={len(ok)} fail={len(fails)}")
    if ttfts:
        print(f"TTFT ok: min={min(ttfts):.2f} avg={sum(ttfts)/len(ttfts):.2f} max={max(ttfts):.2f}")
    else:
        print("TTFT: no successful responses")
    if err_types:
        print("ERROR TYPES (ищи 402/429/connection):")
        for k, v in sorted(err_types.items(), key=lambda x: -x[1]):
            print(f"  {v:>3}x {k}")
    else:
        print("ERROR TYPES: none")
    print("=== END ===")
    # Блокер гейта: любой 402 / connection error под нагрузкой = AVM-0b FAIL
    blocker = [r for r in fails if r["err"] and ("402" in r["err"] or "connect" in r["err"].lower())]
    if blocker:
        print(f"[AVM-0b] FAIL: {len(blocker)} запросов с 402/обрывом под нагрузкой")
    else:
        print("[AVM-0b] PASS: 402/обрыв не обнаружены под нагрузкой")


if __name__ == "__main__":
    asyncio.run(main())
