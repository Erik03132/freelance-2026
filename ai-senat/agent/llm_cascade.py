"""
Каскадный LLM-движок для Senator AI.
Приоритет: Gemini Direct → OpenRouter → Ollama (offline).
Паттерн переиспользован из ai-eggs/angelochka_core.py.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:12b")

# Применяем прокси для Google API
GOOGLE_PROXY = os.getenv("TELEGRAM_PROXY", "socks5h://Q3NeJXTY:dsBaWh2L@172.120.21.141:64469")
if GOOGLE_PROXY:
    os.environ["HTTP_PROXY"] = GOOGLE_PROXY
    os.environ["HTTPS_PROXY"] = GOOGLE_PROXY

def _call_gemini_direct(prompt, history=None, temperature=0.7):
    """Вызов Gemini API напрямую."""
    if not GEMINI_API_KEY:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash") # gemini-2.0 is deprecated for new users
        chat = model.start_chat(history=history or [])
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        print(f"⚠️ Gemini Direct failed: {e}")
        return None


def _call_openrouter(prompt, history=None, temperature=0.7):
    """Вызов через OpenRouter (работает из любого региона)."""
    if not OPENROUTER_KEY:
        return None

    messages = []
    if history:
        for msg in history:
            role = "assistant" if msg.get("role") == "model" else msg.get("role", "user")
            content = msg.get("parts", [msg.get("content", "")])[0] if isinstance(msg.get("parts"), list) else msg.get("content", "")
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": prompt})

    or_models = [
        "moonshotai/kimi-k2.6", # 🚀 Kimi K2.6 - Новейшая имба
        "google/gemini-2.5-flash",
        "google/gemini-flash-1.5",
        "openrouter/auto",
    ]

    for model_name in or_models:
        try:
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model_name,
                    "messages": messages,
                    "temperature": temperature,
                },
                timeout=30,
                proxies={"http": "", "https": ""} # OpenRouter не может идти через наш прокси
            )
            data = resp.json()
            if "choices" in data:
                return data["choices"][0]["message"]["content"]
            else:
                print(f"⚠️ OpenRouter {model_name}: {data.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"⚠️ OpenRouter {model_name} exception: {e}")

    return None


def _call_ollama_local(prompt, history=None, temperature=0.7):
    """Оффлайн-фоллбэк через Ollama."""
    try:
        messages = []
        if history:
            for msg in history:
                role = "assistant" if msg.get("role") == "model" else msg.get("role", "user")
                content = msg.get("parts", [msg.get("content", "")])[0] if isinstance(msg.get("parts"), list) else msg.get("content", "")
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": prompt})

        resp = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": False,
                "options": {"temperature": temperature},
            },
            timeout=120,
        )
        data = resp.json()
        if "message" in data and "content" in data["message"]:
            print(f"✅ Ollama/{OLLAMA_MODEL} ответила (offline mode)")
            return data["message"]["content"]
        return None
    except requests.exceptions.ConnectionError:
        print(f"⚠️ Ollama не запущена ({OLLAMA_URL} недоступен)")
        return None
    except Exception as e:
        print(f"⚠️ Ollama/{OLLAMA_MODEL} failed: {e}")
        return None


def call_llm(prompt, history=None, temperature=0.7):
    """
    Каскадный вызов LLM.
    Gemini Direct → OpenRouter → Ollama (offline).
    """
    # 1. OpenRouter (основной)
    result = _call_openrouter(prompt, history, temperature)
    if result:
        return result

    # 2. Gemini Direct (бэкап)
    result = _call_gemini_direct(prompt, history, temperature)
    if result:
        return result

    # 3. Ollama (оффлайн-страховка)
    print("🔌 Облачные модели недоступны. Переключаюсь на Ollama...")
    result = _call_ollama_local(prompt, history, temperature)
    if result:
        return result

    return "⚠️ Все LLM-провайдеры недоступны. Повторите позже."


def call_llm_structured(system_prompt, user_prompt, history=None, temperature=0.5):
    """
    Вызов LLM со структурированным системным промптом.
    Для аналитических задач используем пониженную temperature.
    """
    full_prompt = f"{system_prompt}\n\n---\n\nЗАДАЧА:\n{user_prompt}"
    return call_llm(full_prompt, history, temperature)
