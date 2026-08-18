import re

def refactor():
    with open("userbot_ai_handler.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Imports
    content = content.replace("from telegram import Update, Message", "from pyrogram import Client\nfrom pyrogram.types import Message\nfrom pyrogram.enums import ChatAction, ParseMode")
    content = content.replace("from telegram.ext import ContextTypes", "")
    content = content.replace("from telegram.constants import ChatAction", "")

    # 2. Function Signatures
    content = re.sub(r"async def (cmd_\w+)\(update: Update, context: ContextTypes\.DEFAULT_TYPE\) -> None:", r"async def \1(client: Client, msg: Message) -> None:", content)
    content = re.sub(r"async def check_auto_ai\(update: Update, context: ContextTypes\.DEFAULT_TYPE\) -> None:", r"async def check_auto_ai(client: Client, msg: Message) -> None:", content)
    
    # 3. msg assignments
    content = content.replace("msg = update.effective_message", "")
    content = content.replace("if not msg:", "")
    content = content.replace("if not msg or (msg.from_user and msg.from_user.is_bot):", "if not msg or (msg.from_user and msg.from_user.is_bot):")

    # 4. attribute fixes
    content = content.replace("msg.chat_id", "msg.chat.id")
    content = content.replace("context.bot.username", "client.me.username")
    content = content.replace("context.bot.id", "client.me.id")
    content = content.replace("msg.reply_chat_action(\"record_voice\")", "pass")
    content = content.replace("msg.reply_chat_action(\"typing\")", "pass")
    content = content.replace("context.args", "msg.command[1:] if hasattr(msg, 'command') and msg.command else []")
    content = content.replace("msg.chat.type == 'private'", "msg.chat.type.name == 'PRIVATE'")

    # 5. `execute_moderation_tool`
    # We can just stub this or replace it because Userbot cannot do inline callbacks easily,
    # but userbot CAN ban/unban if it is admin.
    # For now, let's pass client instead of update, context
    content = content.replace("async def execute_moderation_tool(update, context, action, duration_minutes=0):", "async def execute_moderation_tool(client, msg, action, duration_minutes=0):")
    content = content.replace("await _check_and_execute_raw_tool_call(message.content or \"\", update, context)", "await _check_and_execute_raw_tool_call(message.content or \"\", client, msg)")
    content = content.replace("async def _check_and_execute_raw_tool_call(text: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:", "async def _check_and_execute_raw_tool_call(text: str, client: Client, msg: Message) -> str:")
    
    content = content.replace("await execute_moderation_tool(update, context, args.get(\"action\")", "await execute_moderation_tool(client, msg, args.get(\"action\")")
    
    # 6. file downloads (vision)
    # python-telegram-bot uses `await photo_file.download_to_memory(out)`
    # pyrogram uses `await client.download_media(msg, in_memory=True)`
    # This requires manual patching below.

    with open("userbot_ai_handler.py", "w", encoding="utf-8") as f:
        f.write(content)

refactor()

