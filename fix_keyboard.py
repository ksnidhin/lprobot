import re

def fix():
    with open("bot.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Find the function definition
    match = re.search(r"def _get_main_keyboard\(\) -> InlineKeyboardMarkup:.*?\]\)", content, re.DOTALL)
    if match:
        old_func = match.group(0)
        # We can extract the emojis/text from old_func if needed, but since it is just 4 buttons,
        # we can just write the correct UTF-8 emojis.
        new_func = """def _get_main_keyboard(user_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton("✨ AI Features", callback_data="menu_ai"),
            InlineKeyboardButton("🛡️ Moderation", callback_data="menu_mod_1")
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings")
        ]
    ]
    if _is_owner(user_id):
        buttons.append([InlineKeyboardButton("📂 Active Groups", callback_data="menu_groups_0")])
    buttons.append([InlineKeyboardButton("❌ Close", callback_data="menu_close")])
    return InlineKeyboardMarkup(buttons)"""
        
        content = content.replace(old_func, new_func)
        
        # ensure menu_main passes user_id in button_callback_handler
        # the previous patch_ui did: keyboard = _get_main_keyboard(query.from_user.id)
        # let us ensure it is correct
        
        with open("bot.py", "w", encoding="utf-8") as f:
            f.write(content)
            print("Fixed _get_main_keyboard")
    else:
        print("Function not found")

fix()

