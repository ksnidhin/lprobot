import sqlite3

def patch():
    with open("bot.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    schema_target = "CREATE TABLE IF NOT EXISTS bot_settings ("
    schema_replacement = """CREATE TABLE IF NOT EXISTS bot_groups (
    chat_id INTEGER PRIMARY KEY,
    title TEXT,
    username TEXT,
    is_active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS bot_settings ("""
    if "CREATE TABLE IF NOT EXISTS bot_groups" not in content:
        content = content.replace(schema_target, schema_replacement)
    
    helpers_target = "def _is_owner(user_id: int) -> bool:"
    helpers_replacement = """def update_bot_group(chat_id: int, title: str, username: str, is_active: int):
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with closing(conn.cursor()) as c:
            c.execute(
                "INSERT INTO bot_groups (chat_id, title, username, is_active) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(chat_id) DO UPDATE SET title=excluded.title, username=excluded.username, is_active=excluded.is_active",
                (chat_id, title, username, is_active)
            )
        conn.commit()

def get_active_bot_groups():
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with closing(conn.cursor()) as c:
            c.execute("SELECT chat_id, title, username FROM bot_groups WHERE is_active=1 ORDER BY title")
            return c.fetchall()

def _is_owner(user_id: int) -> bool:"""
    if "update_bot_group(" not in content:
        content = content.replace(helpers_target, helpers_replacement)
        
    msg_target = """async def on_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    if not msg:
        return"""
    msg_replacement = """async def on_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    if not msg:
        return
    if msg.chat.type in ["group", "supergroup"]:
        update_bot_group(msg.chat.id, msg.chat.title, msg.chat.username, 1)"""
    if "msg.chat.type in [\"group\", \"supergroup\"]" not in content:
        content = content.replace(msg_target, msg_replacement)

    media_target = """async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    if not msg:
        return"""
    media_replacement = """async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    if not msg:
        return
    if msg.chat.type in ["group", "supergroup"]:
        update_bot_group(msg.chat.id, msg.chat.title, msg.chat.username, 1)"""
    content = content.replace(media_target, media_replacement)

    chat_member_code = """
async def chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    \"\"\"Track bot being added or removed from groups.\"\"\"
    result = update.my_chat_member
    if not result:
        return
    chat = result.chat
    if chat.type not in ["group", "supergroup"]:
        return
    
    status = result.new_chat_member.status
    if status in ["kicked", "left"]:
        update_bot_group(chat.id, chat.title, chat.username, 0)
    elif status in ["member", "administrator"]:
        update_bot_group(chat.id, chat.title, chat.username, 1)

"""
    handler_target = "app.add_handler(CommandHandler(\"en\", cmd_en))"
    handler_replacement = "app.add_handler(CommandHandler(\"en\", cmd_en))\n    app.add_handler(ChatMemberHandler(chat_member_update, ChatMemberHandler.MY_CHAT_MEMBER))"
    if "chat_member_update" not in content:
        content = content.replace(handler_target, handler_replacement)
        main_target = "def main() -> None:"
        content = content.replace(main_target, chat_member_code + "def main() -> None:")

    with open("bot.py", "w", encoding="utf-8") as f:
        f.write(content)

patch()

