from __future__ import annotations

"""
🖼️ Фотокаскад v2 — генерация и поиск изображений.

Каскад из 4 уровней:
  1. Leonardo AI (Imagen4/Phoenix) — платный премиум, точные детали
  2. Ideogram 4 (через fal.ai) — ЛУЧШАЯ open-source модель,
                                    9.3B парам., #1 среди открытых на Design Arena
                                    Особо хороша для текста на картинках, поддерживает JSON-промпты
  3. Unsplash — бесплатный сток (нужен UNSPLASH_ACCESS_KEY)
  4. Placeholder — заглушка-URL (последняя надежда)

Переменные окружения:
  LEONARDO_API_KEY    — ключ Leonardo AI
  FAL_KEY             — ключ fal.ai (для Ideogram 4)
  UNSPLASH_ACCESS_KEY — ключ Unsplash
  PHOTO_PROXY_US      — URL прокси вида http://user:pass@host:port
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY", "")
UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")
FAL_KEY = os.getenv("FAL_KEY", "")  # fal.ai — Ideogram 4
PROXY_US = os.getenv("PHOTO_PROXY_US", "")  # http://user:pass@host:port

# Leonardo model ID
LEONARDO_MODEL_ID = os.getenv(
    "LEONARDO_MODEL_ID",
    "b24e16ff-06e3-43eb-8d33-4416c2d75876",  # Leonardo Imagen4 / Phoenix 1.0
)

# Ideogram 4 — fal.ai endpoint
IDEOGRAM_MODEL = "fal-ai/ideogram/v4"


def _build_proxy_kwargs() -> dict:
    """Возвращает kwargs для httpx с US-прокси (если задан)."""
    if PROXY_US:
        return {"proxies": {"https://": PROXY_US, "http://": PROXY_US}}
    return {}


# ============================================================
# УРОВЕНЬ 1 — Leonardo AI (Imagen4)
# ============================================================

async def _generate_leonardo(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    num_images: int = 1,
) -> list[str]:
    """
    Генерирует изображение через Leonardo AI (Imagen4/Phoenix).
    Запрос идёт через US-прокси.

    Returns:
        Список URL готовых изображений или [] при ошибке.
    """
    if not LEONARDO_API_KEY:
        print("⚠️ LEONARDO_API_KEY не задан")
        return []

    proxy_kwargs = _build_proxy_kwargs()

    try:
        async with httpx.AsyncClient(timeout=60, **proxy_kwargs) as client:
            # Шаг 1: запустить генерацию
            resp = await client.post(
                "https://cloud.leonardo.ai/api/rest/v1/generations",
                headers={
                    "Authorization": f"Bearer {LEONARDO_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "modelId": LEONARDO_MODEL_ID,
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                    "num_images": num_images,
                    "alchemy": True,           # улучшенное качество
                    "photoReal": False,
                    "presetStyle": "DYNAMIC",
                },
            )

            if resp.status_code != 200:
                print(f"⚠️ Leonardo: {resp.status_code} — {resp.text[:120]}")
                return []

            generation_id = resp.json()["sdGenerationJob"]["generationId"]
            print(f"🎨 Leonardo: запрос отправлен, id={generation_id}")

            # Шаг 2: polling результата (до 60 сек)
            for attempt in range(12):
                await asyncio.sleep(5)
                poll = await client.get(
                    f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}",
                    headers={"Authorization": f"Bearer {LEONARDO_API_KEY}"},
                )
                gen = poll.json().get("generations_by_pk", {})
                status = gen.get("status", "")

                if status == "COMPLETE":
                    urls = [img["url"] for img in gen.get("generated_images", [])]
                    print(f"✅ Leonardo: {len(urls)} изображений готово")
                    return urls

                if status == "FAILED":
                    print(f"❌ Leonardo: генерация провалилась")
                    return []

                print(f"   Leonardo: ожидание ({attempt+1}/12)... статус={status}")

            print("⚠️ Leonardo: таймаут ожидания")
    except Exception as e:
        print(f"❌ Leonardo: {e}")

    return []


# ============================================================
# УРОВЕНЬ 2 — Ideogram 4 (через fal.ai)
# Лучшая open-source модель: 9.3B парам., #1 Design Arena
# Особо хороша для текста на картинках
# ============================================================

async def _generate_ideogram(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    style: str = "auto",              # auto / realistic / design / anime
    magic_prompt: bool = True,        # fal.ai auto-улучшает промпт
    rendering_speed: str = "BALANCED",  # TURBO / BALANCED / QUALITY
) -> list[str]:
    """
    Генерирует изображение через Ideogram 4 (fal.ai).

    Особенности:
    - Лучший текст на картинках среди open-source
    - magic_prompt автоматически улучшает промпт
    - Поддержка аспектных соотношений (1:1, 16:9, 9:16, 4:3)
    - До 2K разрешения

    Returns:
        Список URL готовых изображений или [] при ошибке.
    """
    if not FAL_KEY:
        print("⚠️ FAL_KEY не задан (см. ai-eggs/.env)")
        return []

    # Определяем аспект по размерам
    ratio = width / height
    if ratio > 1.4:
        aspect_ratio = "16:9"
    elif ratio < 0.7:
        aspect_ratio = "9:16"
    elif 0.9 < ratio < 1.1:
        aspect_ratio = "1:1"
    else:
        aspect_ratio = "4:3"

    payload = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "style": style,
        "magic_prompt_option": "AUTO" if magic_prompt else "OFF",
        "rendering_speed": rendering_speed,
        "num_images": 1,
    }

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            # fal.ai работает из РФ напрямую, прокси не нужен
            resp = await client.post(
                f"https://fal.run/{IDEOGRAM_MODEL}",
                headers={
                    "Authorization": f"Key {FAL_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            if resp.status_code != 200:
                print(f"⚠️ Ideogram 4: {resp.status_code} — {resp.text[:120]}")
                return []

            data = resp.json()
            images = data.get("images", [])
            if not images:
                print("⚠️ Ideogram 4: пустой ответ")
                return []

            urls = [img["url"] for img in images if img.get("url")]
            if urls:
                seed = data.get("seed", "?")
                print(f"✅ Ideogram 4: {len(urls)} изображений, seed={seed}")
            return urls

    except Exception as e:
        print(f"❌ Ideogram 4: {e}")

    return []


def ideogram_prompt_builder(
    subject: str,
    text_on_image: str = "",
    style: str = "realistic",
    color_palette: list[str] = None,
    background: str = "",
) -> str:
    """
    Строит структурированный промпт для Ideogram 4.

    Ideogram особенно хорошо обрабатывает чёткие описания,
    а magic_prompt автоматически улучшает промпт.

    Args:
        subject:       главный объект ("цыплёнок бройлер")
        text_on_image: текст на картинке ("Свежие цыплята!")
        style:         стиль (realistic / design / anime / auto)
        color_palette: hex-цвета (["#FF6B35", "#FFFFFF"])
        background:    фон ("зелёный луг")
    """
    parts = [subject]
    if text_on_image:
        parts.append(f'with text "{text_on_image}" clearly visible')
    if background:
        parts.append(f"background: {background}")
    if color_palette:
        colors = ", ".join(color_palette)
        parts.append(f"color palette: {colors}")
    parts.append(f"style: {style}, high quality, professional")
    return ", ".join(parts)


# ============================================================
# УРОВЕНЬ 3 — Unsplash (сток)
# ============================================================

async def _search_unsplash(
    query: str,
    count: int = 1,
    orientation: str = "landscape",
) -> list[str]:
    """
    Ищет фото на Unsplash по ключевым словам.

    Returns:
        Список URL изображений (raw) или [] при ошибке.
    """
    if not UNSPLASH_KEY:
        print("⚠️ UNSPLASH_ACCESS_KEY не задан")
        return []

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://api.unsplash.com/search/photos",
                params={
                    "query": query,
                    "per_page": count,
                    "orientation": orientation,
                    "order_by": "relevant",
                },
                headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"},
            )
            data = resp.json()
            urls = [item["urls"]["regular"] for item in data.get("results", [])]
            if urls:
                print(f"🔍 Unsplash: найдено {len(urls)} фото")
            return urls
    except Exception as e:
        print(f"⚠️ Unsplash: {e}")
        return []


# ============================================================
# УРОВЕНЬ 3 — Placeholder (заглушка)
# ============================================================

def _placeholder_url(prompt: str, width: int = 1024, height: int = 1024) -> list[str]:
    """Возвращает URL заглушки через picsum.photos."""
    seed = abs(hash(prompt)) % 1000
    url = f"https://picsum.photos/seed/{seed}/{width}/{height}"
    print(f"🖼️ Placeholder: {url}")
    return [url]


# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ — КАСКАД
# ============================================================

async def get_photo(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    prefer_generated: bool = True,
) -> dict:
    """
    Железобетонный фотокаскад.

    Порядок:
      1. Leonardo AI / Imagen4 (генерация, US-прокси)
      2. Unsplash (сток, по ключевым словам)
      3. Picsum Placeholder (заглушка, всегда работает)

    Args:
        prompt:            Текстовый промпт / описание нужного фото
        width, height:     Размер (по умолчанию 1024×1024)
        prefer_generated:  True → сначала пробовать Leonardo,
                           False → сначала пробовать Unsplash

    Returns:
        dict: {
            "url": str,          # URL готового изображения
            "source": str,       # "leonardo" | "unsplash" | "placeholder"
            "all_urls": list     # все URL если было несколько
        }
    """
    providers = (
        ["leonardo", "ideogram", "unsplash", "placeholder"]
        if prefer_generated
        else ["unsplash", "ideogram", "placeholder"]
    )

    for provider in providers:
        urls = []

        if provider == "leonardo":
            urls = await _generate_leonardo(prompt, width=width, height=height)

        elif provider == "ideogram":
            urls = await _generate_ideogram(prompt, width=width, height=height)

        elif provider == "unsplash":
            search_query = prompt[:50]
            urls = await _search_unsplash(search_query)

        elif provider == "placeholder":
            urls = _placeholder_url(prompt, width=width, height=height)

        if urls:
            return {"url": urls[0], "source": provider, "all_urls": urls}

    # Никогда не должно дойти сюда — placeholder всегда работает
    return {"url": "", "source": "none", "all_urls": []}


async def download_photo(
    prompt: str,
    save_path: str,
    width: int = 1024,
    height: int = 1024,
) -> str | None:
    """
    Скачивает фото в файл.

    Returns:
        Путь к файлу или None при ошибке.
    """
    result = await get_photo(prompt, width=width, height=height)
    url = result["url"]
    if not url:
        return None

    proxy_kwargs = _build_proxy_kwargs() if result["source"] == "leonardo" else {}

    try:
        async with httpx.AsyncClient(timeout=30, **proxy_kwargs) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            with open(save_path, "wb") as f:
                f.write(resp.content)
            print(f"💾 Сохранено: {save_path} (источник: {result['source']})")
            return save_path
    except Exception as e:
        print(f"❌ Ошибка скачивания: {e}")
        return None


# ============================================================
# ТЕСТ
# ============================================================

if __name__ == "__main__":
    import asyncio

    async def _test():
        print("🧪 Тест фотокаскада...\n")

        # Тест генерации
        result = await get_photo(
            prompt="кур бройлер в загоне, деревенское хозяйство, фотореалистично",
            width=1024,
            height=1024,
        )
        print(f"\n📷 Результат: {result['source']} → {result['url'][:80]}...\n")

    asyncio.run(_test())
