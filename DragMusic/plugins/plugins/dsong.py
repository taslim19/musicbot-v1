import os
import tempfile
from datetime import timedelta
from pyrogram.enums import ParseMode
import httpx
from pyrogram import filters
from pyrogram.types import Message
from DragMusic import app
from DragMusic.platforms.Youtube import YouTubeAPI
from config import BITFLOW_API_KEY

@app.on_message(filters.command(["vsong"]))
async def vsong_cmd(client, message):
    """Command to download and send a YouTube video using Bitflow API."""
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ <b>Video not found,</b>\nPlease enter the correct video title.",
        )
    infomsg = await message.reply_text("<b>🔍 Searching...</b>", quote=False)
    query = message.text.split(None, 1)[1]
    try:
        bitflow = await YouTubeAPI().get_video_info_from_bitflow(query, video=True)
        if not bitflow or bitflow.get("status") != "success":
            return await infomsg.edit("<b>🔍 Searching...\n\n No result from Bitflow API.</b>")
        url = bitflow["url"]
        title = bitflow.get("title", "Unknown")
        duration = bitflow.get("duration", 0)
        views = bitflow.get("views", 0)
        channel = bitflow.get("channel", "Unknown")
        thumb = bitflow.get("thumbnail", None)
        ext = bitflow.get("ext", "mp4")
    except Exception as error:
        return await infomsg.edit(f"<b>🔍 Searching...\n\n{error}</b>")

    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"{title}.{ext}")
    try:
        await infomsg.edit("<b>Downloading video...</b>")
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            with open(file_path, "wb") as f:
                f.write(r.content)
        thumbnail_path = None
        if thumb:
            thumb_path = os.path.join(temp_dir, f"{title}_thumb.jpg")
            async with httpx.AsyncClient() as client:
                r = await client.get(thumb)
                with open(thumb_path, "wb") as f:
                    f.write(r.content)
            thumbnail_path = thumb_path
        await message.reply_video(
            video=file_path,
            thumb=thumbnail_path,
            duration=duration,
            supports_streaming=True,
            caption=(
                f"<blockquote><b> Information {title}</b></blockquote>\n\n"
                f"<blockquote><b> Name:</b> {title}\n"
                f"<b> Duration:</b> {timedelta(seconds=duration)}\n"
                f"<b> Views:</b> {views:,}\n"
                f"<b> Channel:</b> {channel}\n"
                f"<b> Link:</b> <a href='{url}'>YouTube</a></blockquote>\n\n"
                f"<blockquote><b>⚡ Powered by: @dragbotsupport</b></blockquote> "
            ),
            reply_to_message_id=message.id,
        )
    finally:
        if 'thumbnail_path' in locals() and thumbnail_path and os.path.isfile(thumbnail_path):
            os.remove(thumbnail_path)
        if file_path and os.path.isfile(file_path):
            os.remove(file_path)
    await infomsg.delete()

@app.on_message(filters.command(["song"]))
async def song_cmd(client, message):
    """Command to download and send a YouTube audio file using Bitflow API."""
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ <b>Audio not found,</b>\nPlease enter the correct audio title.",
        )
    infomsg = await message.reply_text("<b>🔍 Searching...</b>", quote=False)
    query = message.text.split(None, 1)[1]
    try:
        bitflow = await YouTubeAPI().get_video_info_from_bitflow(query, video=False)
        if not bitflow or bitflow.get("status") != "success":
            return await infomsg.edit("<b>🔍 Searching...\n\nNo result from Bitflow API.</b>")
        url = bitflow["url"]
        title = bitflow.get("title", "Unknown")
        duration = bitflow.get("duration", 0)
        views = bitflow.get("views", 0)
        channel = bitflow.get("channel", "Unknown")
        thumb = bitflow.get("thumbnail", None)
        ext = bitflow.get("ext", "mp3")
    except Exception as error:
        return await infomsg.edit(f"<b>🔍 Searching...\n\n{error}</b>")

    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"{title}.{ext}")
    try:
        await infomsg.edit("<b>Downloading audio...</b>")
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            with open(file_path, "wb") as f:
                f.write(r.content)
        thumbnail_path = None
        if thumb:
            thumb_path = os.path.join(temp_dir, f"{title}_thumb.jpg")
            async with httpx.AsyncClient() as client:
                r = await client.get(thumb)
                with open(thumb_path, "wb") as f:
                    f.write(r.content)
            thumbnail_path = thumb_path
        await message.reply_audio(
            audio=file_path,
            thumb=thumbnail_path,
            title=title,
            performer=channel,
            duration=duration,
            caption=(
                f"<blockquote><b> Information {title}</b></blockquote>\n\n"
                f"<blockquote><b> Name:</b> {title}\n"
                f"<b> Duration:</b> {timedelta(seconds=duration)}\n"
                f"<b> Views:</b> {views:,}\n"
                f"<b> Channel:</b> {channel}\n"
                f"<b> Link:</b> <a href='{url}'>YouTube</a></blockquote>\n\n"
                f"<blockquote><b>⚡ Powered by: @dragbotsupport</b></blockquote>"
            ),
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message.id,
        )
    finally:
        if 'thumbnail_path' in locals() and thumbnail_path and os.path.isfile(thumbnail_path):
            os.remove(thumbnail_path)
        if file_path and os.path.isfile(file_path):
            os.remove(file_path)
    await infomsg.delete()
