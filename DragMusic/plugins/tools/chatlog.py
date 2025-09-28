from pyrogram import Client
from pyrogram.types import Message
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import LOGGER_ID as LOG_GROUP_ID
from DragMusic import app

@app.on_message(filters.new_chat_members, group=2)
async def join_watcher(_, message):    
    chat = message.chat
    link = await app.export_chat_invite_link(message.chat.id)
    for members in message.new_chat_members:
        if members.id == (await app.get_me()).id:
            count = await app.get_chat_members_count(chat.id)
            msg = (f"  ʙᴏᴛ ᴀᴅᴅᴇᴅ ɪɴ ᴀ ɴᴇᴡ ɢʀᴏᴜᴘ \n\n"
                   f" ɢʀᴏᴜᴘ ɴᴀᴍᴇ ➠ {message.chat.title}\n"
                   f" ɢʀᴏᴜᴘ ɪᴅ ➠ {message.chat.id}\n"
                   f" ɢʀᴏᴜᴘ ᴜsᴇʀɴᴀᴍᴇ ➠ @{message.chat.username if message.chat.username else 'Private'}\n"
                   f" ɢʀᴏᴜᴘ ʟɪɴᴋ ➠ [Click Here]({link})\n"
                   f" ɢʀᴏᴜᴘ ᴍᴇᴍʙᴇʀs ➠ {count}\n"
                   f" ᴀᴅᴅᴇᴅ ʙʏ ➠ {message.from_user.mention}")
            try:
                await app.send_message(
                    LOG_GROUP_ID,
                    text=msg,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"sᴇᴇ ʙᴏᴛ ᴀᴅᴅᴇᴅ ɢʀᴏᴜᴘ", url=f"{link}")]
                    ]),
                    message_thread_id=12279
                )
            except Exception as e:
                print(f"Error sending message: {e}")

@app.on_message(filters.left_chat_member)
async def on_left_chat_member(_, message: Message):
    if (await app.get_me()).id == message.left_chat_member.id:
        remove_by = message.from_user.mention if message.from_user else "𝐔ɴᴋɴᴏᴡɴ 𝐔sᴇʀ"
        title = message.chat.title
        username = f"@{message.chat.username}" if message.chat.username else "𝐏ʀɪᴠᴀᴛᴇ 𝐂ʜᴀᴛ"
        chat_id = message.chat.id
        left = (f"<b><u>ʙᴏᴛ ʟᴇғᴛ ɢʀᴏᴜᴘ </u></b> \n\n"
                f" ɢʀᴏᴜᴘ ɴᴀᴍᴇ ➠ {title}\n\n"
                f" ɢʀᴏᴜᴘ ɪᴅ ➠ {chat_id}\n\n"
                f" ʙᴏᴛ ʀᴇᴍᴏᴠᴇᴅ ʙʏ ➠ {remove_by}\n\n"
                f" ʙᴏᴛ ɴᴀᴍᴇ ➠ @{(await app.get_me()).username}")
        try:
            await app.send_message(
                LOG_GROUP_ID,
                text=left,
                message_thread_id=12279
            )
        except Exception as e:
            print(f"Error sending message: {e}")
