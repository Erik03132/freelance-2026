import asyncio, os, httpx
from openai import AsyncClient

MODELS = [
    "oc/deepseek-v4-flash-free",
    "deepseek/deepseek-chat",
    "openai/gpt-4o-mini",
    "anthropic/claude-3.5-haiku",
    "google/gemini-2.5-flash",
    "opencode-go/minimax-m3",
]


async def t(model):
    c = AsyncClient(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ["LLM_BASE"],
        http_client=httpx.AsyncClient(proxy=None, trust_env=False, timeout=20),
    )
    try:
        r = await asyncio.wait_for(
            c.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "ок"}],
                max_tokens=20,
                stream=True,
                timeout=15,
            ),
            timeout=16,
        )
        async for ch in r:
            if ch.choices[0].delta.content:
                print(model, "-> OK", flush=True)
                return
        print(model, "-> EMPTY", flush=True)
    except Exception as e:
        print(model, "-> ERR", str(e)[:160], flush=True)


async def main():
    for m in MODELS:
        await t(m)


asyncio.run(main())
