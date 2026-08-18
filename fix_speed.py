import sqlite3

def fix_speed():
    with open("bot.py", "r", encoding="utf-8") as f:
        content = f.read()

    target = """def update_bot_group(chat_id: int, title: str, username: str, is_active: int):
    with closing(sqlite3.connect(DB_FILE)) as conn:"""
    
    replacement = """_seen_groups_cache = set()

def update_bot_group(chat_id: int, title: str, username: str, is_active: int):
    global _seen_groups_cache
    if is_active == 1 and chat_id in _seen_groups_cache:
        return
    if is_active == 1:
        _seen_groups_cache.add(chat_id)
    elif chat_id in _seen_groups_cache:
        _seen_groups_cache.discard(chat_id)

    with closing(sqlite3.connect(DB_FILE)) as conn:"""
    
    if "_seen_groups_cache" not in content:
        content = content.replace(target, replacement)
        with open("bot.py", "w", encoding="utf-8") as f:
            f.write(content)
        print("Fixed bot.py speed")

fix_speed()

