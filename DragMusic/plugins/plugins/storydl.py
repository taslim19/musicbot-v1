"""
/story <username or userid> <story_id>

Download a Telegram story (video or photo) from a user by username/userid and story id, using the userbot. The story will be sent to the chat where the command was used.

Example:
/story @Itzabhi16 1
/story 123456789 2
"""

import tempfile
import os
from pyrogram import filters
from pyrogram.types import Message
from DragMusic import userbot, app

@app.on_message(filters.command("story", prefixes=["/", "!"]))
async def story_download_handler(client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text("Usage: /story <username or userid> <story_id>")
    target = message.command[1]
    try:
        story_id = int(message.command[2])
    except ValueError:
        return await message.reply_text("Story ID must be an integer.")
    try:
        stories = await userbot.one.get_stories(target, [story_id])
        # If only one story is returned, wrap in a list for uniformity
        if not isinstance(stories, list):
            stories = [stories]
        sent = False
        for s in stories:
            temp_dir = tempfile.gettempdir()
            if hasattr(s, "video") and s.video:
                file = await userbot.one.download_media(s.video.file_id, file_name=os.path.join(temp_dir, f"story_{s.id}.mp4"))
                await userbot.one.send_video(message.chat.id, file, caption=f"Story ID: {s.id}")
                sent = True
            elif hasattr(s, "photo") and s.photo:
                file = await userbot.one.download_media(s.photo.file_id, file_name=os.path.join(temp_dir, f"story_{s.id}.jpg"))
                await userbot.one.send_photo(message.chat.id, file, caption=f"Story ID: {s.id}")
                sent = True
        if sent:
            await message.reply_text("Story sent to this chat!")
        else:
            await message.reply_text("No video or photo found in the specified story.")
    except Exception as e:
        await message.reply_text(f"Failed to download story: {e}") 