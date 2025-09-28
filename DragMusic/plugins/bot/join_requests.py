from DragMusic import app
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions

# A dictionary to store the message ID of the join request notification
join_request_message = {}

@app.on_chat_join_request()
async def D_A_X_X(_, message):
    try:
        chat = message.chat
        user = message.from_user
        
        # Check if the bot is an admin in the chat
        bot_member = await app.get_chat_member(chat.id, (await app.get_me()).id)
        if not bot_member.privileges.can_invite_users:
            # Silently ignore if the bot can't manage join requests
            return

        # Send join request notification to the group
        msg = await app.send_message(
            chat.id,
            f"""
ɴᴇᴡ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ
            
ᴜsᴇʀ : {user.mention}
ᴜsᴇʀɴᴀᴍᴇ : @{user.username}
ᴜsᴇʀ ɪᴅ : {user.id}
            """,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "ᴀᴘᴘʀᴏᴠᴇ", callback_data=f"j_approve_{chat.id}_{user.id}"
                        ),
                        InlineKeyboardButton(
                            "ʀᴇᴊᴇᴄᴛ", callback_data=f"j_reject_{chat.id}_{user.id}"
                        ),
                    ]
                ]
            ),
        )
        join_request_message[user.id] = msg.id

    except Exception as e:
        print(f"Error in chat_join_request handler: {e}")

async def is_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.privileges is not None
    except Exception:
        return False

@app.on_callback_query(filters.regex("j_approve_(.*)"))
async def approve_request(_, query):
    try:
        chat_id, user_id = query.data.split("_")[2:]
        chat_id = int(chat_id)
        user_id = int(user_id)

        user_who_pressed = query.from_user

        if not await is_admin(chat_id, user_who_pressed.id):
            await query.answer("ᴛʜɪs ɪs ɴᴏᴛ ғᴏʀ ʏᴏᴜ.", show_alert=True)
            return

        await app.approve_chat_join_request(chat_id, user_id)
        
        original_message_id = join_request_message.pop(user_id, None)
        if original_message_id:
            original_message = await app.get_messages(chat_id, original_message_id)
            await original_message.edit_text(
                f"{original_message.text}\n\n**sᴛᴀᴛᴜs :** ᴀᴘᴘʀᴏᴠᴇᴅ ✅\n**ʙʏ :** {user_who_pressed.mention}"
            )
    except Exception as e:
        await query.answer(f"An error occurred: {e}", show_alert=True)
        print(f"Error in approve_request handler: {e}")

@app.on_callback_query(filters.regex("j_reject_(.*)"))
async def reject_request(_, query):
    try:
        chat_id, user_id = query.data.split("_")[2:]
        chat_id = int(chat_id)
        user_id = int(user_id)
        
        user_who_pressed = query.from_user

        if not await is_admin(chat_id, user_who_pressed.id):
            await query.answer("ᴛʜɪs ɪs ɴᴏᴛ ғᴏʀ ʏᴏᴜ.", show_alert=True)
            return

        await app.decline_chat_join_request(chat_id, user_id)

        original_message_id = join_request_message.pop(user_id, None)
        if original_message_id:
            original_message = await app.get_messages(chat_id, original_message_id)
            await original_message.edit_text(
                f"{original_message.text}\n\n**sᴛᴀᴛᴜs :** ʀᴇᴊᴇᴄᴛᴇᴅ ❌\n**ʙʏ :** {user_who_pressed.mention}"
            )
    except Exception as e:
        await query.answer(f"An error occurred: {e}", show_alert=True)
        print(f"Error in reject_request handler: {e}") 