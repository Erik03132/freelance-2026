import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import F
from dotenv import load_dotenv
import google.generativeai as genai
import psycopg2

# 1. Загрузка окружения
load_dotenv()
TELEGRAM_TOKEN = os.getenv("ANGELOCHKA_BOT_TOKEN")
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("NEON_DATABASE_URL")

# 2. Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 3. Инициализация ИИ (Gemini)
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

# 4. Загрузка "Прошивки" Анжелочки (Global Skill)
# Если файл недоступен (например на сервере), используем встроенный дефолт
SKILL_PATH = os.path.expanduser("~/.gemini/antigravity/skills/angelochka-sales/SKILL.md")
def get_system_prompt():
    try:
        with open(SKILL_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "Вы — Анжелочка, эксперт по инкубационным яйцам и кормам. Ваша цель: консультировать и продавать с заботой."

# 5. Функция поиска товаров в БД (RAG-подход)
def get_products_info(query):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        # Простой текстовый поиск по названию для MVP
        cur.execute("SELECT name, price, stock_status, description FROM products WHERE name ILIKE %s LIMIT 3", (f"%{query}%",))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        if rows:
            res = "\n".join([f"- {r[0]}: {r[1]} руб. ({r[2]}) - {r[3]}" for r in rows])
            return f"Данные из базы товаров:\n{res}"
        return "В базе данных по этому запросу ничего не найдено."
    except Exception as e:
        logger.error(f"DB Error: {e}")
        return "Ошибка доступа к базе товаров."

# 6. Бот
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привет! Я Анжелочка 🐣 Чем я могу вам помочь? У нас есть отличные инкубационные яйца и корма!")

@dp.message()
async def chat_handler(message: types.Message):
    user_text = message.text
    
    # Пытаемся найти товары, если клиент спрашивает про породы или цены
    product_context = ""
    keywords = ["цена", "почем", "есть", "наличии", "кобб", "росс", "индейка", "яйцо", "корм"]
    if any(k in user_text.lower() for k in keywords):
        product_context = get_products_info(user_text)

    # Формируем промпт для Gemini
    full_prompt = f"{get_system_prompt()}\n\n{product_context}\n\nКлиент: {user_text}\nАнжелочка:"
    
    try:
        response = await asyncio.to_thread(model.generate_content, full_prompt)
        await message.answer(response.text)
    except Exception as e:
        logger.error(f"AI Error: {e}")
        await message.answer("Ой, что-то я задумалась... Простите, повторите вопрос еще раз! 😊")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    if not TELEGRAM_TOKEN:
        print("ОШИБКА: Не установлен ANGELOCHKA_BOT_TOKEN в .env")
    else:
        asyncio.run(main())
