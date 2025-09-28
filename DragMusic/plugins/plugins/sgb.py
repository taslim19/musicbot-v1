import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw.functions.messages import DeleteHistory
from DragMusic import userbot as us, app
from DragMusic.core.userbot import assistants

@app.on_message(filters.command(["sg", "sgb"], prefixes=["/", "!", ".", "-"]))
async def sg(client: Client, message: Message):
    if not message:
        return  

    # Determine target user from command or reply
    if message.reply_to_message:
        target = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        target = message.command[1]  # Extract the username or ID from the command
    else:
        return await message.reply("ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ, ᴜsᴇʀ ɪᴅ, ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ.")

    # Indicate processing
    lol = await message.reply("<b>ᴘʀᴏᴄᴇssɪɴɢ...</b>")
    for i in range(3):
        await asyncio.sleep(0.5)
        await lol.edit("<b>ᴘʀᴏᴄᴇssɪɴɢ" + "." * (i + 1) + "</b>")

    try:
        # Resolve the target user
        user = await client.get_users(target)
    except Exception as e:
        return await lol.edit(f"<b>Invalid user: {e}</b>")

    # Pick a bot randomly
    bots = ["sangmata_bot", "sangmata_beta_bot"]
    sg_bot = random.choice(bots)

    # Select the userbot
    if 1 in assistants:
        ubot = us.one
    else:
        return await lol.edit("<b>No available assistant bot found.</b>")

    try:
        # Send the ID or username to the Sangmata bot
        bot_message = await ubot.send_message(sg_bot, f"{user.id}")
        await bot_message.delete()  # Delete the sent message to avoid clutter
    except Exception as e:
        return await lol.edit(f"Error while sending message to Sangmata bot: {e}")

    await asyncio.sleep(1)

    # Retrieve Sangmata's response
    async for stalk in ubot.search_messages(sg_bot):
        if stalk.text:
            await message.reply(f"{stalk.text}")
            break
    else:
        await message.reply("ᴛʜᴇ ʙᴏᴛ ɪs ᴜɴʀᴇsᴘᴏɴsɪᴠᴇ.")

    # Delete Sangmata's chat history for privacy
    try:
        user_info = await ubot.resolve_peer(sg_bot)
        await ubot.send(DeleteHistory(peer=user_info, max_id=0, revoke=True))
    except Exception:
        pass

    await lol.delete()
