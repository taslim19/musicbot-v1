from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from DragMusic import app

@app.on_message(filters.command("id") & filters.group)
async def id_handler(client, message: Message):
    group_id = message.chat.id
    user = None
    show_group_id = False

    # Case 1: If replied to a user
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user

    # Case 2: If mentioned user with @username
    elif len(message.command) > 1:
        username = message.command[1].replace("@", "")
        try:
            user = await client.get_users(username)
        except Exception:
            return await message.reply_text("❌ Invalid username or user not found.")

    # Case 3: Just /id → show self and group ID
    else:
        user = message.from_user
        show_group_id = True

    user_id = user.id
    name = user.first_name or "Unknown"

    # Prepare text and buttons
    if show_group_id:
        text = (
            f"User:     {name}\\n"
            f"User ID:  {user_id}\\n"
            f"Group ID: {group_id}"
        )
        buttons = [
            [
                InlineKeyboardButton("Copy User ID", switch_inline_query=str(user_id)),
                InlineKeyboardButton("Copy Group ID", switch_inline_query=str(group_id)),
            ]
        ]
    else:
        text = f"User: {name}\\nUser ID: {user_id}"
        buttons = [[InlineKeyboardButton("Copy User ID", switch_inline_query=str(user_id))]]

    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons)) 