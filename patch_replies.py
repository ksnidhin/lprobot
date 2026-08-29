
import re

with open("userbot_ai_handler.py", "r", encoding="utf-8") as f:
    text = f.read()

# Replace msg.reply_text with a try-except block globally
def replacer(match):
    indent = match.group(1)
    args = match.group(2)
    return f"{indent}try:\n{indent}    await msg.reply_text({args})\n{indent}except Exception as e:\n{indent}    try:\n{indent}        await client.send_message(msg.chat.id, {args})\n{indent}    except:\n{indent}        pass"

text = re.sub(r"^([ \t]+)await msg\.reply_text\((.*)\)", replacer, text, flags=re.MULTILINE)
text = text.replace("parse_mode=\"Markdown\"", "parse_mode=ParseMode.MARKDOWN")

with open("userbot_ai_handler.py", "w", encoding="utf-8") as f:
    f.write(text)

