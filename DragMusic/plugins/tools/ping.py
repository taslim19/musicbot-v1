from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message

from DragMusic import app
from DragMusic.core.call import Drag
from DragMusic.utils.decorators.language import language
from DragMusic.utils.inline.extras import supp_markup
from DragMusic.utils.sys import bot_sys_stats
from config import BANNED_USERS, PING_IMG_URL, lyrical


@app.on_message(filters.command(["ping", "alive"]) & ~BANNED_USERS)
@language
async def ping_com(client, message: Message, _):
    print(f"Ping command triggered by user {message.from_user.id}")
    try:
        start = datetime.now()
        print("Sending initial photo response...")
        response = await message.reply_photo(
            photo=PING_IMG_URL,
            caption=_["ping_1"].format(app.mention),
        )
        print("Getting pytgping...")
        pytgping = await Drag.ping()
        print("Getting system stats...")
        UP, CPU, RAM, DISK = await bot_sys_stats()
        resp = (datetime.now() - start).microseconds / 1000
        print("Editing response...")
        await response.edit_text(
            _["ping_2"].format(resp, app.mention, UP, RAM, CPU, DISK, pytgping),
            reply_markup=supp_markup(_),
        )
        print("Ping command completed successfully")
    except Exception as e:
        print(f"Error in ping command: {e}")
        await message.reply_text(f"Error in ping command: {e}")
