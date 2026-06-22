# Telegram Bot Architecture & Patterns

## Architecture overview
```
User → Telegram API
        ↓
    Bot Handler (polling/webhook)
        ↓
    Router (по командам/состояниям)
        ↓
    LLM API (Gemini/GPT) / CRM
        ↓
    Response → User
```

## Best Practices

### 1. Error Handling
Всегда оборачивай handler в try/except:
```python
@router.message()
async def handle_message(message: Message):
    try:
        response = await get_ai_response(message.text)
        await message.answer(response)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        await message.answer("Произошла ошибка, попробуйте позже.")
```

### 2. Rate Limiting
Не больше 30 сообщений/сек в один чат.
Не больше 20 сообщений/мин в группу.
```python
from asyncio import Semaphore
semaphore = Semaphore(25)  # Ограничение параллельности

async def safe_send(chat_id, text):
    async with semaphore:
        await bot.send_message(chat_id, text)
```

### 3. Webhook vs Polling
| Метод | Когда использовать |
|-------|-------------------|
| **Polling** | Разработка, быстрый старт, нет SSL |
| **Webhook** | Production, высокая нагрузка, SSL обязателен |

### 4. FSM (Finite State Machine) для диалогов
```python
class OrderStates(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    confirm = State()

@router.message(OrderStates.waiting_phone)
async def process_phone(message: Message, state: FSMContext):
    if not validate_phone(message.text):
        await message.answer("Некорректный номер, попробуйте снова")
        return
    await state.update_data(phone=message.text)
    await state.set_state(OrderStates.confirm)
    await message.answer("Всё верно?")
```

## Security
- Храни `BOT_TOKEN` только в environment variables.
- Защищай API Webhook с помощью `X-Telegram-Bot-Api-Secret-Token`.
- Логируй события прозрачно, избегая PII.
