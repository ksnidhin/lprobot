
import re
with open("userbot.py", "r", encoding="utf-8") as f:
    content = f.read()

# Remove & filters.me from commands
content = content.replace(" & filters.me)", ")")

# But wait, auto_ai_handler is: @app.on_message(filters.text & ~filters.me, group=1)
# That should stay ~filters.me so the bot doesn't reply to its OWN messages!

# Add /start command
start_cmd = """
@app.on_message(filters.command("start", prefixes="/"))
async def start_handler(client, message):
    text = (
        "🤖 **LaluBot (Userbot Mode)**\\n\\n"
        "This account is powered by AI. You can talk to me naturally, or use these commands:\\n\\n"
        "🎙️ `/speak <prompt>` - Generate a voice message\\n"
        "🔥 `/roast` - Roast someone\\n"
        "🧠 `/ai <prompt>` - Ask a direct question\\n"
        "📜 `/summary` - Summarize recent chat"
    )
    await message.reply_text(text)
"""

if "def start_handler" not in content:
    content = content.replace("@app.on_message(filters.command(\"ai\", prefixes=\"/\"))", start_cmd + "\n@app.on_message(filters.command(\"ai\", prefixes=\"/\"))")

with open("userbot.py", "w", encoding="utf-8") as f:
    f.write(content)

