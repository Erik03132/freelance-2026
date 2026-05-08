import re

path = "/root/antigravity/ai-eggs/agent/angelochka_core.py"
content = open(path, "r").read()

# Fix 1: расширяем проверку города
old_check = '        elif "город" in last_bot_msg or "количество" in last_bot_msg:'
new_check = '        elif any(w in last_bot_msg for w in ["город", "количество", "доставк", "населённ", "населенн", "куда"]):'

# Fix 2: улучшаем инструкцию
old_instr = 'ТВОЯ ЗАДАЧА СЕЙЧАС: Ты уже спросила про город/количество. Теперь дословно спроси: \xabКак я могу к Вам обращаться?\xbb \U0001F6AB КРИТИЧЕСКИЙ ЗАПРЕТ: НЕ ПОВТОРЯЙ ВОПРОС О ГОРОДЕ/КОЛИЧЕСТВЕ, НЕ НАЗЫВАЙ ЦЕНЫ ПОВТОРНО!'
new_instr = 'ТВОЯ ЗАДАЧА СЕЙЧАС: Ты уже спросила про город/доставку/количество. Клиент мог ответить на часть вопросов. Если он назвал город но не количество \u2014 спроси количество. Если назвал количество но не город \u2014 спроси город. Если оба уже известны \u2014 дословно спроси: \xabКак я могу к Вам обращаться?\xbb \U0001F6AB КРИТИЧЕСКИЙ ЗАПРЕТ: НЕ ПОВТОРЯЙ ВОПРОС НА КОТОРЫЙ КЛИЕНТ УЖЕ ОТВЕТИЛ!'

n = 0
if old_check in content:
    content = content.replace(old_check, new_check, 1)
    n += 1
    print(f"  [1] Check pattern replaced")

if old_instr in content:
    content = content.replace(old_instr, new_instr, 1)
    n += 1
    print(f"  [2] Instruction pattern replaced")

if n > 0:
    open(path, "w").write(content)
    print(f"✅ Fixed {n} patterns!")
else:
    print("❌ Patterns not found, debug:")
    lines = content.split("\n")
    for i, l in enumerate(lines[650:660], 651):
        print(f"  {i}: {repr(l[:120])}")
