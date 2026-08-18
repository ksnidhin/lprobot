import os
import sys
import logging
import asyncio

# Workaround for Pyrogram asyncio bug on Python 3.10+
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import MessageEntityType, ChatMemberStatus
import aiosqlite
from dotenv import load_dotenv

# Import logic from the main bot
from bot import LINK_REGEX, _normalize_for_link_scan
from userbot_ai_handler import cmd_ai, cmd_speak, cmd_roast, cmd_summary, check_auto_ai

load_dotenv()

API_ID_STR = os.getenv("API_ID", "0")
API_ID = int(API_ID_STR) if API_ID_STR else 0
API_HASH = os.getenv("API_HASH", "")
SQLITE_PATH = "data/bot_data.db"


if not API_ID or not API_HASH:
    sys.exit("ERROR: API_ID or API_HASH not set in .env")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("userbot")

app = Client("lalubot_userbot", api_id=API_ID, api_hash=API_HASH)
db_conn = None

async def setup_db():
    global db_conn
    db_conn = await aiosqlite.connect(SQLITE_PATH)
    db_conn.row_factory = aiosqlite.Row
    logger.info("Database connected.")

def contains_link(msg: Message) -> bool:
    """Check if the pyrogram message contains a link."""
    # Check entities
    entities = msg.entities or []
    if msg.caption_entities:
        entities.extend(msg.caption_entities)
    
    for ent in entities:
        if ent.type in (MessageEntityType.URL, MessageEntityType.TEXT_LINK):
            return True
            
    # Check text/caption with regex
    raw_text = msg.text or msg.caption or ""
    text = _normalize_for_link_scan(raw_text)
    if text and LINK_REGEX.search(text):
        return True
        
    # Check inline keyboards
    if msg.reply_markup and getattr(msg.reply_markup, "inline_keyboard", None):
        for row in msg.reply_markup.inline_keyboard:
            for button in row:
                if getattr(button, "url", None):
                    return True
                    
    return False

@app.on_message(filters.group & ~filters.me)
async def enforce_link_blacklist(client: Client, message: Message):
    if not db_conn:
        return
        
    sender = message.from_user
    if not sender:
        return
    
    # We query the link_blacklist table directly
    async with db_conn.execute(
        "SELECT 1 FROM link_blacklist WHERE chat_id = ? AND user_id = ?",
        (message.chat.id, sender.id)
    ) as cursor:
        row = await cursor.fetchone()
        if not row:
            return
            
    # Sender is blacklisted in this chat. Check for links.
    if not contains_link(message):
        return
        
    try:
        await message.delete()
        logger.info(f"Deleted link from blacklisted user {sender.id} in chat {message.chat.id}")
    except Exception as e:
        logger.error(f"Failed to delete message: {e}")

@app.on_message(filters.command("banall", prefixes="/") & filters.me & filters.group)
async def cmd_banall(client: Client, message: Message):
    import datetime
    if message.date:
        now = datetime.datetime.now(datetime.timezone.utc)
        if (now - message.date).total_seconds() > 120:
            return
            
    if not db_conn:
        await message.reply_text("Database not connected.")
        return
        
    chat_id = message.chat.id
    status_msg = await message.reply_text("Fetching member list... this may take a moment.")
    
    to_ban = []
    try:
        async for member in app.get_chat_members(chat_id):
            if member.user.is_bot or member.user.is_deleted:
                continue
            if member.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR):
                continue
                
            to_ban.append(member.user.id)
            
        if not to_ban:
            await status_msg.edit_text("No non-admin members found to ban.")
            return
            
        await status_msg.edit_text(f"Found {len(to_ban)} members to ban. Pushing to main bot's ban queue...")
        
        for uid in to_ban:
            await db_conn.execute(
                "INSERT OR IGNORE INTO ban_queue (chat_id, user_id) VALUES (?, ?)", 
                (chat_id, uid)
            )
        await db_conn.commit()
        
        await status_msg.edit_text(f"✅ Successfully queued {len(to_ban)} members for banning! The main bot will begin executing the bans now in the background.")
        
    except Exception as e:
        logger.error(f"Error in /banall: {e}")
        await status_msg.edit_text(f"Error fetching members: {e}")


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

if __name__ == "__main__":
    app.loop.run_until_complete(setup_db())
    logger.info("Starting userbot... (First run may prompt for login)")
    app.run()
