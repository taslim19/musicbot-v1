import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from DragMusic import LOGGER, app, userbot
from DragMusic.core.call import Drag
from DragMusic.misc import sudo
from DragMusic.plugins import ALL_MODULES
from DragMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("Assɪsᴛᴀɴᴛ ᴄʟɪᴇɴᴛ ᴠᴀʀɪᴀʙʟᴇs ɴᴏᴛ ᴅᴇғɪɴᴇᴅ, ᴇxɪᴛɪɴɢ...")
        exit()
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("DragMusic.plugins" + all_module)
    LOGGER("DragMusic.plugins").info("Sᴜᴄᴄᴇssғᴜʟʟʏ Iᴍᴘᴏʀᴛᴇᴅ Mᴏᴅᴜʟᴇs...")
    await userbot.start()
    await Drag.start()
    try:
        await Drag.stream_call("https://telegra.ph/file/cba632240b79207bf8a9c.mp4")
    except NoActiveGroupCall:
        LOGGER("DragMusic").error(
            "Pʟᴇᴀsᴇ ᴛᴜʀɴ ᴏɴ ᴛʜᴇ ᴠɪᴅᴇᴏᴄʜᴀᴛ ᴏғ ʏᴏᴜʀ ʟᴏɢ ɢʀᴏᴜᴘ\ᴄʜᴀɴɴᴇʟ\n\nsᴛᴏᴘᴘɪɴɢ Bᴏᴛ..."
        )
        exit()
    except:
        pass
    await Drag.decorators()
    LOGGER("DragMusic").info("\n  𝑴𝑨𝑫𝑬 𝑩𝒀 𝑫𝑹𝑨𝑮𝑮𝑮 \n")
        
    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("DragMusic").info("\n  𝑴𝑨𝑫𝑬 𝑩𝒀 𝑫𝑹𝑨𝑮𝑮𝑮 \n")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
