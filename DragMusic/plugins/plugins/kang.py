import imghdr
import os
from asyncio import gather
from traceback import format_exc

from pyrogram import filters
from pyrogram.errors import (
    PeerIdInvalid,
    ShortnameOccupyFailed,
    StickerEmojiInvalid,
    StickerPngDimensions,
    StickerPngNopng,
    UserIsBlocked,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.enums import ParseMode


from DragMusic import app
from config import BOT_USERNAME  # Still used elsewhere, but not for short name anymore
from DragMusic.utils.errors import capture_err
from DragMusic.utils.files import (
    get_document_from_file_id,
    resize_file_to_sticker_size,
    upload_document,
)
from DragMusic.utils.stickerset import (
    add_sticker_to_set,
    create_sticker,
    create_sticker_set,
    get_sticker_set_by_name,
)

MAX_STICKERS = 120
SUPPORTED_TYPES = ["jpeg", "png", "webp"]

@app.on_message(filters.command("get_sticker"))
@capture_err
async def sticker_image(_, message: Message):
    r = message.reply_to_message

    if not r:
        return await message.reply("Reply to a sticker.")

    if not r.sticker:
        return await message.reply("Reply to a sticker.")

    m = await message.reply("Sending..")
    f = await r.download(f"{r.sticker.file_unique_id}.png")

    await gather(
        *[
            message.reply_photo(f),
            message.reply_document(f),
        ]
    )

    await m.delete()
    os.remove(f)

@app.on_message(filters.command("kang"))
@capture_err
async def kang(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a sticker/image to kang it.")
    if not message.from_user:
        return await message.reply_text("You are anon admin, kang stickers in my PM.")

    msg = await message.reply_text("Kanging Sticker..")

    # Determine sticker emoji
    args = message.text.split()
    if len(args) > 1:
        sticker_emoji = str(args[1])
    elif message.reply_to_message.sticker and message.reply_to_message.sticker.emoji:
        sticker_emoji = message.reply_to_message.sticker.emoji
    else:
        sticker_emoji = "🤔"

    doc = message.reply_to_message.photo or message.reply_to_message.document
    try:
        if message.reply_to_message.sticker:
            sticker = await create_sticker(
                await get_document_from_file_id(
                    message.reply_to_message.sticker.file_id
                ),
                sticker_emoji,
            )
        elif doc:
            if doc.file_size > 10_000_000:
                return await msg.edit("File size too large.")

            temp_file_path = await app.download_media(doc)
            image_type = imghdr.what(temp_file_path)
            if image_type not in SUPPORTED_TYPES:
                return await msg.edit(f"Format not supported! ({image_type})")

            try:
                temp_file_path = await resize_file_to_sticker_size(temp_file_path)
            except OSError as e:
                await msg.edit_text("Something wrong happened while resizing.")
                raise Exception(f"Resize error at {temp_file_path}: {e}")

            sticker = await create_sticker(
                await upload_document(client, temp_file_path, message.chat.id),
                sticker_emoji,
            )
            if os.path.isfile(temp_file_path):
                os.remove(temp_file_path)
        else:
            return await msg.edit("Nope, can't kang that.")
    except ShortnameOccupyFailed:
        await message.reply_text("Change your Telegram name or username.")
        return
    except Exception as e:
        await message.reply_text(str(e))
        print(format_exc())
        return

    # --- LIVE BOT USERNAME & VALID SHORT_NAME ---
    me = await client.get_me()
    bot_username = me.username
    packnum = 0

    def sanitize_packname(uid: int, bot_username: str, packnum: int = 0) -> str:
        base = f"{'f' if packnum == 0 else f'f{packnum}_'}{uid}_by_{bot_username}"
        base = base.replace("__", "_").strip("_")
        if not base[0].isalpha():
            base = "a" + base
        return base

    packname = sanitize_packname(message.from_user.id, bot_username, packnum)
    limit = 0

    try:
        while True:
            if limit >= 50:
                return await msg.delete()

            print(f"[DEBUG] packname: {packname}")
            print(f"[DEBUG] bot_username: {bot_username}")

            stickerset = await get_sticker_set_by_name(client, packname)
            if not stickerset:
                stickerset = await create_sticker_set(
                    client,
                    message.from_user.id,
                    f"{message.from_user.first_name[:32]}'s kang pack",
                    packname,
                    [sticker],
                )
            elif stickerset.set.count >= MAX_STICKERS:
                packnum += 1
                packname = sanitize_packname(
                    message.from_user.id, bot_username, packnum
                )
                limit += 1
                continue
            else:
                try:
                    await add_sticker_to_set(client, stickerset, sticker)
                except StickerEmojiInvalid:
                    return await msg.edit("[ERROR]: INVALID_EMOJI_IN_ARGUMENT")

            limit += 1
            break

        await msg.edit(
            f"Sticker Kanged To <a href='https://t.me/addstickers/{packname}'>Sticker Pack</a>\nEmoji: {sticker_emoji}",
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Sticker Pack", url=f"https://t.me/addstickers/{packname}")]
            ])
        )

    except (PeerIdInvalid, UserIsBlocked):
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Start", url=f"https://t.me/{bot_username}")]]
        )
        await msg.edit(
            "You Need To Start A Private Chat With Me.",
            reply_markup=keyboard,
        )
    except StickerPngNopng:
        await message.reply_text("Stickers must be PNG files but the provided image was not a PNG.")
    except StickerPngDimensions:
        await message.reply_text("The sticker PNG dimensions are invalid.")
