import sqlite3

def patch_ui():
    with open("bot.py", "r", encoding="utf-8") as f:
        content = f.read()

    kb_target = """def _get_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("? AI Features", callback_data="menu_ai"),
            InlineKeyboardButton("??? Moderation", callback_data="menu_mod_1")
        ],
        [
            InlineKeyboardButton("?? Settings", callback_data="menu_settings")
        ],
        [
            InlineKeyboardButton("? Close", callback_data="menu_close")
        ]
    ])"""
    kb_replacement = """def _get_main_keyboard(user_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton("? AI Features", callback_data="menu_ai"),
            InlineKeyboardButton("??? Moderation", callback_data="menu_mod_1")
        ],
        [
            InlineKeyboardButton("?? Settings", callback_data="menu_settings")
        ]
    ]
    if _is_owner(user_id):
        buttons.append([InlineKeyboardButton("?? Active Groups", callback_data="menu_groups_0")])
    buttons.append([InlineKeyboardButton("? Close", callback_data="menu_close")])
    return InlineKeyboardMarkup(buttons)"""
    if "def _get_main_keyboard(user_id: int)" not in content:
        content = content.replace(kb_target, kb_replacement)

    start_target = "keyboard = _get_main_keyboard()"
    start_replacement = "keyboard = _get_main_keyboard(msg.from_user.id)"
    content = content.replace(start_target, start_replacement)

    cb_main_target = """if data == "menu_main":
        text = _get_start_text(query.from_user)
        keyboard = _get_main_keyboard()"""
    cb_main_replacement = """if data == "menu_main":
        text = _get_start_text(query.from_user)
        keyboard = _get_main_keyboard(query.from_user.id)"""
    content = content.replace(cb_main_target, cb_main_replacement)

    callbacks = """
    elif data.startswith("menu_groups_"):
        if not _is_owner(query.from_user.id):
            await query.answer("Owner only.", show_alert=True)
            return
        page = int(data.split("_")[2])
        groups = get_active_bot_groups()
        per_page = 10
        total_pages = max(1, (len(groups) + per_page - 1) // per_page)
        start_idx = page * per_page
        end_idx = start_idx + per_page
        page_groups = groups[start_idx:end_idx]
        
        text = f"?? **Active Groups** (Page {page+1}/{total_pages})\\n\\nSelect a group to manage:"
        keyboard_buttons = []
        for chat_id, title, username in page_groups:
            display_title = title if title else str(chat_id)
            keyboard_buttons.append([InlineKeyboardButton(display_title, callback_data=f"group_view_{chat_id}")])
            
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("?? Prev", callback_data=f"menu_groups_{page-1}"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("Next ??", callback_data=f"menu_groups_{page+1}"))
            
        if nav_buttons:
            keyboard_buttons.append(nav_buttons)
        keyboard_buttons.append([InlineKeyboardButton("?? Back", callback_data="menu_main")])
        
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard_buttons), parse_mode=ParseMode.MARKDOWN)

    elif data.startswith("group_view_"):
        if not _is_owner(query.from_user.id):
            await query.answer("Owner only.", show_alert=True)
            return
        chat_id = int(data.split("group_view_")[1])
        groups = get_active_bot_groups()
        group_info = next((g for g in groups if g[0] == chat_id), None)
        if not group_info:
            await query.answer("Group not found.", show_alert=True)
            return
            
        title = group_info[1]
        username = group_info[2]
        
        text = f"?? **Group Info**\\n\\n**Title:** {title}\\n**ID:** `{chat_id}`"
        if username:
            text += f"\\n**Username:** @{username}"
            
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("?? Leave Group", callback_data=f"group_leave_{chat_id}")],
            [InlineKeyboardButton("?? Back to Groups", callback_data="menu_groups_0")]
        ])
        await query.edit_message_text(text=text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

    elif data.startswith("group_leave_"):
        if not _is_owner(query.from_user.id):
            await query.answer("Owner only.", show_alert=True)
            return
        chat_id = int(data.split("group_leave_")[1])
        try:
            await context.bot.leave_chat(chat_id)
            update_bot_group(chat_id, "", "", 0)
            await query.answer("Left group successfully.", show_alert=True)
            # go back to groups list
            groups = get_active_bot_groups()
            per_page = 10
            total_pages = max(1, (len(groups) + per_page - 1) // per_page)
            text = f"?? **Active Groups** (Page 1/{total_pages})\\n\\nSelect a group to manage:"
            keyboard_buttons = []
            for cid, title, username in groups[:10]:
                display_title = title if title else str(cid)
                keyboard_buttons.append([InlineKeyboardButton(display_title, callback_data=f"group_view_{cid}")])
            if total_pages > 1:
                keyboard_buttons.append([InlineKeyboardButton("Next ??", callback_data="menu_groups_1")])
            keyboard_buttons.append([InlineKeyboardButton("?? Back", callback_data="menu_main")])
            await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard_buttons), parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            await query.answer(f"Failed to leave: {e}", show_alert=True)

"""
    cb_target = "if data == \"menu_close\":"
    if "menu_groups_" not in content:
        content = content.replace(cb_target, callbacks + "    if data == \"menu_close\":")

    with open("bot.py", "w", encoding="utf-8") as f:
        f.write(content)

patch_ui()

