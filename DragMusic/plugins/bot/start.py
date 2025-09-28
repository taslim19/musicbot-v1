import asyncio
import time
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from DragMusic import app
from DragMusic.misc import _boot_
from DragMusic.plugins.sudo.sudoers import sudoers_list
from DragMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from DragMusic.utils.decorators.language import LanguageStart
from DragMusic.utils.formatters import get_readable_time
from DragMusic.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS, OWNER_ID
from strings import get_string


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)

    loading_1 = await message.reply_text("🔥")
    await asyncio.sleep(0.3)
    
    await loading_1.edit_text("<b>ʟᴏᴀᴅɪɴɢ</b>")
    await asyncio.sleep(0.2)
    await loading_1.edit_text("<b>ʟᴏᴀᴅɪɴɢ.</b>")
    await asyncio.sleep(0.1)
    await loading_1.edit_text("<b>ʟᴏᴀᴅɪɴɢ..</b>")
    await asyncio.sleep(0.1)
    await loading_1.edit_text("<b>ʟᴏᴀᴅɪɴɢ...</b>")
    await asyncio.sleep(0.1)
    await loading_1.delete()

    started_msg = await message.reply_text(text="<b>sᴛᴀʀᴛᴇᴅ...</b>")
    await asyncio.sleep(0.2)
    await started_msg.delete()

    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name.startswith("help"):
            keyboard = help_pannel(_)
            await message.reply_text(
                text=(
                    f"<b>ʏᴏᴏ {message.from_user.mention}, <a href='https://files.catbox.moe/w8m75t.jpg' target='_blank'>🫧</a></b>\n\n"
                    f"<b>ɪ'ᴍ {app.mention}</b>\n"
                    f"<b>ɪ ᴄᴀɴ sᴛʀᴇᴀᴍ ʜɪɢʜ-ǫᴜᴀʟɪᴛʏ ᴍᴜsɪᴄ ᴀɴᴅ ᴠɪᴅᴇᴏs ᴇғғᴏʀᴛʟᴇssʟʏ ᴡɪᴛʜ ᴛʜɪs ᴀᴅᴠᴀɴᴄᴇᴅ ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ.</b>\n\n"
                    f"<b>sʜᴀʀᴇ ᴛʀᴀᴄᴋs ᴀɴᴅ ᴄʀᴇᴀᴛᴇ ᴛʜᴇ ᴘᴇʀғᴇᴄᴛ ᴀᴛᴍᴏsᴘʜᴇʀᴇ ғᴏʀ ᴇᴠᴇʀʏ ᴄʜᴀᴛ.</b>"
                ),
                reply_markup=keyboard,
            )
        if name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} ᴄʜᴇᴄᴋᴇᴅ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n"
                         f"<b>• ɪᴅᴇɴᴛɪғɪᴇʀ ⌯</b> <code>{message.from_user.id}</code>\n"
                         f"<b>• ʜᴀɴᴅʟᴇ ⌯</b> @{message.from_user.username}",
                    message_thread_id=9,
                )
            return

        if name.startswith("inf"):
            m = await message.reply_text("⚡️")
            query = name.replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)

            next_result = await results.next()

            if isinstance(next_result, dict) and "result" in next_result:
                for result in next_result["result"]:
                    title = result["title"]
                    duration = result["duration"]
                    views = result["viewCount"]["short"]
                    thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                    channellink = result["channel"]["link"]
                    channel = result["channel"]["name"]
                    link = result["link"]
                    published = result["publishedTime"]
                    searched_text = _["start_6"].format(
                        title, duration, views, published, channellink, channel
                    )
                    key = InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="ʏᴏᴜᴛᴜʙᴇ", url=link)]]
                    )
                await m.delete()

                await app.send_photo(
                    chat_id=message.chat.id,
                    photo=thumbnail,
                    caption=searched_text,
                    reply_markup=key,
                )
                if await is_on_off(2):
                    await app.send_message(
                        chat_id=config.LOGGER_ID,
                        text=f"<b>{message.from_user.mention} ᴄʜᴇᴄᴋᴇᴅ ᴛʀᴀᴄᴋ ɪɴғᴏ.</b>\n\n"
                             f"<b>• ɪᴅᴇɴᴛɪғɪᴇʀ ⌯</b> <code>{message.from_user.id}</code>\n"
                             f"<b>• ʜᴀɴᴅʟᴇ ⌯</b> @{message.from_user.username}",
                        message_thread_id=9,
                    )
            else:
                await m.edit_text("ғᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴛʀɪᴇᴠᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ.")
                return
    else:
        out = private_panel(_)
        await message.reply_text(
            text=(
                 f"<b>ʏᴏᴏ {message.from_user.mention}, <a href='https://files.catbox.moe/w8m75t.jpg' target='_blank'>🫧</a></b>\n\n"
                 f"<b>ɪ'ᴍ {app.mention}</b>\n"
                 f"<b>ɪ ᴄᴀɴ sᴛʀᴇᴀᴍ ʜɪɢʜ-ǫᴜᴀʟɪᴛʏ ᴍᴜsɪᴄ ᴀɴᴅ ᴠɪᴅᴇᴏs ᴇғғᴏʀᴛʟᴇssʟʏ ᴡɪᴛʜ ᴛʜɪs ᴀᴅᴠᴀɴᴄᴇᴅ ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ.</b>\n\n"
                 f"<b>sʜᴀʀᴇ ᴛʀᴀᴄᴋs ᴀɴᴅ ᴄʀᴇᴀᴛᴇ ᴛʜᴇ ᴘᴇʀғᴇᴄᴛ ᴀᴛᴍᴏsᴘʜᴇʀᴇ ғᴏʀ ᴇᴠᴇʀʏ ᴄʜᴀᴛ.</b>"
            ),
            reply_markup=InlineKeyboardMarkup(out),
        )
        if await is_on_off(2):
            await app.send_message(
                chat_id=config.LOGGER_ID,
                text=f"<b>{message.from_user.mention} sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.</b>\n\n"
                     f"<b>• ɪᴅᴇɴᴛɪғɪᴇʀ ⌯</b> <code>{message.from_user.id}</code>\n"
                     f"<b>• ʜᴀɴᴅʟᴇ ⌯</b> @{message.from_user.username}",
                message_thread_id=9,
            )


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    await message.reply_text(
        text=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
    )
    await add_served_chat(message.chat.id)