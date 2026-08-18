
with open("userbot.py", "r", encoding="utf-8") as f:
    content = f.read()

if "from userbot_ai_handler import" not in content:
    content = content.replace("from bot import LINK_REGEX", "from bot import LINK_REGEX\nfrom userbot_ai_handler import cmd_ai, cmd_speak, cmd_roast, cmd_summary, check_auto_ai")
    
    handlers = """
@app.on_message(filters.command("ai", prefixes="/") & filters.me)
async def ai_handler(client, message):
    await cmd_ai(client, message)

@app.on_message(filters.command("speak", prefixes="/") & filters.me)
async def speak_handler(client, message):
    await cmd_speak(client, message)

@app.on_message(filters.command("roast", prefixes="/") & filters.me)
async def roast_handler(client, message):
    await cmd_roast(client, message)

@app.on_message(filters.command("summary", prefixes="/") & filters.me)
async def summary_handler(client, message):
    await cmd_summary(client, message)

@app.on_message(filters.text & ~filters.me, group=1)
async def auto_ai_handler(client, message):
    await check_auto_ai(client, message)
"""
    content = content.replace("if __name__ == \"__main__\":", handlers + "\nif __name__ == \"__main__\":")
    
    with open("userbot.py", "w", encoding="utf-8") as f:
        f.write(content)

